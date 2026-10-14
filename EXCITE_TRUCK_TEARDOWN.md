# Excite Truck (USA) — Wii Teardown Documentation

**Game:** Excite Truck (USA)  
**Platform:** Nintendo Wii  
**Developer:** Monster Games (US)  
**Publisher:** Nintendo  
**Year:** 2006 (Wii launch title)  
**Game ID:** R4QE (likely)  
**Region:** NTSC (USA)  

---

## 1. Game Engine

**Custom Monster Games Engine** (proprietary)
- **Developer:** Monster Games (US, known for Excite Truck, Excitebots, Pilotwings Resort)
- **Publisher:** Nintendo
- **Platform:** Nintendo Wii
- **SDK:** Nintendo Wii SDK (Nintendo Revolution SDK)
- **Middleware:** **Bink Video** (Rad Game Tools), likely **Havok Physics** or custom
- **Scripting:** None found (C++ only)

**Evidence:**
- `.bik` files for video (Bink Video)
- `.brsar` for audio (Nintendo BRSTM/BRSAR format)
- `.tpl` for textures (Wii TPL format)
- `.vtf` for vector fonts
- Custom `.trk`/`.toc` track format
- Custom `.car`/`.toc` vehicle format
- Custom `.res`/`.toc` resource format

---

## 2. Disc Layout

**Disc Format:** Wii Optical Disc (single layer, ~4.7 GB)

**Main Executable:** **Missing from dump** — likely `main.dol` or `boot.dol` from the root of the Wii disc image (not included in this extracted dump)

**Present Files:**
```
opening.bnr          305,320 bytes  — Wii banner (animated)
video/uisingle.bik    86,933,648  — Bink video (UI)
video/credits.bik    59,776,964  — Bink video (credits)
uiaction.res         25,574,848  — UI action resources
uiaction.toc          33,632      — UI action TOC
overlays.res          3,673,536  — Overlay resources
overlays.toc          10,376      — Overlay TOC
vc.cfg                5            — Virtual Console config
```

---

## 3. Asset Formats

### Vehicle Models (`.car` / `.toc`)
| Vehicle | Model Size | TOC |
|---|---|---|
| Alpine | 1,024 KB | 1,808 B |
| Blaster | 934 KB | 1,332 B |
| Boulder | 908 KB | 1,264 B |
| Dominator | 1,000 KB | 1,264 B |
| Dynamo | 1,033 KB | 1,400 B |
| Firefly | 1,002 KB | 1,332 B |
| Dominator | 1,000 KB | 1,264 B |
| Kodiac | 1,119 KB | 1,672 B |
| Mako | 959 KB | 1,468 B |
| Mammoth | 924 KB | 1,332 B |
| Mongoose | 822 KB | 1,196 B |
| Rad | 1,095 KB | 1,536 B |
| Raven | 938 KB | 1,332 B |
| Razor | 946 KB | 1,264 B |
| Saguaro | 885 KB | 1,468 B |
| Serpent | 871 KB | 1,400 B |
| Summit | 1,074 KB | 1,740 B |
| Trekker | 1,055 KB | 1,400 B |
| Wasp | 852 KB | 1,264 B |
| Wolf | 1,092 KB | 1,740 B |
| Wolverine | 817 KB | 1,196 B |

**Format:** `.car` (model data) + `.toc` (table of contents)
- Each vehicle has base model + `_e` variant (enhanced/alternate)
- `.toc` files are small (1,264-1,808 bytes) — table of contents

### Track Data (`.trk` / `.toc`)
| Track | Size | Variants |
|---|---|---|
| canada.trk | 12,035,520 | 6 variants (Opt1, Opt5, Opt6, Rainy, Sunny) |
| china.trk | 8,539,584 | 3 variants |
| fiji.trk | 12,481,312 | 3 variants |
| finland.trk | 14,064,416 | 5 variants |
| kenya.trk | 6,449,952 | 4 variants |
| mexico.trk | 4,580,800 | 3 variants |
| scotland.trk | 7,998,240 | 4 variants |
| hugh_test.trk | 17,454,528 | (test track) |

**Format:** `.trk` (track geometry) + `.toc` (table of contents)
- Large files (6-17 MB) — contain track geometry, collision, objects
- Each track has multiple variants (Opt1-Opt6, Rainy, Sunny, Snowy, Rainy, Sunny)

### Vehicle Audio (`.sng` / `.toc`)
| File | Size |
|---|---|
| mus_canada.sng | 7,497,576 |
| mus_china.sng | 4,690,528 |
| mus_fiji.sng | 5,404,216 |
| mus_finland.sng | 6,277,136 |
| mus_hugh_test.sng | 3,301,384 |
| mus_kenya.sng | 4,525,920 |
| mus_mexico.sng | 6,813,200 |
| mus_postrace.sng | 3,493,968 |
| mus_prerace.sng | 539,152 |
| mus_scotland.sng | 5,159,936 |
| mus_ui.sng | 6,349,328 |
| mus_credits.sng | 3,115,104 |

### Resources (`.res` / `.toc`)
| File | Size |
|---|---|
| common.res | 308,497 |
| genesis.res | 20,736 |
| ghostcar.res | 3,940,520 |
| hobby_set.res | 1,764,800 |
| overlays.res | 3,673,536 |
| part.res | 129,824 |
| race.res | 5,602,752 |
| racesnd.res | 3,074,856 |
| tocres.res | 562,172 |
| uiaction.res | 25,574,848 |
| UIBig.res | 128 |

### Audio (`.brsar`, `.wma`, `.sng`)
| File | Count | Format |
|---|---|---|
| `.brsar` | 2 | Nintendo BRSTM/BRSAR audio archive |
| `.wma` | 19 | Windows Media Audio (music) |
| `.sng` | 12 | Custom audio (track music) |
| `.wma` (Music/) | 19 | Track music |

### Video (`.bik`)
| File | Size |
|---|---|
| video/uisingle.bik | 86,933,648 |
| video/credits.bik | 59,776,964 |

### Textures (`.tpl`)
- **`.tpl`** — Wii TPL texture format (2 files)

### Vector Fonts
- **`.vtf`** — Vector texture fonts (2 files)

### Config
- `vc.cfg` — Virtual Console config (5 bytes)

---

## 3. Engine Analysis

| Aspect | Detail |
|---|---|
| **Engine** | Custom Monster Games Engine |
| **Middleware** | **Bink Video** (Rad Game Tools), likely **Havok** or custom physics |
| **Graphics** | Wii GX API (fixed-function + TEV) |
| **Physics** | Custom (vehicle physics, terrain deformation) |
| **Audio** | Custom `.sng` + `.brsar` (Nintendo BRSTM) |
| **Scripting** | None found (C++ only) |
| **Build System** | Custom (track/vehicle `.toc` system) |

---

## 3. Track Format Analysis (`.trk` / `.toc`)

### Track Structure
- **`.trk`** — Large binary track data (6-17 MB)
- **`.toc`** — Table of contents (small, few KB)
- **Variants per track:** Opt1-Opt6, Rainy, Sunny, Snowy, etc.
- **Track count:** ~20 base tracks × 4-6 variants = ~80+ track variants

### Track List
| Region | Tracks |
|---|---|
| **Canada** | 6 variants |
| **China** | 4 variants |
| **Fiji** | 4 variants |
| **Finland** | 5 variants |
| **Kenya** | 4 variants |
| **Mexico** | 3 variants |
| **Scotland** | 4 variants |

---

## 4. Vehicle Format (`.car` / `.toc`)

### Structure
- **`.car`** — Binary model data (vertex, normals, UVs, materials)
- **`.toc`** — Table of contents (offsets, sizes, part names)
- **Variants:** Base + `_e` (enhanced) per vehicle

### Vehicle List (20 vehicles × 2 variants = 40 models)
| Vehicle | Base Size | Enhanced Size |
|---|---|---|
| Alpine | 1,024 KB | 1,084 KB |
| Blaster | 934 KB | 971 KB |
| Boulder | 908 KB | 946 KB |
| Dominator | 1,000 KB | 1,031 KB |
| Dynamo | 1,033 KB | 1,060 KB |
| Firefly | 1,002 KB | 1,011 KB |
| Dominator | 1,000 KB | 1,031 KB |
| Kodiac | 1,119 KB | 1,207 KB |
| Mako | 959 KB | 1,064 KB |
| Mammoth | 924 KB | 924 KB |
| Mongoose | 822 KB | 930 KB |
| Rad | 1,095 KB | 1,183 KB |
| Raven | 938 KB | 963 KB |
| Razor | 946 KB | 992 KB |
| Saguaro | 885 KB | 912 KB |
| Serpent | 871 KB | 933 KB |
| Summit | 1,074 KB | 1,127 KB |
| Trekker | 1,055 KB | 1,059 KB |
| Wasp | 852 KB | 916 KB |
| Wolf | 1,092 KB | 1,155 KB |
| Wolverine | 817 KB | 860 KB |

---

## 4. Engine Summary

| Aspect | Detail |
|---|---|
| **Engine** | Custom Monster Games Engine |
| **Language** | C++ (PowerPC) |
| **SDK** | Nintendo Wii SDK (Revolution SDK) |
| **Middleware** | Bink Video (Rad Game Tools) |
| **Physics** | Custom (terrain deformation, vehicle physics) |
| **Audio** | Custom `.sng` + `.brsar` (Nintendo BRSTM) |
| **Video** | Bink Video (`.bik`) |
| **Textures** | `.vtf` (vector), `.tpl` (Wii TPL) |
| **Scripting** | None (C++ only) |

---

## 3. Tools for Exploration

| Task | Tool |
|---|---|
| **View 3D models** | Custom parser for `.car` format (similar to NSBMD) |
| **Extract textures** | `texconv.exe` for `.tpl`, custom for `.ptx` |
| **Audio** | VGMToolbox for `.brsar`, `ffmpeg` for `.wma`/`.sng` |
| **Video** | `ffmpeg` for `.bik` (Bink) |
| **Track data** | Custom parser for `.trk`/`.toc` |

---

## 4. Documentation Files Created

| File | Description |
|---|---|
| `EXCITE_TRUCK_TEARDOWN.md` | This document |
| `GAMES_KNOWLEDGE_BASE.md` | Updated with Excite Truck entry |

---

## 5. Knowledge Base Entry

```markdown
Excite Truck (USA)
├── Engine: Monster Games proprietary
├── Middleware: Bink Video (Rad Game Tools)
├── Platform: Nintendo Wii
├── Formats: .car/.toc (vehicles), .trk/.toc (tracks), .sng/.brsar (audio), .bik (video)
├── Vehicles: 20 (2 variants each)
├── Tracks: ~20 base × 4-6 variants
├── Middleware: Bink Video only
└── Year: 2006 (Wii launch title)
```

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Excite Truck (USA)\`*  
*Wii ISO extracted assets, Monster Games 2006*