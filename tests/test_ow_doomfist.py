"""Tests for Overwatch Doomfist to Elden Ring modding pipeline.

Covers:
- Coordinate transformation and height normalization (OW Z-up -> FromSoft Y-up, 1.95m canon height)
- PBR texture map packing and DirectX normal map compliance
- Skill physics, timing, charge levels, and hyperarmor contracts
- ModEngine2 package structure and parameter schema verification
"""
import pytest
from pathlib import Path
import json

from tools.ow_doomfist.models import ModelTransformer, ModelPart, BoundingBox
from tools.ow_doomfist.textures import PBRTexturePacker
from tools.ow_doomfist.skills import (
    DoomfistSkillManager,
    RocketPunchSpec,
    RisingUppercutSpec,
    SeismicSlamSpec,
    HandCannonSpec,
)
from tools.ow_doomfist.packager import DoomfistModPackager


def test_doomfist_model_scale_and_coordinate_transform():
    # Overwatch mesh data is typically in Z-up (x: right, y: forward, z: up) in cm or m
    # Elden Ring Dantelion engine expects Y-up (x: right, y: up, z: forward) in metres
    transformer = ModelTransformer(target_height_m=1.95)
    
    raw_vertices_z_up = [
        # (x, y, z) in cm where Z is height (feet at 0, head at 230)
        (0.0, 0.0, 0.0),        # feet
        (0.0, 0.0, 230.0),      # head top
        (45.0, 10.0, 120.0),    # right gauntlet shoulder
        (-40.0, 5.0, 120.0),    # left arm
    ]
    
    transformed = transformer.transform_vertices(raw_vertices_z_up, source_coord_system="ow_z_up_cm")
    
    # In FromSoft Y-up in metres:
    # y must be height, starting from 0.0 up to 1.95m
    y_coords = [v[1] for v in transformed]
    min_y = min(y_coords)
    max_y = max(y_coords)
    assert pytest.approx(min_y, abs=1e-3) == 0.0
    assert pytest.approx(max_y, abs=1e-3) == 1.95
    
    # Gauntlet should be on the right (x > 0)
    gauntlet_v = transformed[2]
    assert gauntlet_v[0] > 0.0  # right side
    assert 0.9 <= gauntlet_v[1] <= 1.2  # around torso/shoulder height


def test_doomfist_pbr_texture_packing(tmp_path):
    packer = PBRTexturePacker()
    
    # FromSoft Dantelion engine expects:
    # Albedo: sRGB BC7 / DXT1
    # Normal: DirectX format (Y-down / Green flipped if source is OpenGL Y-up)
    # Metallic / Roughness: packed into specific channels (R: Metallic, G: Roughness, etc.)
    result = packer.pack_material(
        albedo_rgb=(200, 160, 120),
        normal_gl=(128, 200, 255),  # OpenGL normal with Green pointing up
        roughness=180,
        metallic=220,
    )
    
    # Assert normal map green channel is inverted for DirectX
    assert result["normal_dx"][1] == 255 - 200
    assert result["normal_dx"][0] == 128
    assert result["normal_dx"][2] == 255
    
    # Assert material properties packed properly
    assert result["packed_specular"]["metallic"] == 220
    assert result["packed_specular"]["roughness"] == 180


def test_doomfist_skills_physics_and_timing():
    mgr = DoomfistSkillManager()
    
    # 1. Rocket Punch verification
    rp = mgr.get_rocket_punch()
    assert isinstance(rp, RocketPunchSpec)
    # Must have 3 distinct charge tiers
    assert len(rp.charge_tiers) == 3
    # Max charge tier must provide substantial velocity and knockback
    tier3 = rp.charge_tiers[2]
    assert tier3.charge_time_sec >= 1.0
    assert tier3.dash_velocity_mps >= 18.0
    assert tier3.damage_multiplier >= 3.0
    assert tier3.knockback_impulse >= 15.0
    # Must feature unbreakable hyperarmor during charge and release
    assert rp.hyperarmor_active is True
    assert rp.hyperarmor_poise_multiplier >= 5.0
    
    # 2. Rising Uppercut verification
    up = mgr.get_rising_uppercut()
    assert isinstance(up, RisingUppercutSpec)
    assert up.vertical_launch_velocity_mps >= 8.5
    assert up.launch_enemy_into_air is True
    
    # 3. Seismic Slam verification
    slam = mgr.get_seismic_slam()
    assert isinstance(slam, SeismicSlamSpec)
    assert slam.aoe_radius_m >= 8.0
    assert slam.cone_angle_deg >= 60.0
    assert slam.applies_ground_knockdown is True
    
    # 4. Hand Cannon verification
    hc = mgr.get_hand_cannon()
    assert isinstance(hc, HandCannonSpec)
    assert hc.pellet_count == 4
    assert hc.spread_angle_deg <= 15.0


def test_modengine2_packaging_and_deep_validation(tmp_path):
    packager = DoomfistModPackager(staging_dir=tmp_path / "doomfist_mod")
    pack_result = packager.build_mod_package()
    
    assert pack_result.success is True
    assert pack_result.output_dir.is_dir()
    
    # Deep directory check: ModEngine2 expects parts/ and config
    parts_dir = pack_result.output_dir / "parts"
    assert parts_dir.is_dir()
    
    # Gauntlet weapon part, body armor part, head part
    gauntlet_file = parts_dir / "wp_a_2040.dcx"  # Caestus / Fist ID
    torso_file = parts_dir / "bd_m_2040.dcx"     # Body armor ID
    head_file = parts_dir / "hd_m_2040.dcx"      # Head ID
    
    assert gauntlet_file.is_file()
    assert torso_file.is_file()
    assert head_file.is_file()
    assert gauntlet_file.stat().st_size > 0
    assert torso_file.stat().st_size > 0
    
    # ModEngine2 TOML configuration check
    config_file = pack_result.output_dir / "config_eldenring.toml"
    assert config_file.is_file()
    config_content = config_file.read_text(encoding="utf-8")
    assert "parts" in config_content
    assert "enabled = true" in config_content
    
    # Param patch metadata check (AttackParam, SwordArtsParam, EquipParamWeapon)
    param_patch = pack_result.output_dir / "param_patches.json"
    assert param_patch.is_file()
    data = json.loads(param_patch.read_text(encoding="utf-8"))
    assert "RocketPunch" in data["skills"]
    assert "RisingUppercut" in data["skills"]
    assert "SeismicSlam" in data["skills"]
    assert data["skills"]["RocketPunch"]["knockback_type"] == "KNOCKDOWN_WALL_SLAM"


def test_doomfist_injection_pipeline(tmp_path):
    from tools.ow_doomfist.inject import DoomfistInjector

    game_dir = tmp_path / "ELDEN_RING" / "Game"
    adapter_dir = game_dir / "mods" / "mc_adapter"
    adapter_dir.mkdir(parents=True)

    # Initial mock files
    orig_skin = adapter_dir / "steve.png"
    orig_skin.write_bytes(b"OLD_STEVE_SKIN_BYTES")
    orig_model = adapter_dir / "steve.bbmodel"
    orig_model.write_text('{"name": "steve", "elements": []}', encoding="utf-8")
    cfg_file = game_dir / "mc_er_steve.txt"
    cfg_file.write_text("hide_native=0\nocclusion=0\n", encoding="utf-8")

    injector = DoomfistInjector(game_dir=game_dir)
    report = injector.inject()

    assert report.success is True
    assert report.backup_dir.is_dir()
    assert (report.backup_dir / "steve.png").read_bytes() == b"OLD_STEVE_SKIN_BYTES"

    # Deployed skin must be valid 64x64 PNG
    from PIL import Image
    import io
    deployed_skin = adapter_dir / "steve.png"
    assert deployed_skin.is_file()
    img = Image.open(io.BytesIO(deployed_skin.read_bytes()))
    assert img.size == (64, 64)

    # Deployed model must have Doomfist elements (including gauntlet)
    deployed_model = adapter_dir / "steve.bbmodel"
    model_data = json.loads(deployed_model.read_text(encoding="utf-8"))
    element_names = [e["name"] for e in model_data.get("elements", [])]
    assert "doomfist_gauntlet" in element_names or "right_arm" in element_names

    # Config must ensure native model hidden and occlusion active
    cfg_content = cfg_file.read_text(encoding="utf-8")
    assert "hide_native=1" in cfg_content
    assert "occlusion=1" in cfg_content

    # Param patches must be present
    assert (game_dir / "param_patches.json").is_file()
