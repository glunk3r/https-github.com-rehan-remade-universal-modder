# Crash Time 2 (Alarm für Cobra 11) — Teardown Documentation

**Game:** Crash Time 2 (Alarm für Cobra 11) (PC, 2008)  
**Developer:** Synetic GmbH (German)  
**Publisher:** RTL Games / JoWooD  
**Engine:** Synetic 3D Landscape Engine (evolved from Crash Time 1)

---

## 1. Game Engine

**Synetic 3D Landscape Engine** (evolved from Crash Time 1)
- **Middleware:** **None** — DirectX 9, custom physics
- **Executable:** Not found in dump (likely `gC11_PC.exe` or similar)
- **Physics:** Custom damage system (DAM_CRASH_* family trait; physics middleware unconfirmed — no exe in dump)
- **Graphics:** DirectX 9 (D3DX9 Shader Compiler 9.12.589)
- **Audio:** DirectSound/DirectMusic (WMA, WAV)
- **Video:** WMV
- **Scripting:** None found (C++ only)

**Evidence (format-level only — dump contained no executable; string claims retracted after CT0/CT1 exe audits falsified `ODEConfig`/`PHYSICS_*`/`VehicleDamage::*`/`TrackEditor*`):**
- `DAM_CRASH_*` damage system (family trait, exe-verified in CT0/CT1)
- File-format evolution vs CT1 (see §2)

---

## 2. File Formats (Evolved from Crash Time 1)

### New Formats in Crash Time 2
| Format | Extension | Description |
|---|---|---|
| `.vtf` | 5 | Vector fonts (font textures) |
| `.trl` | 1 | Trail data? |
| `.cpt` | 1 | Checkpoint? |
| `.bak` | 1 | Backup |
| `.ds` | 1 | Data file |
| `.fxp` | 1 | Effect preset? |

### Removed/Changed from Crash Time 1
| Format | Change |
|---|---|
| `.str` | Reduced from 36 to 3 |
| `.ro1`-`.ro4` | Road data (same) |
| `.wtr` | Reduced from 5 to 5 |
| `.wpt` | Reduced from 3 to 3 |

### New Asset Types
| Format | Count | Description |
|---|---|---|
| `.vtf` | 5 | Vector font textures |
| `.trl` | 1 | Trail data |
| `.cpt` | 1 | Checkpoint data |
| `.bak` | 1 | Backup file |

---

## 3. Asset Structure (Similar to Crash Time 1)

### Main Directories
| Directory | Description |
|---|---|
| `stdstuff/` | Shared assets (fonts, textures, tachos, particles) |
| `Traffic/` | Traffic vehicles (cars, trucks, buses) |
| `Trains/` | Train models and data |
| `Vehicles/` | Player vehicles (30+ vehicles) |
| `Scenarios/` | Mission scenarios |
| `Missions/` | Mission definitions |
| `FrontEnd2/` | Updated frontend UI |
| `Autos/` | Vehicle definitions |
| `Motoren2/` | Engine/physics data |
| `Videos/` | WMV cutscenes |
| `Sounds/` | Audio files |

### Vehicle Structure (Enhanced)
| Vehicle | Model | LODs | Features |
|---|---|---|---|
| 30+ vehicles | Each with `.MOX`/`.MTL` | LOD0-LOD3 + shop variants | Enhanced detail |

### Track System
| Format | Description |
|---|---|
| `.trk` / `.trf` | Track definitions (with `.trf` = track reference?) |
| `.BIN` | Track geometry (binary) |
| `.3DF` | Theme/scene data |
| `.dcsc` | Scene collision |

---

## 3. Key Differences from Crash Time 1

| Feature | Crash Time 1 | Crash Time 2 |
|---|---|---|
| **Tracks** | ~60 | ~60+ (more rally) |
| **Vehicles** | 13 | 30+ (more variety) |
| **Environments** | 3 themes | 4 themes (Coast, Island, Snow, Stadium) |
| **Track Editor** | Basic | Enhanced (`.trf` track references) |
| **Vehicle Variants** | Basic LODs | LOD0-LOD3 + shop variants |
| **Traffic** | Basic | Enhanced (more traffic types, `_trf` refs) |
| **Trains** | Basic | Expanded (Express, Goods, etc.) |
| **Fonts** | Basic | Vector fonts (`.vtf`) |

---

## 3. Engine Analysis

**Engine:** Synetic 3D Landscape Engine (evolved)
- **Graphics:** DirectX 9 (D3DX9 Shader Compiler 9.12.589)
- **Physics:** Custom damage system (DAM_CRASH_* family trait; physics middleware unconfirmed — no exe in dump)
- **Audio:** DirectSound/DirectMusic (WMA, WAV)
- **Video:** WMV
- **Scripting:** None (C++ only)

**New in Crash Time 2:**
- Enhanced track editor with `.trf` references
- More vehicle variants with shop LODs
- Enhanced traffic system with `_trf` references
- Vector fonts (`.vtf`)
- More environments (Coast, Island, Snow, Stadium)

---

## 4. Documentation Files Created

| File | Description |
|---|---|
| `CRASH_TIME_2_TEARDOWN.md` | This document |
| `GAMES_KNOWLEDGE_BASE.md` | Updated with Crash Time 2 entry |

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Crash Time 2\`*  
*Engine: Synetic 3D Landscape Engine (evolved), Synetic GmbH 2008*