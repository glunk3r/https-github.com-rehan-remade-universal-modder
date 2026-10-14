# Blur DS (Beta, NDS) — Teardown Documentation

**Game:** Blur (DS beta, Europe)  
**Platform:** Nintendo DS  
**Developer:** Firebrand Games (verified: `Firebrand` ×12, `Octane` ×6 in ROM)  
**Publisher:** Activision (maker code `36`, region `P`/Europe)  
**Year:** ~2010 (unreleased beta)  
**Format:** NDS ROM (`BlurDSBeta.nds`, 64 MB)

---

## 1. Game Engine

**Engine:** **Firebrand Octane Engine** (same pipeline as TrackMania DS/Turbo DS, GRID DS)  
- **Middleware:** **NONE** — Nintendo NitroSDK only
- **ROM:** 64 MB, ARM9 858,360 bytes, ARM7 156,716 bytes, 13 files + `vfs.zip`
- **Container:** `vfs.zip` (24.6 MB, **3,146 files**) + `vfs.bin`/`vfs.dat`
- **Scripting:** **Lua** (`.luac` ×18 in zip, `Lua` ×12 in ROM)
- **Video:** Mobiclip/Actimagine (`.mob` ×3: `act.mob`, `FBlogo.mob`, `TutorialTest.mob`)
- **Audio:** SDAT (`sound_data.sdat` + Network variant)
- **Distribution:** DSi download-play stubs (`download.char/.plt`, `downloadeu/us.srl`), DWC utility

**Evidence from dump:**
- `Firebrand` ×12, `Octane` ×6, `Mobiclip`/`Actimagine` in ROM strings
- Zip extension profile matches TrackMania Turbo DS short-ext style (`.n` models, `.hzc` collision, `.dcsc` scenes, NitroSDK 2D formats)
- NDS header: title `BLUR`, game code `BBRP`, maker `36`

---

## 2. File Formats

| Location | Format | Count | Description |
|---|---|---|---|
| ROM FAT | `.srl` | 2 | DSi download-play binaries (EU/US) |
| ROM FAT | `.mob` | 3 | Mobiclip video |
| ROM FAT | `.sdat` | 2 | Audio (+Network) |
| ROM FAT | `.zip` | 1 | `vfs.zip` asset container |
| vfs.zip | `.n` | 2,035 | Models (Turbo-DS short style) |
| vfs.zip | `.dcsc` / `.tsf` | 191 / 191 | Scenes / track section files |
| vfs.zip | `.ncgr`/`.ncer`/`.nanr`/`.nclr` | 100/100/100/35 | NitroSDK 2D graphics |
| vfs.zip | `.p` / `.c` / `.s` | 81 / 58 / 58 | Firebrand internal data |
| vfs.zip | `.na` / `.nm` | 55 / 14 | Signage / navmesh(?) |
| vfs.zip | `.bin` / `.str` | 37 / 36 | Binary / strings |
| vfs.zip | `.hzc` | 28 | Collision |
| vfs.zip | `.luac` | 18 | Lua 5.1 bytecode |
| vfs.zip | `.bmp` | 7 | Bitmaps |

---

## 3. Key Technical Details

- **Unreleased Bizarre racer on Firebrand tech** — Activision-published DS counterpart to the 2010 console Blur (Bizarre Creations, Horizon Engine); the DS version never shipped, this EU beta survives
- **Octane fingerprint:** `vfs.zip` + `.luac` + NitroSDK 2D + `.dcsc` + `.hzc` = identical pipeline to TrackMania DS (3,457 files) / Turbo DS (4,258 files)
- **Short-extension variant** (`.n` models) matches Turbo DS, not original TrackMania DS (`.nsbmd`)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Blur (NDS)\BlurDSBeta.nds`*  
*Engine: Firebrand Octane Engine (unreleased beta) — https://en.wikipedia.org/wiki/Firebrand_Games*