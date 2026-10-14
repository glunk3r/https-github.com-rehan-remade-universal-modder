# Driver Renegade (3DS) — Teardown Documentation

**Game:** Driver Renegade (CTR-P-ADRE)  
**Platform:** Nintendo 3DS  
**Developer:** VD-dev  
**Publisher:** Ubisoft  
**Year:** 2011  
**Format:** CIA (Citizen Archive) - Nintendo 3DS installable format

---

## 1. Game Engine

**Engine:** VD-dev Proprietary Engine  
- **Middleware:** NitroSDK (Nintendo 3DS SDK)  
- **Format:** CIA (encrypted NCCH/CXI)  
- **Graphics:** Nintendo 3DS PICA200 GPU  
- **Audio:** CSND (3DS audio)  
- **Scripting:** None found (C++ only)

**Evidence:**
- Developed by VD-dev (Velez & Dubail), published by Ubisoft — corrected: not Firebrand
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
        └── data/ (.bin, .dat)
```

---

## 4. Documentation Notes

- **CIA file requires decryption** (needs 3DS keys / ticket)
- **VD-dev Proprietary Engine** - in-house VD-dev technology on 3DS
- **No PC port** - 3DS exclusive
- **Ubisoft Reflections** - original Driver series developer

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Driver Renegade\`*  
*Engine: VD-dev Proprietary Engine (NitroSDK), VD-dev 2011*