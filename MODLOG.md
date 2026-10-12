# Modding Log: Overwatch Doomfist & Genji in Elden Ring

## 1. Intake & Recon
- **Host**: Elden Ring (Steam AppID: 1245620), Dantelion Engine (DirectX 12), located at `C:\Program Files (x86)\Steam\steamapps\common\ELDEN RING\Game`.
  - Anti-cheat: EasyAntiCheat. Launch offline only via ModEngine2 / launcher bypass.
- **Guest**: Overwatch 2 (Steam AppID: 2357570), located at `G:\SteamLibrary\steamapps\common\Overwatch`.
  - Online live-service game protected by Blizzard anti-cheat.
  - **Safety Policy**: Offline extraction only (`Overwatch/data`), strictly zero injection or hooking of the online `Overwatch.exe` process.

## 2. Route Selected: Pattern 1 (Asset & Content Port + Parameter Mapping)
- **Why**: Native FromSoftware rendering, PBR material lighting, zero ban risk, native ragdoll, full physics & combat hitboxes.
- **Characters**: Starting with Doomfist (铁拳 - Akande Ogundimu), followed by Genji (源氏).

## 3. Character & Skill Mechanics Contract
- **Doomfist (铁拳)**:
  - Canonical Height: 1.95m. Coordinate transformation from OW (Z-up, cm) to Elden Ring (Y-up, m).
  - PBR Texture Packing: DirectX Y-down normal mapping (invert Green), specular/metallic/roughness channel packing.
  - **Rocket Punch (火箭重拳)**: 3-tier charge, unbreakable hyperarmor, forward displacement dash (up to 20.5 m/s), 3.6x damage multiplier, wall-slam knockdown impulse.
  - **Rising Uppercut (上勾拳)**: 9.5 m/s vertical impulse, lifts both player and target airborne.
  - **Seismic Slam (裂地重击)**: 7.5m forward leap, 9.0m 65° shockwave cone, applies knockdown.
  - **Hand Cannon (手炮)**: 4 pellets shotgun spread (12° cone), rapid left-hand projectile.

## 4. Pipeline Modules Created
- `tools/ow_doomfist/models.py`: BoundingBox, ModelTransformer (OW Z-up cm -> ER Y-up m, 1.95m normalization).
- `tools/ow_doomfist/textures.py`: PBRTexturePacker (DirectX normal conversion & channel packing).
- `tools/ow_doomfist/skills.py`: DoomfistSkillManager & physical parameters.
- `tools/ow_doomfist/packager.py`: DoomfistModPackager (ModEngine2 packaging, parts generation, TOML config).
- `tests/test_ow_doomfist.py`: TDD test suite validating coordinate transformation, texture packing, skill physics, and packaging.
