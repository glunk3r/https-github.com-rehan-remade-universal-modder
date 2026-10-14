# Ridge Racer 3D (3DS) — Teardown Documentation

**Game:** Ridge Racer 3D (CTR-P-ARRE)  
**Platform:** Nintendo 3DS  
**Developer:** Namco Bandai Games  
**Publisher:** Namco Bandai Games  
**Year:** 2011 (3DS launch window)  
**Format:** CIA (Citizen Archive) - Nintendo 3DS installable format

---

## 1. Game Engine

**Engine:** Namco Bandai proprietary 3DS engine  
- **Middleware:** NitroSDK (Nintendo 3DS SDK)  
- **Format:** CIA (encrypted NCCH/CXI)  
- **Graphics:** Nintendo 3DS PICA200 GPU (stereoscopic 3D showcase title)
- **Audio:** CSND (3DS audio)  
- **Scripting:** None found (C++ only)  
- **Physics:** Custom arcade drift physics (Ridge Racer drift model)

**Evidence:**
- Namco Bandai in-house 3DS launch title (ID CTR-P-ARRE)
- NitroSDK standard for 3DS development

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
        ├── tracks/ (.bin, .dat)
        └── cars/ (.bch, .bfres)
```

---

## 4. Documentation Notes

- **3DS launch-window title** — stereoscopic 3D showcase for the hardware
- **Classic Ridge Racer drift model** carried to handheld
- **CIA requires decryption** (needs 3DS keys / ticket)
- Sibling of the Vita F2P experiment (Ridge Racer Vita, Cellius Proprietary) — different engine lineage

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Ridge Racer 3D\`*  
*Engine: Namco Bandai proprietary 3DS engine (NitroSDK), Namco Bandai Games 2011*