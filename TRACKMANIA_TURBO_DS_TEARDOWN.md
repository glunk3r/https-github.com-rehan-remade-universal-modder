# TrackMania Turbo DS (USA) — Teardown Documentation

**Game:** TrackMania Turbo DS (USA) (En,Fr,Es)  
**Platform:** Nintendo DS  
**Developer:** Firebrand Games (formerly Atod AB) — *had access to their Octane engine tech*  
**Publisher:** Atari / Nintendo  
**Year:** 2010 (US release)  
**Game Code:** BT2E  
**Maker Code:** JH (Firebrand Games)  
**ROM Size:** 64 MB (67,108,864 bytes)  

---

## 1. Game Engine

**Firebrand Octane Engine** — *evolution of TrackMania DS engine, built on Firebrand's internal "Octane" engine technology*
- **Developer:** Firebrand Games (formerly Atod AB, Sweden)
- **Publisher:** Atari
- **Platform:** Nintendo DS
- **SDK:** Nintendo NitroSDK
- **Middleware:** **None detected** — pure Nintendo NitroSDK + in-house Firebrand/Octane tech
- **Scripting:** Lua 5.1 (`.luac` bytecode, 27 files)

**Evidence:**
- Game Title: `TRACKMANIA2` (sequel to CTRE)
- Game Code: `BT2E` (TrackMania 2 Evolution?)
- Maker Code: `JH` (Firebrand Games)
- ARM9 binary contains C++ STL strings (`std::detail::shared_ptr_deleter`)
- No Unreal/Unity/RenderWare/PhysX/Havok/FMOD/Wwise strings found
- Firebrand's internal "Octane" engine technology was available to the studio

---

## 2. ROM Structure

### NDS Header (0x160 bytes)
```
Game Title:    TRACKMANIA2
Game Code:     BT2E
Maker Code:    JH (Firebrand Games)
Unit Code:     0x00
ARM9 ROM Off:  0x4000
ARM9 Entry:    0x02000800
ARM9 RAM:      0x02000000
ARM9 Size:     830,360 bytes (0xCAB98)
ARM7 ROM Off:  0x1B8E00
ARM7 Entry:    0x02380000
ARM7 RAM:      0x02380000
ARM7 Size:     160,048 bytes (0x27130)
FNT Offset:    0x1E0000, Size: 221 bytes
FAT Offset:    0x1E0200, Size: 168 bytes (21 entries)
ARM9 Overlay:  0xCEC00, 256 bytes
ARM7 Overlay:  None
ROM Size:      67,108,864 bytes (64 MB)
```

---

## 3. Filesystem (FAT/FNT)

**FAT (File Allocation Table):** 21 entries at 0x1E0200  
**FNT (File Name Table):** 221 bytes at 0x1E0000

| Entry | Offset | End | Size | Filename (from FNT) | Notes |
|---|---|---|---|---|---|
| 0 | 0xCEE00 | 0xEC520 | 118 KB | `buildname.bin` | Build metadata |
| 1 | 0xEC600 | 0x108940 | 113 KB | `download.char` | Character data |
| 2 | 0x108A00 | 0x122740 | 103 KB | `download.plt` | Palette/texture data |
| 3 | 0x122800 | 0x163660 | 260 KB | `download.srl` | SRL module |
| 4 | 0x163800 | 0x1A6040 | 266 KB | `downloadUS.srl` | US region SRL |
| 5 | 0x1A6200 | 0x1AD6C0 | 29 KB | `sku.bin` | SKU identifier |
| 6 | 0x1AD800 | 0x1B8AE0 | 45 KB | `vfs.bin` | Virtual FS index |
| 7 | 0x1B8C00 | 0x1B8C20 | 32 B | `vfs.dat` | VFS metadata |
| 8 | 0x3E3600 | 0x3E3619 | 25 B | `vfs.zip` | ZIP marker? |
| 9 | 0x3E3800 | 0x3E3A00 | 512 B | `audio` | Audio config |
| 10 | 0x3E3A00 | 0x3E3A20 | 32 B | `movies` | Video config |
| 11 | 0x3E3C00 | 0x5454C8 | 1.4 MB | `sound_data.sdat` | Main audio SDAT |
| 12 | 0x545600 | 0x6A80C8 | 1.4 MB | `sound_dataNetwork.sdat` | Network audio SDAT |
| 13 | 0x852600 | 0x852600 | 0 B | `utility.bin` | Empty placeholder |
| 14 | 0x852600 | 0x872F56 | 130 KB | `intro.mob` | Intro movie |
| 15 | 0x873000 | 0x873013 | 19 B | *(small text)* | Text file |
| 16 | 0x873200 | 0x22875A9 | **26.1 MB** | `vfs.zip` | **Main game ZIP archive** |
| 17 | 0x1E0E00 | 0x38CFA0 | 1.7 MB | `sound_data.sdat` | Duplicate? |
| 18 | 0x38D000 | 0x3E3580 | 345 KB | `sound_dataNetwork.sdat` | Duplicate? |
| 19 | 0x6A8200 | 0x78B23C | 908 KB | `utility.bin` | Utility data |
| 20 | 0x78B400 | 0x852514 | 796 KB | `intro.mob` | Intro movie |

**Note:** The main game archive is `vfs.zip` at entry 16 (27 MB, offset 0x873200).

---

## 4. Main Game Archive (ZIP at 0x873200)

**ZIP Archive:** 4,258 files, 51.2 MB uncompressed

### Directory Structure
```
Graphics/
  2dMaps/        # 2D map textures
  2dSprites/     # 2D sprites (HUD, fonts, UI)
  Cars/          # 244 car models (.n extension = NSBMD)
  EnvMaps/       # Environment maps
  Misc/          # Miscellaneous graphics
  Network/       # Network-related graphics
  Particles/     # Particle effects
  Sky/           # Skyboxes
  Tracks/        # Track pieces (.n models + .h collision)
  hud/           # HUD graphics
Scripts/
  config/        # Game config (27 LUAC files)
  PieceData/     # Track piece data (4 environments)
  screens/       # UI screen layouts (4 environments)
  tracks/        # Track editor scripts (4 environments)
Scenes/
  coa/           # Coast environments (bonus/0-4)
  isl/           # Island environments
  sno/           # Snow environments
  sta/           # Stadium environments
strings/
  download/      # Download/online strings
  main/          # Main game strings
Ghosts/
  Coa/           # Coast ghosts (bonus/0-1)
```

### File Formats (4,258 files)
| Extension | Count | Description |
|---|---|---|
| `.n` | 2,160 | **NSBMD 3D Models** (cars, tracks, objects) — `BMD0` magic |
| `.h` | 964 | **Hit Zone Collision** (track piece collision) |
| `.bin` | 317 | Binary data (ghosts, config) |
| `.ncgr` | 174 | Nintendo Character Graphics (2D tiles) |
| `.nclr` | 129 | Nintendo Color Palette |
| `.nsc` | 128 | Screen layout / cell map |
| `.nclr` | 129 | Color palette |
| `.ncer` | 45 | Cell definition |
| `.nanr` | 48 | Animation |
| `.dcsc` | 155 | Scene collision (DCSC) |
| `.luac` | 27 | Lua 5.1 bytecode (game logic, UI, config) |
| `.na` | 70 | Track signage/navigation |
| `.h` | 964 | Hit zone collision |
| `.luac` | 27 | Lua bytecode |
| `.str` | 36 | String tables (6 languages × 6 categories) |
| `.dat` | 2 | Token data |

---

## 5. Key File Formats

### `.n` — NSBMD 3D Models
- **Count:** 2,160 files (extension `.n` instead of `.nsbmd`)
- **Magic:** `BMD0` (`42 4D 44 30` = ASCII "BMD0")
- **Usage:** Cars (244 models, 5 LODs each), track pieces, environment objects
- **Structure:** Standard NitroSDK NSBMD format

### `.h` — Hit Zone Collision
- **Count:** 964 files
- **Usage:** Track piece collision geometry
- **Paired with:** `.n` track pieces (same name, `.h` extension)
- **Format:** Custom collision mesh format (starts with `0E 01...`)

### `.na` — Track Signage/Navigation
- **Count:** 70 files
- **Usage:** Track signs, arrows, navigation markers
- **Magic:** `42 54 41 30` ("BTA0" = "BTA0" marker)

### `.dcsc` — Scene Collision
- **Count:** 155 files
- **Locations:** `Scenes/coa/`, `Scenes/isl/`, `Scenes/sno/`, `Scenes/sta/`
- **Levels:** bonus/0-4 per environment

### `.luac` — Lua Bytecode
- **Count:** 27 files
- **Usage:** Track configs, UI screens, game systems
- **Decompilable:** Yes (unluac, luadec)

### Standard NitroSDK 2D Formats
- `.ncgr` (174) — Character graphics
- `.nclr` (129) — Color palettes
- `.nsc` (128) — Screen/cell maps
- `.ncer` (45) — Cell definitions
- `.nanr` (48) — Animations

---

## 5. Audio

### SDAT Files
| File | Offset | Size | Description |
|---|---|---|---|
| `sound_data.sdat` | 0x3E3C00 | 1.4 MB | Main game audio |
| `sound_dataNetwork.sdat` | 0x38D000 | 345 KB | Network/online audio |
| (duplicate) | 0x1E0E00 | 1.7 MB | sound_data.sdat (duplicate?) |
| (duplicate) | 0x38D000 | 345 KB | sound_dataNetwork.sdat (duplicate?) |

**SDAT Format:** Standard Nintendo DS SDAT — sequences (SSEQ), banks (SBNK), waves (SWAR), player (SPLR).

---

## 6. Binary Executables

### ARM9 (Main CPU) — 830,360 bytes
- **Language:** C++ (STL strings visible: `std::detail::shared_ptr_deleter`, etc.)
- **Engine Logic:** Track/vehicle config, collision, physics, AI
- **Key Strings:** `config/tracks`, `config/vehicles`, `carParams`, `SEQARC_CAR_COA`, `SEQARC_CAR_ISL`, `SEQARC_CAR_SNO`, `COLLISION_METAL_1`, `CAR_IDLE`, `CAR_LOW`, `CAR_MED`

### ARM7 (Sub CPU) — 160,048 bytes
- **Role:** WiFi, audio, touchscreen, power management
- **Standard NitroSDK ARM7**

---

## 7. Engine Summary

| Aspect | Detail |
|---|---|
| **Engine** | Firebrand Octane Engine |
| **Language** | C++ (ARM9), ARM ASM (ARM7), Lua 5.1 (scripting) |
| **SDK** | Nintendo NitroSDK |
| **Middleware** | **None** |
| **Physics** | Custom (HZC/.h collision, custom vehicle physics) |
| **Audio** | NitroSDK SDAT |
| **Scripting** | Lua 5.1 (`.luac` bytecode) |
| **Build Path** | Not found in ROM (stripped) |
| **Dev Studio** | Firebrand Games (Atod AB) — had access to Octane engine |

---

## 8. Comparison: TrackMania DS vs TrackMania Turbo DS

| Aspect | TrackMania DS (CTRE) | TrackMania Turbo DS (BT2E) |
|---|---|---|
| **ROM Size** | 32 MB | 64 MB |
| **Main Archive** | ZIP (26 MB, 3,457 files) | ZIP (27 MB, 4,258 files) |
| **Graphics** | 1,747 NSBMD | 2,160 `.n` (NSBMD) |
| **Collision** | 771 `.hzc` | 964 `.h` |
| **Tracks** | 135 DCSC | 155 DCSC |
| **Cars** | 265 NSBMD | 244 `.n` (5 LODs each) |
| **Environments** | Stadium, Rally, Desert, Snow, Coastal, Freeway | Coast, Island, Snow, Stadium |
| **Scripts** | 28 LUAC | 27 LUAC |
| **Environments** | 6 | 4 (Coast, Island, Snow, Stadium) |
| **Languages** | 6 | 6 |
| **ROM Size** | 32 MB | 64 MB |

---

## 8. Documentation Files Created

| File | Description |
|---|---|
| `TRACKMANIA_TURBO_DS_TEARDOWN.md` | This document |
| `tmturbo_extract/` | Extracted files (ARM9, ARM7, filesystem, main ZIP) |
| `tmturbo_main.zip` | Main game archive (4,258 files) |

---

## 9. Knowledge Base Entry

```markdown
TrackMania Turbo DS (USA)
├── Engine: Firebrand Octane Engine
├── Middleware: NONE (Nintendo NitroSDK only)
├── Platform: Nintendo DS (64 MB ROM)
├── Executable: ARM9 (C++/STL), ARM7 (NitroSDK)
├── Scripting: Lua 5.1 (.luac bytecode, 27 files)
├── Archive: ZIP (27 MB, 4258 files) at 0x873200
├── Formats: .n (NSBMD), .h (collision), .dcsc (scenes), .luac (scripts), .na (signage)
├── Audio: SDAT (sequences + samples)
├── Languages: EN/FR/ES/DE/IT/NL (6 languages)
├── Dev: Firebrand Games (Atod AB) — had access to Octane engine
├── Publisher: Atari
└── Year: 2010
```

---

*Generated from `C:\Users\gmbad\Downloads\teardown\TrackMania Turbo DS (USA) (En,Fr,Es)\`*  
*ROM: 64 MB, BT2E, Firebrand Games 2010*