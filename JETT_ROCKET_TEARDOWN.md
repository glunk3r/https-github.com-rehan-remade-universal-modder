# Jett Rocket (WiiWare) — Teardown Documentation

**Game:** Jett Rocket  
**Platform:** Nintendo Wii (WiiWare)  
**Developer:** Shin'en Multimedia  
**Publisher:** Shin'en Multimedia  
**Year:** 2010  
**Format:** WAD (Wii Archive)

---

## 1. Game Engine

**Engine:** SHIN'ENGINE (formally C-Engine) — Shin'en Multimedia proprietary Wii engine (same as FAST Racing League)  
- **Middleware:** None (custom Wii engine)  
- **Format:** WAD (encrypted Wii Archive)  
- **Graphics:** Nintendo Wii Hollywood GPU (TEV pipeline)  
- **Audio:** DSP ADPCM / Nintendo Wii audio  
- **Scripting:** None found (C++ only)  
- **Physics:** Custom platforming physics

**Evidence:**
- Same developer as FAST Racing League
- Shin'en's first WiiWare title
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

- **Shin'en Multimedia** - First WiiWare title
- **Platformer** - 3D platforming (Mario 64 style)
- **Custom engine** - No middleware, highly optimized
- **WiiWare size limit** - ~40MB compressed
- **Sequel** - Jett Rocket II on 3DS (different engine)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Jett Rocket (USA) (WiiWare)\`*  
*Engine: SHIN'ENGINE (C-Engine), Shin'en Multimedia 2010*