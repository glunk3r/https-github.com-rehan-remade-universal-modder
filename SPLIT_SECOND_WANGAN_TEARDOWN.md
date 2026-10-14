# Split/Second: Arcade Edition Wangan (PC) — Teardown Documentation

**Game:** Split/Second: Arcade Edition Wangan  
**Platform:** PC (Windows)  
**Developer:** Silent Bay Studios (port) / Black Rock Studio (original)  
**Publisher:** Disney Interactive Studios  
**Year:** 2010 (Arcade Edition)  
**Engine:** Adobe Director / Shockwave 3D (same as Arcade Edition, Japanese variant)

---

## 1. Game Engine

**Engine:** **Adobe Director 11.5 / Shockwave 3D** (identical to Arcade Edition)  
- **Middleware:** Same as Arcade Edition
  - **Adobe Director / Shockwave Player** (Projector.exe)
  - **Havok Physics** (Havok.x32 Xtra)
  - **Dynamiks** (physics Xtra)
  - **QuickTime** (QT6Asset.x32, QTAuth.x32, QTExport.x32)
  - **Flash** (Flash Asset.x32, FLVAsset.x32, F4VAsset.x32, MP4Asset.x32)
  - **SketchUp** (MixSkp.x32, SketchUpReader.dll)
  - **Collada** (MixCollada.x32)
- **Executable:** `Projector.exe` + `SPR.exe`
- **Main Movie:** `split_second_wangan.dcr` (Japanese variant)
- **Graphics:** DirectX 9 (via Director 3D)
- **Scripting:** **Lingo**
- **Physics:** Havok + Dynamiks

**Evidence from dump:**
- Identical Xtras folder to Arcade Edition
- `split_second_wangan.dcr` - Main movie (Wangan variant)
- `shaders_level1-3.w3d` - Additional shader W3D files
- `advert_loader.swf` - Flash advert loader
- `dummy.cct` - Dummy cast

---

## 2. File Formats (Same as Arcade Edition)

| Format | Extension | Description |
|---|---|---|
| `.dcr` | Director Movie | Protected Director movie |
| `.w3d` | Shockwave 3D | 3D scene/models |
| `.cct` | Cast | Shockwave cast member |
| `.swf` | Flash | Flash movie (advert_loader) |
| `.x32` | Xtra | Director extension |

---

## 3. Asset Structure (Same + Wangan Specific)

```
Split Second Arcade Edition Wangan/
├── Projector.exe              # Director Projector
├── SPR.exe                    # Silent Bay Studios wrapper
├── split_second_wangan.dcr    # Main game movie (Wangan)
├── level.w3d                  # 3D level data
├── shaders_level1.w3d         # Shader level 1
├── shaders_level2.w3d         # Shader level 2
├── shaders_level3.w3d         # Shader level 3
├── sounds.cct                 # Audio cast
├── gameloader.dcr             # Loader movie
├── lingo.ini                  # Lingo config
├── Projector.ini              # Projector settings
├── advert_loader.swf          # Flash advert loader
├── dummy.cct                  # Dummy cast
├── wrapper_silentbaystudios.dcr
├── Dirapi.dll / Iml32.dll / Proj.dll
├── msvcp71.dll / msvcr71.dll
└── Xtras/                     # Identical to Arcade Edition
    ├── Havok.x32
    ├── Dynamiks.x32
    ├── Flash Asset.x32
    └── ... (80+ Xtras)
```

---

## 4. Key Technical Details

- **Wangan variant** - Japanese highway racing theme (Wangan Midnight style)
- **Same engine** as Arcade Edition - Director/Shockwave
- **Additional shaders** - `shaders_level1-3.w3d` for visual variants
- **Flash integration** - `advert_loader.swf` for dynamic ads
- **Japanese localization** - Wangan branding, possible different tracks

---

## 5. Documentation Notes

- **Same engine** as Split/Second Arcade Edition
- **Wangan** = "Bayshore Route" (Tokyo highway racing culture)
- **Silent Bay Studios** - Ported both variants
- **Director/Shockwave** - Unusual choice for racing game
- **DLC/Variant strategy** - Same codebase, different content

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Split Second Arcade Edition Wangan\`*  
*Engine: Adobe Director 11.5 / Shockwave 3D, Silent Bay Studios 2010*