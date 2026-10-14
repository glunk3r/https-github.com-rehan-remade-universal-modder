# Game Engine Reverse Engineering Research

This repository contains reverse engineering research and documentation for various game engines and titles, focusing on proprietary engines with zero or minimal licensed middleware.

## 📚 Documentation Index

| Game | Platform | Engine | Year | Middleware | Status |
|---|---|---|---|---|---|
| [Pursuit Force](TRACKMANIA_DS_TEARDOWN.md) | PSP | Bigbig `Game03` | 2005 | None | ✅ Complete |
| [Pursuit Force: Extreme Justice](PURSUIT_FORCE_EJ_TEARDOWN.md) | PSP | Bigbig `Game03` | 2007 | None | ✅ Complete |
| [MotorStorm: Arctic Edge (PSP)](MOTORSTORM_ARCTIC_EDGE_PSP_TEARDOWN.md) | PSP | Bigbig `Game03` | 2009 | None | ✅ Complete |
| [MotorStorm: Arctic Edge (PS2)](MOTORSTORM_ARCTIC_EDGE_PSP_TEARDOWN.md#motorstorm-arctic-edge-ps2---ps2-2009) | PS2 | Bigbig `Game03` (Virtuos port) | 2009 | CRI, ODE (names only) | ✅ Complete |
| [TrackMania DS](TRACKMANIA_DS_TEARDOWN.md) | NDS | Firebrand Games (Octane) | 2009 | None | ✅ Complete |
| [TrackMania Turbo DS](TRACKMANIA_TURBO_DS_TEARDOWN.md) | NDS | Firebrand Games (Octane) | 2010 | None | ✅ Complete |
| [Metal Gear Rising Revengeance](MGRR_TEARDOWN.md) | PC/PS3/X360 | PlatinumGames | 2013 | Havok + Wwise | ✅ Complete |

## 🏗️ Engine Lineages

### Bigbig Studios `Game03` Engine (2005–2009)
```
Pursuit Force 1 (PSP, 2005)          → PAK v2 (`02 PAK`)
Pursuit Force: Extreme Justice (2007) → PAK v2, AdHoc multiplayer
MotorStorm: Arctic Edge PSP (2009)    → PAK (`PAK `), same engine
MotorStorm: Arctic Edge PS2 (2009)    → Virtuos port, same PAK format
```
**Key finding:** 100% proprietary, zero licensed middleware across all 4 titles.

### Firebrand Games NDS Engine (Octane Lineage, 2009–2010)
```
TrackMania DS (2009)         → 32 MB ROM, ZIP (26 MB, 3457 files)
TrackMania Turbo DS (2010)   → 64 MB ROM, ZIP (27 MB, 4258 files)
```
**Key finding:** Firebrand Games proprietary NDS engine with Octane engine lineage. Zero licensed middleware across both titles.

### PlatinumGames Engine (Separate Lineage)
```
Metal Gear Rising Revengeance (2013) → Havok + Wwise, FBX/HKX/DDS/BNK
```
**Key finding:** Only title in this set using licensed middleware (Havok physics, Wwise audio).

## 📁 Documentation Files

| File | Description |
|------|-------------|
| `GAMES_KNOWLEDGE_BASE.md` | Consolidated knowledge base for all 7+ games |
| `PURSUIT_FORCE_TEARDOWN.md` | Pursuit Force 1 teardown |
| `PURSUIT_FORCE_EJ_TEARDOWN.md` | Extreme Justice teardown |
| `MOTORSTORM_ARCTIC_EDGE_PSP_TEARDOWN.md` | MotorStorm Arctic Edge (PSP) teardown |
| `TRACKMANIA_DS_TEARDOWN.md` | TrackMania DS teardown |
| `TRACKMANIA_TURBO_DS_TEARDOWN.md` | TrackMania Turbo DS teardown |
| `MGRR_TEARDOWN.md` | Metal Gear Rising Revengeance teardown |

## 🔍 Key Findings Summary

| Engine Family | Games | Middleware | Key Insight |
|---|---|---|---|
| Bigbig `Game03` | 4 games | **None** | Pure Sony PSP/PS2 SDK + custom formats |
| Firebrand NDS | 2 games | **None** | Pure Nintendo NitroSDK + Lua scripting |
| PlatinumGames | 1 game | Havok + Wwise | Only title with licensed middleware |

## 🛠️ Common Tools Used

| Tool | Purpose |
|------|---------|
| `psmfdump.exe` | PMF video demux (PSP) |
| `dattool.exe` | `.dat` archive extraction (NDS) |
| `unluac` / `luadec` | Lua bytecode decompilation |
| `ffmpeg` | Video/audio conversion |
| `py7zr` / `7z` | 7z archive extraction |
| Custom Python scripts | ROM parsing, PAK/ZIP extraction, format analysis |

## 📦 Archive Formats Discovered

| Game | Container | Format |
|------|-----------|--------|
| Pursuit Force 1/Extreme Justice | PAK v2 | `02 PAK` magic, 16-byte index entries |
| MotorStorm Arctic Edge (PSP) | PAK | `PAK ` magic, 24-byte linked-list entries |
| MotorStorm Arctic Edge (PS2) | PAK | Same as PSP version |
| TrackMania DS | ZIP | Standard ZIP at 0x645C00 (26 MB) |
| TrackMania Turbo DS | ZIP | Standard ZIP at 0x873200 (27 MB) |

## 🎮 File Formats Catalog

| Extension | Game(s) | Description |
|---|---|---|
| `.pspptx` / `.PSP_PTX_MAIN` | Pursuit Force, MotorStorm PSP | PSP texture (swizzled, paletted) |
| `.pspp3d` / `.pspl3d` | Pursuit Force | 3D models |
| `.psppve` | Pursuit Force | Vehicle models |
| `.pspppprt` | Pursuit Force | Particle systems |
| `.chpsp` / `.anp` | Pursuit Force | Characters / animations |
| `.nsbmd` / `.n` | TrackMania DS / Turbo DS | NSBMD 3D models (BMD0 magic) |
| `.hzc` / `.h` | TrackMania DS / Turbo DS | Hit zone collision |
| `.dcsc` | TrackMania DS / Turbo DS | Scene collision |
| `.luac` | TrackMania DS / Turbo DS | Lua 5.1 bytecode |
| `.hzc` / `.h` | TrackMania | Hit zone collision |
| `.sdat` | All NDS games | Nintendo DS audio (SDAT) |
| `.at3` / `.vib/.vdb` | PSP games | ATRAC3 audio / VIB+VDB audio |

## 🔧 Tools Developed

Custom Python scripts for:
- NDS ROM parsing (FAT/FNT extraction)
- PAK container parsing (PSP/PS2)
- ZIP archive extraction from ROM offsets
- File format identification (magic bytes, structure analysis)
- ARM9/ARM7 binary analysis (string extraction, engine detection)

---

## 📝 License & Usage

This research is for educational and preservation purposes only. All game assets, binaries, and code remain the property of their respective owners (Sony, Atari, Nintendo, Konami, PlatinumGames, Firebrand Games, Bigbig Studios).

**Do not** use this research to:
- Bypass DRM or anti-cheat systems
- Create cheats for online multiplayer
- Redistribute game assets or binaries
- Violate EULA terms

This research is intended for:
- Game preservation and documentation
- Engine architecture education
- Modding framework development (offline/single-player only)
- Historical documentation of game engine evolution

---

*Research conducted 2026. All analysis performed on legally obtained game dumps owned by the researcher.*