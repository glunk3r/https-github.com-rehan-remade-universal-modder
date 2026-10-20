---
kind: game
title: 'Recon: porting a Metro 2033 level into the Exodus SDK'
game: "Metro Exodus Enhanced Edition"
games_also: ["Metro 2033"]
game_version: "Metro Exodus Enhanced Edition Steam AppID 1449560, build 24973569; MetroExodus.exe file version 2.0.0.1. Source: original Metro 2033 Steam AppID 43110, executable file version 1.0.0.1"
platform: windows
engine: native
route: data
tools: ["um scan", "PowerShell file metadata", "Exodus SDK documentation"]
anti_cheat: none found by um scan
status: in-progress
agents:
- Copilot SDK in VS Code
humans: []
date: '2026-10-15'
links:
- https://www.4a-games.com.mt/4a-dna/studio-update-exodus-sdk
- https://exodus-sdk.atlassian.net/wiki/spaces/ESDK/overview
- https://exodus-sdk.atlassian.net/wiki/spaces/ESDK/pages/1714598145/EULA
- https://www.moddb.com/games/metro-exodus
- https://mod.io/g/exodussdk
- https://github.com/itsloopyo/metro-exodus-enhanced-edition-headtracking
tags: [recon, steam, enhanced-edition, 4a-engine, exodus-sdk]
---
# Recon: porting a Metro 2033 level into the Exodus SDK

Read-only reconnaissance of the Steam Enhanced Edition. The actual game executable is native x64
(`MetroExodus.exe`, file version 2.0.0.1); `um scan` initially labels the install .NET because the
separate benchmark executable is managed. The strongest supported route for new content is the official
Exodus SDK. The project goal is now to recreate/port one level from the original Metro 2033 into the
Enhanced Edition as host-native level content; this is not an engine/executable port. No mod or game
change was made, and no gameplay behavior or source-to-host compatibility has been verified.

## Setup

- Install: `D:\Steam\steamapps\common\Metro Exodus Enhanced Edition`, Steam AppID 1449560.
- Steam build ID: 24973569 (from the local `appmanifest_1449560.acf`); executable file version: 2.0.0.1.
- `MetroExodus.exe` is x64 and not managed; `Benchmark.exe` is x64 and managed.
- No anti-cheat or mod loader was detected by `um scan`. This is a local folder scan, not a complete
  system-wide anti-cheat audit.
- Saves and config: `%USERPROFILE%\Saved Games\Metro Exodus\<SteamID>\`; observed `.player` saves,
  `profile.cfg` and `user.cfg`, plus a `shared_saves` directory.
- Local log: `<install>\logs\metroexodus.log`.
- Exodus SDK is installed separately at `D:\Steam\steamapps\common\Exodus SDK` (Steam AppID 2069150,
  build ID 10516378). `bin_x64\Exodus_SDK.exe` reports version 1.0.0.1.
- `um scan` recognizes the SDK as “Unknown native engine” at 10% confidence; this means no signature
  matched, not that the engine is known. It finds the SDK editor as x64/native and indexes 80,662 files
  with a truncated index.
- SDK test map folders are present in `content\maps\sdk`: `sdk_ai_monsters`, `sdk_ai_npc`,
  `sdk_test_environment`, and `sdk_test_weapons_armory`. These paths were listed only; no map/editor was
  launched.

## Route and why

Use the official Exodus SDK to build host-native level content. The user is considering Exhibition (the
opening level) or Dead City; use Exhibition as the provisional first candidate, with Dead City as an
alternative if inspection shows it is the better first slice. Start with a small playable greybox after
inspecting the SDK's sample Volga level and verifying which import/conversion paths work. Preserve the
selected source route's key spaces, landmarks, traversal and progression; confirm exact acceptance
criteria before expanding. Do not assume 2033 archive or asset formats can load directly in Exodus.

The SDK is the supported authoring route, not a general-purpose code loader. Its EULA limits SDK use to
non-commercial personal use. The earlier Godot dialogue lab and its New Vegas / Call of Pripyat design
references are separate work, not the current first slice. Native x64 hooks are not planned unless the
SDK cannot support a specifically required behavior.

## How the game works (what we had to learn)

The game executable is native x64; the scan's `.NET` classification is a benchmark false positive. The
game folder contains large `content_*.vfs*` archives and `content.vfx`, but their internal format and
compatibility with any unpacker were not investigated. Do not infer the format from the extension or
extract/modify the shipped archives before checking the SDK documentation and a tool that explicitly
supports this exact game build.

The public Exodus SDK describes a full editor with scene/model editing, custom-content import, visual
scripting, NPC scripting and questline authoring. ModDB's overview says the SDK can be installed as a
Steam Tool, or as additional content for GOG/Epic, when a supported Metro Exodus edition is installed.
The SDK's official documentation requires agreement to its EULA. The engine/build details beyond the
native executable and SDK-facing workflow remain unknown.

## Build steps

No mod was built. For the level port:

1. Select one source level and write down its required layout and gameplay scope.
2. Read the [official SDK documentation](https://exodus-sdk.atlassian.net/wiki/spaces/ESDK/overview)
   and [EULA](https://exodus-sdk.atlassian.net/wiki/spaces/ESDK/pages/1714598145/EULA).
3. Install/launch the Exodus SDK using the route for the user's store. On Steam it is a separate Tool;
   do not copy files into the game folder as a substitute.
4. Inspect the SDK sample level, then greybox one representative playable segment before converting assets.
5. Test any format/import hypothesis on copies of source files from the user's install. Keep extracted game
   content outside this repository and never redistribute it.
6. Before changing saves or profile files, back up `%USERPROFILE%\Saved Games\Metro Exodus` with
   `um backup`. Test in a separate SDK project/profile where supported.

## Verification

- Read-only `um scan` reported Steam AppID 1449560, the game path, the managed benchmark executable,
  the native x64 game executable, and no detected loader or anti-cheat.
- Checked the local app manifest and executable file metadata for the Steam build ID and version.
- Confirmed the save/config and log locations by listing the user's existing files; no save data was read.
- Read the local log only for version identifiers; this is not runtime mod verification.
- No game launch, SDK installation, archive extraction, code decompilation, file modification, or in-game
  test was performed.

## Gotchas

1. **Symptom:** `um scan` says `.NET application`. **Cause:** the separate `Benchmark.exe` is managed;
   `MetroExodus.exe` is native x64. **Fix:** choose the main game executable when selecting analysis tools.
2. **Symptom:** the scan lists no mod loader and that is taken to mean no supported modding route.
   **Cause:** the official Exodus SDK is a separately distributed authoring tool, not a loader inside the
   game directory. **Fix:** check Steam Tools or the store's SDK/additional-content route first.
3. **Symptom:** a mod made for original Metro Exodus or another build is assumed to work on this Enhanced
   Edition build. **Cause:** compatibility is version-specific. **Fix:** pin the SDK/game build and verify
   the exact target edition before installing or testing any mod.
4. **Symptom:** `.vfs*` files are passed to a generic archive tool based only on the extension.
   **Cause:** the archive format and build compatibility have not been established here. **Fix:** use
   SDK-supported workflows or validate an exact-build parser on copies before any asset work.
5. **Symptom:** an Enhanced Edition head-tracking plugin is treated as a general extension API.
   **Cause:** the repository documents one native-hook feature and build-specific behavior, not a reusable
   public gameplay API. **Fix:** prefer the official SDK; use native hooks only for a defined gap.

## Assets

None generated, extracted or modified.

## Cost and time

No paid services or generation used.

## Open questions

- Is Exhibition tractable as the first port after checking the source level and SDK, or should the project
  switch to Dead City?
- What does success mean for that level: matching geometry/layout, a playable/completable route, gameplay
  and encounters, scripting, or some defined subset?
- Which exact Exodus SDK version is currently distributed for Steam build 24973569, and does its content
  pipeline support importing/rebuilding that level without runtime hooks?
- Which Metro 2033 source assets/data are needed, and what conversion/authoring workflow does the EULA and
  SDK support?
- User reports the SDK was downloaded separately; install path, exact version, and sample-project status
  are not yet verified.
- What exact SDK map/editor workflow opens the sample environments and tests custom level imports?

## Research queries and sources

- Knowledge-base searches: `Metro Exodus`, `4A Engine`, `Exodus SDK`. No Metro Exodus note existed at the
  time of this recon.
- GitHub repository searches: `"Metro Exodus" mod`, `4A Engine modding`.
- Direct source checks: 4A Games' Exodus SDK announcement, the official SDK docs and EULA, ModDB's
  Metro Exodus page, mod.io's Exodus SDK page, and the README/commit history of the
  [Enhanced Edition head-tracking project](https://github.com/itsloopyo/metro-exodus-enhanced-edition-headtracking).
- Nexus Mods returned HTTP 403 to this fetch; no Nexus compatibility claim is made.
- The ModDB page reports SDK availability for the original and Enhanced editions and gives store-specific
  installation routes. The SDK documentation/EULA is primary for licensing; the tool-install route was
  cross-checked against ModDB because the official article did not return readable setup instructions.
