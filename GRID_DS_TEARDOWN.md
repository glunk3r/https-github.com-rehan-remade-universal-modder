# GRID DS (NDS) — Teardown Documentation

**Game:** GRID (Race Driver: GRID, DS, USA)  
**Platform:** Nintendo DS  
**Developer:** Firebrand Games (verified: `Firebrand` ×7 in ROM; Octane pipeline fingerprint)  
**Publisher:** Codemasters (box; ROM maker code `36`)  
**Year:** 2008  
**Format:** NDS ROM (`Grid (USA) (En,Fr,Es).nds`, 64 MB)

---

## 1. Game Engine

**Engine:** **Firebrand Octane Engine** (same pipeline as TrackMania DS, Blur DS beta)  
- **Middleware:** **NONE** — Nintendo NitroSDK only
- **ROM:** 64 MB, ARM9 980,248 bytes, ARM7 159,528 bytes, 16 files + `vfs.zip`
- **Container:** `vfs.zip` (36 MB, **4,616 files**) + `vfs.bin`/`vfs.dat` + `sku.bin`
- **Scripting:** **Lua** (`.luac` ×19 in zip, `Lua` ×14 in ROM)
- **Video:** Actimagine (`.vx` ×2: `codemasters.vx`, `GridIntro.vx`)
- **Audio:** SDAT (`sound_data.sdat` + Network variant)
- **Distribution:** DSi download-play stubs, DWC utility

**Evidence from dump:**
- `Firebrand` ×7, `Actimagine` ×1 in ROM strings
- Zip profile: `.nsbmd` models + `.hzc` collision + `.nsbta` animation + `.dcsc` + NitroSDK 2D = original TrackMania DS variant (long extensions)
- NDS header: title `GRID`, game code `YG6E`, maker `36`

---

## 2. File Formats

| Location | Format | Count | Description |
|---|---|---|---|
| ROM FAT | `.srl` | 2 | DSi download-play binaries (EU/US) |
| ROM FAT | `.vx` | 2 | Actimagine video |
| ROM FAT | `.sdat` | 2 | Audio (+Network) |
| ROM FAT | `.zip` / `.bin` | 1 / 4 | `vfs.zip` + `vfs.bin`/`vfs.dat` + `sku.bin`(+`.bak`) |
| vfs.zip | `.nsbmd` | 2,370 | Models (long-ext style, like TM DS) |
| vfs.zip | `.hzc` | 686 | Collision |
| vfs.zip | `.nsbta` | 407 | Animations |
| vfs.zip | `.ncgr` / `.nclr` / `.nsc` / `.nanr` / `.ncer` | 274/156/151/126/126 | NitroSDK 2D graphics |
| vfs.zip | `.dcsc` | 210 | Scenes |
| vfs.zip | `.pvs` | 38 | Potentially-visible sets(?) |
| vfs.zip | `.str` / `.bin` | 36 / 15 | Strings / binary |
| vfs.zip | `.luac` | 19 | Lua 5.1 bytecode |

---

## 3. Key Technical Details

- **Firebrand's Codemasters era** — DS companion to Race Driver: GRID (2008, Ego engine on console); Firebrand ported the franchise to DS on Octane
- **Long-extension variant** (`.nsbmd`/`.hzc`) matches original TrackMania DS, while Blur DS beta (same year-ish) uses Turbo DS short style — both pipelines coexisted
- Largest Octane zip observed so far: 4,616 files (vs 3,146 Blur, 3,457 TM DS, 4,258 Turbo DS)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Grid (NDS)\Grid (USA) (En,Fr,Es).nds`*  
*Engine: Firebrand Octane Engine — https://en.wikipedia.org/wiki/Firebrand_Games*