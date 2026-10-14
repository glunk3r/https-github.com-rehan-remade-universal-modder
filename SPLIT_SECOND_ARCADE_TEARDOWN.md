# Split/Second: Arcade Edition (PC) — Teardown Documentation

**Game:** Split/Second: Arcade Edition  
**Platform:** PC (Windows)  
**Developer:** Silent Bay Studios (port) / Black Rock Studio (original)  
**Publisher:** Disney Interactive Studios  
**Year:** 2010 (Arcade Edition)  
**Engine:** Adobe Director / Shockwave 3D (NOT the Black Rock Studio engine)

---

## 1. Game Engine

**Engine:** **Adobe Director 11.5 / Shockwave 3D** (NOT the original console engine)  
- **Middleware:** 
  - **Adobe Director / Shockwave Player** (Projector.exe)
  - **Havok Physics** (Havok.x32 Xtra)
  - **Dynamiks** (physics Xtra)
  - **QuickTime** (QT6Asset.x32, QTAuth.x32, QTExport.x32)
  - **Flash** (Flash Asset.x32, FLVAsset.x32, F4VAsset.x32, MP4Asset.x32)
  - **SketchUp** (MixSkp.x32, SketchUpReader.dll)
  - **Collada** (MixCollada.x32)
  - **PhysX?** (Dynamiks physics Xtra)
- **Executable:** `Projector.exe` (Director Projector) + `SPR.exe` (custom wrapper)
- **Main Movie:** `split_second.dcr` (Director protected movie)
- **Graphics:** DirectX 9 (via Director 3D)
- **Scripting:** **Lingo** (Director's native scripting language)
- **Physics:** Havok (via Havok.x32 Xtra) + Dynamiks

**Evidence from dump:**
- `Projector.exe` - Adobe Director Projector (360KB)
- `SPR.exe` - Silent Bay Studios wrapper (369KB)
- `split_second.dcr` - Main Director movie (2.8MB)
- `level.w3d` - Shockwave 3D level (3MB)
- `sounds.cct` - Shockwave audio cast (306KB)
- `gameloader.dcr` - Loader movie
- `lingo.ini` - Lingo configuration
- `Xtras/Havok.x32` - Havok Physics Xtra (573KB)
- `Xtras/Dynamiks.x32` - Dynamiks physics (2.5MB)
- `Xtras/Flash Asset.x32` - Flash integration (6MB)
- `Xtras/SketchUpReader.dll` - SketchUp importer (3.8MB)
- `Xtras/QuickTime*` - QuickTime Xtras
- `wrapper_silentbaystudios.dcr` - Silent Bay Studios wrapper

---

## 2. File Formats

| Format | Extension | Description |
|---|---|---|
| `.dcr` | Director Movie | Protected Director movie (executable content) |
| `.dir` | Director Movie | Unprotected Director movie (source) |
| `.w3d` | Shockwave 3D | 3D scene/models (Intel 3D format) |
| `.cct` | Cast | Shockwave cast member (audio, scripts, etc.) |
| `.x32` | Xtra | Director extension (DLL-based) |
| `.dll` | Native | Windows DLLs (Director runtime) |

---

## 3. Asset Structure

```
Split Second Arcade Edition/
├── Projector.exe              # Director Projector (runtime)
├── SPR.exe                    # Silent Bay Studios wrapper
├── split_second.dcr           # Main game movie
├── level.w3d                  # 3D level data
├── sounds.cct                 # Audio cast
├── gameloader.dcr             # Loader movie
├── lingo.ini                  # Lingo config
├── Projector.ini              # Projector settings
├── sponsor1-3.jpg             # Sponsor images
├── wrapper_silentbaystudios.dcr
├── Dirapi.dll                 # Director API
├── Iml32.dll                  # Image library
├── Proj.dll                   # Projector core
├── msvcp71.dll / msvcr71.dll  # VC++ 2003 runtime
└── Xtras/                     # Director Xtras (plugins)
    ├── Havok.x32              # Havok Physics
    ├── Dynamiks.x32           # Physics
    ├── Flash Asset.x32        # Flash
    ├── Shockwave 3D Asset.x32 # 3D
    ├── SketchUpReader.dll     # SketchUp import
    ├── MixCollada.x32         # Collada import
    ├── MixSkp.x32             # SketchUp import
    ├── QuickTime*             # QuickTime
    └── ... (80+ Xtras)
```

---

## 4. Key Technical Details

- **NOT the Black Rock Studio engine** - This is a Director/Shockwave port!
- **Silent Bay Studios** - Porting studio (specialized in Director/Shockwave)
- **Adobe Director 11.5** - Last major Director version (2009)
- **Shockwave 3D** - Intel 3D technology (acquired by Adobe)
- **Lingo scripting** - Director's proprietary language (similar to JavaScript)
- **Xtras system** - Plugin architecture for extensions
- **Web-originated** - Originally browser-based (Shockwave Player)
- **Havok Physics** - Via Xtra (not native integration)

---

## 5. Documentation Notes

- **Major finding:** This is NOT the same engine as console Split/Second
- **Console version** - Black Rock Studio proprietary engine (Havok + custom)
- **PC Arcade Edition** - Complete rewrite in Director/Shockwave
- **Silent Bay Studios** - Known for Director/Shockwave ports
- **Director EOL** - Adobe discontinued Director in 2017
- **Shockwave EOL** - Discontinued 2019

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Split Second Arcade Edition\`*  
*Engine: Adobe Director 11.5 / Shockwave 3D, Silent Bay Studios 2010*