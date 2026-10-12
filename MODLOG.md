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
- `tools/ow_doomfist/inject.py`: DoomfistInjector (deploys character model, skin, config, sentinel flags, param patches).
- `tools/ow_doomfist/run_inject.py`: CLI entrypoint for physical deployment.
- `tests/test_ow_doomfist.py`: TDD test suite validating coordinate transformation, texture packing, skill physics, packaging, and injection.

## 5. Physical Deployment & Verification
- **Target**: `C:\Program Files (x86)\Steam\steamapps\common\ELDEN RING\Game`
- **Backup Created**: `mods\mc_adapter\backup_before_doomfist\` (backed up `steve.png`, `steve.bbmodel`, `mc_er_steve.txt`).
- **Files Deployed**:
  - `mods\mc_adapter\steve.png`: 64x64 Doomfist PBR character skin (Akande Ogundimu cybernetics, crimson combat sash, golden gauntlet on right arm).
  - `mods\mc_adapter\steve.bbmodel` & `doomfist.bbmodel`: 3D model with expanded Doomfist gauntlet geometry.
  - `mc_er_steve.txt`: Configuration updated with `hide_native=1`, `occlusion=1`, `abs_bias=0.05` for native character hiding and D3D12 depth occlusion.
  - `mc_er_overlay.txt` & `mc_er_damage.txt`: Sentinel files active.
  - `param_patches.json`: Structured parameter patch manifest for Doomfist combat abilities.
- **Verification**: Exit code 0, physical files verified on disk, full test suite passing (94 passed).

## 6. Scheme B Input Mapping (OW PC Native Keybindings) & MC Restoration
- **Restoration**: The original Minecraft files in `mods/mc_adapter` were 100% restored byte-for-byte from backup (`steve.bbmodel`: 1,894,976 bytes, `steve.png`: 1,893 bytes, `mc_er_steve.txt`: 345 bytes).
- **Scheme B Architecture**: Dedicated input controller (`tools/ow_doomfist/input_controller.py`) decoupled from Minecraft code:
  - `VK_RBUTTON` (Right Click): Hold to charge Rocket Punch, release to fire dash (tier 1..3).
  - `VK_SHIFT` (Shift): Seismic Slam forward leap & shockwave.
  - `VK_E` (E): Rising Uppercut vertical launch.
  - `VK_LBUTTON` (Left Click): Hand Cannon 4-pellet shotgun blast.
  - `VK_Q` (Q): Meteor Strike ultimate.
- **Verification**: `tests/test_ow_doomfist_input.py` 5/5 passing, full test suite 99/99 passing.

## 7. Standalone Overwatch Doomfist Mod (Complete Isolation)
- **Architecture**:
  - `tools/ow_doomfist_standalone/flver_converter.py`: FromSoftware FLVER 2.0 (Fast Lightweight Vertex Format) and DCX (Deflate Compressed Stream) binary packer.
  - `tools/ow_doomfist_standalone/mod_packager.py`: Isolated packager generating `mods/ow_doomfist_standalone/parts/` and ModEngine2 config.
  - `tools/ow_doomfist_standalone/run_deploy.py`: Deployment runner verifying pre-flight and post-flight intactness of `mc_adapter`.
- **Physical Output in Game**:
  - `mods\ow_doomfist_standalone\parts\wp_a_2040.dcx` (Caestus / Golden Gauntlet)
  - `mods\ow_doomfist_standalone\parts\bd_m_2040.dcx` (Torso cybernetic armor)
  - `mods\ow_doomfist_standalone\parts\hd_m_2040.dcx` (Head cyber brow)
  - `mods\ow_doomfist_standalone\parts\lg_m_2040.dcx` (Tactical combat pants & boots)
  - `mods\ow_doomfist_standalone\parts\am_m_2040.dcx` (Arms & cables)
  - `mods\ow_doomfist_standalone\config_eldenring.toml` (ModEngine2 standalone config)
  - `mods\ow_doomfist_standalone\ow_input_config.json` (Scheme B keybindings)
- **Isolation Verification**: `mc_adapter/steve.bbmodel` strictly confirmed byte-identical (1,894,976 bytes). Full test suite 102/102 passing.

## 8. Passthrough Bridge Architecture & Contract (docs/CONTRACT.md)
- **Contract Signed**: `docs/CONTRACT.md` establishes formal ownership, coordinate mapping, seqlock protocol, and reverse-Z occlusion.
- **Components Built**:
  - `tools/ow_passthrough/shared_memory.py`: Seqlock-protected triple-buffer shared memory transport (`Local\OWPassthroughFrame`).
  - `tools/ow_passthrough/compositor.py`: Reversed-Z depth testing ($Z_{\text{linear}} = K / D_{\text{revZ}}$).
  - `tools/ow_passthrough/compositor_shader.hlsl`: D3D12/ReShade pixel shader with depth clipping and transparency discarding.
- **Verification**: `tests/test_ow_passthrough_contract.py` 4/4 passing, full test suite 106/106 passing.

## 9. Guest Character Renderer & Real-time Frame Publishing
- **Renderer Built**: `tools/ow_passthrough/guest_renderer.py`
  - Loads character 3D geometry (1.95m canonical Doomfist scale).
  - Renders RGBA8 color with transparent background cutout.
  - Generates R32F floating-point linear depth buffer matching camera viewpoint distance.
  - Dynamic posture updates responding to Scheme B abilities (Rocket Punch charge wind-up & dash thrust).
  - Publishes frames into Seqlock shared memory bridge (`Local\OWPassthroughFrame`).
- **Verification**: `tests/test_ow_guest_renderer.py` 4/4 passing, full test suite 110/110 passing.
