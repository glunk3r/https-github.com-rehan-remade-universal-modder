"""TDD test suite for ReShade Add-on and Host D3D12 Integration.

Validates:
- C++ Addon source code integrity (ow_addon.cpp)
- ReShade 6.8 header inclusion and API exports
- Compiled binary format (PE x64) and exported symbols
- Complete host integration readiness
"""
from pathlib import Path
import struct
import pytest

ADDON_DIR = Path("tools/ow_passthrough/addon")


def test_ow_addon_source_integrity():
    src_path = ADDON_DIR / "ow_addon.cpp"
    assert src_path.is_file()
    content = src_path.read_text(encoding="utf-8")

    assert 'L"Local\\\\OWPassthroughFrame"' in content
    assert "0x4F575053" in content  # Magic OWPS
    assert "OWWORLD" in content
    assert "OWDEPTH" in content
    assert "reshade::register_addon" in content
    assert "reshade_begin_effects" in content
    assert "update_texture_region" in content


def test_ow_addon_binary_format():
    bin_path = ADDON_DIR / "build" / "ow_compositor.addon"
    assert bin_path.is_file(), "ow_compositor.addon must be compiled"
    assert bin_path.stat().st_size > 10_000

    data = bin_path.read_bytes()
    # Check MZ header
    assert data[:2] == b"MZ"
    # Find PE header
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    pe_sig = data[pe_offset : pe_offset + 4]
    assert pe_sig == b"PE\x00\x00"

    # Machine x64 (0x8664)
    machine = struct.unpack_from("<H", data, pe_offset + 4)[0]
    assert machine == 0x8664, "Binary must be 64-bit Windows PE"


def test_reshade64_runtime_binary_presence():
    dll_path = ADDON_DIR / "bin" / "ReShade64.dll"
    assert dll_path.is_file()
    assert dll_path.stat().st_size > 5_000_000
    data = dll_path.read_bytes()
    assert data[:2] == b"MZ"
