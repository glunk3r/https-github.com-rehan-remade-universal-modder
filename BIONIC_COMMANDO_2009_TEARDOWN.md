# Bionic Commando (PC, 2009) — Teardown Documentation

**Game:** Bionic Commando  
**Platform:** PC (Windows)  
**Developer:** GRIN  
**Publisher:** Eidos Interactive  
**Year:** 2009  
**Engine:** GRIN Diesel Engine

---

## 1. Game Engine

**Engine:** GRIN Diesel Engine (verified: `Diesel` ×5, `GRIN` ×4 in exe; `dieselx.cfg` + `context.xml` boot config)  
- **Middleware (verified via binary/config/DLL evidence):**
  - **PhysX** (`PhysX` ×9, `NxCooking` ×2 + `NxCooking.dll`; `physx_effects=hardware`, `nx_hint_collision_speed` in configs)
  - **Bink Video** (`Bink` ×38 + `binkw32.dll`; 25 `.bik` movies in `data/`)
  - **Lua** (`.lua` ×61 + `mainmenu` ×23 inside `quick.bundle`; `memory_lua_limit = 25` in `dieselx.cfg`; script exec `menu/mainmenu/mainmenu` in `context.xml`)
  - **OpenAL + Ogg** (`offset() not supported for OggStreams` — OpenAL audio path)
  - **SecuROM** (×27 — DRM)
  - **DirectX 9/10** (`D3DX` ×4; `ati/nv_dx10_*`, `dx10_debug` in cfg)
- **Executable:** `bionic_commando.exe` (22,528,512 bytes) + `Launcher.exe`
- **Container:** `BNDL` v2 (`quick.bundle` 445 MB, `stream.bundle`, `stream_disc.bundle`) + per-level `.fcl` chunks (60+: `city_*`, `fissure_*`, `flood_*`, `harbor_*`, `park_*`, `mp_*`, `boss_*`, `tutorial_*`) + `game.lhd` build manifest (`Z:\boot compile...`)
- **Scripting:** **Lua** (bundled scripts)
- **Physics:** PhysX, 60 fps (`fps="60"`, multithreaded, fluids off)

**Falsified:** `luaL_`/`lua_State` ×0 (statically linked/stripped Lua — scripts live in bundles, not the exe). `fmod` ×3 = CRT math. No Havok/FMOD/Miles/Steam/Emergent/Unreal.

**Evidence from dump (`context.xml` — Diesel boot config):**
- Script base `data`, GUI in `\data\gui` (optimized), effects/particles TNG multithreaded, texture DB + static scope, animation state machines, camera effects, `use_rendez_vous=true`, shader templates, global materials `global_v2`

---

## 2. File Formats

| Format | Description |
|---|---|
| `.bundle` (`BNDL` v2) | Main archives (quick/stream/stream_disc) |
| `.fcl` | Per-level bundle chunks (MP maps included) |
| `.lhd` | Build manifest |
| `.bik` | Movies (25, in `data/`) |
| `.lua` (in-bundle) | Game scripts (61 refs) |
| `.cfg` / `.xml` / `.dat` | `dieselx.cfg`, `context.xml`, `Lang.dat` |

---

## 3. Key Technical Details

- **Diesel config pair** (`dieselx.cfg` + `context.xml`) identical in role to Rearmed's — same engine family, full-game scale (multiplayer maps, 60 fps hardware PhysX)
- **Version:** `ver 1.005 euna_en` (EU NA English)
- No Steamworks (GFWL/SecuROM era)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Bionic Commando\`*  
*Engine: GRIN Diesel Engine — https://www.pcgamingwiki.com/wiki/Engine:Diesel*