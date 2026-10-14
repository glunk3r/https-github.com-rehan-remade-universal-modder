# Ridge Racer Vita — Teardown Documentation

**Game:** Ridge Racer (Vita)  
**Platform:** PlayStation Vita  
**Developer:** Cellius Inc. (Namco Bandai Games)  
**Publisher:** Namco Bandai Games  
**Year:** 2011 (Vita launch title)  
**Format:** PS Vita app (PCSE000xx) + DLC packages

---

## 1. Game Engine

**Engine:** Cellius Proprietary (Vita)  
- **Middleware:** 
  - **Havok Physics** - possible (common in Vita games)
- **Format:** PS Vita application (PCSE000xx) + DLC
- **Graphics:** PS Vita SGX543MP4+ (OpenGL ES 2.0 / PSVita GXM)
- **Audio:** PS Vita audio (ATRAC9, ADPCM)
- **Scripting:** Lua (possible, common in Vita titles)
- **Physics:** Havok or custom

**Evidence from dump:**
- `app/PCSE00...` - Vita application structure
- `addcont/PC...` - DLC packages (addcont = additional content)
- Standard Vita app structure with eboot.bin, param.sfo

---

## 2. File Formats (PS Vita Standard)

| Format | Description |
|---|---|
| `.self` / `.elf` | Executable (signed ELF) |
| `.pkg` | Package (installable) |
| `.rif` | License file |
| `.gxt` | Vita texture (GXT) |
| `.gxm` | Shader binary |
| `.psarc` | Archive (PSARC) |
| `.at9` | ATRAC9 audio |
| `.bin` | Binary data |
| `.lua` | Lua scripts |

---

## 3. Asset Structure

```
Ridge Racer Vita/
├── app/
│   └── PCSE00xxx/         # Main application
│       ├── eboot.bin      # Signed executable
│       ├── param.sfo      # Title parameters
│       ├── icon0.png      # Icon
│       ├── pic0.png       # LiveArea background
│       ├── sce_sys/       # System files
│       │   ├── param.sfo
│       │   └── ...
│       └── game/          # Game assets
│           ├── data.psarc # Main archive
│           ├── shaders/
│           ├── textures/
│           └── models/
└── addcont/
    └── PC.../             # DLC packages
        └── (same structure)
```

---

## 4. Key Technical Details

- **Vita Launch Title** - Showcased Vita graphics capabilities
- **Free-to-play model** - Base game free, cars/tracks as DLC
- **DLC-heavy** - Many addcont packages in dump
- **Cellius Proprietary engine** - Namco Bandai subsidiary tech for Vita
- **Online features** - Ghost data, leaderboards (PSN)

---

## 5. Documentation Notes

- **Cellius Inc.** - Namco Bandai subsidiary for Vita development
- **Ridge Racer series** - Long-running arcade racing franchise
- **F2P experiment** - Controversial at launch (little content in base)
- **Vita GXM API** - Low-level graphics API
- **Requires Vita keys** - For decryption/extraction

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Ridge Racer Vita\`*  
*Engine: Cellius Proprietary, Cellius / Namco Bandai Games 2011*