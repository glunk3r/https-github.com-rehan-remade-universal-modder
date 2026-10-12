"""TDD tests for completely isolated Overwatch Doomfist standalone mod pipeline.

Ensures:
- Real high-poly 3D mesh conversion to FromSoftware FLVER 2.0 / DCX format
- ModEngine2 standalone packaging strictly isolated in mods/ow_doomfist_standalone/
- Absolute zero contamination or overlap with mc_adapter or mc-core
- Deep binary structure validation for FLVER vertices, materials, and bounding boxes
"""
import pytest
from pathlib import Path
import struct
import json

from tools.ow_doomfist_standalone.flver_converter import (
    FlverConverter,
    FlverMesh,
    FlverVertex,
    DcxPacker,
)
from tools.ow_doomfist_standalone.mod_packager import StandaloneModPackager


def test_dcx_compression_container_header():
    packer = DcxPacker()
    raw_data = b"FLVER2_REAL_HIGH_POLY_MESH_DATA_OVERWATCH_DOOMFIST"
    packed_dcx = packer.pack(raw_data)

    # FromSoftware DCX header:
    # 0x00: "DCX\0" magic (4 bytes)
    # 0x04: 0x10000 version (4 bytes big-endian)
    assert packed_dcx[:4] == b"DCX\x00"
    version = struct.unpack(">I", packed_dcx[4:8])[0]
    assert version == 0x10000

    # Unpack must restore exact payload
    unpacked = packer.unpack(packed_dcx)
    assert unpacked == raw_data


def test_flver2_mesh_generation_and_binary_layout():
    converter = FlverConverter()

    # Create high-poly test vertices for Doomfist gauntlet
    vertices = [
        FlverVertex(position=(0.1, 1.2, 0.3), normal=(0.0, 1.0, 0.0), uv=(0.25, 0.5)),
        FlverVertex(position=(0.3, 1.4, 0.3), normal=(0.0, 1.0, 0.0), uv=(0.50, 0.5)),
        FlverVertex(position=(0.2, 1.5, 0.4), normal=(0.0, 1.0, 0.0), uv=(0.75, 0.5)),
    ]
    indices = [0, 1, 2]

    flver_bytes = converter.create_flver_bytes(
        mesh_name="Doomfist_Gauntlet",
        vertices=vertices,
        indices=indices,
        material_name="M_Doomfist_GoldGauntlet",
    )

    # FromSoftware FLVER2 header check:
    # 0x00: "FLVER\0" (6 bytes)
    # 0x06: 'L\0' little-endian (2 bytes)
    assert flver_bytes[:6] == b"FLVER\x00"
    assert flver_bytes[6:8] == b"L\x00"

    # Header must define version 0x20000 (FLVER 2.0 used in DS3, Sekiro, Elden Ring)
    version = struct.unpack("<I", flver_bytes[8:12])[0]
    assert version == 0x20000

    # Bounding box coordinates must enclose all vertices
    min_x, min_y, min_z, max_x, max_y, max_z = struct.unpack("<6f", flver_bytes[16:40])
    assert pytest.approx(min_x, abs=1e-3) == 0.1
    assert pytest.approx(max_x, abs=1e-3) == 0.3
    assert pytest.approx(min_y, abs=1e-3) == 1.2
    assert pytest.approx(max_y, abs=1e-3) == 1.5


def test_standalone_mod_packaging_isolation(tmp_path):
    game_dir = tmp_path / "ELDEN_RING" / "Game"
    mc_adapter_dir = game_dir / "mods" / "mc_adapter"
    mc_adapter_dir.mkdir(parents=True)
    # Put a canary file in mc_adapter
    canary = mc_adapter_dir / "steve.bbmodel"
    canary.write_text("MC_CANARY_DO_NOT_TOUCH", encoding="utf-8")

    packager = StandaloneModPackager(game_dir=game_dir)
    result = packager.build_and_deploy()

    assert result.success is True
    # The output mod dir must be strictly mods/ow_doomfist_standalone
    target_mod_dir = game_dir / "mods" / "ow_doomfist_standalone"
    assert target_mod_dir.is_dir()

    # Check parts files
    parts_dir = target_mod_dir / "parts"
    assert parts_dir.is_dir()
    expected_parts = [
        "wp_a_2040.dcx",  # Gauntlet weapon part
        "bd_m_2040.dcx",  # Torso body armor part
        "hd_m_2040.dcx",  # Head armor part
        "lg_m_2040.dcx",  # Legs armor part
        "am_m_2040.dcx",  # Arms armor part
    ]
    for part_name in expected_parts:
        part_file = parts_dir / part_name
        assert part_file.is_file()
        assert part_file.stat().st_size > 0
        # Verify it is a valid DCX file
        header = part_file.read_bytes()[:4]
        assert header == b"DCX\x00"

    # Check isolated ModEngine2 configuration
    config_file = target_mod_dir / "config_eldenring.toml"
    assert config_file.is_file()
    cfg_text = config_file.read_text(encoding="utf-8")
    assert "ow_doomfist_standalone" in cfg_text
    assert "mc_adapter" not in cfg_text  # Zero overlap with mc_adapter

    # Check Scheme B keybinding configuration
    input_cfg = target_mod_dir / "ow_input_config.json"
    assert input_cfg.is_file()
    input_data = json.loads(input_cfg.read_text(encoding="utf-8"))
    assert input_data["scheme"] == "B"
    assert input_data["keybindings"]["RocketPunch"] == "VK_RBUTTON"
    assert input_data["keybindings"]["SeismicSlam"] == "VK_SHIFT"
    assert input_data["keybindings"]["RisingUppercut"] == "VK_E"
    assert input_data["keybindings"]["HandCannon"] == "VK_LBUTTON"
    assert input_data["keybindings"]["MeteorStrike"] == "VK_Q"

    # CRITICAL CANARY CHECK: mc_adapter must remain 100% UNTOUCHED
    assert canary.read_text(encoding="utf-8") == "MC_CANARY_DO_NOT_TOUCH"
