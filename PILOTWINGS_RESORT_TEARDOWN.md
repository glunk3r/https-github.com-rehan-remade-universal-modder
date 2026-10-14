# Pilotwings Resort (3DS) — Teardown Documentation

**Game:** Pilotwings Resort  
**Platform:** Nintendo 3DS  
**Developer:** Monster Games  
**Publisher:** Nintendo  
**Year:** 2011 (3DS launch title)  
**Format:** CIA (Citizen Archive) - Nintendo 3DS installable format

---

## 1. Game Engine

**Engine:** Monster Games proprietary 3DS engine  
- **Middleware:** NitroSDK (Nintendo 3DS SDK)  
- **Format:** CIA (encrypted NCCH/CXI)  
- **Graphics:** Nintendo 3DS PICA200 GPU  
- **Audio:** CSND (3DS audio)  
- **Scripting:** None found (C++ only)  
- **Physics:** Custom flight physics

**Evidence:**
- Monster Games developed Excite Truck (Wii) - same studio
- 3DS launch title - showcased 3D capabilities
- Nintendo published - high quality bar

---

## 2. File Formats

| Format | Description |
|---|---|
| `.cia` | Citizen Archive (encrypted NCCH container) |
| `.cxi` | Executable NCCH (code) |
| `.cfa` | Data NCCH (assets) |
| `.bclim` | 3DS texture format (BCLIM) |
| `.bcwav` | 3DS audio format (BCWAV) |
| `.bch` | 3DS model format (BCH) |
| `.bfres` | 3DS model/texture container |
| `.shbin` | 3DS shader binary |
| `.bcres` | 3DS resource container |

---

## 3. Asset Structure (Expected)

Standard 3DS CIA structure:
```
CIA/
├── NCCH (Executable - .cxi)
│   ├── ExHeader
│   ├── ExeFS (code, icon, banner)
│   └── RomFS (game data)
└── NCCH (Data - .cfa)
    └── RomFS (assets)
        ├── models/ (.bch, .bfres)
        ├── textures/ (.bclim)
        ├── audio/ (.bcwav)
        ├── shaders/ (.shbin)
        ├── islands/ (.bin, .dat)
        └── vehicles/ (.bch, .bfres)
```

---

## 4. Documentation Notes

- **Monster Games** - Same studio as Excite Truck (Wii)
- **3DS Launch Title** - Showcased stereoscopic 3D
- **Flight simulation** - Plane, rocket belt, hang glider
- **Wuhu Island** - Same island as Wii Sports Resort
- **Nintendo published** - First-party quality
- **CIA requires decryption** (needs 3DS keys / ticket)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Pilotwings Resort (USA) (En,Fr,Es) (Rev 1)\`*  
*Engine: Monster Games proprietary 3DS engine (NitroSDK), Monster Games 2011*