# Onslaught (WiiWare) — Teardown Documentation

**Game:** Onslaught  
**Platform:** Nintendo Wii (WiiWare)  
**Developer:** Hudson Soft  
**Publisher:** Hudson Soft  
**Year:** 2009  
**Format:** WAD (Wii Archive)

---

## 1. Game Engine

**Engine:** Hudson Soft proprietary Wii engine  
- **Middleware:** None (custom Wii engine)  
- **Format:** WAD (encrypted Wii Archive)  
- **Graphics:** Nintendo Wii Hollywood GPU (TEV pipeline)  
- **Audio:** DSP ADPCM / Nintendo Wii audio  
- **Scripting:** None found (C++ only)  
- **Physics:** Custom FPS physics

**Evidence:**
- Hudson Soft developed WiiWare titles
- FPS on Wii (rare for WiiWare)
- No third-party middleware signatures

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
    └── levels/        # Level data
```

---

## 4. Documentation Notes

- **Hudson Soft** - Japanese developer (Bomberman, Adventure Island)
- **WiiWare FPS** - Rare genre for WiiWare
- **Motion controls** - Wii Remote pointer aiming
- **Online multiplayer** - Nintendo Wi-Fi Connection (defunct)
- **Custom engine** - No middleware
- **WiiWare size limit** - ~40MB compressed

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Onslaught (USA) (WiiWare)\`*  
*Engine: Hudson Soft proprietary Wii engine, Hudson Soft 2009*