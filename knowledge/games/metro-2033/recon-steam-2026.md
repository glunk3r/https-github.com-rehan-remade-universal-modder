---
kind: game
title: 'Recon: original Steam release and modding routes'
game: Metro 2033
games_also: []
game_version: 'Steam AppID 43110; metro2033.exe file version 1.0.0.1'
platform: windows
engine: native
route: other
tools: ["um scan", "Godot 4.7.2 stable", "um win", "Metro 2033 Config Editor (ModDB listing; not installed)", "Metro-specific QuickBMS scripts (read, not run)"]
anti_cheat: none detected; recon only, no game launch
status: in-progress
agents:
- Copilot SDK in VS Code
humans: []
date: '2026-10-15'
links:
- https://www.moddb.com/games/metro-2033/mods
- https://www.moddb.com/mods/metro-2033-config-editor
- https://store.steampowered.com/app/43110/Metro_2033/
- https://github.com/XeNTaXBackup/XeNTaXBackup.github.io/blob/main/markdown/Metro%202033%20vfs%20file_4229.md
- https://github.com/D13FORME/quickbms-scripts/blob/main/M/metro2033_unpack_upk.bms
- https://www.4a-games.com.mt/
- https://en.wikipedia.org/wiki/4A_Engine
- https://github.com/BlackPhrase/YuRei/blob/master/docs/specs.txt
- https://godotengine.org/download/windows/
- https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html
- https://github.com/ixray-team/ixray-1.6-stcop/blob/478899e687b1e5d7eab834120a252ca01b3dca36/gamedata_soc/configs/fonts.ltx
- https://github.com/google/fonts/tree/1d0e46c7933245c8180fe83e47917961c913bbdb/ofl/robotocondensed
tags: [recon, original-release, native-x86, config]
---
# Recon: original Steam release and modding routes

Read-only reconnaissance of the original Steam release of Metro 2033 (AppID 43110), not Metro 2033 Redux.
The main executable is native x86, file version 1.0.0.1, and identifies 4A Games; the scan's .NET result
came from the separate managed benchmark executable. No general-purpose supported code loader was found
in the sources checked. A separate Godot dialogue prototype was later built as a behavior lab; it is not
a Metro mod and did not change or launch the Metro installation.
The selected S.T.A.L.K.E.R. UI reference is Call of Pripyat; see the separate
[Call of Pripyat recon note](../s-t-a-l-k-e-r-call-of-pripyat/recon-call-of-pripyat-steam-1-6-02-for-dialogue-ui-reference.md).
For the Metro project's donor split, use Fallout: New Vegas as a design reference for dialogue branching/
quest mechanics and Call of Pripyat as a presentation/UI reference only. Neither donor's format is known
to load in Metro; see the donor comparison in the project [MODLOG](https://github.com/wh1tem0nst3r/universal-modder/blob/main/mods/metro-dialogue-lab/MODLOG.md).

## Setup
Windows; Steam AppID 43110. `metro2033.exe` is x86, not managed, and reports file version 1.0.0.1.
The install contains `content.vfi`, `content.vfs*`, `textures.vfs*`,
`sounds*.vfs*`, and `*.upk*` data files plus `user.cfg`. The game data is packed; no unpacking or patching
was attempted. No anti-cheat or mod loader was detected.

## Route and why
For configuration changes, start with the existing `user.cfg` or the Metro 2033 Config Editor listed on
ModDB; that listing specifically says it targets the original Steam game, not Redux. ModDB also lists
standalone campaign content. A maintained general-purpose scripting/plugin loader or official SDK was not
identified in the sources checked. For a feature that cannot be expressed as configuration or supported
content, native x86 reverse engineering/hooks are a last resort, not the default. The desired mod idea is
not yet specified.

## How the game works (what we had to learn)
The game executable is an unmanaged 32-bit binary; `metro2033benchmark.exe` is a separate managed program
and must not be used to infer the game engine. The game executable imports Direct3D 9-era libraries,
DirectInput 8, XInput, and file I/O APIs; these dependencies identify possible analysis targets but do not
reveal function behavior. The 229-line `user.cfg` is a practical low-risk modding surface, with binding,
AI, and renderer settings. A historical XeNTaX thread describes `content.vfi` as an index for `.vfs0` and
`.vfs1` archives, and Metro-specific QuickBMS scripts describe unpacking VFS and UPK contents; these
2010-era scripts were not run or verified against the current installation and explicitly do not decrypt
data. The `.upk` extension alone does not establish standard Unreal package format. ModDB's listing
includes a config editor and the standalone campaign mod The Guide Story.

The official 4A Games site lists Metro 2033 as a studio project but does not identify the engine or
offer SDK documentation. A secondary reference identifies the proprietary 4A Engine; the local PE
evidence does not establish its version or internals. A community repository contains historical
technical-discussion notes about 4A's engine design, but their provenance and applicability to this
exact build are unverified. The developers' connection to S.T.A.L.K.E.R. is not evidence that the game
uses X-Ray.

For extraction, the historical game-specific VFI/VFS and UPK QuickBMS scripts are plausible starting
points only. They state unpack-only/no-decryption capability and have not been tested against the
installed Steam files. No official public SDK or maintained general-purpose plugin loader was found in
the sources checked; this is not an exhaustive proof of absence.

## Build steps
No Metro build or install was performed. The first experiment for the requested dialogue-tree idea is a
standalone Godot 4.7.2-stable harness in [mods/metro-dialogue-lab](https://github.com/wh1tem0nst3r/universal-modder/blob/main/mods/metro-dialogue-lab/README.md).
It uses original dialogue and primitive geometry and exports to `build/MetroDialogueLab.exe`; this does not
produce a Metro-compatible executable. Reproduce its tests from PowerShell at the repository root:

```powershell
& "$env:LOCALAPPDATA\Godot\4.7.2-stable\Godot_v4.7.2-stable_win64.exe" --headless --path "mods\metro-dialogue-lab" --script "res://tests/run_dialogue_tests.gd"
```

The prototype's schema version 2 separates conversation-scoped flags from simple declared quest states:
choice requirements gate visible responses, choice effects change quest state, and that state persists
across conversations in memory (it is not a save system). Its original Ukrainian example tests a generator
fuse task from offer through completion and a gated follow-up. The standalone UI uses a left-aligned
response list with an amber selection and Roboto Condensed. A public X-Ray 1.6 CoP reference config names
RobotoCondensed as its condensed OpenType family; the lab uses the separately obtained Google Fonts file
under the SIL Open Font License, not a font extracted from CoP:
[CoP reference](https://github.com/ixray-team/ixray-1.6-stcop/blob/478899e687b1e5d7eab834120a252ca01b3dca36/gamedata_soc/configs/fonts.ltx),
[font source and license](https://github.com/google/fonts/tree/1d0e46c7933245c8180fe83e47917961c913bbdb/ofl/robotocondensed).

Only when attempting later Metro integration, start with:
1. Back up the existing `user.cfg` and the user-data folder.
2. Check whether the requested change is expressible as a config setting or existing supported content.
3. Test in a disposable copy/profile; preserve original files and restore from backup if needed.
4. Only investigate native hooks if there is no lower-risk route.

## Verification
Verified by read-only scan, executable version metadata, and local file listing: the main game executable
is native x86; the benchmark executable is managed; the install includes packed game data and `user.cfg`.
The AppData location `%LOCALAPPDATA%\4A Games\Metro 2033\11000010f1232ff` exists. No game
launch, mod installation, archive parsing, or Metro gameplay verification was performed. Separately,
Godot 4.7.2 headless project import and startup passed; 21 model/UI integration checks passed; the
64-bit debug export was launched and its room, NPC prompt, and dialogue panel were visually inspected.
Those prototype checks are not a Metro gameplay oracle.
After the quest-state/UI update, the same headless test script passed 48 checks covering state persistence,
choice effects, gated follow-up, keyboard selection, and Cyrillic font rendering; the Windows x86_64 debug
export also completed. These checks still exercise only the separate Godot prototype, not Metro gameplay.

## Gotchas
1. **Symptom:** `um scan` labels the game a .NET application. **Cause:** it found the managed
  `metro2033benchmark.exe`; `metro2033.exe` itself is native x86. **Fix:** select the game executable
  explicitly when researching hooks or mod loaders.
2. **Symptom:** a Metro config tool or mod is assumed to support Redux too. **Cause:** the original game
  and Redux are distinct releases with different app IDs and potentially different files. **Fix:** use
  tools explicitly marked for the original Steam release (43110), and re-check each mod's compatibility.
3. **Symptom:** a generic Unreal package utility is selected because files end in `.upk`. **Cause:** the
  installed `content.upk0` begins with bytes unlike the standard UE3 package tag, and Metro has its own
  historical parser scripts. **Fix:** validate the exact archive/version first; don't infer the engine
  from the extension.
4. **Symptom:** historical VFS/UPK scripts are treated as a verified extraction pipeline. **Cause:** the
  scripts are old, their authors describe unpacking without decryption, and they have not been exercised
  on this Steam build. **Fix:** test only a copy in a disposable workspace, preserve the original
  archives, and validate every output before using it.
5. **Symptom:** a new standalone executable is assumed to use Metro's engine because it tests Metro-like
  dialogue mechanics. **Cause:** the first vertical slice is an independent Godot prototype; no public
  4A SDK/editor was identified. **Fix:** keep it explicitly separate and do not claim Metro integration
  until the installed x86 game is changed and verified.
6. **Symptom:** Godot's `--export-debug` command returns without producing the EXE. **Cause:** export was
  invoked without explicit editor mode in this environment. **Fix:** use
  `--editor --quit --export-debug "Windows Desktop" <absolute-output-path>`.

## Assets
No Metro assets were used. The separate dialogue prototype uses original JSON text, placeholder geometry,
and the openly licensed Roboto Condensed font; it includes the font's SIL Open Font License. No asset was
extracted from Metro, Fallout: New Vegas, or S.T.A.L.K.E.R.

## Cost and time
No generation or installation cost; no game files were changed.

## Open questions
Whether the installed Metro build exposes a usable dialogue hook or data-driven script route; validation
of the historical archive parsers; a safe edit/repack workflow; exact save and game log locations.
