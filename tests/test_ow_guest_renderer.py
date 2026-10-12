"""TDD test suite for Guest Standalone Character Renderer and Frame Producer.

Covers:
- Character 3D mesh loading and bounding box validation
- Software/GPU rasterization of RGBA color with alpha cutout
- Linear R32F depth buffer generation in metres
- Publishing rendered frames directly to Seqlock shared memory bridge
- Dynamic posture update based on Scheme B abilities (Rocket Punch, Slam, Uppercut)
"""
import pytest
import struct

from tools.ow_passthrough.guest_renderer import (
    GuestCharacterRenderer,
    RenderCamera,
    RenderFrame,
)
from tools.ow_passthrough.shared_memory import (
    SharedMemoryBridge,
    PoseData,
)
from tools.ow_doomfist.input_controller import (
    DoomfistInputController,
    VirtualKey,
    AbilityState,
)


def test_guest_renderer_initialization_and_mesh_loading():
    renderer = GuestCharacterRenderer(width=64, height=64)
    assert renderer.character_name == "Doomfist"
    assert renderer.vertex_count > 0
    # Bounding box height should be approximately 1.95m
    assert pytest.approx(renderer.bounding_height_m, abs=0.1) == 1.95


def test_guest_renderer_renders_color_and_depth_buffers():
    renderer = GuestCharacterRenderer(width=64, height=64)

    # Camera looking at character center (0.0, 1.0, 0.0) from 3 metres away along -Z
    cam = RenderCamera(
        eye=(0.0, 1.0, -3.0),
        target=(0.0, 1.0, 0.0),
        fov_deg=60.0,
    )

    frame = renderer.render_frame(camera=cam)
    assert isinstance(frame, RenderFrame)
    assert len(frame.color_rgba) == 64 * 64 * 4
    assert len(frame.depth_r32f) == 64 * 64 * 4

    # Check background transparency: corner pixel (0, 0) should be transparent
    corner_alpha = frame.color_rgba[3]
    assert corner_alpha == 0

    # Center pixel (looking directly at character) should have character color and alpha > 0
    center_idx = (32 * 64 + 32) * 4
    center_alpha = frame.color_rgba[center_idx + 3]
    assert center_alpha > 0

    # Depth at center pixel should be around ~3.0 metres (distance from camera to character)
    center_depth_bytes = frame.depth_r32f[32 * 64 * 4 + 32 * 4 : 32 * 64 * 4 + 32 * 4 + 4]
    center_depth = struct.unpack("<f", center_depth_bytes)[0]
    assert pytest.approx(center_depth, abs=0.6) == 3.0


def test_guest_renderer_publishes_to_shared_memory():
    bridge = SharedMemoryBridge(width=64, height=64)
    renderer = GuestCharacterRenderer(width=64, height=64, bridge=bridge)

    cam = RenderCamera(eye=(0.0, 1.0, -2.5), target=(0.0, 1.0, 0.0), fov_deg=60.0)
    slot_idx = renderer.render_and_publish(camera=cam)
    assert slot_idx in (0, 1, 2)

    # Verify frame readable via shared memory bridge
    read_res = bridge.read_latest_frame(max_age_ms=100.0)
    assert read_res.is_valid is True
    assert len(read_res.color_data) == 64 * 64 * 4


def test_guest_renderer_ability_animation_update():
    renderer = GuestCharacterRenderer(width=32, height=32)
    ctrl = DoomfistInputController()

    # Trigger Rocket Punch charge
    ctrl.on_key_down(VirtualKey.RBUTTON)
    ctrl.update(0.6)  # Tier 2 charge

    # Update renderer posture
    renderer.update_ability_state(ctrl)
    assert renderer.current_ability == AbilityState.ROCKET_PUNCH_CHARGING
    assert renderer.charge_tier == 2

    # Gauntlet offset must reflect charge stance (retracted back to wind up)
    assert renderer.gauntlet_offset_z < 0.0
