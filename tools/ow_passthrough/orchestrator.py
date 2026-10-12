"""End-to-End Orchestrator for Overwatch inside Elden Ring Passthrough.

Unifies:
1. Input Controller (Scheme B: Right-click charge, Shift, E, Left-click, Q)
2. Guest Character Renderer (Postures, RGBA color with alpha cutout, linear R32F depth)
3. Named Shared Memory Bridge (Seqlock triple-buffering)
4. Compositor Loop (Reverse-Z depth testing and occlusion checks)
"""
from dataclasses import dataclass
from typing import Tuple, Optional
import struct

from tools.ow_doomfist.input_controller import (
    DoomfistInputController,
    VirtualKey,
    AbilityState,
)
from tools.ow_passthrough.shared_memory import (
    SharedMemoryBridge,
)
from tools.ow_passthrough.guest_renderer import (
    GuestCharacterRenderer,
    RenderCamera,
)
from tools.ow_passthrough.compositor import (
    DepthCompositor,
    CompositePixel,
)


@dataclass
class FrameStatistic:
    frame_id: int
    is_valid: bool
    composite_drawn_pixels: int
    charge_tier: int
    active_ability: str


class PassthroughOrchestrator:
    def __init__(self, width: int = 128, height: int = 128):
        self.width = width
        self.height = height
        self.is_running = False
        self.frame_count = 0

        self.input_controller = DoomfistInputController()
        self.shared_memory = SharedMemoryBridge(width=width, height=height)
        self.guest_renderer = GuestCharacterRenderer(width=width, height=height, bridge=self.shared_memory)
        self.compositor = DepthCompositor()

    def start(self) -> None:
        self.is_running = True
        self.frame_count = 0

    def stop(self) -> None:
        self.is_running = False

    def on_key_down(self, vk: VirtualKey) -> None:
        self.input_controller.on_key_down(vk)

    def on_key_up(self, vk: VirtualKey) -> None:
        self.input_controller.on_key_up(vk)

    def step_frame(
        self,
        dt: float = 0.016,
        host_cam_eye: Tuple[float, float, float] = (0.0, 1.0, -2.5),
        host_reversed_z_depth: float = 0.010,
    ) -> FrameStatistic:
        self.frame_count += 1

        # 1. Update Input & Animation State Machine
        self.input_controller.update(dt)
        self.guest_renderer.update_ability_state(self.input_controller)

        # 2. Render guest frame and publish to Seqlock shared memory
        cam = RenderCamera(eye=host_cam_eye, target=(0.0, 1.0, 0.0), fov_deg=60.0)
        self.guest_renderer.render_and_publish(camera=cam)

        # 3. Read back from shared memory (Compositor side)
        read_res = self.shared_memory.read_latest_frame(max_age_ms=200.0)
        if not read_res.is_valid:
            return FrameStatistic(
                frame_id=self.frame_count,
                is_valid=False,
                composite_drawn_pixels=0,
                charge_tier=self.input_controller.charge_tier,
                active_ability=self.input_controller.current_state.name,
            )

        # 4. Composite pixels against Elden Ring depth
        drawn_pixels = 0
        total_pixels = self.width * self.height
        c_bytes = read_res.color_data
        d_bytes = read_res.depth_data

        for i in range(total_pixels):
            alpha = c_bytes[i * 4 + 3] / 255.0
            if alpha > 0.01:
                z_linear = struct.unpack_from("<f", d_bytes, i * 4)[0]
                pix_decision = self.compositor.test_depth(
                    guest_linear_z=z_linear,
                    guest_alpha=alpha,
                    host_reversed_z=host_reversed_z_depth,
                )
                if pix_decision == CompositePixel.DRAW_GUEST:
                    drawn_pixels += 1

        ability_name = "None"
        state = self.input_controller.current_state
        if state in (AbilityState.ROCKET_PUNCH_CHARGING, AbilityState.ROCKET_PUNCH_DASHING):
            ability_name = "RocketPunch"
        elif state == AbilityState.SEISMIC_SLAM_LEAP:
            ability_name = "SeismicSlam"
        elif state == AbilityState.RISING_UPPERCUT:
            ability_name = "RisingUppercut"
        elif state in (AbilityState.METEOR_STRIKE_TARGETING, AbilityState.METEOR_STRIKE_SLAM):
            ability_name = "MeteorStrike"

        return FrameStatistic(
            frame_id=self.frame_count,
            is_valid=True,
            composite_drawn_pixels=drawn_pixels,
            charge_tier=self.input_controller.charge_tier,
            active_ability=ability_name,
        )
