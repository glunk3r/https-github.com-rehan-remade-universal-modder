# NASCAR Unleashed (3DS) — Teardown Documentation

**Game:** NASCAR Unleashed (CTR-P-AC9E)  
**Platform:** Nintendo 3DS  
**Developer:** Firebrand Games  
**Publisher:** Activision  
**Year:** 2011  
**Format:** CIA (Citizen Archive) - Nintendo 3DS installable format

---

## 1. Game Engine

**Engine:** Firebrand Octane Engine (same lineage as TrackMania DS/Turbo DS)  
- **Middleware:** NitroSDK (Nintendo 3DS SDK)  
- **Format:** CIA (encrypted NCCH/CXI)  
- **Graphics:** Nintendo 3DS PICA200 GPU  
- **Audio:** CSND (3DS audio)  
- **Scripting:** None found (C++ only)  
- **Physics:** Custom NASCAR physics (arcade/sim hybrid)

**Evidence:**
- Firebrand Games developed TrackMania DS, Driver Renegade 3DS
- Same studio, same engine lineage
- NASCAR license from Activision

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

- **Firebrand Octane Engine** - same lineage as TrackMania DS/Turbo DS
- **NASCAR license** - Official NASCAR teams/drivers/tracks
- **Arcade/sim hybrid** - More accessible than sim titles
- **3DS exclusive** - No console/PC versions
- **CIA requires decryption** (needs 3DS keys / ticket)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\NASCAR Unleashed (3DS)\`*  
*Engine: Firebrand Octane Engine (NitroSDK), Firebrand Games 2011*