# Crash Time: Undercover (Steam 64-bit Rerelease) — Teardown Documentation

**Game:** Crash Time: Undercover (Steam-era 64-bit rerelease; product manifest name)  
**Platform:** PC (Windows 64-bit, Steam AppID 1687700)  
**Developer:** Synetic GmbH (German)  
**Publisher:** Unknown (Steam release)  
**Year:** Unknown (Steam era; 64-bit + Steamworks = post-2012 rerelease)  
**Engine:** Synetic 3D Landscape Engine (64-bit rerelease build)

> Distinct release from **Crash Time 5** (2012 32-bit original — see `CRASH_TIME_5_TEARDOWN.md`). Same lineage, materially different build: 64-bit, `.pak` containers, FMOD64, Steamworks. Binary named `CrashTime5.exe`; product manifest reads `Crash Time Undercover`.

---

## 1. Game Engine

**Engine:** Synetic 3D Landscape Engine (verified: `Synetic` ×1 in exe)  
- **Middleware (verified):**
  - **FMOD Ex 64-bit** (×94: `fmodEventSystem`, `traffic.fev`/`autos.fev`/`enginegeneric.fev`, + `fmodex64.dll`/`fmod_event64.dll`/`fmod_event_net64.dll`)
  - **Steamworks** (×32: `SteamUser021`, `SteamUtils010`, user-stats interfaces + `steam_api64.dll` + AppID 1687700)
  - **DirectX 9** (`D3DX9_43.dll`, `D3DCompiler_43.dll`)
- **Executables:** `Bin\Win64\CrashTime5.exe` (5,052,928 bytes) + `Benchmark.exe` + `Launcher\GameLauncher.exe` (modern SkiaSharp/HarfBuzz launcher)
- **Container:** `.pak` era (`Data\Data000.pak`–`Data012.pak`: `Loading packages...`, `Cannot add '%s' to filesystem`)
- **Assets:** `.mox` ×54 refs (models carried over)
- **Physics:** Custom damage system (`DAM_CRASH_*` ×6) — **no ODE** (`ODEConfig`/`PHYSICS_*` absent; `ODE` ×2 = `UNICODE`/`ENEMIES_DESTROYED` substrings)
- **Video:** No Bink (`.bik` ×0, no Bink strings)
- **Scripting:** None evidenced in exe (Lua ×16 = code-byte noise; no Lua version/API strings unlike the 2012 original)

**Falsified:** `Nx` ×42 = opcode noise. No Havok/PhysX/Miles/Ogg/Vorbis/XAudio/SecuROM/Denuvo/CRI.

**Steam-emu crack artifacts (not game tech):** `steam_api64.org` (original DLL backup), `steam_api.ini`, `steamclient64.dll`, `steam_64.dll`.

---

## 2. Key Technical Details

- **64-bit rerelease** of the Synetic lineage: `.pak` containers replace loose files, Steamworks replaces the disc era, FMOD goes 64-bit
- **Bink dropped** vs the 2012 original (no `.bik`, no Bink strings)
- **Lua dropped** vs the 2012 original (no Lua version string; ×16 noise only)

---

*Generated from `Crash.Time.Undercover.zip` (`Bin\Win64\CrashTime5.exe` + `Launcher\steam_appid.txt` = 1687700)*  
*Engine: Synetic 3D Landscape Engine (64-bit rerelease) — https://www.pcgamingwiki.com/wiki/Engine:3D_Landscape_Engine*