"""CS2 Viewmodel Animation Engine and State Machine.

Parses glTF/GLB models and animation clips extracted from CS2, evaluates
hierarchical bone transformations (SLERP/LERP), and manages viewmodel
states (Draw, Idle, Inspect, Light/Heavy Attack).
"""

from __future__ import annotations

import enum
import json
import math
import os
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class CSWeaponState(enum.Enum):
    IDLE = "idle"
    DRAWING = "drawing"
    INSPECTING = "inspecting"
    ATTACK_LIGHT = "attack_light"
    ATTACK_HEAVY = "attack_heavy"


def _read_glb(file_path: Path) -> Tuple[Dict[str, Any], bytes]:
    """Parse GLB container into JSON metadata and binary buffer chunk."""
    with open(file_path, "rb") as f:
        magic, version, length = struct.unpack("<4sII", f.read(12))
        if magic != b"glTF" or version != 2:
            raise ValueError(f"Invalid GLB file: {file_path}")

        chunk0_len, chunk0_type = struct.unpack("<I4s", f.read(8))
        if chunk0_type != b"JSON":
            raise ValueError(f"Expected JSON chunk, got {chunk0_type}")
        json_bytes = f.read(chunk0_len)
        gltf_dict = json.loads(json_bytes.decode("utf-8"))

        bin_data = b""
        if f.tell() < length:
            chunk1_hdr = f.read(8)
            if len(chunk1_hdr) == 8:
                chunk1_len, chunk1_type = struct.unpack("<I4s", chunk1_hdr)
                if chunk1_type == b"BIN\x00":
                    bin_data = f.read(chunk1_len)

    return gltf_dict, bin_data


def _slerp(q0: np.ndarray, q1: np.ndarray, t: float) -> np.ndarray:
    """Spherical linear interpolation between two quaternions [x, y, z, w]."""
    dot = np.dot(q0, q1)
    if dot < 0.0:
        q1 = -q1
        dot = -dot

    if dot > 0.9995:
        result = q0 + t * (q1 - q0)
        norm = np.linalg.norm(result)
        return result / (norm if norm > 1e-8 else 1.0)

    theta_0 = math.acos(np.clip(dot, -1.0, 1.0))
    theta = theta_0 * t
    sin_theta = math.sin(theta)
    sin_theta_0 = math.sin(theta_0)

    s0 = math.cos(theta) - dot * sin_theta / sin_theta_0
    s1 = sin_theta / sin_theta_0
    return (s0 * q0) + (s1 * q1)


def _quat_to_matrix(q: np.ndarray) -> np.ndarray:
    """Convert quaternion [x, y, z, w] to 3x3 rotation matrix."""
    x, y, z, w = q
    return np.array([
        [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
        [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)],
        [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)],
    ], dtype=np.float32)


@dataclass
class AnimationChannel:
    node_index: int
    path: str  # "translation", "rotation", "scale"
    times: np.ndarray  # float array
    values: np.ndarray  # (N, C) float array

    def sample(self, t: float) -> np.ndarray:
        if len(self.times) == 0:
            if self.path == "rotation":
                return np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)
            elif self.path == "scale":
                return np.array([1.0, 1.0, 1.0], dtype=np.float32)
            else:
                return np.array([0.0, 0.0, 0.0], dtype=np.float32)

        if t <= self.times[0]:
            return self.values[0]
        if t >= self.times[-1]:
            return self.values[-1]

        idx = np.searchsorted(self.times, t) - 1
        idx = max(0, min(idx, len(self.times) - 2))

        t0 = self.times[idx]
        t1 = self.times[idx + 1]
        factor = (t - t0) / (t1 - t0) if t1 > t0 else 0.0

        v0 = self.values[idx]
        v1 = self.values[idx + 1]

        if self.path == "rotation":
            return _slerp(v0, v1, factor)
        else:
            return v0 + factor * (v1 - v0)


@dataclass
class AnimationClip:
    name: str
    duration: float
    channels: List[AnimationChannel] = field(default_factory=list)


@dataclass
class BoneNode:
    name: str
    index: int
    parent_index: Optional[int]
    children_indices: List[int] = field(default_factory=list)
    local_translation: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    local_rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32))
    local_scale: np.ndarray = field(default_factory=lambda: np.ones(3, dtype=np.float32))


@dataclass
class SkeletonPose:
    bone_matrices: List[np.ndarray] = field(default_factory=list)


class CSWeaponAnimator:
    """Manages viewmodel skeleton hierarchy, animation sampling and state transitions."""

    def __init__(self) -> None:
        self.bones: List[BoneNode] = []
        self.bone_name_to_idx: Dict[str, int] = {}
        self.clips: Dict[str, AnimationClip] = {}
        self.state: CSWeaponState = CSWeaponState.IDLE
        self.current_time: float = 0.0
        self.active_clip_name: Optional[str] = None

    def load_model(self, glb_path: Path) -> None:
        """Parse nodes and bind pose from glTF/GLB model."""
        gltf, _ = _read_glb(glb_path)
        nodes = gltf.get("nodes", [])

        self.bones.clear()
        self.bone_name_to_idx.clear()

        # Build bones list
        for i, node in enumerate(nodes):
            name = node.get("name", f"bone_{i}")
            trans = np.array(node.get("translation", [0.0, 0.0, 0.0]), dtype=np.float32)
            rot = np.array(node.get("rotation", [0.0, 0.0, 0.0, 1.0]), dtype=np.float32)
            scale = np.array(node.get("scale", [1.0, 1.0, 1.0]), dtype=np.float32)

            b = BoneNode(
                name=name,
                index=i,
                parent_index=None,
                children_indices=node.get("children", []),
                local_translation=trans,
                local_rotation=rot,
                local_scale=scale,
            )
            self.bones.append(b)
            self.bone_name_to_idx[name] = i

        # Assign parent indices
        for i, bone in enumerate(self.bones):
            for child_idx in bone.children_indices:
                if 0 <= child_idx < len(self.bones):
                    self.bones[child_idx].parent_index = i

    def load_clip(self, clip_name: str, glb_path: Path) -> None:
        """Parse animation channels and keyframes from glTF/GLB clip."""
        gltf, bin_data = _read_glb(glb_path)
        anims = gltf.get("animations", [])
        if not anims:
            return

        accessors = gltf.get("accessors", [])
        buffer_views = gltf.get("bufferViews", [])

        clip_channels: List[AnimationChannel] = []
        max_duration = 0.0

        for anim in anims:
            samplers = anim.get("samplers", [])
            for ch in anim.get("channels", []):
                target = ch.get("target", {})
                node_idx = target.get("node", 0)
                path_type = target.get("path", "")
                sampler_idx = ch.get("sampler", 0)

                if sampler_idx >= len(samplers):
                    continue
                sampler = samplers[sampler_idx]
                in_idx = sampler.get("input")
                out_idx = sampler.get("output")

                if in_idx is None or out_idx is None:
                    continue

                in_acc = accessors[in_idx]
                out_acc = accessors[out_idx]

                count = in_acc.get("count", 0)
                if count == 0:
                    continue

                # Read timestamps
                in_bv = buffer_views[in_acc.get("bufferView", 0)]
                in_offset = in_bv.get("byteOffset", 0) + in_acc.get("byteOffset", 0)
                times = np.frombuffer(bin_data, dtype=np.float32, count=count, offset=in_offset)

                if len(times) > 0 and times[-1] > max_duration:
                    max_duration = float(times[-1])

                # Read values
                out_bv = buffer_views[out_acc.get("bufferView", 0)]
                out_offset = out_bv.get("byteOffset", 0) + out_acc.get("byteOffset", 0)
                dim = 4 if path_type == "rotation" else 3
                values = np.frombuffer(bin_data, dtype=np.float32, count=count * dim, offset=out_offset).reshape(-1, dim)

                clip_channels.append(
                    AnimationChannel(
                        node_index=node_idx,
                        path=path_type,
                        times=times,
                        values=values,
                    )
                )

        self.clips[clip_name] = AnimationClip(
            name=clip_name,
            duration=max_duration,
            channels=clip_channels,
        )

    def trigger_draw(self) -> None:
        self.state = CSWeaponState.DRAWING
        self.current_time = 0.0
        self.active_clip_name = "draw"

    def trigger_inspect(self) -> None:
        self.state = CSWeaponState.INSPECTING
        self.current_time = 0.0
        self.active_clip_name = "inspect"

    def trigger_attack_light(self) -> None:
        self.state = CSWeaponState.ATTACK_LIGHT
        self.current_time = 0.0
        self.active_clip_name = "attack_light" if "attack_light" in self.clips else "backstab"

    def trigger_attack_heavy(self) -> None:
        self.state = CSWeaponState.ATTACK_HEAVY
        self.current_time = 0.0
        self.active_clip_name = "backstab"

    def tick(self, dt: float) -> None:
        self.current_time += dt

        if self.state == CSWeaponState.DRAWING:
            dur = self.clips["draw"].duration if "draw" in self.clips else 1.0
            if self.current_time >= dur:
                self.state = CSWeaponState.IDLE
                self.current_time = 0.0
                self.active_clip_name = None

        elif self.state in (CSWeaponState.ATTACK_LIGHT, CSWeaponState.ATTACK_HEAVY):
            clip = self.clips.get(self.active_clip_name or "")
            dur = clip.duration if clip else 1.0
            if self.current_time >= dur:
                self.state = CSWeaponState.IDLE
                self.current_time = 0.0
                self.active_clip_name = None

        elif self.state == CSWeaponState.INSPECTING:
            clip = self.clips.get("inspect")
            if clip and clip.duration > 0.0:
                # Inspect loops continuously until interrupted
                if self.current_time >= clip.duration:
                    self.current_time = self.current_time % clip.duration

    def evaluate_pose(self, t: Optional[float] = None) -> SkeletonPose:
        """Evaluate world bone transform matrices at time t."""
        if t is None:
            t = self.current_time

        num_bones = len(self.bones)
        if num_bones == 0:
            return SkeletonPose()

        local_mats = [np.eye(4, dtype=np.float32) for _ in range(num_bones)]
        clip = self.clips.get(self.active_clip_name or "") if self.active_clip_name else None

        # Sample local transforms
        for b_idx, bone in enumerate(self.bones):
            trans = np.copy(bone.local_translation)
            rot = np.copy(bone.local_rotation)
            scale = np.copy(bone.local_scale)

            if clip:
                for ch in clip.channels:
                    if ch.node_index == b_idx:
                        sample_val = ch.sample(t)
                        if ch.path == "translation":
                            trans = sample_val
                        elif ch.path == "rotation":
                            rot = sample_val
                        elif ch.path == "scale":
                            scale = sample_val

            rot_m = _quat_to_matrix(rot)
            # 4x4 matrix = Translation * Rotation * Scale
            m = np.eye(4, dtype=np.float32)
            m[:3, :3] = rot_m * scale
            m[:3, 3] = trans
            local_mats[b_idx] = m

        # Compute model-space matrices by multiplying down hierarchy
        world_mats = [np.eye(4, dtype=np.float32) for _ in range(num_bones)]
        for b_idx in range(num_bones):
            bone = self.bones[b_idx]
            if bone.parent_index is None:
                world_mats[b_idx] = local_mats[b_idx]
            else:
                world_mats[b_idx] = world_mats[bone.parent_index] @ local_mats[b_idx]

        return SkeletonPose(bone_matrices=world_mats)
