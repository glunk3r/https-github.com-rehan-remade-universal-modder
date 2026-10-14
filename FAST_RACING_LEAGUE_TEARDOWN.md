# FAST - Racing League (WiiWare) — Teardown Documentation

**Game:** FAST - Racing League  
**Platform:** Nintendo Wii (WiiWare)  
**Developer:** Shin'en Multimedia  
**Publisher:** Shin'en Multimedia  
**Year:** 2011  
**Format:** WAD (Wii Archive)

---

## 1. Game Engine

**Engine:** SHIN'ENGINE (formally C-Engine) — Shin'en Multimedia proprietary Wii engine  
- **Middleware:** None (custom Wii engine)  
- **Format:** WAD (encrypted Wii Archive)  
- **Graphics:** Nintendo Wii Hollywood GPU (TEV pipeline)  
- **Audio:** DSP ADPCM / Nintendo Wii audio  
- **Scripting:** None found (C++ only)  
- **Physics:** Custom

**Evidence:**
- Shin'en known for custom Wii engines (Nano Assault, FAST Racing series)
- WAD format standard for WiiWare
- No third-party middleware signatures found

---

## 2. File Formats (WiiWare Standard)

| Format | Description |
|---|---|
| `.wad` | Wii Archive (encrypted container) |
| `.app` | Wii executable (DOL/ELF) |
| `.tmd` | Title Metadata |
| `.tik` | Ticket (encryption keys) |
| `.cert` | Certificate chain |
| `.bnr` | Banner (channel icon/animation) |
| `.brlyt` / `.brlan` | Layout/Animation (UI) |
| `.tpl` | Wii texture format (TPL) |
| `.brsar` | Wii sound archive (BRSTM) |
| `.arc` / `.szs` | Archive (Yaz0 compressed) |

---

## 3. Asset Structure (Expected WAD Contents)

```
WAD/
├── Title.tmd          # Title metadata
├── Title.tik          # Ticket
├── Title.cert         # Certificate
├── 00000001.app       # Main executable (DOL)
├── 00000002.app       # Banner/Channel
└── data/              # Game assets (extracted)
    ├── models/        # Custom model format
    ├── textures/      # .tpl textures
    ├── audio/         # .brsar / .brstm
    ├── shaders/       # TEV shaders
    └── tracks/        # Track data
```

---

## 4. Documentation Notes

- **Shin'en Multimedia** - German developer known for highly optimized Wii engines
- **WiiWare exclusive** - No retail disc release
- **Future racing** - Anti-gravity racing (F-Zero style)
- **Custom engine** - No middleware, highly optimized for Wii hardware
- **Small footprint** - WiiWare size limit (~40MB)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\FAST - Racing League (USA) (WiiWare)\`*  
*Engine: SHIN'ENGINE (C-Engine), Shin'en Multimedia 2011*