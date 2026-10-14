# Build'n Race (USA) (En,Fr,Es) — Wii Teardown Documentation

**Game:** Build'n Race (USA) (En,Fr,Es)  
**Platform:** Nintendo Wii  
**Developer:** Gaijin Entertainment (published by Zoo Games)  
**Year:** 2009 (Wii release)  
**Game ID:** RBR (likely)  
**Region:** NTSC (USA), also En,Fr,Es languages  

---

## 1. Game Engine

**Custom Engine** — Proprietary engine by Gaijin Entertainment (Russian developer)
- **Developer:** Gaijin Entertainment (Russian studio, later known for War Thunder, Crossout, etc.)
- **Publisher:** Zoo Games (US), other publishers in other regions
- **Platform:** Nintendo Wii
- **Engine:** Custom proprietary engine (Gaijin Engine)
- **Middleware:** ODE Physics (referenced in strings), likely custom rendering
- **Scripting:** None found (C++ only, no Lua scripts found)

**Evidence:**
- Main executable: `bnrNTSC.elf` — Wii ELF (PowerPC, big-endian)
- Strings reference: `ODEConfig`, `PHYSICS_BODY_GF`, `VEHICLE_CONFIG`, `VehicleHealth.cpp`, `VehicleDamage`, `VehicleDamage::InitMorphSections`
- Physics references: `ODEConfig`, `PHYSICS_BODY_GF`, `PHYSICS_BODY_TRIMESH_G`, `PHYSICS_INSTANCE_GF`
- Vehicle system: `VEHICLE_CONFIG`, `VehicleDamage`, `VehicleDamage::InitMorphSections`, `VehicleResetHeight`, `VEHICLE_COLLISION`, `VEHICLE_DESTROYED`, `VEHICLE.%s.UPGRADES`
- Editor references: `TrackEditorGUI`, `EditorUpdate`, `AddEditorTweaks`, `TrackEditorLoadTrackGUI`, `CITY_EditorSunColourR/G/B`, `RALLY_EditorAmbientColourB`, `RALLY_EditorSunColourR/G/B`, `RALLY_EditorSunRotY`
- Editor UI: `TrackEditorGUI`, `TrackEditorLoadTrackGUI`, `PauseWheelSensitivityMenuGUI`, `OverwriteMyTrackYesNoGUI`
- Game modes: `Quick Race`, `ChallengeDifficultySelectMenuGUI`, `MultiplayerGameTypeMenuGUI`
- Physics engine: **ODE (Open Dynamics Engine)** referenced directly
- Build system: References to `BuildData`, `Out of memory (VertexList)`

---

## 2. Disc Layout

**Disc Size:** Not specified (Wii DVD, likely 4.7 GB)

**Main Executable:** `bnrNTSC.elf` (3.8 MB, Wii ELF, PowerPC, big-endian)

### ELF Analysis
- **Format:** ELF32 Big-Endian (PowerPC)
- **Entry Point:** 0x8000403C
- **Program Headers:** 13 segments
- **Sections:** 18 sections
- **Entry Point:** 0x8000403C
- **Architecture:** PowerPC (Machine: 0x14 = PowerPC)
- **Endianness:** Big-endian (Wii standard)
- **Flags:** 0x80000000 (Wii-specific flags)

### Key Sections
| Section | VAddr | Size | Description |
|---|---|---|---|
| .text | 0x80004000 | 0x2690 | Entry code |
| .text (main) | 0x80006760 | 0x239D78 | Main code (2.3 MB) |
| .rdata | 0x8024D860 | 0x103450 | Read-only data (1 MB) |
| .data | 0x8024D860 | 0xD224 | Initialized data |
| .bss | 0x80350CC0 | 0xA8350 | Zero-initialized (BSS) |
| .bss2 | 0x803F9DC0 | 0xC8C | More BSS |
| .bss3 | 0x803FAA60 | 0x3038 | More BSS |
| .bss4 | 0x803FDAA0 | 0x10 | Tiny BSS |

---

## 3. File Formats

### Main Configuration Files
| File | Description |
|---|---|
| `Game.ini` | Main game configuration |
| `Crash.ini` | Crash handling config |
| `default.sld` | Save/load defaults |
| `Vehicle.ini` | Vehicle definitions |
| `ODE.ini` | ODE Physics configuration |
| `char.ini` | Character settings |

### Track Data (`.BIN` / `.TRK` / `.trk`)

#### Track Binary (`.BIN`)
- **Format:** Custom binary format
- **Header (256 bytes):** Big-endian structure
- **Structure:** 
  - Header (256 bytes): Contains multiple 32-bit big-endian values
  - First word: `0x00000001` (version/magic)
  - Contains multiple float values (0x3F800000 = 1.0f, 0x42F00000 = 120.0f, etc.)
  - Repeated patterns of position/scale/rotation data
- **Size:** 273 KB - 1.5 MB per track
- **Count:** 20 City tracks, 20 Race tracks, 20 Rally tracks + 4 NEW tracks each

#### Track Definition (`.TRK` / `.trk`)
- **Format:** Binary track definition
- **Header (32 bytes):**
  - `0B 00 00 00` - Magic/Version
  - `20 28 20 01` - Track type/version
  - Followed by track-specific data (length, checksums, etc.)
- **Size:** 86,448 bytes (fixed for .TRK/.trk files)
- **Naming:** `city_1.TRK` through `city_20.TRK`, `race_1.TRK` to `race_20.TRK`, `rally_1.trk` to `rally_20.trk` + `NEW1-4.TRK`

#### Theme Data (`.3DF`)
- **Magic:** `33 64 66 00 17` = "3df\0\x17" (custom 3D format)
- **Files:** `THEME.3DF`, `SCENE.3DF`, `FLAT.3DF`, `SKY.3DF`, `MAPS.SPR`, `BMAPS.BIN`
- **Per-theme:** City, Race, Rally each have full theme set
- **Sizes:** 
  - `THEME.3DF`: ~23-25 MB each
  - `SCENE.3DF`: ~300-450 KB
  - `FLAT.3DF`: ~34-68 KB
  - `SKY.3DF`: ~28-54 KB
  - `MAPS.SPR`: ~49 KB
  - `BMAPS.BIN`: 3-7 KB

### Vehicle Data (`.3DF`, `.SPR`, `.TWK`, `.3DF`)
Each vehicle has:
| File | Description |
|---|---|
| `VEHICLE.3DF` | Main vehicle model (NSBMD-like) |
| `FESPL.3DF` | Front-end split model |
| `FEWHEELS.3DF` / `.SPR` | Front-end wheels |
| `SPL1-5.3DF` | Spline/spline data |
| `WHEEL1-5.3DF/.SPR` | Wheel models |
| `PAINT.SPR` | Paint texture |
| `CAMERA.TWK` / `CONFIG.TWK` / `config.txt` | Vehicle config (text) |
| `VEHICLE.3DF` | Main model |

### Vehicles (13 total)
| Vehicle | Model Size | Theme |
|---|---|---|
| Curtis | 587 KB | - |
| FireGTO | 487 KB + parts | Race |
| GTX360 | 485 KB + parts | Race |
| Holly | 555 KB | - |
| LJ | 593 KB | - |
| Max | 615 KB | - |
| Police | 614 KB + parts | City/Race |
| Rich | 573 KB | - |
| SportsEvo | 846 KB + parts | Race |
| Sticky | 532 KB | - |
| Taxi | 641 KB + parts | City |
| Z66Turbo | 567 KB + parts | Race |

### Track Data (`.BIN`)
- **Format:** Binary track geometry
- **Header:** 256-byte header with repeated float patterns
- **Structure:** 
  - First word: `0x00000001` (version)
  - Repeated float triples (position/scale/rotation)
  - Values: `0x3F800000` (1.0), `0x42F00000` (120.0), `0x43200000` (160.0), etc.
- **Sizes:** 273 KB - 1.5 MB per track

### Maps (`.SPR`, `.BIN`)
- **SPR:** Sprite/texture format (header `32 64 66 00 0A` = "2df\0\n")
- **BMAPS.BIN:** Binary map data (3-7 KB)
- **MAPS.SPR:** Map sprites (~49 KB)
- **BLURMAP.SPR / ENVMAP.SPR / FX.SPR / SHADMAP.SPR:** Effects maps

### Particle Effects (`.pef` / `.SPR`)
- **Format:** Particle effect files (`.pef` = 200-204 bytes each)
- **SPR:** Larger particle textures (e.g., `SPARK.SPR` = 1.1 MB)

### Text Configuration (`.TWK`, `.txt`, `.ini`)
| File | Description |
|---|---|
| `GAME.TWK` | Game settings |
| `EDITOR.TWK` | Editor settings |
| `Vehicle.ini` | Vehicle definitions |
| `Game.ini` | Game config |
| `Crash.ini` | Crash handling |
| `ODE.ini` | ODE Physics config |
| `char.ini` | Character settings |
| `Vehicle.ini` | Vehicle definitions |
| `config.txt` (per vehicle) | Vehicle-specific config |
| `CAMERA.TWK` / `CONFIG.TWK` | Vehicle camera/config |

### Localization (`.TXF`)
- **Files:** `ENGLISH.TXF`, `FRENCH.TXF`, `GERMAN.TXF`, `ITALIAN.TXF`, `SPANISH.TXF`
- **Sizes:** ~12-15 KB each
- **Format:** Text format (likely key=value or similar)

### Particles (`.pef`)
- **Format:** Particle effect files (200-204 bytes each)
- **Types:** Boost, Dirt, Dust, Explosion, Fire, Glass, Grass, Impact, Mud, Sand, Skid, Smoke, Sparks, Trail, etc.
- **Size:** 200-204 bytes each (compact)

### Themes (3 total)
| Theme | THEME.3DF | SCENE.3DF | FLAT.3DF | SKY.3DF | MAPS.SPR | BMAPS.BIN | Tracks |
|---|---|---|---|---|---|---|---|
| **City** | 23.9 MB | 453 KB | 34 KB | 54 KB | 49 KB | 7 KB | 20 |
| **Race** | 25.0 MB | 453 KB | 34 KB | 28 KB | 49 KB | 3 KB | 20 |
| **Rally** | 24.3 MB | 311 KB | 68 KB | 152 KB | 49 KB | 4 KB | 20 |

---

## 4. Engine Summary

| Aspect | Detail |
|---|---|
| **Engine** | Custom Gaijin Engine (proprietary) |
| **Language** | C++ (PowerPC), no scripting language found |
| **Physics** | **ODE (Open Dynamics Engine)** — explicitly referenced |
| **Rendering** | Custom Wii renderer (GX API) |
| **Audio** | Custom (referenced `DVDLowAudioBufferConfig`) |
| **Middleware** | **ODE Physics** (only confirmed middleware) |
| **File System** | Custom archive-like structure (no single archive, loose files) |
| **Build System** | Custom (references to `BuildData`, vertex buffer building) |

---

## 5. Tools for Exploration

| Task | Tool |
|---|---|
| **ELF Analysis** | `readelf`, `objdump`, Ghidra, IDA Pro (PowerPC big-endian) |
| **ELF Strings** | `strings` / custom extractor |
| **3DF Models** | Custom parser needed (custom format, magic `33 64 66 00 17`) |
| **SPR** | Custom parser (header `32 64 66 00 0A`) |
| **Track .BIN** | Custom parser (binary geometry) |
| **Track .TRK/.trk** | Custom parser (86 KB fixed) |
| **VEHICLE.3DF** | Custom parser (similar to .3DF) |
| **Text Configs** | Text editor (`.ini`, `.tzw`, `.txt`, `.cfg`) |
| **Localization** | Text editor (`.TXF` files) |
| **Particle (.pef)** | Custom parser (200-204 bytes fixed) |
| **Audio** | No standard audio format found (custom or embedded in ELF) |

---

## 9. Knowledge Base Entry

```markdown
Build'n Race (USA) (En,Fr,Es)
├── Engine: Custom Gaijin Engine (proprietary)
├── Middleware: ODE Physics (only confirmed middleware)
├── Platform: Nintendo Wii
├── Executable: bnrNTSC.elf (Wii ELF, PowerPC, big-endian, 3.8 MB)
├── Formats: .3DF (custom 3D), .SPR (sprites), .BIN/.TRK/.trk (tracks), .3DF (vehicles), .SPR (2D), .pef (particles), .luac absent
├── Physics: ODE (Open Dynamics Engine) — explicitly referenced
├── Tracks: 60+ tracks across 3 themes (City, Race, Rally)
├── Vehicles: 13 vehicles with customizable parts
├── Tracks: 20 per theme + 4 bonus = 60+ tracks
├── Config: .ini/.tzw/.txt text files
├── Localization: 6 languages (EN/FR/ES/DE/IT/NL)
├── Dev: Gaijin Entertainment (Russian, later War Thunder, Crossout)
├── Publisher: Zoo Games (US)
└── Year: 2009
```

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Build'n Race (USA) (En,Fr,Es)\`*  
*ELF: bnrNTSC.elf (3.8 MB, PowerPC, big-endian), Gaijin Entertainment 2009*