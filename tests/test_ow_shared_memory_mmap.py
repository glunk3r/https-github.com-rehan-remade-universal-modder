"""TDD test suite for Windows Named Shared Memory (mmap) transport.

Validates:
- Real OS-level named shared memory mapping creation (Local\\OWPassthroughFrame)
- Binary struct serialization and deserialization
- Concurrent reader/writer via second mapping handle
"""
import mmap
import os
import struct
import sys
import time
import pytest

from tools.ow_passthrough.shared_memory import (
    SharedMemoryBridge,
    PoseData,
    MAGIC_OWPS,
    PROTOCOL_VERSION,
)


def test_windows_mmap_bridge_lifecycle():
    if sys.platform != "win32":
        pytest.skip("Windows only test for named shared memory")

    mapping_name = r"Local\TestOWPassthroughFrame"
    bridge = SharedMemoryBridge(width=32, height=32, mapping_name=mapping_name, use_mmap=True)

    assert bridge.has_mmap is True

    # Write a test frame
    pose = PoseData(camera_pos=(1.0, 2.0, 3.0), yaw_deg=90.0, pitch_deg=-15.0)
    color = b"\x12\x34\x56\x78" * (32 * 32)
    depth = struct.pack("<f", 4.25) * (32 * 32)

    slot_idx = bridge.write_frame(pose=pose, color_rgba=color, depth_r32f=depth)
    assert slot_idx in (0, 1, 2)

    # Read back through bridge
    res = bridge.read_latest_frame(max_age_ms=200.0)
    assert res.is_valid is True
    assert res.pose.camera_pos == (1.0, 2.0, 3.0)
    assert res.color_data[:4] == b"\x12\x34\x56\x78"

    # Now open a separate independent mmap handle to verify external C++ compatibility
    total_size = bridge.total_mmap_size
    reader_mmap = mmap.mmap(-1, total_size, tagname=mapping_name, access=mmap.ACCESS_READ)

    magic, version, width, height, active_slot, slot_count, stride, pub_seq = struct.unpack_from(
        "<IIIIiiqq", reader_mmap, 0
    )
    assert magic == MAGIC_OWPS
    assert version == PROTOCOL_VERSION
    assert width == 32
    assert height == 32
    assert active_slot == slot_idx

    reader_mmap.close()
    bridge.close()
