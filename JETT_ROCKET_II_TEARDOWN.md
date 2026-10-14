# Jett Rocket II (3DS) — Teardown Documentation

**Game:** Jett Rocket II (CTR-N-JRSE)  
**Platform:** Nintendo 3DS  
**Developer:** Shin'en Multimedia  
**Publisher:** Shin'en Multimedia  
**Year:** 2013  
**Format:** CIA (Citizen Archive) - Nintendo 3DS installable format

---

## 1. Game Engine

**Engine:** SHIN'ENGINE (formally C-Engine) — Shin'en Multimedia proprietary 3DS engine  
- **Middleware:** NitroSDK (Nintendo 3DS SDK)  
- **Format:** CIA (encrypted NCCH/CXI)  
- **Graphics:** Nintendo 3DS PICA200 GPU  
- **Audio:** CSND (3DS audio)  
- **Scripting:** None found (C++ only)  
- **Physics:** Custom platforming physics

**Evidence:**
- Shin'en developed custom engines for all platforms
- 3DS port/sequel of WiiWare Jett Rocket
- Different engine than Wii version (platform-specific)

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
        └── levels/ (.bin, .dat)
```

---

## 4. Documentation Notes

- **Different engine** from WiiWare Jett Rocket (platform-specific)
- **Shin'en 3DS engine** - custom, no middleware beyond NitroSDK
- **eShop exclusive** - 3DS digital only
- **Platformer** - 2.5D platforming
- **CIA requires decryption** (needs 3DS keys / ticket)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Jett Rocket II\`*  
*Engine: SHIN'ENGINE (C-Engine) on 3DS (NitroSDK), Shin'en Multimedia 2013*