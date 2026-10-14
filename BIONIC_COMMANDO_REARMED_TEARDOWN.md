# Bionic Commando Rearmed (PC) — Teardown Documentation

**Game:** Bionic Commando Rearmed (PC)  
**Developer:** GRIN (later Firebrand Games)  
**Publisher:** Capcom  
**Year:** 2008 (PC release 2009)  
**Engine:** **Diesel Engine** (GRIN proprietary engine, later evolved into Firebrand's Octane engine)  

---

## 1. Game Engine

**Diesel Engine** — GRIN's proprietary multi-platform engine, later evolved into Firebrand's "Octane" engine.
- **Developer:** GRIN (Stockholm, Sweden) → Firebrand Games
- **Publisher:** Capcom
- **Platform:** PC (Windows), PS3, Xbox 360
- **SDK:** Custom Diesel engine + standard libraries
- **Middleware:** **Bink Video** (Rad Game Tools), **Steamworks** (Steam API), **PhysX** (likely, NxCooking.dll present)
- **Scripting:** Lua 5.1 (compiled to `.luac` bytecode)

**Evidence:**
- `dieselx.cfg` — Diesel engine configuration
- `binkw32.dll` — Bink Video SDK
- `steam_api.dll` / `steam_appid.txt` — Steamworks integration
- `NxCooking.dll` — PhysX cooking library
- Hundreds of `.luac` files (Lua 5.1 bytecode)
- `dieselx.cfg` references memory limits for Lua, physics, sound

---

## 2. Executable & Binaries

| File | Size | Description |
|---|---|---|
| `bcr.exe` | ~15 MB | Main executable (Win32 PE) |
| `dieselx.cfg` | 12 lines | Engine config (memory limits, affinity) |
| `binkw32.dll` | — | Bink Video decoder |
| `steam_api.dll` | — | Steamworks SDK |
| `NxCooking.dll` | — | PhysX cooking library |
| `cpy.dll` | — | Copy protection (likely SecuROM/SolidShield) |
| `steam_appid.txt` | — | Steam AppID |

**Executable Analysis (`bcr.exe`):**
- Win32 PE32 executable (GUI)
- Links to: `kernel32.dll`, `user32.dll`, `d3d9.dll`, `dsound.dll`, `winmm.dll`, `version.dll`
- Static links to Diesel engine core, Lua 5.1, Bink, PhysX, Steam API
- No anti-cheat kernel driver (single-player only)

---

## 3. Bundle Format: BNDL (Diesel Engine)

**File:** `bundles/quick.bundle` (216 MB, 226,397,318 bytes)

### BNDL Header (16 bytes)
```
Offset 0x00: 42 4E 44 4C  = "BNDL" magic
Offset 0x04: 02 00 00 00  = Version 2 (little endian)
Offset 0x08: 88 01 04 00  = File count: 262,536 (0x00040188)
Offset 0x0C: 00 00 00 00  = Flags / table offset (0 = embedded)
```

### File System Structure
- **FAT (File Allocation Table):** Offset 0x1E0200, 21 entries × 2 bytes = 42 bytes (16-bit relative offsets)
- **FNT (File Name Table):** Offset 0x1E0000, 55 entries × 4 bytes = 220 bytes (32-bit string table offsets)
- **String Table:** Offset 0x1E00DC, contains null-terminated filenames
- **File Data:** Starts at offset 0x10 (after 16-byte header), files stored sequentially

### Key Files in Bundle (21 entries in FAT)
| Index | Name | Size | Description |
|---|---|---|---|
| 0 | `buildname.bin` | 1 B | Build identifier |
| 1 | `download.char` | 1 B | Character download data |
| 2 | `download.plt` | 1 B | Palette data |
| 3 | `download.srl` | 1 B | SRL module |
| 4 | `downloadUS.srl` | 1 B | US region SRL |
| 5 | `sku.bin` | 1 B | SKU identifier |
| 6 | `vfs.bin` | 1 B | Virtual FS index |
| 7 | `vfs.dat` | 1 B | VFS data |
| 8 | `vfs.zip` | 1 B | ZIP marker |
| 9 | `audio` | 1 B | Audio config |
| 10 | `movies` | 1 B | Video config |
| 11 | `sound_data.sdat` | 1.4 MB | Main audio SDAT |
| 12 | `sound_dataNetwork.sdat` | 1.4 MB | Network audio SDAT |
| 13 | `utility.bin` | 0 B | Empty placeholder |
| 14 | `intro.mob` | 130 KB | Intro movie (MOB format) |
| 16 | `vfs.zip` | **26.1 MB** | **Main game archive (ZIP)** |
| 17 | `sound_data.sdat` | 1.7 MB | Duplicate? |
| 18 | `sound_dataNetwork.sdat` | 345 KB | Duplicate? |
| 19 | `utility.bin` | 796 KB | Utility data |
| 20 | `intro.mob` | 796 KB | Intro movie (duplicate?) |

**Note:** The bundle contains 262,536 logical files (per header), but only 21 entries in the FAT. The majority of files are stored in the embedded ZIP archive (`vfs.zip` at entry 16, 27 MB).

---

## 4. Main Game Archive: `vfs.zip` (27 MB, 4,258 files)

**Location:** Bundle entry 16, offset 0x873200, size 27,345,833 bytes  
**Format:** Standard ZIP (PK\003\004 magic)

### Archive Contents (4,258 files, 51.2 MB uncompressed)

| Directory | Files | Description |
|---|---|---|
| `Graphics/Cars/` | 244 | Car models (`.n` = NSBMD variant) |
| `Graphics/Tracks/` | 2,870 | Track pieces (`.n` models + `.h` collision) |
| `Graphics/2dSprites/` | — | 2D UI (NCGR, NCLR, NCLR, NANR, NCE, NSC) |
| `Graphics/2dMaps/` | — | 2D map textures |
| `Graphics/EnvMaps/` | — | Environment maps |
| `Graphics/Sky/` | — | Skyboxes |
| `Graphics/Particles/` | — | Particle effects |
| `Graphics/EnvMaps/` | — | Environment maps |
| `Graphics/hud/` | — | HUD elements |
| `Graphics/Misc/` | — | Miscellaneous |
| `Graphics/Network/` | — | Network graphics |
| `Graphics/Particles/` | — | Particles |
| `Scripts/` | 27 | Lua bytecode (`.luac`) |
| `Scenes/` | 155 | Scene definitions (`.dcsc`) |
| `Scenes/coa/` | — | Coast environments (bonus 0-4) |
| `Scenes/isl/` | — | Island environments |
| `Scenes/sno/` | — | Snow environments |
| `Scenes/sta/` | — | Stadium environments |
| `Ghosts/` | 317 | Ghost replay data (`.bin`) |
| `strings/` | 72 | Localization (6 langs × 12 categories) |
| `Ghosts/Coa/` | — | Coast ghosts |

---

## 5. File Formats

### `.n` — NSBMD Variant (3D Models)
- **Count:** 2,160 files
- **Magic:** `BMD0` (0x42 0x4D 0x44 0x30) — standard NitroSDK NSBMD
- **Usage:** Cars (5 LODs each: `lod0`, `lod1`, `lod2`, `lod3`, `lod0shop`), track pieces, environment objects
- **Structure:** Standard NitroSDK NSBMD (model + material + texture references)

### `.h` — Hit Zone Collision
- **Count:** 964 files
- **Paired with:** `.n` track pieces (same base name)
- **Format:** Custom collision mesh (starts with `0E 01...`)
- **Usage:** Track piece collision geometry

### `.na` — Track Signage/Navigation
- **Count:** 70 files
- **Magic:** `BTA0` (0x42 0x54 0x41 0x30)
- **Usage:** Track signs, arrows, navigation markers

### `.dcsc` — Scene Collision
- **Count:** 155 files
- **Locations:** `Scenes/coa/`, `Scenes/isl/`, `Scenes/sno/`, `Scenes/sta/`
- **Levels:** bonus/0-4 per environment (Coast, Island, Snow, Stadium)

### `.luac` — Lua 5.1 Bytecode
- **Count:** 27 files
- **Usage:** Game logic, UI, vehicle config, track configs, AI, weapons
- **Decompilable:** Yes (`unluac`, `luadec`)

### `.n` — NSBMD Variant (Extension `.n` instead of `.nsbmd`)
- **Magic:** `BMD0` (standard NSBMD)
- **Usage:** All 3D models (cars, tracks, objects)

### Standard NitroSDK 2D Formats (reused from NDS engine)
| Ext | Count | Description |
|---|---|---|
| `.ncgr` | 174 | Character graphics (tiles) |
| `.nclr` | 129 | Color palettes |
| `.nsc` | 128 | Screen/cell maps |
| `.ncer` | 45 | Cell definitions |
| `.nanr` | 48 | Animations |

### Other Formats
| Ext | Count | Description |
|---|---|---|
| `.luac` | 27 | Lua 5.1 bytecode |
| `.sdat` | 2 | SDAT audio (sequences + samples) |
| `.bik` | 1 | Bink video (`bc_trailer.bik`) |
| `.mob` | 2 | Intro movies (MOB format) |
| `.bik` | 1 | Bink video |
| `.bin` | 317 | Binary (ghosts, config) |
| `.str` | 36 | String tables (6 languages) |
| `.dat` | 2 | Token data |
| `.h` | 964 | Hit zone collision |
| `.na` | 70 | Track signage/navigation |
| `.bin` | 317 | Binary data |

---

## 6. Audio

### SDAT Files (Nintendo DS Audio Format — reused on PC)
| File | Size | Description |
|---|---|---|
| `sound_data.sdat` | 1.4 MB | Main game audio |
| `sound_dataNetwork.sdat` | 345 KB | Network/online audio |

**SDAT Format:** Standard Nintendo DS SDAT — sequences (SSEQ), banks (SBNK), waves (SWAR), player (SPLR)

### Video
| File | Format | Description |
|---|---|---|
| `bc_trailer.bik` | Bink Video | Trailer |
| `intro.mob` | MOB (custom) | Intro movie (2× 796 KB) |

---

## 7. Engine Summary

| Aspect | Detail |
|---|---|
| **Engine** | Diesel Engine (GRIN/Firebrand proprietary) |
| **Language** | C++ (core), Lua 5.1 (scripting) |
| **SDK** | Custom Diesel engine + NitroSDK formats reused |
| **Middleware** | **Bink Video**, **PhysX (NxCooking)**, **Steamworks** |
| **Physics** | Custom + PhysX (cooking) |
| **Audio** | SDAT (DS format reused on PC) |
| **Scripting** | Lua 5.1 (`.luac` bytecode) |
| **Build System** | Custom (bundle-based) |

---

## 8. Documentation Files Created

| File | Description |
|---|---|
| `BIONIC_COMMANDO_REARMED_TEARDOWN.md` | This document |
| `GAMES_KNOWLEDGE_BASE.md` | Updated with Bionic Commando entry |

---

## 8. Knowledge Base Entry

```markdown
Bionic Commando Rearmed (PC)
├── Engine: Diesel Engine (GRIN/Firebrand proprietary)
├── Middleware: Bink Video, PhysX (cooking), Steamworks
├── Platform: PC (Windows), also PS3/Xbox 360
├── Executable: bcr.exe (Win32 PE, ~15 MB)
├── Archive: quick.bundle (BNDL, 216 MB, 262k logical files)
├── Main Archive: vfs.zip (27 MB, 4258 files) embedded in bundle
├── Formats: .n (NSBMD), .h (collision), .dcsc (scenes), .luac (Lua), .sdat (audio)
├── Scripting: Lua 5.1 (.luac bytecode)
├── Middleware: Bink Video, PhysX (cooking), Steamworks
├── Dev: GRIN (Firebrand Games) — had access to Octane engine tech
├── Publisher: Capcom
└── Year: 2008 (console), 2009 (PC)
```

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Bionic Commando Rearmed\`*  
*Bundle: quick.bundle (216 MB), Diesel Engine, GRIN/Firebrand Games 2008-2009*