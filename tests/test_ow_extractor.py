"""TDD test suite for Overwatch Asset Extractor and Mesh Importer.

Covers:
- Scanning local Overwatch CASC installation (data/ directory, .build.config)
- Parsing character 3D geometry from extracted mesh files (Wavefront OBJ / SMD)
- Feeding high-poly meshes directly into GuestCharacterRenderer
"""
import pytest
from pathlib import Path

from tools.ow_passthrough.ow_extractor import (
    OverwatchAssetScanner,
    WavefrontMeshParser,
    ExtractedHeroAsset,
)
from tools.ow_passthrough.guest_renderer import GuestCharacterRenderer


def test_ow_installation_discovery_and_casc_validation(tmp_path):
    # Mock Overwatch directory
    ow_dir = tmp_path / "Overwatch"
    data_dir = ow_dir / "data"
    data_dir.mkdir(parents=True)
    (data_dir / ".build.config").write_text("build=1.0", encoding="utf-8")
    (ow_dir / "Overwatch.exe").write_bytes(b"MZ_DUMMY_EXE")

    scanner = OverwatchAssetScanner(ow_dir=ow_dir)
    assert scanner.is_valid_installation() is True
    assert scanner.has_casc_data() is True


def test_ow_mesh_loader_parses_obj_and_textures(tmp_path):
    obj_file = tmp_path / "doomfist.obj"
    obj_content = (
        "# Doomfist Test Mesh\n"
        "v -0.5 0.0 0.0\n"
        "v 0.5 0.0 0.0\n"
        "v 0.0 1.95 0.0\n"
        "vn 0.0 1.0 0.0\n"
        "vt 0.0 0.0\n"
        "vt 1.0 0.0\n"
        "vt 0.5 1.0\n"
        "f 1/1/1 2/2/1 3/3/1\n"
    )
    obj_file.write_text(obj_content, encoding="utf-8")

    parser = WavefrontMeshParser()
    mesh = parser.parse_file(obj_file)

    assert mesh.vertex_count == 3
    assert mesh.face_count == 1
    assert pytest.approx(mesh.height_m, abs=1e-3) == 1.95

    # Integrate into GuestCharacterRenderer
    renderer = GuestCharacterRenderer(width=32, height=32)
    renderer.load_custom_mesh(mesh)
    assert renderer.vertex_count == 3
    assert pytest.approx(renderer.bounding_height_m, abs=1e-3) == 1.95


def test_real_ow_directory_scanner():
    real_path = Path(r"G:\SteamLibrary\steamapps\common\Overwatch")
    if real_path.is_dir():
        scanner = OverwatchAssetScanner(ow_dir=real_path)
        assert scanner.is_valid_installation() is True
        assert scanner.has_casc_data() is True
