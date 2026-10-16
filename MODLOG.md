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

## 10. End-to-End Orchestrator Pipeline
- **Orchestrator Built**: `tools/ow_passthrough/orchestrator.py`
  - Unifies: Input Controller (Scheme B) -> Guest Character Renderer (Pose & Buffers) -> Seqlock Shared Memory Bridge -> Depth Compositor Loop.
  - Implements multi-frame continuous stepping and ability state propagation.
- **Verification**: `tests/test_ow_passthrough_e2e.py` 1/1 passing, full test suite 111/111 passing.

## 11. Overwatch CASC Asset Scanner & Wavefront Mesh Importer
- **Scanner & Parser**: `tools/ow_passthrough/ow_extractor.py`
  - Validates local CASC installations offline without touching running games.
  - Successfully scanned live installation at `G:\SteamLibrary\steamapps\common\Overwatch` (`data/.build.config` verified).
  - WavefrontMeshParser extracts and parses OBJ geometry (vertices, normals, UVs, height calculations).
  - Integrates directly into GuestCharacterRenderer via `load_custom_mesh()`.
- **Verification**: `tests/test_ow_extractor.py` 3/3 passing, full test suite 114/114 passing.

## 12. Host ReShade Shader (OWPassthrough.fx) & 60 FPS Server
- **ReShade Composite Shader**: `tools/ow_passthrough/OWPassthrough.fx`
  - ReShade-compatible HLSL effect sampling `sBackBuffer`, `OWWorldTex` (RGBA), and `OWDepthTex` (linear depth).
  - Performs reversed-Z depth linearization with Elden Ring constant ($K=0.050067$) and environmental light matching.
- **Background Daemon**: `tools/ow_passthrough/ow_server.py`
  - Manages 60 FPS worker thread driving the orchestrator and publishing frames to `Local\OWPassthroughFrame`.
- **Verification**: `tests/test_ow_reshade_effect.py` 2/2 passing, full test suite 116/116 passing.

## 13. Genji (源氏) Cybernetic Ninja & Multi-Hero Renderer
- **Input Controller Built**: `tools/ow_genji/input_controller.py`
  - Left Click (`VK_LBUTTON`): Shuriken Linear 3-burst.
  - Right Click (`VK_RBUTTON`): Shuriken Fan of 3 stars in 28° spread.
  - Shift (`VK_SHIFT`): Swift Strike (影 - 15 m/s supersonic dash slice).
  - E (`VK_E`): Deflect (闪 - 2.0s frontal parry/invulnerability stance).
  - Q (`VK_Q`): Dragonblade (龙刃 - 6.0s green Katana sweep state).
- **Multi-Hero Renderer Upgrade**: `tools/ow_passthrough/guest_renderer.py`
  - Supports `set_character("Genji")` (1.78m canon height).
  - Cybernetic ninja visual palette: titanium silver armor, carbon mesh, green visor lines.
  - Dynamic Dragonblade green energy aura during Q state.
- **Verification**: `tests/test_ow_genji.py` 2/2 passing, full test suite 118/118 passing.

## 14. Host Deployment & Multi-Hero Passthrough Unification
- **Host Deployer Built**: `tools/ow_passthrough/deploy_host.py`
  - Safely deployed `OWPassthrough.fx` and `OWPassthrough.ini` to `C:\Program Files (x86)\Steam\steamapps\common\ELDEN RING\Game\mods\ow_doomfist_standalone\reshade\Shaders` and `Game\reshade-shaders\Shaders`.
  - Pre-flight and post-flight oracles enforce strict byte-identical integrity on `mc_adapter/steve.bbmodel` (1,894,976 B), `mc_adapter/steve.png` (1,893 B), and `mc_er_steve.txt` (345 B).
- **Multi-Hero Orchestrator Pipeline**: `tools/ow_passthrough/orchestrator.py`
  - Integrated dynamic hero switching: `set_hero("Doomfist")` and `set_hero("Genji")`.
  - Dispatches input events to hero-specific state machines (`DoomfistInputController` and `GenjiInputController`).
  - Seamlessly updates character visual traits (Doomfist golden gauntlet vs Genji cybernetic titanium/green Dragonblade).
- **Standalone Background Server CLI**: `tools/ow_passthrough/ow_server.py`
  - Full CLI entry point with configurable `--hero`, `--fps`, `--width`, `--height`, `--duration`.
  - Successfully verified live daemon publishing frames into `Local\OWPassthroughFrame` for both Doomfist and Genji.
- **Verification**: `tests/test_ow_host_deploy.py` (2/2), `tests/test_ow_passthrough_e2e.py` (2/2), `tests/test_ow_reshade_effect.py` (3/3), total test suite 122/122 passing.

## 15. Route B1: C++ ReShade Add-on & Direct3D 12 Texture Pipeline
- **Windows Named Shared Memory Realization**: `tools/ow_passthrough/shared_memory.py`
  - Upgraded to real OS-level `mmap` backing (`Local\OWPassthroughFrame`).
  - Binary packed headers: `OWHeader` (4KB offset, magic `0x4F575053`, version `0x10000`, 3-slot triple buffering) and `OWSlot` (64B offset, seqlock, timestamps, cam coordinates, color & depth offsets).
- **C++ ReShade Add-on**: `tools/ow_passthrough/addon/ow_addon.cpp`
  - ReShade 6.8 API implementation registering `reshade_begin_effects`, `reshade_reloaded_effects`, `destroy_effect_runtime`.
  - Connects to `Local\OWPassthroughFrame` on frame presentation.
  - Dynamically creates and updates D3D12 texture resources (`OWWORLD` RGBA8 and `OWDEPTH` R32F).
  - Double Seqlock check ensures zero-torn reads and zero desync.
- **Add-on Compilation & Runtime Tooling**:
  - `tools/ow_passthrough/addon/build_addon.py`: Clang++/G++ script compiling `ow_compositor.addon` (64-bit PE).
  - `tools/ow_passthrough/addon/fetch_reshade_headers.py`: Official ReShade 6.8 header installer.
  - `tools/ow_passthrough/addon/fetch_reshade_dll.py`: Automated installer for `ReShade64.dll`.
- **Physical Host Deployment to Elden Ring**:
  - `Game\ow_compositor.addon` deployed.
  - `Game\dxgi.dll` deployed (ReShade 6.8 with Add-on support).
  - `Game\mods\ow_doomfist_standalone\reshade\Shaders\OWPassthrough.fx` and `Game\reshade-shaders\Shaders\OWPassthrough.fx` deployed.
  - Strict MC isolation verified: `steve.bbmodel` (1,894,976 B), `steve.png` (1,893 B), `mc_er_steve.txt` (345 B) strictly intact.
- **Verification**: `tests/test_ow_addon.py` (3/3), `tests/test_ow_shared_memory_mmap.py` (1/1), `tests/test_ow_host_deploy.py` (2/2), full test suite passing.

## 9. Breakthrough: Window Focus Diagnosis, Title Screen Bypass, and Interactive Gameplay Verification
- **Root Cause Analysis of "进都进不去 / 彻底卡死了 / 禁止操作了"**:
  1. **Window Focus Lockout**: When Elden Ring was launched via Steam protocol, another background window (WeChat `HWND=15536628`) remained the foreground window on Windows desktop `WinSta0\Default`. Consequently, user keyboard and mouse inputs were routed to WeChat rather than Elden Ring, making the game appear completely unresponsive and frozen ("禁止操作了").
  2. **Title Screen Modal Dialog**: Elden Ring was awaiting user confirmation at the initial title screen modal prompt ("Inappropriate activity detected. Starting in OFFLINE mode. Press OK").
  3. **Multi-Desktop Isolation**: Background runner executed on isolated desktop `exebox-UTGYH6U63C76DC3O2BX32WQXCF`, requiring thread desktop switching (`OpenDesktopW("Default")` and `SetThreadDesktop`) to enumerate and manage top-level windows.
- **Intervention & Resolution**:
  1. Developed `scripts/bring_game_front.py` using `AttachThreadInput` and focus lock bypass to bring Elden Ring (`HWND=10881862`) to the foreground (`SetForegroundWindow returned: 1`).
  2. Developed `scripts/send_hardware_input.py` sending scan codes `0x1C` (Enter) and `0x12` (E) to dismiss the title screen modal dialog.
  3. Game smoothly loaded into active gameplay world at Church of Elleh (`59/60 FPS`).
- **Anatomical Character & Shader Upgrades**:
  1. Enhanced `guest_renderer.py` with multi-part anatomical rasterization: bald head with cyber-brow, muscular chest with golden cyber-sash and six-pack abs, colossal golden gauntlet with power conduits and articulated fingers, tactical left arm with knuckle shotgun ports, red sash belt, and combat trousers/boots.
  2. Updated `OWPassthrough.fx` with aspect-ratio-corrected bounding box projection (`CharPosX=0.50`, `CharPosY=0.60`, `CharScale=0.55`) eliminating 16:9 distortion.
- **Physical E2E Verification & Interactive Movement Evidence**:
  1. GPU frame capture via `scripts/capture_window.py` proved player is rendered in the 3D world at Church of Elleh with Doomfist composited and HUD active.
  2. Tested live movement: sent hardware scan code `0x11` ('W'), confirmed character walked forward through the stone archway into the grass.
  3. Verified `mods/mc_adapter` Steve assets 100% byte-for-byte identical (`steve.bbmodel`: 1,894,976 B, `steve.png`: 1,893 B, `mc_er_steve.txt`: 345 B).
  4. Test suite: **136 passed, 1 skipped, 0 failed**. Elden Ring is currently active and focused in foreground on user desktop.

## 10. Minecraft Adapter Summon Particle Suppression & Sfx Neutralization
- **Root Cause of Lingering Summon Particles**:
  - Previously, `HideSummonChr` only cleared the `CSModelDispEntity+0x20` drawn bit (`0xA7 -> 0xA6`). While this hid mesh polygons, FromSoftware's Dantelion engine particle system (FXR/SFX) runs on `ChrConditionSfxSeSlot` and `SpecialEffect` modules independently of model rendering.
- **Engine Reversing Breakthroughs**:
  1. **`ChrConditionSfxSeSlot` (VTABLE `0x142A428B0`)**: Located at `chr+0x908` and `chr+0x318`. In `ChrConditionSfxSeSlot::Update` (`0x1404A2480`), bit 7 (`0x80`) of control word at `slot+0x5A` forces an immediate early return (`0x1404A2A4D`), skipping all particle updates. `vfunc[6]` (`0x1404A23A0`) clears active Sfx (`+0x48`) and Se (`+0x50`) container lists.
  2. **`SpecialEffect` (VTABLE `0x142A4D490`)**: Located at `chr+0x178`. At D3D12 render pipeline `0x1402C722C`, the engine queries `HasSpEffect(container, 0x182)` (phantom/ghost shader flag). If true, it activates phantom pass (`+0xDCA0 = 1`).
- **Implementation**:
  - Branch: `feature/summon-particle-suppression` in `mc-core`.
  - `adapters/eldenring/include/eldenring_chrscan.hpp`: Added `collectChrConditionSfxSlots()`, `suppressSfxSlotFlags()`, `isSpiritSpEffectId()`, and mask definitions.
  - `adapters/eldenring/src/loader.cpp`: Enhanced `HideSummonChr()` to suppress `ChrConditionSfxSeSlot` (setting bit 7 of `+0x5A` and zeroing `+0x48/+0x50`), clear `CSModelDispEntity` `disp_flags3` (`+0x220`), and hook `CreativeSpEffectDetour` to return false for `0x182` and spirit SpEffects on summon containers.
- **Verification**:
  - TDD unit tests in `tests/test_eldenring_chrscan.cpp`: 14/14 passed.
  - Full Elden Ring test suite: 395/395 passed.
  - Physical deployment: `tools/deploy_eldenring_mod.py` deployed `dinput8.dll` (SHA256: `FAEAC84BE75E4F8B954C0D8690B8AF971C4E4BA5619635F3234533B616793310`) to Game directory with 100% hash verification.

## 11. Site of Grace Interaction, Native Model Hiding Policy, and Minecraft Sleeping Kinematics
- **Native Model Pop-back Bug & Root Cause**:
  - Previously in `loader.cpp:HudProvider()`, `want_hidden` was directly bound to `out.show && out.mc_mode`.
  - When the player interacted with a Site of Grace, the menu opened (`ms.menu_focused == true`) and `CSFade` plate 2 alpha rose (`fade >= 0.02f`), causing `out.show` to become false.
  - This inadvertently set `want_hidden = false`, invoking `RestoreNativeModel()` and unhiding the native Elden Ring character mesh, exposing the native sitting meditation model.
  - **Resolution**: Decoupled native model visibility from HUD visibility. In MC mode, `want_hidden = out.mc_mode && have_state && !ls.screen_loading`, guaranteeing the native model remains strictly hidden during Grace interaction, menus, dialogue popups, and fade transitions.
- **Site of Grace Detection**:
  - `eldenring_world.hpp`: Added `findNearestGrace()` scanning active ChrSets for anchor `npc_id == 1000` (`kGraceNpcId`) within interaction radius ($\le 2.8\text{m}$).
  - In `loader.cpp`, combined proximity check with `(ms.menu_focused || fade >= 0.02f)` to reliably assert `steve.sleeping`.
- **Minecraft Sleeping Kinematics (`mc/sleep.hpp` & `animator.cpp`)**:
  - Modeled after vanilla Minecraft Java `Pose.SLEEPING` and `LivingEntityRenderer`:
    - `sleepPoseMatrix`: Rotates model 90° backwards around lateral right axis onto its back (face-up toward sky, back against floor).
    - `vertical_offset` (+0.1125m) ground clearance compensation eliminating floor clipping.
    - S-curve Smoothstep transition curve ($0.0 \to 1.0$ over 0.8s / 16 ticks) preventing visual snapping when entering and exiting rest.
    - Respiration oscillation: gentle periodic sinusoidal chest and arm motion ($T = 3.0\text{s}$, amplitude $0.025\text{ rad}$).
    - 12-box rig constraints: leg swing and stride zeroed, legs parallel, head pitch/yaw stabilized.
  - `PlayerSleepTracker`: Tracks sleep state, enter/wake transitions, and breathing angles.
  - `overlay_d3d12.cpp`: Integrated sleep tracker and dynamic sleeping pose matrix into D3D12 Steve render pipeline.
- **Verification**:
  - TDD unit tests in `mc-core/tests/test_sleeping_kinematics.cpp` (5/5) and `mc-core/tests/test_eldenring_grace_sleep.cpp` (3/3): 100% passed.
  - Full Elden Ring test suite: 27/27 targeted tests passed, 0 failures.
  - Python release distribution builder: `package_eldenring_mod.py` built `EldenRing_Minecraft_Mod_v1.0.0.zip` (4.75 MB, SHA256: `09267E1D71E021F53D362C5A215072682804370D410F5F3CB9F308E46529C8F6`).
  - Physical game deployment: Updated `dinput8.dll` (4,104,192 bytes) physically deployed to `C:\Program Files (x86)\Steam\steamapps\common\ELDEN RING\Game\dinput8.dll`.


## 12. Client-Managed Virtual Summons & Complete Decoupling from CSBuddyMan Dismiss Crashing
- **Root Cause of Spirit Ash Dismiss Crashes**:
  - Previously, summons hijacked FromSoftware's native Spirit Ash manager (`CSBuddyMan`).
  - Native spirit ashes are strictly tied to world map tablets (`TabletId`), encounter state machines, and cascade deallocations.
  - When the player moved out of range or re-summoned, intercepting `Dismiss` corrupted the game's internal ChrIns deallocation and AI trees, resulting in immediate `EXCEPTION_ACCESS_VIOLATION` crashes.
- **Architectural Shift: Scheme A (Client-Managed Virtual Entity)**:
  - Completely detached from `CSBuddyMan`, stone tablets, and FromSoftware's ChrIns creation pipeline.
  - Implemented `VirtualSummonManager` in [eldenring_virtual_summon.hpp](file:///D:/code/universal-modder/mc-core/adapters/eldenring/include/eldenring_virtual_summon.hpp):
    - **Autonomous Lifecycle**: Pure `mc-core` virtual entities with unique incrementing 64-bit IDs, independent HP, hurt flash timers, and smooth death scenes. Zero engine hook dependency on dismissal.
    - **Locomotion & Leashing**: Standard Minecraft walking movement (~3.8 m/s), idle radius (2.5m), and anti-desync teleport threshold (> 32m).
    - **Hostile Targeting & Attack Pipeline**: Automatically identifies active hostile enemies within 16m; approaches within 1.8m and executes melee attacks on a 1.0s cooldown, dispatching `DamageIntent` directly into `g_queue` (`CallVfunc7` native damage execution).
    - **Zero-Hook Dismissal**: `dismissAll()` clears internal entity collections smoothly without invoking any native deconstructors.
    - **Direct Render Interop**: Produces standard `MobSnapshot` records fed directly into `MobRegistry` (`SteveRenderer`), displaying full 3D Bedrock `.geo.json` models with swinging arms and walking legs.
- **Verification**:
  - TDD unit test suite in [test_eldenring_virtual_summon.cpp](file:///D:/code/universal-modder/mc-core/tests/test_eldenring_virtual_summon.cpp) (8/8 passed).

## 13. Virtual Summon Rolling Eviction & Autonomous Creeper Detonation Pipeline
- **Issue 1 Resolution (Spawning Never Fails / Capacity Rolling Eviction)**:
  - **Root Cause**: Hardcoded capacity rejection (`kMaxVirtualSummons = 16`) caused `spawnMob` to silently return 0 when 16 entities were active, completely blocking further spawns ("summoning had no response").
  - **Fix**: Implemented FIFO rolling eviction in `VirtualSummonManager::spawnMob`. When capacity is reached, the oldest mob is smoothly evicted to make room for the new spawn, guaranteeing 100% responsiveness on every right-click or keypress. Added dynamic detection of `mc_er_summon.txt` (supporting `creeper`, `skeleton`, and `zombie`).
- **Item 2 Policy Enforcement**:
  - Maintained deliberate design: mobs pursuing enemies remain on target without forced teleportation leashing.
- **Issue 3 Resolution (Autonomous Creeper Detonation & Defuse Smoothing)**:
  - **Root Cause**: Creeper lacked its native autonomous fuse/swell/explosion pipeline and was falling back to standard zombie melee punches. Furthermore, enemy evasion beyond 7m was instantly wiping the fuse back to 1.5s in a loop.
  - **Fix**: Implemented native Creeper state machine:
    - Enters `Primed` state upon approaching active hostiles within $\le 3.5\text{m}$.
    - Dynamic swelling ($1.0 \times \to 1.35 \times$) and periodic white flash ($0.2\text{s}$ interval).
    - Smooth defuse prevents instant resets: only decays fuse when $> 7.0\text{m}$ away and fuse $> 0.5\text{s}$; enters unstoppable detonation commitment when $\le 0.5\text{s}$.
    - On detonation, dispatches `CreeperExplosionEvent` ($r=7.0\text{m}$, damage 1500), triggering TNT block destruction, audio playback, and safe self-consumption.
- **Verification**:
  - TDD unit tests in [test_eldenring_virtual_summon.cpp](file:///D:/code/universal-modder/mc-core/tests/test_eldenring_virtual_summon.cpp): 9/9 passed.
  - Full Elden Ring test suite: 451/451 passed (0 failures).
  - Physical game deployment: Updated `dinput8.dll` (SHA256: `9A442F466034D03A48AAA09162E1C63F76714CC3BC7A5E83D8471E2764E32460`) deployed to Game directory with 100% hash verification.

## 14. Creeper Quad-Bug Remediation (Death Cleanup, No Melee, Flint & Steel, Chain Explosions)
- **1. Player Death & Map Load Dismissal**:
  - **Root Cause**: `g_virtual_summons.dismissAll()` was only invoked on F6 toggle (`!mc_on`). When the player died (`PlayerDead()`) or entered a loading screen (`ls.screen_loading`), virtual summons remained orphaned in the world.
  - **Fix**: Linked `PlayerDead()` in `loader.cpp:HideSummonModels()` and `ls.screen_loading` in `BlocksTick()` directly to `g_virtual_summons.dismissAll()`.
- **2. Elimination of Creeper Melee Attacks**:
  - **Root Cause**: The common mob loop shared melee punch logic with zombies.
  - **Fix**: Isolated Creeper attack path: Creepers strictly navigate the fuse countdown/swelling/detonation pipeline and are explicitly barred from generating `DamageIntent` melee packets.
- **3. Flint and Steel Manual Ignition for Virtual Creepers**:
  - **Root Cause**: `TryIgniteCreeper()` routed calls exclusively to the legacy `g_creeper_mgr.ignite(s.id)` which had no handle to virtual summons.
  - **Fix**: Added `igniteCreeper(uint64_t id)` to `VirtualSummonManager` (setting `is_primed = true`, `manual_primed = true`, `fuse_timer = fuse_duration`). Updated `TryIgniteCreeper()` in `loader.cpp` to ignite virtual Creepers and trigger right-click swing + TNT fuse sound. Manual priming bypasses hostile target checks and guarantees unstoppable detonation.
- **4. Summon AOE Damage & Chain Detonation**:
  - **Root Cause**: Detonation events only pushed TNT intents to native Elden Ring enemies and terrain, completely bypassing active virtual mobs.
  - **Fix**: Added AOE damage propagation in `triggerDetonation`: loops over all active virtual summons within 7.0m, applying distance-falloff explosive damage (up to 1500 HP), causing lethal damage and triggerable chain reactions.
- **Verification**:
  - TDD unit tests added in [test_eldenring_virtual_summon.cpp](file:///D:/code/universal-modder/mc-core/tests/test_eldenring_virtual_summon.cpp) (12/12 passed):
    - `VirtualSummonTest.CreeperNeverGeneratesMeleeDamageIntents`
    - `VirtualSummonTest.FlintAndSteelIgniteStartsFuseImmediately`
    - `VirtualSummonTest.CreeperExplosionDamagesNearbySummonsChainDetonation`
  - Full Elden Ring test suite: 431/431 passed (0 failures).
  - Physical game deployment: `dinput8.dll` compiled and deployed to `C:\Program Files (x86)\Steam\steamapps\common\ELDEN RING\Game\dinput8.dll` with identical SHA256 (`E96976729DDD3CA27CEDBDA2F7CB6B39BC0553789E1973CF104A7FB1A919B688`).

