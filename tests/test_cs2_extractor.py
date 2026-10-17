import os
import json
import struct
import pytest
from pathlib import Path

from tools.cs2.extractor import (
    find_cs2_vpk_path,
    ensure_vrf_cli,
    list_vpk_entries,
    extract_vpk_asset,
    verify_gltf_structure,
    verify_animation_monotonicity,
)


def test_find_cs2_vpk():
    """Verify that CS2 pak01_dir.vpk is discovered in the Steam install path."""
    vpk_path = find_cs2_vpk_path()
    assert vpk_path is not None
    assert os.path.isfile(vpk_path)
    assert vpk_path.lower().endswith("pak01_dir.vpk")


def test_ensure_vrf_cli():
    """Verify that Source2Viewer-CLI binary is retrieved or located and functional."""
    vrf_exe = ensure_vrf_cli(target_dir=Path("./build/tools/vrf"))
    assert os.path.isfile(vrf_exe)
    assert os.access(vrf_exe, os.X_OK) or vrf_exe.lower().endswith(".exe")


def test_list_knife_and_arms_assets():
    """Verify that knife_butterfly and viewmodel arms assets are indexed in VPK."""
    vpk_path = find_cs2_vpk_path()
    vrf_exe = ensure_vrf_cli(target_dir=Path("./build/tools/vrf"))

    entries = list_vpk_entries(vrf_exe, vpk_path, pattern="knife_butterfly")
    assert any("knife_butterfly" in e.lower() and e.lower().endswith(".vmdl_c") for e in entries)

    arm_entries = list_vpk_entries(vrf_exe, vpk_path, pattern="arms")
    assert any(e.lower().endswith(".vmdl_c") for e in arm_entries)


def test_extract_and_verify_butterfly_knife():
    """E2E Test: extract butterfly knife to glTF/GLB and verify mesh + animation slices."""
    vpk_path = find_cs2_vpk_path()
    vrf_exe = ensure_vrf_cli(target_dir=Path("./build/tools/vrf"))
    output_dir = Path("./build/cs2assets/butterfly_knife")

    # Find knife_butterfly vmdl_c
    entries = list_vpk_entries(vrf_exe, vpk_path, pattern="knife_butterfly")
    knife_vmdl = next(e for e in entries if "knife_butterfly" in e.lower() and e.lower().endswith(".vmdl_c"))

    # Extract asset
    extracted_files = extract_vpk_asset(vrf_exe, vpk_path, knife_vmdl, output_dir, export_format="glb")
    assert len(extracted_files) > 0

    glb_file = next(f for f in extracted_files if f.suffix.lower() in [".glb", ".gltf"])
    
    # Deep semantic verification: nodes, joints, animations
    parsed_gltf = verify_gltf_structure(glb_file)
    assert len(parsed_gltf.get("nodes", [])) > 0
    assert len(parsed_gltf.get("animations", [])) > 0

    # Verify animation slices (Inspect / Draw / Attack)
    anim_names = [a.get("name", "").lower() for a in parsed_gltf.get("animations", [])]
    has_inspect_or_draw = any(
        any(k in name for k in ["inspect", "lookat", "draw", "idle", "attack"])
        for name in anim_names
    )
    assert has_inspect_or_draw, f"Expected inspect/draw/attack animations, found: {anim_names}"

    # Verify temporal monotonicity and non-zero duration
    verify_animation_monotonicity(glb_file, parsed_gltf)


def test_extract_and_verify_viewmodel_arms():
    """E2E Test: extract CS2 first-person arms/gloves and verify skeleton & mesh bindings."""
    vpk_path = find_cs2_vpk_path()
    vrf_exe = ensure_vrf_cli(target_dir=Path("./build/tools/vrf"))
    output_dir = Path("./build/cs2assets/viewmodel_arms")

    # Locate glove_hardknuckle (classic CT viewmodel arms)
    entries = list_vpk_entries(vrf_exe, vpk_path, pattern="glove_hardknuckle")
    arms_vmdl = next(e for e in entries if e.lower().endswith("glove_hardknuckle.vmdl_c"))

    extracted_files = extract_vpk_asset(vrf_exe, vpk_path, arms_vmdl, output_dir, export_format="glb")
    assert len(extracted_files) > 0

    arms_glb = next(f for f in extracted_files if f.name.lower() == "glove_hardknuckle.glb")
    parsed_arms = verify_gltf_structure(arms_glb)

    # Assert skeleton nodes (wrists, fingers, forearm)
    nodes = parsed_arms.get("nodes", [])
    node_names = [n.get("name", "").lower() for n in nodes]
    assert any("wrist" in n or "hand" in n or "arm" in n or "finger" in n for n in node_names), (
        f"Missing arm/hand bone hierarchy in arms model: {node_names}"
    )

    # Assert mesh primitive skinning (JOINTS_0 and WEIGHTS_0 attributes)
    meshes = parsed_arms.get("meshes", [])
    assert len(meshes) > 0
    has_skinning = False
    for mesh in meshes:
        for prim in mesh.get("primitives", []):
            attrs = prim.get("attributes", {})
            if "JOINTS_0" in attrs and "WEIGHTS_0" in attrs:
                has_skinning = True
                break
    assert has_skinning, "Arms mesh primitives must contain JOINTS_0 and WEIGHTS_0 skinning attributes"


def test_extract_and_verify_butterfly_knife_viewmodel_clips():
    """E2E Test: extract specific viewmodel animation clips (draw, inspect/lookat01, lookat02, backstab)."""
    vpk_path = find_cs2_vpk_path()
    vrf_exe = ensure_vrf_cli(target_dir=Path("./build/tools/vrf"))
    output_dir = Path("./build/cs2assets/butterfly_knife/clips")

    target_clips = [
        "animation/anims/viewmodel/knife/knife_butterfly/draw_butterfly.vnmclip_c",
        "animation/anims/viewmodel/knife/knife_butterfly/lookat01_butterfly.vnmclip_c",
        "animation/anims/viewmodel/knife/knife_butterfly/lookat02_butterfly.vnmclip_c",
        "animation/anims/viewmodel/knife/knife_butterfly/heavy_backstab_butterfly.vnmclip_c",
    ]

    for clip_entry in target_clips:
        extracted = extract_vpk_asset(vrf_exe, vpk_path, clip_entry, output_dir, export_format="glb")
        assert len(extracted) > 0, f"Failed to extract animation clip: {clip_entry}"
        clip_file = extracted[0]
        parsed = verify_gltf_structure(clip_file)
        assert len(parsed.get("animations", [])) > 0, f"No animations found in clip: {clip_file}"
        verify_animation_monotonicity(clip_file, parsed)
