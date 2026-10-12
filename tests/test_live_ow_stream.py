"""Test live Overwatch frame stream in Local\\OWPassthroughFrame."""
import mmap
import struct
import sys
import time
import pytest

from tools.ow_passthrough.shared_memory import MAGIC_OWPS, PROTOCOL_VERSION


def test_live_mmap_stream_active():
    if sys.platform != "win32":
        pytest.skip("Windows only")

    mapping_name = r"Local\OWPassthroughFrame"
    # Header is 4096 bytes
    try:
        reader = mmap.mmap(-1, 4096, tagname=mapping_name, access=mmap.ACCESS_READ)
    except FileNotFoundError:
        pytest.fail(f"Shared memory mapping {mapping_name} not found! Is ow_server running?")

    magic, version, width, height, active_slot, slot_count, stride, pub_seq_1 = struct.unpack_from(
        "<IIIIiiqq", reader, 0
    )
    assert magic == MAGIC_OWPS, f"Magic mismatch: {hex(magic)} != {hex(MAGIC_OWPS)}"
    assert version == PROTOCOL_VERSION
    print(f"\n[DEBUG_INFO] width={width}, height={height}, stride={stride}, pub_seq={pub_seq_1}")
    assert width > 0 and height > 0
    assert slot_count == 3
    assert active_slot in (0, 1, 2)

    # Verify stream is actively publishing frames
    time.sleep(0.05)
    magic, version, width, height, active_slot, slot_count, stride, pub_seq_2 = struct.unpack_from(
        "<IIIIiiqq", reader, 0
    )
    reader.close()

    assert pub_seq_2 > pub_seq_1, f"Frame sequence not advancing: {pub_seq_1} == {pub_seq_2}"

    # Now map the full buffer and inspect slot data
    total_size = 4096 + stride * slot_count
    reader_full = mmap.mmap(-1, total_size, tagname=mapping_name, access=mmap.ACCESS_READ)
    slot_offset = 4096 + active_slot * stride
    seqlock, ts, cx, cy, cz, yaw, pitch, c_off, d_off = struct.unpack_from(
        "<qqfffffII", reader_full, slot_offset
    )
    raw_color = reader_full[slot_offset + c_off : slot_offset + c_off + width * height * 4]
    reader_full.close()

    assert len(raw_color) == width * height * 4
    # Check that we have non-transparent pixels (Doomfist rendered)
    non_zero_alphas = [raw_color[i * 4 + 3] for i in range(width * height) if raw_color[i * 4 + 3] > 0]
    assert len(non_zero_alphas) > 100, f"Expected character pixels, found only {len(non_zero_alphas)}"

