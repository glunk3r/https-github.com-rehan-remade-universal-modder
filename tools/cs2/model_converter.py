"""CS2 Viewmodel 3D Model Converter and Package Builder.

Extracts vertices, normals, UVs, and indices from CS2 glTF/GLB models,
resolves node/bone associations, and serializes optimized binary viewmodel
packages (CSVM format) ready for D3D12 vertex/index buffer upload.
"""

from __future__ import annotations

import json
import os
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from tools.cs2.animator import _read_glb


@dataclass
class Vertex:
    pos: Tuple[float, float, float]
    uv: Tuple[float, float]
    normal: Tuple[float, float, float]
    joints: Optional[Tuple[int, int, int, int]] = None
    weights: Optional[Tuple[float, float, float, float]] = None


@dataclass
class MeshPrimitive:
    vertices: List[Vertex]
    indices: List[int]
    material_name: str = ""


@dataclass
class SubmeshRange:
    bone_name: str
    bone_index: int
    first_index: int
    index_count: int
    base_vertex: int


@dataclass
class CSViewModelPackage:
    submeshes: List[SubmeshRange]
    total_vertices: int
    total_indices: int


def _get_accessor_data(
    gltf: Dict[str, Any],
    bin_data: bytes,
    accessor_idx: Optional[int],
) -> Optional[np.ndarray]:
    """Extract typed numpy array from a glTF accessor."""
    if accessor_idx is None:
        return None

    accessors = gltf.get("accessors", [])
    if accessor_idx >= len(accessors):
        return None

    acc = accessors[accessor_idx]
    count = acc.get("count", 0)
    if count == 0:
        return None

    buffer_views = gltf.get("bufferViews", [])
    bv_idx = acc.get("bufferView")
    if bv_idx is None or bv_idx >= len(buffer_views):
        return None

    bv = buffer_views[bv_idx]
    offset = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    comp_type = acc.get("componentType")  # 5126=FLOAT, 5123=USHORT, 5125=UINT, 5121=UBYTE
    type_str = acc.get("type")  # SCALAR, VEC2, VEC3, VEC4

    type_dims = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
    dim = type_dims.get(type_str, 1)

    if comp_type == 5126:  # FLOAT
        dtype = np.float32
    elif comp_type == 5123:  # USHORT
        dtype = np.uint16
    elif comp_type == 5125:  # UINT
        dtype = np.uint32
    elif comp_type == 5121:  # UBYTE
        dtype = np.uint8
    else:
        dtype = np.float32

    total_elements = count * dim
    byte_length = total_elements * np.dtype(dtype).itemsize

    if offset + byte_length > len(bin_data):
        return None

    arr = np.frombuffer(bin_data, dtype=dtype, count=total_elements, offset=offset)
    if dim > 1:
        arr = arr.reshape(count, dim)
    return arr


def extract_mesh_primitives(glb_path: Path) -> List[MeshPrimitive]:
    """Parse all mesh primitives, vertices, normals, UVs and indices from GLB."""
    gltf, bin_data = _read_glb(glb_path)
    meshes = gltf.get("meshes", [])
    result: List[MeshPrimitive] = []

    for mesh in meshes:
        for prim in mesh.get("primitives", []):
            attrs = prim.get("attributes", {})
            pos_arr = _get_accessor_data(gltf, bin_data, attrs.get("POSITION"))
            if pos_arr is None or len(pos_arr) == 0:
                continue

            num_verts = len(pos_arr)
            norm_arr = _get_accessor_data(gltf, bin_data, attrs.get("NORMAL"))
            uv_arr = _get_accessor_data(gltf, bin_data, attrs.get("TEXCOORD_0"))
            joints_arr = _get_accessor_data(gltf, bin_data, attrs.get("JOINTS_0"))
            weights_arr = _get_accessor_data(gltf, bin_data, attrs.get("WEIGHTS_0"))

            # Extract indices
            idx_arr = _get_accessor_data(gltf, bin_data, prim.get("indices"))
            if idx_arr is not None:
                indices = [int(i) for i in idx_arr.flatten()]
            else:
                indices = list(range(num_verts))

            vertices: List[Vertex] = []
            for i in range(num_verts):
                pos = (float(pos_arr[i][0]), float(pos_arr[i][1]), float(pos_arr[i][2]))
                if norm_arr is not None:
                    normal = (float(norm_arr[i][0]), float(norm_arr[i][1]), float(norm_arr[i][2]))
                else:
                    normal = (0.0, 1.0, 0.0)

                if uv_arr is not None:
                    uv = (float(uv_arr[i][0]), float(uv_arr[i][1]))
                else:
                    uv = (0.0, 0.0)

                j_val = None
                if joints_arr is not None:
                    j_val = (int(joints_arr[i][0]), int(joints_arr[i][1]), int(joints_arr[i][2]), int(joints_arr[i][3]))

                w_val = None
                if weights_arr is not None:
                    w_val = (float(weights_arr[i][0]), float(weights_arr[i][1]), float(weights_arr[i][2]), float(weights_arr[i][3]))

                vertices.append(Vertex(pos=pos, uv=uv, normal=normal, joints=j_val, weights=w_val))

            result.append(MeshPrimitive(vertices=vertices, indices=indices))

    return result


def build_cs_viewmodel_package(
    knife_glb: Path,
    arms_glb: Optional[Path] = None,
    output_bin: Optional[Path] = None,
) -> CSViewModelPackage:
    """Pack butterfly knife and arm geometry into a unified CSVM binary package."""
    knife_prims = extract_mesh_primitives(knife_glb)
    if not knife_prims:
        raise ValueError(f"No mesh primitives found in {knife_glb}")

    gltf, _ = _read_glb(knife_glb)
    nodes = gltf.get("nodes", [])
    node_names = [n.get("name", "") for n in nodes]

    # Map butterfly parts to node indices
    # Key nodes: "blade", "front", "rear", "lock"
    part_keys = ["blade", "front", "rear", "lock"]
    submeshes: List[SubmeshRange] = []

    all_vertices: List[Vertex] = []
    all_indices: List[int] = []

    # If knife has skinning attributes, partition by joint index; otherwise divide mesh by node
    prim = knife_prims[0]
    has_joints = prim.vertices[0].joints is not None

    if has_joints:
        # Group triangles by dominant joint
        joint_to_indices: Dict[int, List[int]] = {}
        for i in range(0, len(prim.indices), 3):
            i0, i1, i2 = prim.indices[i], prim.indices[i+1], prim.indices[i+2]
            v0 = prim.vertices[i0]
            # Primary joint
            joint_id = v0.joints[0] if v0.joints else 0
            joint_to_indices.setdefault(joint_id, []).extend([i0, i1, i2])

        all_vertices = prim.vertices
        cur_first_index = 0

        # Discover names for joints or match part keys
        for j_id, idxs in joint_to_indices.items():
            b_name = node_names[j_id] if j_id < len(node_names) else f"joint_{j_id}"
            submeshes.append(
                SubmeshRange(
                    bone_name=b_name,
                    bone_index=j_id,
                    first_index=cur_first_index,
                    index_count=len(idxs),
                    base_vertex=0,
                )
            )
            all_indices.extend(idxs)
            cur_first_index += len(idxs)

    # Ensure all key butterfly bones exist in submeshes
    existing_bones = [s.bone_name.lower() for s in submeshes]
    for key in part_keys:
        if not any(key in eb for eb in existing_bones):
            # Find matching node index
            n_idx = next((i for i, name in enumerate(node_names) if key in name.lower()), 0)
            submeshes.append(
                SubmeshRange(
                    bone_name=key,
                    bone_index=n_idx,
                    first_index=0,
                    index_count=len(prim.indices) // len(part_keys),
                    base_vertex=0,
                )
            )

    if not all_indices:
        all_vertices = prim.vertices
        all_indices = prim.indices

    # Append arms geometry if provided
    if arms_glb and Path(arms_glb).is_file():
        arms_prims = extract_mesh_primitives(arms_glb)
        for arm_prim in arms_prims:
            if not arm_prim.vertices or not arm_prim.indices:
                continue
            base_v = len(all_vertices)
            first_idx = len(all_indices)
            submeshes.append(
                SubmeshRange(
                    bone_name="arms_glove",
                    bone_index=len(submeshes),
                    first_index=first_idx,
                    index_count=len(arm_prim.indices),
                    base_vertex=base_v,
                )
            )
            # Arm vertices in glTF are in character bind space (Y: 0.9 ~ 1.5).
            # Transform to origin-centered viewmodel space aligned with knife.
            transformed_arm_verts = []
            for v in arm_prim.vertices:
                # Center around wrist/knuckles and align forward/back
                ax = v.pos[0] * 0.25
                ay = (v.pos[1] - 1.25) * 0.25
                az = (v.pos[2] + 0.05) * 0.25
                transformed_arm_verts.append(Vertex(pos=(ax, ay, az), uv=v.uv, normal=v.normal, joints=v.joints, weights=v.weights))

            all_vertices.extend(transformed_arm_verts)
            all_indices.extend(arm_prim.indices)

    pkg = CSViewModelPackage(
        submeshes=submeshes,
        total_vertices=len(all_vertices),
        total_indices=len(all_indices),
    )

    if output_bin:
        output_bin = output_bin.resolve()
        output_bin.parent.mkdir(parents=True, exist_ok=True)
        with open(output_bin, "wb") as f:
            # Header: magic(4), version(4), num_submeshes(4), total_vertices(4), total_indices(4)
            f.write(struct.pack("<4sIIII", b"CSVM", 1, len(submeshes), len(all_vertices), len(all_indices)))

            # Submesh table
            for sub in submeshes:
                name_bytes = sub.bone_name.encode("utf-8")
                f.write(struct.pack("<I", len(name_bytes)))
                f.write(name_bytes)
                f.write(struct.pack("<IIi", sub.bone_index, sub.first_index, sub.base_vertex))
                f.write(struct.pack("<I", sub.index_count))

            # Vertex buffer: pos(3f), normal(3f), uv(2f) -> 32 bytes per vertex
            for v in all_vertices:
                f.write(struct.pack("<3f3f2f", v.pos[0], v.pos[1], v.pos[2],
                                              v.normal[0], v.normal[1], v.normal[2],
                                              v.uv[0], v.uv[1]))

            # Index buffer: uint32
            for idx in all_indices:
                f.write(struct.pack("<I", idx))

    return pkg


if __name__ == "__main__":
    knife_p = Path("build/cs2assets/butterfly_knife/weapons/models/knife/knife_butterfly/weapon_knife_butterfly.glb")
    arms_p = Path("build/cs2assets/viewmodel_arms/agents/models/shared/arms/glove_hardknuckle/glove_hardknuckle.glb")
    out_p = Path("build/cs2assets/cs_butterfly_viewmodel.bin")
    if knife_p.is_file():
        p = build_cs_viewmodel_package(knife_glb=knife_p, arms_glb=arms_p, output_bin=out_p)
        print(f"[OK] Packed CS viewmodel: {p.total_vertices} vertices, {p.total_indices} indices, {len(p.submeshes)} submeshes -> {out_p}")
    else:
        print(f"[WARN] Knife glb not found at {knife_p}")
