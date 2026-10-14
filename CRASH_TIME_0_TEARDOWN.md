# Crash Time 0 — Alarm für Cobra 11: Nitro (PC, Full-Rip) — Teardown Documentation

**Game:** Alarm für Cobra 11: Nitro (Crash Time 0)  
**Platform:** PC (Windows, EN-DE Full-Rip)  
**Developer:** Synetic GmbH (German)  
**Publisher:** RTL Games / JoWooD  
**Year:** 2006/07  
**Engine:** Synetic 3D Landscape Engine v1

---

## 1. Game Engine

**Engine:** Synetic 3D Landscape Engine v1 (verified in exe strings)  
- **Middleware:** **NONE verified** — full `C11_PC.exe` strings scan (2.49 MB) shows zero licensed middleware
- **Executable:** `C11_PC.exe` (2,490,382 bytes) + `C11_Setup.exe`
- **Physics:** Custom damage system (`DAM_CRASH_*` ×6 in exe; plaintext tuning in `damage.txt`)
- **Graphics:** DirectX 9 (D3DX9 Shader Compiler 9.12.589)
- **Audio:** DirectSound/DirectMusic (WAV 492, WMA 19)
- **Video:** WMV (61 files)
- **Scripting:** None (C++ only)
**Evidence from dump (exe-verified where marked ✓; the 2006-build-only strings below were reported from a prior analysis whose dump is gone — kept with caveat):**
- ✓ `Interne Synetic Version`, `.mox` ×43, `DAM_CRASH_*` ×6, `tachokmh%d.tga` tachometer system
- `ExecEngine`, `EngineMuckt` (prior analysis, unverified)
- `damage.txt`: 27 plaintext tuning vars (`DAM_CRASH_HULL/MOTOR/GEAR/BRAKE/CHASS/ANIM`, tire/brake/gear thermals, German comments)
- **False-positive audit:** `XACT` (×62), `CRI` (×31), `ODE` (×80), `Nx` (×15), `fmod` (×2), `lua` (×1) hits are ALL Windows HRESULT / DirectX / CRT substrings — no middleware. No `Bink`/`Havok`/`PhysX`/`FMOD`/`Miles` strings, no DLLs in dump.
- **Retracted:** `TrackEditorGUI`/`TrackEditorLoadTrackGUI`/`EditorUpdate`, `PHYSICS_BODY_GF`, `PHYSICS_INSTANCE_GF`, `VehicleDamage::InitMorphSections` — absent from the Full-Rip exe; the CT1 shipping exes (same engine family) confirm the absence.

---

## 2. File Formats

| Format | Count | Description |
|---|---|---|
| `.ptx` | 945 | Textures |
| `.wav` / `.wma` | 492 / 19 | Audio |
| `.mox` / `.mtl` | 429 / 390 | Models / materials (×43 `.mox` refs in exe) |
| `.tga` | 88 | Targa images (tachos) |
| `.cpo` / `.cob` | 87 / 39 | Collision / physics objects |
| `.wmv` | 61 | Video |
| `.trk` | 59 | Track definitions |
| `.tree` | 45 | Scene graph |
| `.tob` | 20 | Unknown binary |
| `.ro1`–`.ro4`, `.sni`/`.smp`/`.dat`/`.vef`/`.slt`/`.str` | 3 each | Road / misc per-track data |
| `.wtr` / `.wpt` / `.geo` / `.lvl` / `.qad` | 5 / 3 / 3 / 3 / 3 | Water / waypoints / geometry / levels / quads |
| `.txt` | 24 | Config incl. `damage.txt` |
| `.cpt` / `.trl` / `.fxp` / `.ds` | 1 each | Checkpoint / trail / FX / data |

---

## 3. Asset Structure

```
Alarm-for-Cobra-11-Nitro_Win_EN-DE_Full-Rip/
├── C11_PC.exe / C11_Setup.exe
├── damage.txt                   # Plaintext damage tuning (German comments)
├── SampleVolumes.ini / SetUp_Loka.ini / Readme_EN.txt
├── Autos/ Motoren2/ Traffic/    # Vehicles (13) + traffic
├── Scenarios/ RaceDat/          # Missions + race data
├── FrontEnd/ Logos/ Clouds/     # UI + sky
├── stdstuff/ Haenger/           # Shared assets + trailers(?)
├── Sounds/ Music/ MyMusic/      # Audio
├── Videos/ ReplayRec/           # WMV + replays
└── ScreenShots/
```

---

## 4. Key Technical Details

- **Zero-middleware reference** for the whole Synetic lineage: exe-proven, no Bink/Havok/PhysX/FMOD/Miles/Lua
- **Plaintext vehicle tuning** (`damage.txt`) — thermal + crash damage model with perverse detail (drift tire wear, 2-wheel driving damage, wind-shadow from hull damage)
- **ODE claims in Crash Time 1–5 docs are FALSIFIED for CT0/CT1** (shipping exes audited: no `ODEConfig`/`PHYSICS_*`; `ODE` hits are Windows error strings) and **unverified for CT2–CT5** (dumps contain no executables). Treat CT2–CT5 "ODE Physics" rows as unconfirmed.

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Alarm-for-Cobra-11-Nitro_Win_EN-DE_Full-Rip\`*  
*Engine: Synetic 3D Landscape Engine v1, Synetic GmbH 2006 — https://www.pcgamingwiki.com/wiki/Engine:3D_Landscape_Engine*