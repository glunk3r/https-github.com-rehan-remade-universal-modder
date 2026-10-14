# Mega Halo Game (Xbox 360 UE3 Vertical Slice) — Teardown Documentation

**Game:** Mega Halo Game (Halo UE3 vertical-slice prototype)  
**Platform:** Xbox 360  
**Developer:** Unknown (`C:\Projects\MegaHalo\` — no company in paths)  
**Publisher:** Unknown (presumed Microsoft/Xbox, unconfirmed)  
**Year:** 2013 (profiling sessions Jun–Sep 2013; stray 2005 stamps)  
**Engine:** **Unreal Engine 3** (verified)

---

## 1. Game Engine

**Engine:** **Unreal Engine 3** (verified: stock `UDKBase`/`UTGame`/`Engine`/`Core`/`GameFramework`/`IpDrv` packages + UE3 Xbox 360 toolchain)  
- **Middleware (verified via file evidence):**
  - **Wwise** (Audiokinetic) — 100+ `.bnk` banks + `.txt` metadata + numeric `.wem` voices (`MasterChief`, `Grunt`, `Elite`, `Jackal`, `Hunter`, `Warthog`, `Needler`, `Scorpion`, `Ghost`, `PlasmaPistol`, `Storm_Rifle`, `Takedowns`, `MagicMoments`...)
  - **Scaleform GFx** (`GFxUI.xxx`)
  - **Autodesk GameWare Navigation** (`GwNavEngine.xxx`)
  - **FaceFX** (OC3 facial animation — full `FxSDK` object set in PDB, VS2010 Xenon build at `C:\Projects\MegaHalo\`)
  - **Bink Video** (`UDKFrontEnd.udk_loading.bik`, `UE3_logo.bik`, `MultichannelTest_LOC.bik`)
  - **Xbox Live** (`OnlineSubsystemLive.xxx`, `CloudStorage.ini`)
- **Executables:** `MegaHaloGame-Xbox360-Release.MProfP1.xex` (12.4 MB) + **220 MB PDB** (full symbols!)
- **Container:** UE3 cooked packages (`.xxx`: `2_1C`/`2_2C`/`2_3C` mission chapters — ai/ds/mi/nav/wb/vs/mis per map) + `.tfc` textures + `GlobalShaderCache-Xbox360.bin` + `Coalesced_INT.bin`
- **Scripting:** UnrealScript (`.xxx` bytecode)
- **Content:** Forerunner/ONI/Covenant (Grunts, Jackals, Hunters, Elites), UNSC (Pelican crash, Warthog, Scorpion, Banshee, Wraith), Master Chief VO, `2_All_Cheats.xxx`

**Evidence from dump:**
- `Xbox360TOC.txt` (30 KB disc layout), `MegaHaloGame.XGD` (XGD layout), `Binaries/` (`build.properties`, `EpicInternal.txt`, splash, stats)
- `Movies/`, `Cloud/`, `Logs/` (incl. `Launch-backup-2026.04.19` — booted as recently as 2026)
- `Profiling/` `.gprof` sessions Jun–Sep 2013 (+ stray `2005.11.22` stamps — clock skew or inherited data)

---

## 2. Key Technical Details

- **Halo on UE3** — full vertical slice (3+ mission chapters, cinematics, cheat package) that never shipped; Storm Rifle + vertical-slice structure suggest early-2010s exploration
- PDB makes this fully reverse-engineerable (symbols for every function); profiling history inline
- Stock UE3 + licensed middleware stack (Wwise/FaceFX/GFx/GwNav/Bink/Live) = AAA Xbox 360 pipeline, zero custom engine code evidenced at container level

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Mega Halo Game\`*  
*Engine: Unreal Engine 3, Unknown Developer 2013*