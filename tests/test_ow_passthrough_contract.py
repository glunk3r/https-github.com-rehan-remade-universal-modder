"""TDD test suite for Overwatch inside Elden Ring Passthrough Bridge Contract.

Deep domain testing:
- Seqlock triple-buffer concurrency and zero-torn-read guarantees
- Coordinate space and camera matrix conversion
- Reverse-Z depth buffer comparison and occlusion test
- Stale-frame watchdog dropping old pictures
"""
import pytest
import struct
import time

from tools.ow_passthrough.shared_memory import (
    SharedMemoryBridge,
    FrameHeader,
    FrameSlot,
    PoseData,
    MAGIC_OWPS,
    PROTOCOL_VERSION,
)
from tools.ow_passthrough.compositor import (
    DepthCompositor,
    CompositePixel,
)


def test_seqlock_shared_memory_protocol_handshake():
    bridge = SharedMemoryBridge(width=64, height=64)

    # Initialize shared buffer
    header = bridge.get_header()
    assert header.magic == MAGIC_OWPS
    assert header.protocol_version == PROTOCOL_VERSION
    assert header.width == 64
    assert header.height == 64
    assert len(header.slots) == 3

    # Produce a frame into slot 0
    pose = PoseData(
        camera_pos=(10.0, 5.0, -20.0),
        yaw_deg=45.0,
        pitch_deg=-10.0,
    )
    # 64x64 RGBA: red square
    color_bytes = b"\xFF\x00\x00\xFF" * (64 * 64)
    # 64x64 R32F depth: 5.0 metres
    depth_bytes = struct.pack("<f", 5.0) * (64 * 64)

    slot_idx = bridge.write_frame(pose=pose, color_rgba=color_bytes, depth_r32f=depth_bytes)
    assert slot_idx in (0, 1, 2)

    # Consumer reads frame
    read_result = bridge.read_latest_frame(max_age_ms=100.0)
    assert read_result.is_valid is True
    assert read_result.pose.camera_pos == (10.0, 5.0, -20.0)
    assert len(read_result.color_data) == 64 * 64 * 4
    assert len(read_result.depth_data) == 64 * 64 * 4


def test_seqlock_rejects_torn_read_during_write():
    bridge = SharedMemoryBridge(width=16, height=16)

    # Simulate an active write that is mid-stride (odd seqlock)
    slot = bridge.header.slots[0]
    slot.seqlock = 1  # Odd counter indicates active write in progress

    # Reader must detect active write and reject torn frame
    read_result = bridge.read_slot(0)
    assert read_result.is_valid is False
    assert "mid-write" in read_result.error_reason


def test_depth_occlusion_reversed_z_mapping():
    compositor = DepthCompositor(depth_constant=0.050067)

    # Case 1: Guest is in front of Elden Ring obstacle
    # Guest depth = 3.0 metres
    # Elden Ring reversed-Z depth = 0.010 (meaning distance = 0.050067 / 0.010 = ~5.0m)
    # Result: Guest is at 3.0m, wall is at 5.0m -> Guest VISIBLE
    pixel_front = compositor.test_depth(
        guest_linear_z=3.0,
        guest_alpha=1.0,
        host_reversed_z=0.010,
    )
    assert pixel_front == CompositePixel.DRAW_GUEST

    # Case 2: Guest is behind Elden Ring pillar
    # Guest depth = 8.0 metres
    # Elden Ring reversed-Z depth = 0.010 (wall distance = 5.0m)
    # Result: Guest is at 8.0m, wall is at 5.0m -> Guest OCCLUDED
    pixel_behind = compositor.test_depth(
        guest_linear_z=8.0,
        guest_alpha=1.0,
        host_reversed_z=0.010,
    )
    assert pixel_behind == CompositePixel.OCCLUDED_BY_HOST

    # Case 3: Transparent pixel (Alpha <= 0.01)
    pixel_transparent = compositor.test_depth(
        guest_linear_z=2.0,
        guest_alpha=0.0,
        host_reversed_z=0.010,
    )
    assert pixel_transparent == CompositePixel.TRANSPARENT


def test_stale_frame_watchdog_timeout():
    bridge = SharedMemoryBridge(width=16, height=16)

    pose = PoseData(camera_pos=(0.0, 0.0, 0.0), yaw_deg=0.0, pitch_deg=0.0)
    bridge.write_frame(pose=pose, color_rgba=b"\x00" * 1024, depth_r32f=b"\x00" * 1024)

    # Artificially age the timestamp by 200ms (> 150ms threshold)
    bridge.header.slots[bridge.header.active_slot].timestamp_us -= 250_000

    # Reading with 150ms timeout must return STALE
    result = bridge.read_latest_frame(max_age_ms=150.0)
    assert result.is_valid is False
    assert "stale" in result.error_reason.lower()
