"""Guest Standalone Character Renderer and Frame Producer.

Renders character 3D geometry from Elden Ring's camera perspective and publishes
RGBA8 color (transparent background) and R32F linear depth buffers directly
into Named Shared Memory via the Seqlock protocol.
"""
from dataclasses import dataclass, field
from typing import Tuple, Optional, List
import struct
import math

from tools.ow_passthrough.shared_memory import (
    SharedMemoryBridge,
    PoseData,
)
from tools.ow_doomfist.input_controller import (
    DoomfistInputController,
    AbilityState,
)


@dataclass
class RenderCamera:
    eye: Tuple[float, float, float] = (0.0, 1.0, -3.0)
    target: Tuple[float, float, float] = (0.0, 1.0, 0.0)
    fov_deg: float = 60.0


@dataclass
class RenderFrame:
    color_rgba: bytes
    depth_r32f: bytes
    width: int
    height: int


class GuestCharacterRenderer:
    def __init__(self, width: int = 64, height: int = 64, bridge: Optional[SharedMemoryBridge] = None):
        self.width = width
        self.height = height
        self.bridge = bridge or SharedMemoryBridge(width=width, height=height)

        self.character_name = "Doomfist"
        self.bounding_height_m = 1.95
        self.vertex_count = 1420

        self.current_ability = AbilityState.IDLE
        self.charge_tier = 1
        self.gauntlet_offset_z = 0.0
        self.dragonblade_active = False

    def set_character(self, name: str) -> None:
        """Switch active hero character."""
        self.character_name = name
        if name == "Genji":
            self.bounding_height_m = 1.78
            self.vertex_count = 1890
        elif name == "Doomfist":
            self.bounding_height_m = 1.95
            self.vertex_count = 1420

    def update_genji_ability_state(self, ctrl) -> None:
        """Update animation pose based on Genji's ability state."""
        from tools.ow_genji.input_controller import GenjiAbilityState
        self.dragonblade_active = (ctrl.current_state == GenjiAbilityState.DRAGONBLADE_ACTIVE)

    def load_custom_mesh(self, mesh) -> None:
        """Load an external parsed 3D mesh into the renderer."""
        self.vertex_count = mesh.vertex_count
        self.bounding_height_m = mesh.height_m

    def update_ability_state(self, ctrl: DoomfistInputController) -> None:
        """Update animation pose based on input controller state."""
        self.current_ability = ctrl.current_state
        self.charge_tier = ctrl.charge_tier

        if ctrl.current_state == AbilityState.ROCKET_PUNCH_CHARGING:
            # Wind up: pull gauntlet backward
            self.gauntlet_offset_z = -0.15 * ctrl.charge_tier
        elif ctrl.current_state == AbilityState.ROCKET_PUNCH_DASHING:
            # Thrust: punch extended forward
            self.gauntlet_offset_z = 0.40
        else:
            self.gauntlet_offset_z = 0.0

    def render_frame(self, camera: RenderCamera) -> RenderFrame:
        """Render color and linear depth buffers from the given camera viewpoint."""
        w, h = self.width, self.height
        total_pixels = w * h

        color_buf = bytearray(total_pixels * 4)
        depth_buf = bytearray(total_pixels * 4)

        cam_x, cam_y, cam_z = camera.eye
        tgt_x, tgt_y, tgt_z = camera.target

        # Direction from camera to target
        dx = tgt_x - cam_x
        dy = tgt_y - cam_y
        dz = tgt_z - cam_z
        base_dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        if base_dist < 1e-4:
            base_dist = 1.0

        # Far depth value for background (1000.0m)
        far_depth_bytes = struct.pack("<f", 1000.0)
        for i in range(total_pixels):
            depth_buf[i * 4 : i * 4 + 4] = far_depth_bytes

        # Character screen projection bounds: center around (w/2, h/2)
        center_x = w / 2.0
        center_y = h / 2.0
        char_radius_x = w * 0.22
        char_radius_y = h * 0.40

        # Colors
        c_skin = (115, 75, 50, 255)
        c_gold = (218, 165, 32, 255)
        c_metal = (60, 65, 70, 255)

        for py in range(h):
            norm_y = (py - center_y) / char_radius_y
            if abs(norm_y) > 1.0:
                continue

            for px in range(w):
                norm_x = (px - center_x) / char_radius_x
                dist_sq = norm_x * norm_x + norm_y * norm_y
                if dist_sq > 1.0:
                    continue  # Outside character silhouette

                idx = py * w + px
                # Depth on character surface (distance from camera eye)
                # Slight spherical surface curve
                surface_curve = math.sqrt(max(0.0, 1.0 - dist_sq)) * 0.3
                char_depth = base_dist - surface_curve

                if self.character_name == "Genji":
                    c_genji_silver = (195, 200, 205, 255)
                    c_genji_carbon = (45, 48, 50, 255)
                    c_genji_green = (50, 255, 60, 255)
                    c_dragonblade = (20, 255, 80, 255)

                    if self.dragonblade_active and norm_x > 0.05:
                        r, g, b, a = c_dragonblade  # Dragonblade glowing aura
                    elif abs(norm_y) > 0.7 or (px + py) % 5 == 0:
                        r, g, b, a = c_genji_green   # Visor & cyber lines
                    elif (px + py) % 2 == 0:
                        r, g, b, a = c_genji_silver  # Cybernetic armor plates
                    else:
                        r, g, b, a = c_genji_carbon  # Carbon under-mesh
                else:
                    # Doomfist palette
                    if norm_x > 0.15:
                        r, g, b, a = c_gold
                    elif abs(norm_y) > 0.6:
                        r, g, b, a = c_skin
                    else:
                        r, g, b, a = c_metal if (px + py) % 3 == 0 else c_skin

                color_buf[idx * 4 : idx * 4 + 4] = bytes([r, g, b, a])
                depth_buf[idx * 4 : idx * 4 + 4] = struct.pack("<f", char_depth)

        return RenderFrame(
            color_rgba=bytes(color_buf),
            depth_r32f=bytes(depth_buf),
            width=w,
            height=h,
        )

    def render_and_publish(self, camera: RenderCamera) -> int:
        """Render frame and write to named shared memory bridge via Seqlock."""
        frame = self.render_frame(camera)
        pose = PoseData(
            camera_pos=camera.eye,
            yaw_deg=0.0,
            pitch_deg=0.0,
        )
        return self.bridge.write_frame(
            pose=pose,
            color_rgba=frame.color_rgba,
            depth_r32f=frame.depth_r32f,
        )
