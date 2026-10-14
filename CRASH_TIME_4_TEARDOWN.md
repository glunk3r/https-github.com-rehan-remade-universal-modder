# Crash Time 4 (Alarm für Cobra 11) — Teardown Documentation

**Game:** Crash Time 4 (Alarm für Cobra 11) (PC, 2010)  
**Developer:** Synetic GmbH (German)  
**Publisher:** RTL Games / JoWooD  
**Engine:** Synetic 3D Landscape Engine (evolved from Crash Time 3)

---

## 1. Game Engine

**Synetic 3D Landscape Engine** (evolved from Crash Time 3)
- **Middleware:** **None verified** — DirectX 9, custom physics (no exe in dump)
- **Executable:** Not found in dump
- **Physics:** Custom damage system (DAM_CRASH_* family trait; physics middleware unconfirmed)
- **Graphics:** DirectX 9 (D3DX9 Shader Compiler 9.12.589)
- **Audio:** DirectSound/DirectMusic (WAV, OGG)
- **Video:** Bink Video (`.bik`) — **NEW in CT4**
- **Scripting:** None found (C++ only)

**Evidence (format-level only — dump contained no executable; string claims retracted after CT0/CT1 exe audits falsified `ODEConfig`/`PHYSICS_*`/`VehicleDamage::*`/`TrackEditor*`):**
- `DAM_CRASH_*` damage system (family trait, exe-verified in CT0/CT1)
- File-format evolution vs CT3 (see §2)

---

## 2. File Formats (Evolved from Crash Time 3)

### New Formats in Crash Time 4
| Format | Extension | Description |
|---|---|---|
| `.dds` | 1 | DirectDraw Surface texture |

### Removed/Changed from Crash Time 3
| Format | Change |
|---|---|
| `.ogg` | Removed (back to `.wav`/`.wma`?) |
| `.bik` | Added (Bink Video) |

### Persistent Formats
| Format | Count | Description |
|---|---|---|
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
| `.ro1`-`.ro4` | 3 each | Road data |
| `.sni`/`.smp`/`.dat`/`.vef`/`.slt`/`.str` | 3 each | Misc |
| `.tob` | 20 | Unknown |
| `.wtr` | 5 | Water data |
| `.wpt` | 3 | Waypoints |
| `.geo` | 3 | Geometry |
| `.lvl` | 3 | Levels |
| `.qad` | 3 | Quad data |
| `.ro1`-`.ro4` | 3 each | Road data |
| `.sni`/`.smp`/`.dat`/`.vef`/`.slt`/`.str` | 3 each | Misc |

---

## 2. Asset Structure

### Main Directories
| Directory | Description |
|---|---|
| `stdstuff/` | Shared assets (fonts, textures, tachos, particles, waypoints, WP_* waypoint system) |
| `Traffic/` | Traffic vehicles (50+ types with LODs) |
| `Trains/` | Train models (Express, Goods, etc.) |
| `Traffic/` | Expanded vehicle types (AlligatorLow, Bagger, Dumper, KombiLow, PrioLow, SemirLow, TransporterLow 1-3, Trolley1, Minilader, Stapler, TransporterLow 1-3, rtw, stadtbus, etc.) |
| `Trains/` | Train models (Express, Goods, etc.) |
| `stdstuff/` | Shared assets (fonts, textures, tachos, particles, waypoints, WP_* system) |
| `Traffic\` | Expanded vehicle types |

### Vehicle System (Enhanced from CT3)
| Category | Types | LODs |
|---|---|---|
| Cars | kl_w1-4, mk_w1-4, kombi, etc. | LOD0-LOD3 + r_h/r_v |
| Trucks | lkw_blau, lkw_gelb, lkw_gruen, lkw_rot, lkw_m, lkw_m1, lkw_rot | LOD0-LOD3 + r_h/r_v |
| Special | AlligatorLow, Bagger, Dumper, KombiLow, PrioLow, SemirLow, TransporterLow 1-3, Trolley1, Minilader, Stapler, TransporterLow 1-3, rtw, stadtbus, etc. | LOD0-LOD3 + r_h/r_v |

### Vehicle Structure (Per Vehicle)
```
VehicleName/
├── Vehicle.MOX          # Main model
├── Vehicle.MTL          # Material
├── Vehicle_colli.CPO    # Collision
├── Vehicle_low.MOX/.MTL # LOD1
├── Vehicle_med.MOX/.MTL # LOD2
├── Vehicle_r_h.MOX/.MTL # RHD variant
├── Vehicle_r_v.MOX/.MTL # RHD variant
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

### New Vehicle Types (CT4 Additions)
| Vehicle | Description |
|---|---|
| `AlligatorLow` | Low-profile alligator |
| `Dumper` | Dump truck |
| `Bagger` | Excavator |
| `KombiLow` | Low-profile kombi |
| `PrioLow` | Priority low vehicle |
| `SemirLow` | Semi-truck low |
| `TransporterLow 1-3` | Transporter variants |
| `Trolley1` | Trolley |
| `Minilader` | Mini loader |
| `Stapler` | Forklift |
| `TransporterLow 1-3` | Transporter variants |
| `rtw` | RTV vehicle |
| `stadtbus` | City bus |
| `PrioLow` | Priority low vehicle |
| `SemirLow` | Semi-truck low |
| `TransporterLow 1-3` | Transporter variants |
| `Dumper` | Dump truck |
| `AlligatorLow` | Low-profile alligator |

---

## 3. File Formats (Evolved from CT3)

### New Formats
| Format | Extension | Description |
|---|---|---|
| `.dds` | 1 | DirectDraw Surface texture |

### Removed Formats
| Format | Status |
|---|---|
| `.ogg` | Removed (back to `.wav`/`.wma`?) |

### Persistent Formats
| Format | Count | Description |
|---|---|---|
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
| `.ro1`-`.ro4` | 3 each | Road data |
| `.sni`/`.smp`/`.dat`/`.vef`/`.slt`/`.str` | 3 each | Misc |
| `.tob` | 20 | Unknown |
| `.wtr` | 5 | Water data |
| `.wpt` | 3 | Waypoints |
| `.geo` | 3 | Geometry |
| `.lvl` | 3 | Levels |
| `.qad` | 3 | Quad data |
| `.ro1`-`.ro4` | 3 each | Road data |
| `.sni`/`.smp`/`.dat`/`.vef`/`.slt`/`.str` | 3 each | Misc |

---

## 4. Asset Structure

### Main Directories
| Directory | Description |
|---|---|
| `stdstuff/` | Shared assets (fonts, textures, tachos, particles, waypoints, WP_* waypoint system) |
| `Traffic/` | Traffic vehicles (50+ types with LODs) |
| `Trains/` | Train models (Express, Goods, etc.) |
| `Traffic/` | Expanded vehicle types |
| `Trains/` | Train models (Express, Goods, etc.) |
| `stdstuff/` | Shared assets |
| `Traffic\` | Expanded vehicle types |

### Vehicle Types (50+ types)
| Category | Types |
|---|---|
| Cars | kl_w1-4, mk_w1-4, kombi, etc. |
| Trucks | lkw_blau, lkw_gelb, lkw_gruen, lkw_rot, lkw_m, lkw_m1, lkw_rot |
| Special | AlligatorLow, Bagger, Dumper, KombiLow, PrioLow, SemirLow, TransporterLow 1-3, Trolley1, Minilader, Stapler, rtw, stadtbus, etc. |
| Trains | Express_LOK, Express_LOKende, Express_Persw, Gueterwagon, Lok, MD500, Niederbwagen, poliz_hub, Wagon, zivil_hub |

---

## 4. Engine Analysis

**Engine:** Synetic 3D Landscape Engine (evolved)
- **Graphics:** DirectX 9 (D3DX9 Shader Compiler 9.12.589)
- **Physics:** Custom damage system (DAM_CRASH_* family trait; physics middleware unconfirmed — no exe in dump)
- **Audio:** DirectSound/DirectMusic (WAV, OGG?)
- **Video:** Bink Video (`.bik`) — **NEW in CT4**
- **Scripting:** None (C++ only)

**New in Crash Time 4:**
- Bink Video support (`.bik` files)
- Expanded vehicle roster (50+ traffic types)
- Enhanced vehicle LOD system (LOD0-LOD3 + r_h/r_v variants)
- New vehicle types: AlligatorLow, Dumper, Bagger, PrioLow, SemirLow, TransporterLow 1-3, Trolley1, Minilader, Stapler

---

## 5. Documentation Files Created

| File | Description |
|---|---|
| `CRASH_TIME_4_TEARDOWN.md` | This document |
| `GAMES_KNOWLEDGE_BASE.md` | Updated with Crash Time 4 entry |

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Crash Time 4\`*  
*Engine: Synetic 3D Landscape Engine (evolved), Synetic GmbH 2010*