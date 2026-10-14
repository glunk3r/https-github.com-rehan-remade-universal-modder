# Crash Time 1 (Alarm für Cobra 11 – Crash Time) — Teardown Documentation

**Game:** Crash Time (Alarm für Cobra 11 – Crash Time, Germany En/De Rerelease ISO)  
**Platform:** PC (Windows)  
**Developer:** Synetic GmbH (German)  
**Publisher:** RTL Games / JoWooD  
**Year:** 2007 (game exes dated Oct 23, 2007; ISO mastered Jun 28, 2011, Ashampoo UDF, 4.2 GB, 5,902 entries)  
**Engine:** Synetic 3D Landscape Engine (evolved from CT0)

---

## 1. Game Engine

**Engine:** Synetic 3D Landscape Engine (verified in shipping exe strings)  
- **Middleware:** **NONE verified** — full `CrashTime_sse1.exe`/`sse2.exe` strings audit
- **Executables:** `CrashTime.exe` (69 KB launcher stub) + `CrashTime_sse1.exe` (2.53 MB) + `CrashTime_sse2.exe` (2.62 MB, SSE-optimized builds) + `CT_Setup.exe` + `AutoRun.exe`
- **Physics:** Custom damage system (`DAM_CRASH_*` ×6, full `DAM_TEMP_*`/`DAM_TIRE_*` table + `damage.txt` refs in exe)
- **Graphics:** DirectX 9 (`D3DX` ×162; DX redist + `WMCodec` installers on disc)
- **Audio:** DirectSound/DirectMusic (WAV 1,586, WMA 15)
- **Video:** WMV (202 files)
- **Scripting:** None (C++ only)

**Verified exe strings:** `Interne Synetic Version`, `damage.txt` + full DAM table, `stdstuff\tachos\tachokmh%02d.tga` (+tachomph/tachorpm/tachol), `.mox` ×49.

**Falsified (absent from both shipping exes):** `ODEConfig`, `PHYSICS_BODY_*`, `PHYSICS_INSTANCE_*`, `VehicleDamage::*`, `TrackEditor*`, `Editor*`, Lua API, Bink, Havok, PhysX, Miles, Ogg/Vorbis, XACT, XAudio, SecuROM, Steam. (`ODE` ×81, `XACT` ×62, `Nx`, `fmod` ×2, `Lua` ×12 are all Windows/DirectX/CRT/code-byte false positives — same audit method as the CT0 Full-Rip.)

> Correction: earlier revisions of this doc (and CT2–CT5) listed `ODEConfig`/`PHYSICS_BODY_GF`/`VehicleDamage::InitMorphSections`/`TrackEditorGUI` as string evidence from dumps that contained **no executables**. The shipping CT1 exes prove those strings absent. Those claims are retracted wherever they appear.

---

## 2. File Formats (from ISO listing)

### Vehicles (37 dirs)
Per vehicle: `VEHICLE.MOX`/`.MTL` + `_colli.CPO` + `_r_hl/_r_hr/_r_vl/_r_vr` LOD variants + `Driver/` (driver models + `textures/*.ptx`) + `Textures/` (`.ptx`: paint, dirt, scratch, plates, brakes) + `Hupe.wav`. E.g. Chris, Coach, Drone, Polizei ×4, Semir ×2, Saphir ×3, Seat_Leon, Seat_WTCC, Transporter ×3, Monsun ×3, Rennwagen, Rwagen ×2, Limo, MPV ×2, Taxi, Truck1, TOM, Senator, G_Laende ×3, Geldtransporter, Phantom, fuchs.

### Mission/Race Formats (new vs CT0)
| Format | Count | Description |
|---|---|---|
| `.trg` | 72 | Triggers (?) |
| `.dyn` | 42 | Dynamic objects (?) |
| `.trx` | 18 | Tracks/routes (?) |
| `.ral` | 10 | Rally (?) |
| `.par` | 7 | Parameters (?) |
| `.vtf` | 5 | Vector fonts |
| `.wyp` / `.hli` / `.trn` / `.net` | 2 each | Waypoints/highlights/tournaments/network (?) |

### Persistent Formats
| Format | Count | Description |
|---|---|---|
| `.wav` / `.wma` | 1,586 / 15 | Audio |
| `.ptx` | 1,467 | Textures |
| `.mox` / `.mtl` | 936 / 832 | Models / materials |
| `.wmv` | 202 | Video |
| `.cpo` | 157 | Collision/physics |
| `.tga` | 63 | Targa images |
| `.trk` | 50 | Track definitions |
| `.txt` | 25 | Config |
| `.ro1`–`.ro4`, `.sni`/`.dat`/`.vef`/`.slt`, `.geo`/`.lvl`/`.qad` | 2 each | Road / misc / geometry |
| `.cab` | 61 | DirectX redist |

---

## 3. Key Technical Details

- **SSE-split shipping builds** (sse1/sse2 + stub launcher) — CPU-dispatch era packaging
- **37 vehicles** with full LOD + driver + texture sets (vs 13 in CT0)
- **WMV video era** (202 files, WMCodec installers) — pre-Bink Synetic
- **Zero-middleware lineage anchor**: exe-proven, same result as CT0 Full-Rip

---

*Generated from `Crash-Time_Win_EN-DE_ISO/Alarm fuer Cobra 11 - Crash Time (Germany) (En,De) (Rerelease).iso`*  
*Engine: Synetic 3D Landscape Engine, Synetic GmbH 2007 — https://www.pcgamingwiki.com/wiki/Engine:3D_Landscape_Engine*