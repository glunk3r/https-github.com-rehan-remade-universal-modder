# Race Driver: GRID (PC) — Teardown Documentation

**Game:** Race Driver: GRID  
**Platform:** PC (Windows)  
**Developer:** Codemasters  
**Publisher:** Codemasters  
**Year:** 2008  
**Engine:** EGO Engine (Neon lineage)

---

## 1. Game Engine

**Engine:** EGO Engine (Neon lineage — `Neon Thread` job system + `Neon Errno` in exe, zero `Ego` strings; EGO retained Neon's threading)  
- **Middleware (verified via binary/DLL evidence):**
  - **Bink Video** (`binkw32.dll` 166 KB + `_BinkSetMixBins`/`_BinkWait`/`_BinkPause` imports ×16; `video/` dir)
  - **Ogg Vorbis** (`ogg.dll`, `vorbis.dll`, `vorbisfile.dll`; `ov_open_callbacks` + `CMStream_InitialiseLoadedBank: Ogg Vorbis DLLs not loaded, replay from bank WILL FAIL` — Codemasters CMStream banked audio)
  - **DirectX 9** (`D3DX` ×7)
  - **ZOOM Platform** patcher (`README-ZOOM Platform.txt`, `zoom_changelog.txt`, `win_000.000`/`win_000.nfs` patch containers)
- **Executables:** `GRID.exe` (14,137,760 bytes, unpacked) + `GRIDLauncher.exe` + `LaunchGRID.bat`
- **Registry/DataCache:** `SOFTWARE\Codemasters\GRID`, `\Codemasters\GRID\DataCache`
- **Physics:** In-house (no Havok/PhysX strings)
- **Scripting:** None found (C++ only; no Lua)

**Falsified:** `Miles` ×2 = `MilestoneInfoMap`/`MNotifyMilestone*` (career milestone strings, not RAD Miles). `fmod` ×2 = CRT math. `Speed` ×134 = AI driver params (`Speed_In`/`Speed_Out`/`Virtual_Performance`), not EAGL Speed. `Steam` ×1 = noise.

**Evidence from dump:**
- 29 asset dirs: `cars/`, `tracks/`, `audio/`, `anims/`, `database/`, `shaderpack/`, `video/`, `language/`, `network/`, `ghostlaps/`, `skidmarks/`, `interiors/`, `effects/`, `frontend/`, `cutscene/`, `characters/`, `postprocess/`, `forcefeedback/`, `gameconfig/`, `hardwaresettings/`, `system/`, `simplefonts/`, `Osd/`, `track_sponsors/`, `dlc_info/`, `debug/`, `ai/`, `ActionMap/`
- `car_materials.xml` (6 KB), `surface_materials.xml` (35 KB), `car_monitor_setup.xml`, `SkipFrontEnd.xml`, `raceload.jpk`
- Localised manuals (EN/FR/DE/IT/RU/ES PDFs)

---

## 2. File Formats

| Format | Description |
|---|---|
| `.bik` | Bink Video (`video/`) |
| `.nfs` / `.000` | Patch containers (`win_000.nfs`, ZOOM platform) |
| `.jpk` | Packed data (`raceload.jpk`) |
| `.xml` | Materials, monitor setup, frontend skip |
| `.id` | Stub files (`1.id`–`3.id`, 4 bytes each) |
| Ogg Vorbis banks | CMStream audio (DLLs + `audio/` dir) |

---

## 3. Key Technical Details

- **EGO confirmed by lineage evidence**: Neon threading system throughout, Codemasters registry/DataCache paths, CMStream audio — no Havok/PhysX/Lua/FMOD anywhere
- **Distinct from GRID DS** (Firebrand Octane, separate doc) — same franchise, unrelated engine
- PC release used ZOOM patch delivery, not Steam

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Race Driver - GRID\`*  
*Engine: EGO Engine (Neon lineage), Codemasters 2008*