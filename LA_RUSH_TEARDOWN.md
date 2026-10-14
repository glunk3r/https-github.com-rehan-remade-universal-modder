# L.A. Rush (PC) — Teardown Documentation

**Game:** L.A. Rush  
**Platform:** PC (Windows)  
**Developer:** Midway Studios (Los Angeles)  
**Publisher:** Midway Games  
**Year:** 2005  
**Engine:** Midway in-house (unconfirmed — no executable in dump)

---

## 1. Game Engine

**Engine:** Midway in-house (no binary evidence — dump contains no game exe)  
- **Middleware (verified via file evidence):**
  - **Bink Video** (24 `.bik` in `movies/`: `midway.bik`, `pitbull.bik`, `rushlogo.bik`, `seq_*`, licensed-music videos)
  - **XACT** (`media/Sound.xsb` + `Wave.xwb` — Microsoft XACT sound/wave banks)
- **Scripting:** `.freak` mission scripts (`scripts/`: `AcquireDT/HH/SB/SC/SM*`, `ADVCam`, `AcceptDecline*` — Midway script format)
- **Audio banks:** `.bkh`/`.bks` pairs (`EngineExtras`, `Impact`, `Skid`, `Siren`, `Speech`, `Traffic`, `WMA`, 30+ banks + `Music/` + `GUI/`)
- **Shaders:** `pshaders.pak` / `vshaders.pak` (precompiled pixel/vertex shaders)
- **Resources:** `EngineRes.res` (1 MB) + `EngineRes.dir` (engine resource index)
- **Fonts:** `media/ArialUni.Ttf`; Xbox leftovers: `media/dlcustom.xpr` (XPR texture)
- **Copy protection:** `protect.msg` (359 KB protection message)

**Third-party mod artifacts (not game tech):** `plugins/LARush.WidescreenFix.asi` (+`.ini`) — modern widescreen mod.

**Evidence from dump:**
- 20+ asset dirs: `ai/`, `ai_line/`, `ai_race/`, `cardata/`, `cars/`, `District/`, `frontend/`, `grid/`, `Lowrider/`, `media/`, `overlays/`, `scripts/`, `SoundBanks/`, `subtitles/` + 16-byte init `.bin` stubs (`fpsdata`, `inputdata`, `memmanager`...)
- `save.dat` (116 KB), `lightList.dat` (372 KB)

---

## 2. Key Technical Details

- Licensed-soundtrack arcade racer (Pitbull/mid-2000s videos ship as Bink)
- XACT + Bink is the standard Midway PC stack of the era; engine core unconfirmed without the exe

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\L.A Rush\`*  
*Engine: Midway in-house (unconfirmed — no exe in dump)*