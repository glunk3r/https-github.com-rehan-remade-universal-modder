# TrackMania DS (USA) — Teardown Documentation

**Game:** TrackMania DS (USA) (En,Fr,Es)  
**Platform:** Nintendo DS  
**Developer:** Firebrand Games (formerly Atod AB)  
**Publisher:** Atari / Nintendo  
**Year:** 2009 (US release)  
**Game Code:** CTRE  
**Maker Code:** EB (Atari)  
**ROM Size:** 32 MB (33,554,432 bytes)  

---

## 1. Game Engine

**Custom Firebrand Games Engine** (proprietary NDS engine)
- **Developer:** Firebrand Games (formerly Atod AB, Sweden)
- **Publisher:** Atari (Atari Europe / Atari Inc.)
- **Platform:** Nintendo DS
- **SDK:** Nintendo NitroSDK (official NDS SDK)
- **Languages:** C++ (ARM9), ARM assembly (ARM7), Lua (scripting)
- **Middleware:** **None detected** — pure Nintendo NitroSDK + in-house engine

**Evidence:**
- ARM9 binary contains C++ STL strings (`std::detail::shared_ptr_deleter`, etc.)
- References to `config/tracks`, `config/vehicles`, `carParams`
- `SEQARC_CAR_STADIUM`, `SEQARC_CAR_RALLY`, `SEQARC_CAR_DESERT` car categories
- `COLLISION_METAL_1`, `COLLISION_METAL_2`, `COLLISION_METAL_3`, `COLLISION_WOOD_1`
- `CAR_IDLE`, `CAR_LOW`, `CAR_MED` vehicle states
- No Unreal/Unity/RenderWare/PhysX/Havok strings found

---

## 2. ROM Structure

### NDS Header (0x160 bytes)
```
Game Title:    TRACKMANIA
Game Code:     CTRE (TrackMania E?)
Maker Code:    EB (Atari)
Unit Code:     0x00
ARM9 ROM Off:  0x4000
ARM9 Entry:    0x02000800
ARM9 RAM:      0x02000000
ARM9 Size:     972,760 bytes (0xED7D8)
ARM7 ROM Off:  0x147400
ARM7 Entry:    0x02380000
ARM7 RAM:      0x02380000
ARM7 Size:     159,192 bytes (0x26DD8)
FNT Offset:    0x16E200, Size: 144 bytes
FAT Offset:    0x16E400, Size: 104 bytes (13 entries)
ARM9 Overlay:  0xF1800, 128 bytes
ARM7 Overlay:  None
ROM Size:      33,554,432 bytes (32 MB)
```

---

## 3. Filesystem (FAT/FNT)

**FAT (File Allocation Table):** 13 entries at 0x16E400
**FNT (File Name Table):** 144 bytes at 0x16E200

| Entry | Offset | End | Size | Filename (from FNT) | Notes |
|---|---|---|---|---|---|
| 0 | 0xF1A00 | 0xF1A20 | 32 B | `download.char` | Small header |
| 1 | 0xF1C00 | 0xF1C20 | 32 B | `download.plt` | Small header |
| 2 | 0xF1E00 | 0x120240 | 1,185 KB | `download.srl` | ARM9 overlay? |
| 3 | 0x120400 | 0x1473E0 | 156 KB | `download.plr` | ARM7 binary (159,712 B) |
| 4 | 0x34AE00 | 0x34B000 | 512 B | `download.srl` | Small file |
| 5 | 0x34B000 | 0x34B020 | 32 B | `downloadus.srl` | Region variant |
| 6 | 0x34B200 | 0x4BA6C8 | 1,469 KB | `vfs.bin` | Main virtual FS? |
| 7 | 0x4BA800 | 0x62B0C8 | 1,474 KB | `vfs.dat` | Virtual FS data |
| 8 | 0x62B200 | 0x64590A | 106 KB | `vfs.zip` | Compressed data |
| 9 | 0x645A00 | 0x645A13 | 19 B | `audio` | Text file: "3716, 3457, 6473" |
| 10 | 0x645C00 | 0x1FDF60C | **25.6 MB** | `sound_data.sdat` | **Main game ZIP archive** |
| 11 | 0x16F000 | 0x2F49E0 | 1.5 MB | `sound_dataNetwork.sdat` | Network audio SDAT |
| 12 | 0x2F4A00 | 0x34AC40 | 345 KB | (no name) | Network audio SDAT |

**Note:** The main game archive at 0x645C00 (26 MB) is a **ZIP file** containing 3,457 files (47.4 MB uncompressed).

---

## 4. Main Game Archive (ZIP at 0x645C00)

**ZIP Archive:** 3,457 files, 47.4 MB uncompressed

### Directory Structure
```
Graphics/
  2dMaps/        # 2D map textures
  2dSprites/     # 2D sprites (HUD, fonts, UI)
  Cars/          # 265 NSBMD car models (LODs, shop views)
  EnvMaps/       # Environment maps
  Misc/          # Miscellaneous graphics
  Network/       # Network-related graphics
  Particles/     # Particle effects
  Sky/           # Skyboxes
  Tracks/        # Track pieces (NSBMD + HZC collision)
  hud/           # HUD graphics
  2dMaps/        # 2D map textures
  2dSprites/     # 2D sprites
Scripts/
  tracks/        # Track prebuild scripts (LUAC)
  screens/       # UI screen logic (LUAC)
  config/        # Game config (LUAC)
Scenes/
  sta/           # Stadium tracks (practice/medium/hard/extreme)
  ral/           # Rally tracks
  des/           # Desert tracks
strings/
  main/          # Main game strings (6 languages)
  download/      # Download/online strings (6 languages)
Ghosts/
  Sta/           # Stadium ghosts (practice/medium/hard/extreme)
Scripts/
  tracks/prebuild*.luac
  screens/*/PieceData.luac, TrackPieceLayout.luac
  config/*.luac (BlockShop, cameras, caraudio, challenges, etc.)
```

### File Formats (3,457 files)
| Extension | Count | Description |
|---|---|---|
| `.nsbmd` | 1,747 | **Nintendo DS 3D Model** (track pieces, cars, objects) |
| `.hzc` | 771 | **Hit Zone Collision** (track piece collision) |
| `.bin` | 270 | Binary data (ghosts, config) |
| `.nsbca` | 115 | Animation? |
| `.ncgr` | 158 | Nintendo Character Graphics (2D tiles) |
| `.nclr` | 105 | Nintendo Color Palette |
| `.nsc` | 115 | Screen layout / cell map |
| `.ncer` | 45 | Cell definition |
| `.nanr` | 45 | Animation |
| `.luac` | 28 | **Lua bytecode** (game logic, UI, config) |
| `.dcsc` | 135 | Scene definition (DCSC = DS Collision Scene?) |
| `.hzc` | 771 | **Hit Zone Collision** (track physics) |
| `.ncgr` | 158 | 2D character graphics |
| `.nclr` | 105 | Color palette |
| `.nsc` | 115 | Screen/cell map |
| `.ncer` | 45 | Cell definition |
| `.nanr` | 45 | Animation |
| `.luac` | 28 | Lua bytecode |
| `.dcsc` | 135 | Scene collision |
| `.hzc` | 771 | Hit zone collision |
| `.bin` | 270 | Binary (ghosts, etc.) |
| `.nsc` | 115 | Screen config |
| `.luac` | 28 | Lua bytecode |
| `.str` | 36 | String tables (6 languages × 6 categories) |
| `.dat` | 2 | Token data |

---

## 4. Audio

### SDAT Files (Nintendo DS Audio Format)
| File | Offset | Size | Description |
|---|---|---|---|
| `sound_data.sdat` | 0x16F000 | 1.5 MB | Main game audio |
| `sound_dataNetwork.sdat` | 0x2F4A00 | 345 KB | Network/online audio |
| Main archive `audio/` | In ZIP | — | Additional audio in main ZIP? |

**SDAT Format:** Standard Nintendo DS SDAT (Sound Data) — contains sequences (SSEQ), banks (SBNK), waves (SWAR), player (SPLR).

---

## 5. Binary Executables

### ARM9 (Main CPU) — 972,760 bytes
- **Language:** C++ (STL strings visible: `std::detail::shared_ptr_deleter`, etc.)
- **Engine Logic:** Track/vehicle config, collision, physics, AI
- **Key Strings:** `config/tracks`, `config/vehicles`, `carParams`, `SEQARC_CAR_STADIUM`, `COLLISION_METAL_1`, `CAR_IDLE`, `CAR_LOW`, `CAR_MED`

### ARM7 (Sub CPU) — 159,192 bytes
- **Role:** WiFi, audio, touchscreen, power management
- **Standard NitroSDK ARM7**

---

## 6. Key File Formats

### NSBMD — Nintendo DS 3D Model
- **Count:** 1,747 files
- **Usage:** Track pieces, cars, environment objects
- **Structure:** Standard NitroSDK NSBMD (polygon + material + texture references)

### HZC — Hit Zone Collision
- **Count:** 771 files
- **Usage:** Track piece collision geometry
- **Paired with:** NSBMD track pieces (same name, .hzc extension)

### DCSC — Scene Collision
- **Count:** 135 files
- **Location:** `Scenes/sta/`, `Scenes/ral/`, `Scenes/des/`
- **Levels:** practice/medium/hard/extreme (0-4)

### LUAC — Lua Bytecode
- **Count:** 28 files
- **Usage:** Track prebuilds, UI screens, game config
- **Decompilable:** Yes (unluac, luadec)

### NSBMD/NCGR/NCLR/NCER/NANR/NSC — NitroSDK 2D Formats
- Standard Nintendo DS 2D graphics formats

---

## 6. Tools & Reverse Engineering

### Extraction
```bash
# Extract NDS ROM
python tmnds_extract.py  # Custom extractor (included in analysis)

# Extract main ZIP
unzip tmnds_main.zip -d extracted/

# Decompile LUAC
unluac Scripts/config/tracks.luac > tracks.lua

# View NSBMD
# Use tools: NSBMD Viewer, MKDS Course Editor, or custom parser

# SDAT audio
# Use: NDS SDAT tools, VGMToolbox, or kiwi.ds
```

### File Format References
- **NSBMD:** GBATEK "NSBMD Format", MKDS Course Editor source
- **HZC:** Custom collision format (paired with NSBMD)
- **DCSC:** Scene collision format
- **SDAT:** NitroSDK Sound Format (Nintendo docs)
- **LUAC:** Standard Lua 5.1 bytecode (unluac works)

---

## 7. Engine Summary

| Aspect | Detail |
|---|---|
| **Engine** | Firebrand Octane Engine |
| **Language** | C++ (ARM9), ARM ASM (ARM7), Lua (scripting) |
| **SDK** | Nintendo NitroSDK |
| **Middleware** | **None** |
| **Physics** | Custom (HZC collision, custom vehicle physics) |
| **Audio** | NitroSDK SDAT (WAV/ADPCM sequences) |
| **Scripting** | Lua 5.1 (bytecode .luac) |
| **Build Path** | Not found in ROM (stripped) |
| **Dev Studio** | Firebrand Games (Atod AB) |

---

## 8. Documentation Files Created

| File | Description |
|---|---|
| `TRACKMANIA_DS_TEARDOWN.md` | This document |
| `tmnds_extract/` | Extracted files (ARM9, ARM7, filesystem, main ZIP) |
| `tmnds_main.zip` | Main game archive (3,457 files) |

---

## 9. Knowledge Base Entry

```markdown
TrackMania DS (USA)
├── Engine: Firebrand Octane Engine
├── Middleware: NONE (Nintendo NitroSDK only)
├── Platform: Nintendo DS (32 MB ROM)
├── Executable: ARM9 (C++), ARM7 (NitroSDK)
├── Scripting: Lua 5.1 (.luac bytecode)
├── Archive: ZIP (26 MB, 3457 files) at 0x645C00
├── Formats: NSBMD (3D), HZC (collision), DCSC (scenes), LUAC (scripts)
├── Audio: SDAT (sequences + samples)
├── Languages: EN/FR/ES/DE/IT/NL (6 languages)
├── Dev: Firebrand Games (Atod AB)
├── Publisher: Atari
└── Year: 2009
```

---

*Generated from `C:\Users\gmbad\Downloads\teardown\TrackMania DS (USA) (En,Fr,Es)\`*  
*ROM: 32 MB, CTRE, Firebrand Games 2009*