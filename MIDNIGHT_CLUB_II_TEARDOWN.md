# Midnight Club II (PC) — Teardown Documentation

**Game:** Midnight Club II  
**Platform:** PC (Windows)  
**Developer:** Rockstar San Diego (formerly Angel Studios)  
**Publisher:** Rockstar Games  
**Year:** 2003  
**Engine:** Angel Game Engine (AGE) — Rockstar San Diego (Angel Studios lineage)

---

## 1. Game Engine

**Engine:** Rockstar San Diego's Angel Game Engine (AGE) (evolved from the original Midnight Club engine)  
- **Middleware:** 
  - **Bink Video** (Rad Game Tools) - `binkw32.dll`
  - **Miles Sound System** - `mss32.dll`
- **Executable:** `mc2.exe`
- **Graphics:** DirectX 8.1 / 9.0c
- **Scripting:** None found (C++ only)
- **Physics:** Custom vehicle physics (Angel Studios heritage)

**Evidence from dump:**
- `mc2.exe` - Main executable
- `binkw32.dll` - Bink Video
- `mss32.dll` - Miles Sound System (RAD Game Tools)
- `assets_p.dat` - Main asset archive
- `defaults.bat` - Configuration batch file
- `ReadMe.txt` - Readme

---

## 2. File Formats

| Format | Extension | Description |
|---|---|---|
| `.dat` | Archive | Main asset container (`assets_p.dat`) |
| `.bik` | Video | Bink Video cutscenes |
| `.m3d` | Model | Rockstar model format (likely) |
| `.txd` | Texture | Rockstar texture dictionary |
| `.col` | Collision | Collision models |
| `.ide` / `.ipl` | Map | Item definitions / instance placement |
| `.wav` / `.mp3` | Audio | Miles Sound System formats |

---

## 3. Asset Structure

```
Midnight Club II/
├── mc2.exe                  # Main executable
├── binkw32.dll              # Bink Video
├── mss32.dll                # Miles Sound System
├── assets_p.dat             # Main asset archive
├── mc2.ico / mc2_0.ico      # Icons
├── defaults.bat             # Default config
└── ReadMe.txt               # Readme
```

---

## 4. Key Technical Details

- **Angel Studios lineage** - Same team as PS1 Midnight Club
- **Open-world streaming** - Three cities (LA, Paris, Tokyo) seamless
- **Custom vehicle physics** - Arcade/sim hybrid, motorcycle + car handling
- **RenderWare?** - Some Rockstar titles used RenderWare, but MC2 appears custom
- **Miles Sound System** - RAD Game Tools audio (common in 2000s)
- **Bink Video** - RAD Game Tools video

---

## 5. Documentation Notes

- **Separate from PS1 game** - Different engine, not a port
- **Three cities** - Los Angeles, Paris, Tokyo
- **Motorcycles + Cars** - First Midnight Club with bikes
- **Rockstar San Diego** - Studio rename from Angel Studios (2002)
- **No RenderWare** - Unlike GTA III/VC/SA, appears fully custom

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Midnight Club II\`*  
*Engine: Angel Game Engine (AGE), Rockstar San Diego 2003*