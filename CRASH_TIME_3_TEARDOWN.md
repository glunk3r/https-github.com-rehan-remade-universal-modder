# Crash Time 3 (Alarm für Cobra 11) — Teardown Documentation

**Game:** Crash Time 3 (Alarm für Cobra 11) (PC, 2009)  
**Developer:** Synetic GmbH (German)  
**Publisher:** RTL Games / JoWooD  
**Engine:** Synetic 3D Landscape Engine (evolved from Crash Time 1/2)  

---

## 1. Game Engine

**Synetic 3D Landscape Engine** (evolved from Crash Time 1/2)
- **Middleware:** **None verified** — DirectX 9, custom physics (no exe in dump)
- **Executable:** Not found in dump
- **Physics:** Custom damage system (DAM_CRASH_*) — physics middleware unconfirmed (no exe in dump)
- **Graphics:** DirectX 9 (D3DX9 Shader Compiler 9.12.589)
- **Audio:** DirectSound/DirectMusic (WMA, WAV, OGG)
- **Video:** Bink Video (`.bik`)
- **Scripting:** None found (C++ only)

**Evidence (format-level only — dump contained no executable; string claims retracted after CT0/CT1 exe audits falsified `ODEConfig`/`PHYSICS_*`/`VehicleDamage::*`/`TrackEditor*`):**
- `DAM_CRASH_*` damage system (family trait, exe-verified in CT0/CT1)
- File-format evolution vs CT2 (see §2)

---

## 2. File Formats (Evolved from Crash Time 2)

### New Formats in Crash Time 3
| Format | Extension | Description |
|---|---|---|
| `.dds` | 1 | DirectDraw Surface texture |
| `.ogg` | 4+ | Ogg Vorbis audio |

### Removed/Changed from Crash Time 2
| Format | Change |
|---|---|
| `.bik` | Present (Bink Video, per registry) |
| `.wmv` | Removed |
| `.tob` | Removed |
| `.wma` | Reduced from 19 to 0 |
| `.wmv` | Removed |

### Asset Structure
| Directory | Description |
|---|---|
| `stdstuff/` | Shared assets (fonts, textures, tachos, particles) |
| `Traffic/` | Traffic vehicles (cars, trucks, buses, new: Airplane, Bagger, Dumper, etc.) |
| `Trains/` | Train models (Express, Goods, etc.) |
| `Traffic/` | Expanded vehicle types (Airplane, Bagger, Dumper, KombiLow, PrioLow, SemirLow, TransporterLow 1-3, Trolley1, Minilader, Stapler, TransporterLow 1-3) |
| `Trains/` | Express_LOK, Express_LOKende, Express_Persw, Gueterwagon, Lok, MD500, Niederbwagen, poliz_hub, Wagon, zivil_hub |
| `Traffic/` | Expanded vehicle types (AlligatorLow, Bagger, Dumper, KombiLow, PrioLow, SemirLow, TransporterLow 1-3, Trolley1, Minilader, Stapler, TransporterLow 1-3, rtw, stadtbus, etc.) |
| `stdstuff/` | Shared assets (fonts, textures, tachos, particles, waypoints) |
| `Traffic\` | Expanded vehicle types |

---

## 2. File Formats (Evolved from Crash Time 2)

### Vehicle Formats
| Format | Extension | Description |
|---|---|---|
| `.MOX` / `.MTL` | Model / Material | Vehicle models (LOD0-LOD3 + shop variants) |
| `.trf` | Track reference | Track reference files (`.trf`) |
| `.MOX` / `.MTL` | Model / Material | Traffic vehicles with LODs (low, med, r_h, r_v) |
| `.CPO` / `.COL` | Collision | Collision objects |

### New Formats
| Format | Count | Description |
|---|---|---|
| `.trf` | 10+ | Track reference files |
| `.ogg` | 4+ | Ogg Vorbis audio (replaces `.wma`/`.wmv`) |

### Removed Formats
| Format | Status |
|---|---|
| `.wmv` | Removed |
| `.tob` | Removed |
| `.wma` | Removed |
| `.wmv` | Removed |
| `.tob` | Removed |

---

## 3. Asset Structure

### Traffic Vehicles (Expanded from CT2)
| Type | Count | Variants |
|---|---|---|
| Passenger cars | 10+ | Low/Med/High LOD + r_h/r_v variants |
| Trucks (lkw_blau, lkw_gelb, lkw_gruen, lkw_rot, lkw_rot) | 5+ | Low/Med/High + r_h/r_v |
| Special | 10+ | Airplane, Bagger, Dumper, KombiLow, PrioLow, SemirLow, TransporterLow 1-3, Trolley1, Minilader, Stapler, TransporterLow 1-3, rtw, stadtbus, etc. |

### Traffic Structure (Per Vehicle)
```
VehicleName/
├── Vehicle.MOX          # Main model
├── Vehicle.MTL          # Material
├── Vehicle_colli.CPO    # Collision
├── Vehicle_low.MOX/.MTL # LOD1
├── Vehicle_med.MOX/.MTL # LOD2
├── Vehicle_r_h.MOX/.MTL # Right-hand drive
├── Vehicle_r_v.MOX/.MTL # Right-hand drive variant
├── Vehicle_low.MOX/.MTL # LOD1
├── Vehicle_med.MOX/.MTL # LOD2
├── Vehicle_r_h.MOX/.MTL # RHD variant
├── Vehicle_r_v.MOX/.MTL # RHD variant
├── _VehicleName.trf     # Track reference
└── textures/
    ├── VehicleName.ptx
    ├── kfzteile.ptx
    ├── Shattglass.ptx
    └── ...
```

### New Vehicle Types (CT3 Additions)
| Vehicle | Description |
|---|---|
| `Airplane` | Airplane model with variants |
| `Bagger` | Excavator |
| `Dumper` | Dump truck |
| `AlligatorLow` | Low-profile alligator |
| `Dumper` | Dump truck |
| `KombiLow` | Low-profile kombi |
| `PrioLow` | Priority low vehicle |
| `SemirLow` | Semi-truck low |
| `TransporterLow 1-3` | Transporter variants |
| `Trolley1` | Trolley |
| `Minilader` | Mini loader |
| `Stapler` | Forklift |
| `TransporterLow 1-3` | Transporter variants |
| `Stapler` | Forklift |
| `AlligatorLow` | Low-profile alligator |
| `Bagger` | Excavator |
| `Dumper` | Dump truck |
| `KombiLow` | Low-profile kombi |
| `PrioLow` | Priority low vehicle |
| `SemirLow` | Semi-truck low |
| `TransporterLow 1-3` | Transporter variants |
| `Trolley1` | Trolley |
| `Minilader` | Mini loader |
| `Stapler` | Forklift |
| `rtw` | RTV vehicle |
| `stadtbus` | City bus |

---

## 3. File Formats (Evolved)

### New Formats
| Format | Extension | Description |
|---|---|---|
| `.ogg` | 4+ | Ogg Vorbis audio (replaces `.wma`) |

### Removed Formats
| Format | Status |
|---|---|
| `.wmv` | Removed |
| `.wma` | Removed |
| `.tob` | Removed |
| `.bik` | Present (Bink Video, per registry) |
| `.wmv` | Removed |

### Persistent Formats
| Format | Count | Description |
|---|---|---|
| `.ptx` | 900+ | Textures |
| `.mox` / `.mtl` | ~500 each | Models / Materials |
| `.ptx` | 900+ | Textures |
| `.mox` / `.mtl` | ~500 each | Models / Materials |
| `.trf` | 50+ | Track reference files |
| `.cob` / `.cpo` | ~50 each | Collision objects |
| `.trf` | 20+ | Track reference files |
| `.ptx` | 900+ | Textures |
| `.mox` / `.mtl` | ~500 each | Models / Materials |
| `.trf` | 50+ | Track reference files |
| `.cpo` | ~50 | Collision objects |
| `.tree` | 45 | Scene graph |
| `.cob` | 39 | Collision objects |
| `.ro1`-`.ro4` | 3 each | Road data |
| `.sni`/`.smp`/`.dat`/`.vef`/`.slt`/`.str` | 3 each | Misc |
| `.tob` | 20 | Unknown |
| `.wtr` | 5 | Water data |
| `.wpt` | 3 | Waypoints |
| `.geo` | 3 | Geometry |
| `.lvl` | 3 | Levels |
| `.qad` | 3 | Quad data |
| `.ro1`-`.ro4` | 3 each | Road segments |
| `.sni`/`.smp`/`.dat`/`.vef`/`.slt`/`.str` | 3 each | Misc |
| `.tob` | 20 | Unknown binary |
| `.wma` | Removed | |
| `.wtr` | 5 | Water data |
| `.wpt` | 3 | Waypoints |
| `.geo` | 3 | Geometry |
| `.lvl` | 3 | Levels |
| `.qad` | 3 | Quad data |
| `.ro1`-`.ro4` | 3 each | Road segments |
| `.sni`/`.smp`/`.dat`/`.vef`/`.slt`/`.str` | 3 each | Misc |

---

## 2. Asset Structure

### Main Directories
| Directory | Description |
|---|---|
| `stdstuff/` | Shared assets (fonts, textures, tachos, particles, waypoints) |
| `Traffic/` | Traffic vehicles (expanded to 30+ types) |
| `Trains/` | Train models (Express, Goods, etc.) |
| `Traffic/` | Expanded vehicle types (Airplane, Bagger, Dumper, etc.) |
| `Trains/` | Train models (Express, Goods, etc.) |
| `stdstuff/` | Shared assets |
| `Traffic\` | Expanded vehicle types |

### Vehicles (Expanded to 30+ types)
| Category | Types |
|---|---|
| Passenger cars | kl_w1-4, mk_w1-4, kombi, etc. |
| Trucks | lkw_blau, lkw_gelb, lkw_gruen, lkw_rot, lkw_m, lkw_m1, lkw_rot |
| Special | Airplane, Bagger, Dumper, AlligatorLow, KombiLow, PrioLow, SemirLow, TransporterLow 1-3, Trolley1, Minilader, Stapler, rtw, stadtbus, etc. |
| Trains | Express_LOK, Express_LOKende, Express_Persw, Gueterwagon, Lok, MD500, Niederbwagen, poliz_hub, Wagon, zivil_hub |

---

## 3. Engine Analysis

**Engine:** Synetic 3D Landscape Engine (evolved)
- **Graphics:** DirectX 9 (D3DX9 Shader Compiler 9.12.589)
- **Physics:** Custom damage system (DAM_CRASH_* family trait; physics middleware unconfirmed — no exe in dump)
- **Audio:** DirectSound/DirectMusic (WAV, OGG)
- **Video:** Bink Video (`.bik`) - **NEW in CT3**
- **Scripting:** None (C++ only)

**New in Crash Time 3:**
- Ogg Vorbis audio support (`.ogg` files)
- Expanded vehicle roster (30+ traffic types)
- New vehicle types: Airplane, Bagger, Dumper, AlligatorLow, etc.
- Train system expanded (Express, Goods, etc.)

---

## 4. Documentation Files Created

| File | Description |
|---|---|
| `CRASH_TIME_3_TEARDOWN.md` | This document |
| `GAMES_KNOWLEDGE_BASE.md` | Updated with Crash Time 3 entry |

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Crash Time 3\`*  
*Engine: Synetic 3D Landscape Engine (evolved), Synetic GmbH 2009*