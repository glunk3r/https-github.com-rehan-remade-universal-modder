# Just Cause 2 modding plan

- Install: C:\Program Files (x86)\Steam\steamapps\common\Just Cause 2 (steam 8190), version 1.0.0.0 (Steam)
- Engine: Avalanche Engine (proprietary, Avalanche Studios), code: native x86 C++, 32-bit
- Anti-cheat / online: none found — single-player only, no anti-cheat
- Saves: C:\Users\gmbad\Documents\Square Enix\Just Cause 2\Saves   Config: (in-game, likely registry)   Logs: (check My Documents or install folder)
- Community route: dropzone folder for loose-file overrides (native), Gibbed's tools for .arc/.tab extraction, Just Cause 2 Multiplayer (separate Steam app 259080)
- Chosen route for "<idea>": **data/asset mod via dropzone + archive extraction** because the game natively loads loose files from `dropzone/` overriding .arc archives, and community tools exist for .arc/.tab
- Lab plan: backup Saves folder (`um backup`), launch windowed (check launch options or config), use dropzone for testing
- Unknowns to resolve first:
  - Exact .arc/.tab format specification (offset/size/table structure)
  - Whether dropzone works for all asset types or only specific ones
  - Config file location for windowed mode / graphics settings
  - Save file format for backup verification
  - Community tooling status (Gibbed.Avalanche, JC2ModManager, etc.)

---

## Engine & File Format Details

### Archive Format (.arc/.tab pairs)
- `archives_win32/pc0.arc` (1.0 GB) + `pc0.tab` (225 KB) — main game data
- `pc1.arc` (1.0 GB) + `pc1.tab` (17 KB)
- `pc2.arc` (1.0 GB) + `pc2.tab` (56 KB)
- `pc3.arc` (510 MB) + `pc3.tab` (38 KB)
- `pc4.arc` (12 MB) + `pc4.tab` (160 bytes)

**Structure hypothesis**: .tab = index table (hash, offset, size, flags), .arc = concatenated file data. Strings like "LTRIGGER", "GUI_ICONLEGEND" visible in .arc header.

### Dropzone Modding
- Folder: `dropzone/` (already exists, contains `lave.v900_super_sportcar.eez`)
- Game loads loose files from `dropzone/` **instead of** packed .arc files when names match
- This is the primary modding route — no code injection needed

### Middleware Detected
| DLL | Purpose |
|-----|---------|
| `binkw32.dll` | Bink Video (cutscenes) |
| `fmodex.dll`, `fmod_event.dll` | FMOD Ex audio |
| `cudart.dll`, `cufft.dll` | NVIDIA CUDA (physics/particles) |
| `PathEngine.dll` | Pathfinding middleware |
| `steam_api.dll`, `Steamclient.dll` | Steamworks |
| `GDF.dll` | Games for Windows Live (legacy) |

### Executable
- `JustCause2.exe` — x86 PE32, native C++, ~14.5 MB, not managed
- Launcher: `Launcher.DLL` (loaded by Steam)

---

## Next Steps (per mod-any-game loop)

1. **Lab setup**: `um backup create "C:\Users\gmbad\Documents\Square Enix\Just Cause 2\Saves" --name jc2-saves`
2. **Source of truth**: Extract `pc0.arc`/`pc0.tab` using Gibbed.Avalanche tools or custom parser; inspect file types
3. **Vertical slice**: Replace a simple texture or model via dropzone, launch, verify in-game
4. **Assets**: Use `um fal` + `um sprite`/`um render3d` for new content matching game's format
5. **Verify**: Screenshot + in-game check; script a repeatable test (e.g., spawn vehicle)
6. **Showcase**: Record with `um win record`, compile with `um video compile`

---

## References
- Playbook: `skills/mod-any-game/references/engines/native.md` (for native hooking fallback)
- Knowledge base: `knowledge/INDEX.md` (search for "avalanche" or "just cause")
- Community: Nexus Mods "Just Cause 2", JC2-MP (Steam app 259080), Gibbed.Avalanche (GitHub)