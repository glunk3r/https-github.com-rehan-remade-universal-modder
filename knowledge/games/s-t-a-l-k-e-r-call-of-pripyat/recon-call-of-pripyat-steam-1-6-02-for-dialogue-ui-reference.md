---
kind: game
title: 'Recon: Call of Pripyat Steam 1.6.02 for dialogue UI reference'
game: 'S.T.A.L.K.E.R.: Call of Pripyat'
games_also: []
game_version: 'Steam AppID 41700, build 11450453; Stalker-COP.exe and xrEngine.exe 1.6.02'
platform: windows
engine: native
route: other
tools: ["um scan", "PowerShell file/version inspection", "ModDB tutorials (read only)"]
anti_cheat: none found by um scan; reconnaissance only
status: in-progress
agents:
- Copilot SDK in VS Code
humans: []
date: '2026-10-15'
links:
- https://store.steampowered.com/app/41700/STALKER_Call_of_Pripyat/
- https://sdk.stalker-game.com/en/index.php?title=Main_Page
- https://www.moddb.com/games/stalker-call-of-pripyat/mods
- https://www.moddb.com/games/stalker-call-of-pripyat/tutorials/basic-stalker-modding-part-2
- https://github.com/ixray-team/ixray-1.6-stcop/blob/478899e687b1e5d7eab834120a252ca01b3dca36/gamedata_soc/configs/fonts.ltx
- https://github.com/google/fonts/tree/1d0e46c7933245c8180fe83e47917961c913bbdb/ofl/robotocondensed
tags: [recon, x-ray, call-of-pripyat, dialogue-ui]
---
# Recon: Call of Pripyat Steam 1.6.02 for dialogue UI reference

Read-only reconnaissance of the user's Steam copy of S.T.A.L.K.E.R.: Call of Pripyat (AppID 41700,
Steam build 11450453). Its native x86 executables and `xrEngine`/`xrGame` module names, matching 1.6.02
file versions, identify the installed build as X-Ray 1.6 far more specifically than the generic scanner's
"unknown native engine" result. No gameplay launch, mod install, archive extraction, or asset reuse was
performed. The game is being considered as a UI/dialogue-presentation reference for a separate Metro
dialogue project, not as a source of copied assets or dialogue.

## Setup

- Windows Steam install: `D:\Steam\steamapps\common\Stalker Call of Pripyat`.
- Steam AppID 41700, manifest build ID 11450453.
- `Stalker-COP.exe` and `bin\xrEngine.exe`: x86 PE, GSC Game World, file/product version 1.6.02.
- `bin\xrGame.dll` is present (7,258,816 bytes); supporting modules include `xrCore.dll`, `xrAPI.dll`,
  `xrRender_R1.dll` through `xrRender_R4.dll`, `xrSound.dll`, `xrPhysics.dll`, and LuaJIT 1.1.4.
- `fsgame.ltx` configures `user.ltx` and the game data root under the install. `$app_data_root$` maps to
  `_appdata_\`; `$logs$`, `$screenshots$`, and `$game_saves$` map under that root.
- Existing save files are present in `_appdata_\savedgames` (139 files observed); their individual names
  are intentionally not reproduced here. `_appdata_\user.ltx` exists. The configured logs folder was not
  present during this scan. A baseline snapshot of the entire `_appdata_` folder was created after the
  read-only scan: `%USERPROFILE%\.universal-modder\backups\stalker-call-of-pripyat-appdata\20261015-213405.zip`
  (146 files, 64.5 MB), outside the repository and install.
- No `gamedata` loose mod directory is present; `patches\xpatch_02.db` exists alongside the `resources`
  DB archive set.

## Route and why

The current task is reconnaissance for broad dialogue/UI reference. Use the game as a source of design
observations, then implement an original UI and text in the separate Metro dialogue lab. Do not copy
S.T.A.L.K.E.R. UI textures, fonts, dialogue, code, or extracted data into the prototype.

For the donor comparison, Call of Pripyat is the secondary visual/presentation reference; Fallout: New
Vegas is the stronger design reference for a feature-rich quest/branch graph. A community X-Ray 1.6 STCOP
implementation exposes a compact XML graph with numbered phrases, `next` links and preconditions, but
this does not prove the original Steam archive schema or any compatibility with Metro's 4A Engine:
https://github.com/ixray-team/ixray-1.6-stcop/blob/default/gamedata_soc/configs/gameplay/dialogs.xml
That same public implementation's `gamedata_soc/configs/fonts.ltx` names `RobotoCondensed` as the
OpenType family for `font_condensed`. This is evidence about that community reference tree, not proof that
the exact font file is bundled with the local Steam build. The Metro dialogue lab uses the separate
Google Fonts Roboto Condensed file under its included SIL Open Font License, not a CoP extraction.

For actual Call of Pripyat modding, the local `fsgame.ltx` exposes the conventional loose `gamedata\`
tree and the game ships archive files; community tutorials demonstrate config/data editing. A historical
X-Ray SDK 0.7 is mentioned in older community search results for X-Ray 1.6, but no SDK was installed or
verified, and its compatibility/availability for this exact Steam build remains unconfirmed. Do not
install it or overwrite game files without checking the precise version and making a backup.

## How the game works (what we had to learn)

- `um scan` reports `Unknown native engine` at 10% confidence because its signature matcher did not
  recognize the installation. Manual local evidence identifies the engine family: the main launcher
  and `xrEngine.exe` report version 1.6.02, and the install contains `xrCore.dll`, `xrGame.dll`,
  `xrRender_R1`–`R4`, `xrPhysics.dll`, and LuaJIT/luabind libraries. This is strong build-level
  identification, not a function-level analysis.
- The public X-Ray Mod Wiki's page titled "Dialog System" has no article text at the time of this research.
  An `ixray-1.6-stcop` community implementation has `dialog`/`phrase_list`/numbered `phrase` elements,
  `next` edges, and `precondition` expressions; treat this only as a public reference implementation,
  not verified extraction from this local game's packed archives.
- `fsgame.ltx` is the observed file-system path map. The shipped archive files are `resources\configs.db`,
  `resources\resources.db0`–`db4`, and `patches\xpatch_02.db`. Their first bytes are
  `9A 02 00 00 9E 00 00 00 [header]...`; this observation is only a fingerprint, not a decoded format
  specification. No archive was unpacked.
- The title is native x86 rather than managed .NET. The `xrGame.dll` and renderer module set provide
  likely future static-analysis targets if a concrete question requires code tracing. No Ghidra, IDA,
  x64dbg, dumpbin, or strings utility was found on PATH during this pass.
- The installed `user.ltx` and existing saves establish local configuration and user state, but no
  semantics were inferred from them.

## Build steps

No mod or binary was built. Reproduce the read-only fingerprint:

```powershell
& ".\bin\um.cmd" scan "D:\Steam\steamapps\common\Stalker Call of Pripyat"
Get-Item "D:\Steam\steamapps\common\Stalker Call of Pripyat\Stalker-COP.exe",
  "D:\Steam\steamapps\common\Stalker Call of Pripyat\bin\xrEngine.exe" |
  Select-Object FullName, @{Name="FileVersion";Expression={$_.VersionInfo.FileVersion}}
```

The Metro prototype remains under `mods\metro-dialogue-lab`; this recon did not alter it or either game.

## Verification

Verified by `um scan`, Steam appmanifest, local PE version metadata, presence and sizes of named engine
modules, `fsgame.ltx` path entries, archive file headers, and a count-only check of the save directory.
The game was not launched. No dialogue UI screenshot, live behavior, save load, mod, SDK, archive parser,
or code hook was tested. No save files or archive contents were modified or extracted.

## Gotchas

1. **Symptom:** the scanner says "Unknown native engine." **Cause:** engine signature recognition did not
   match. **Fix:** inspect the actual launcher/runtime module names and version metadata; here
   `xrEngine.exe`/`xrGame.dll` and version 1.6.02 indicate X-Ray 1.6.
2. **Symptom:** old X-Ray SDK or tutorial instructions are treated as current and exact-build compatible.
   **Cause:** search surfaced community materials from around 2010–2011, while the local Steam build is
   identified only as 1.6.02/build 11450453. **Fix:** validate tool provenance and compatibility before
   installing or applying changes; neither SDK nor tutorial edits were run here.
3. **Symptom:** `_appdata_` is treated as disposable because it is inside the install. **Cause:** the
   configured `fsgame.ltx` routes user saves, screenshots and logs there, and 139 save files were present.
   **Fix:** back up `_appdata_` before any modded launch or path/config change.
4. **Symptom:** `.db` headers are assumed to reveal their entire archive format. **Cause:** only the first
   32 bytes were observed; archives were not parsed. **Fix:** consult validated X-Ray tooling and test on
   copies before relying on archive extraction or repacking.

## Assets

None. No game assets were extracted or copied.

## Cost and time

No tools installed, no game launched, and no asset generation performed.
The user-data backup used
`um backup create "D:\Steam\steamapps\common\Stalker Call of Pripyat\_appdata_" --name stalker-call-of-pripyat-appdata`;
`um backup list stalker-call-of-pripyat-appdata` confirmed snapshot `20261015-213405.zip` (146 files,
64.5 MB).

## Open questions

Which Call of Pripyat dialogue screen/presentation does the user want to study; whether the exact Steam
build accepts a known X-Ray SDK 0.7 workflow; where runtime logs are created; and what reliable public
sources expose the exact dialogue UI layout and data model without redistributing game content.
