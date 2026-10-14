# Need for Speed: ProStreet (PC) — Teardown Documentation

**Game:** Need for Speed: ProStreet  
**Platform:** PC (Windows)  
**Developer:** EA Black Box  
**Publisher:** Electronic Arts  
**Year:** 2007  
**Engine:** EAGL4 (EA Graphics Library, RenderWare lineage)

---

## 1. Game Engine

**Engine:** EAGL4 (verified: `EAGL4::DynamicLoader CAnimBank`/`CAnimSkeleton` ×44 in exe)  
- **Middleware (verified via binary evidence):**
  - **RenderWare Audio Core** (pitch-sync discussion strings + `RWAudioCore ... XAudio voice` output path — EAGL's RW-derived audio)
  - **Lua** (×28: `PSLuaBinder`, `ILuaBindable`, `LuaCall:raceover/sms/bust load/loading` + `scripts/` dir — gameplay event scripting)
  - **SecuROM** (×46: `SecuROM_pa_web/activation` URLs for Sony DADC online activation — real DRM)
  - **DirectX 9** (`D3DX` ×934 — heavy shader use)
- **Executable:** `nfs.exe` (28,739,656 bytes, unpacked)
- **Physics:** In-house (no Havok/PhysX strings; EAGL-era custom vehicle physics)
- **Scripting:** Lua (race events, SMS, busts, loading)

**Falsified:** `Miles` ×6 = `MilestoneInfoMap`/`MNotifyMilestone*` (career strings, not RAD Miles). `fmod` ×5 = CRT math. No `BlackBox`, FMOD, Bink DLL (no `binkw32.dll` in dump), Havok, Steam strings.

**Evidence from dump:**
- Modded install: `dinput8.dll` (2.2 MB ASI loader) + `scripts/` (mod scripts) + `server.dll`/`server.cfg`/`NFSPS_run_1_core.bat` (NFSPS online-server emulator) — third-party mod artifacts, not game tech
- Toolchain: VC80 CRT + `msvcp71`/`msvcr71` (2003) side by side
- 16 asset dirs: `CARS/`, `TRACKS/`, `SOUND/`, `MOVIES/`, `LANGUAGES/`, `MINI_MAPS/`, `NIS/`, `ONLINE/`, `PB/`, `GLOBAL/`, `FRONTEND/`, `AIRACELINES/`, `MEMCARD/`, `SUBTITLES/`, `Credits/`, `Uninstall/`

---

## 2. File Formats

| Format | Description |
|---|---|
| EAGL containers | `CARS/`, `TRACKS/`, packed game data |
| `SOUND/` | RWAudioCore banks |
| `MOVIES/` | Cutscene video (no Bink DLL shipped) |
| `scripts/` | Lua mod scripts (mod-added) |
| `.nfo` / `.cfg` / `.bat` | Mod/server-emu artifacts (`battery.nfo`, `server.cfg`) |

---

## 3. Key Technical Details

- **EAGL4 on RenderWare lineage**: engine classes + RW Audio Core in one binary — the EA Black Box stack at its peak
- **Lua-bound gameplay events** (`LuaCall:raceover/sms/bust`) — drag/race-mode scripting surface modders still hook today
- **SecuROM online activation** (Sony DADC URLs) — period EA DRM, since sunset

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Need for Speed ProStreet\`*  
*Engine: EAGL4 (RenderWare lineage), EA Black Box 2007*