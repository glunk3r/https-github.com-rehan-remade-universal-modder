# Crash Time 5 (Alarm für Cobra 11 – Crash Time 5, 2012 Original) — Teardown Documentation

**Game:** Crash Time 5 (Alarm für Cobra 11, 2012 original 32-bit release)  
**Platform:** PC (Windows, Germany En/De ISO, Ashampoo UDF)  
**Developer:** Synetic GmbH (German)  
**Publisher:** RTL Games / dtp entertainment  
**Year:** 2012 (game exes dated Sep 3, 2012)  
**Engine:** Synetic 3D Landscape Engine (final 32-bit iteration)

> Distinct from the Steam-era 64-bit rerelease (see `CRASH_TIME_UNDERCOVER_TEARDOWN.md`). The `Undercover` name tie is addressed there.

---

## 1. Game Engine

**Engine:** Synetic 3D Landscape Engine (verified in shipping exe strings)  
- **Middleware (verified):**
  - **FMOD Ex** (×78: `fmodEventSystem->unload()`, `FMOD Load Event`, `traffic.fev`/`autos.fev`/`enginegeneric.fev`, full C++ API imports, `e:\philippe\code\fmodlibfromsource\together\fmod4\` build paths)
  - **Lua 5.1.2** (version string compiled in: `$Lua: Lua 5.1.2 Copyright (C) 1994-2007 Lua.org, PUC-Rio` — first Lua in the Synetic lineage)
  - **DirectX 9** (`D3DX` ×2; DX redist + WMCodec installers on disc)
- **Executables:** `CrashTime5Hi.exe` (7.28 MB) + `CrashTime5Lo.exe` (7.28 MB, detail tiers) + `CT5_Config.exe` + `StartUp.exe` + `setup.exe` (+ `crack\` scene-cracked Hi/Lo, Oct 2012)
- **Physics:** Custom damage system (`DAM_CRASH_*` ×6) — **no ODE** (`ODEConfig`/`PHYSICS_*` absent; `ODE` ×37 = encoding/HTTP/FMOD-source noise)
- **Assets:** `.mox` ×54 refs, `.xml` ×84 refs (data-driven configs), `.ptx` textures
- **Video:** `.pam` (`Videos\dtp.pam|rtl.pam|Synetic.pam`) — Bink traces only (`Logos\Bink.tga`, `ps_Bink.ps` shader), `.bik` ×0, playback unconfirmed
- **Scripting:** **Lua 5.1.2**

**Falsified:** `VehicleDamage::*`, `TrackEditor*`, `PHYSICS_*` (×0). `Nx` ×42 = opcode noise. `fmod` ×119 mostly FMOD-source paths + some CRT. No Havok/PhysX/Miles/Ogg/Vorbis/XAudio/SecuROM/Steam/Denuvo/CRI strings.

---

## 2. File Formats (from installed-loose-dump + ISO)

Loose install layout (`.mox`/`.mtl` models, `.ptx` textures, `.trf` track refs, `.cpo` collision, `.xml` weapon/HUD/evidence defs, `.wav`/FMOD banks). ISO: installer (`setup-1/2/3.bin`), `Autoupdate/`, `Manual/`, `Support/`, DirectX + WMCodec redist roots.

---

## 3. Key Technical Details

- **Hi/Lo detail-split shipping builds** (7.28 MB each) + config tool + launcher
- **FMOD event system** (`traffic/autos/enginegeneric.fev`) replaces the DirectSound era — biggest audio upgrade in the lineage
- **Lua 5.1.2 debut** in Synetic tech (exact PUC-Rio version string)
- **Zero-middleware-except-FMOD/Lua**: no physics/video/security middleware in strings

---

*Generated from `Crash Time 5 Undercover.iso` (`Data\! base\CrashTime5Hi.exe`, Sep 2012)*  
*Engine: Synetic 3D Landscape Engine, Synetic GmbH 2012 — https://www.pcgamingwiki.com/wiki/Engine:3D_Landscape_Engine*