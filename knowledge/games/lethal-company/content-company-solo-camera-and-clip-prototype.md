---
kind: game
title: "A solo-host filming and clip prototype in Lethal Company"
game: "Lethal Company"
games_also: ["Content Warning"]
game_version: "Lethal Company v81 (Steam app 1966720; manifest build 22825947), Unity 2022.3.62f2; Content Warning app 2881650 build 22999514 was inspected read-only as a reference"
platform: windows
engine: unity-mono
route: managed-patch
tools: ["BepInEx 5.4.23.5", "Harmony", ".NET SDK 10.0.401", "UnityPy (existing environment)"]
anti_cheat: "No anti-cheat route used; tests were limited to a private solo/LAN host. No protected online session was entered."
status: in-progress
agents: ["OpenCode (gpt-6-luna)"]
humans: []
date: 2026-10-14
links:
  - "https://lethal.wiki/dev/initial-setup"
tags: ["camera", "recording", "BepInEx", "solo-host", "JPEG", "Harmony"]
---

# A solo-host filming and clip prototype in Lethal Company

> Content Company is an in-progress BepInEx/Harmony prototype that adds a host-local camera, bounded silent JPEG clips, playback and a configurable original scoring model to Lethal Company. Historical in-game runs verified parts of the camera/record/playback loop, but the current source has not passed a complete fresh runtime acceptance run; this is not a co-op mod.

## Setup

- Windows, Steam Lethal Company, Unity Mono 2022.3.62f2; the inspected installation reported game v81 and Steam app 1966720, manifest build 22825947.
- BepInEx 5.4.23.5 and Harmony; the project targets `netstandard2.1` and builds against assemblies in the user's game installation. The project journal records .NET SDK 10.0.401.
- The mod is in `mods/lethal-company-mod/`. Build outputs are directed outside the repository. Game assemblies, decompilations, saves, clips, and extracted assets must not be committed.
- Content Warning was supplied by the owner and inspected read-only as a reference. Its process was not launched or modified. The mod does not distribute its code or assets; an optional private camera-mesh import is local-only and geometry-only.

## Route and why

Use a managed BepInEx plugin with Harmony patches against Lethal Company's Unity/Mono runtime. The prototype recreates a filming loop inside the host game rather than bridging two running games. It is explicitly solo-host/local-only: features stop or disable when another player joins, and remote footage transfer and synchronized playback are not implemented. This keeps the current experiment out of public/client multiplayer and avoids claiming support for game networking that has not been validated.

The implementation preserves ordinary loot spawning for map/apparatus compatibility, while changing the scrap-sale/quota progression for its private prototype loop. This changes campaign state; use a backed-up test save, not a vanilla campaign to preserve.

## How the game works (what we had to learn)

- The plugin uses a thin `BaseUnityPlugin` bootstrap to install Harmony patches. The original bootstrap object was observed being destroyed during chainloader startup, so a separate runtime is attached from a local-player update path. Multiple local player objects can report ownership; runtime input is guarded by frame count to avoid processing a key more than once per frame.
- The camera item is instantiated from the host flashlight network prefab and customized per instance. It is a solo-host convenience, not a proven networked custom item. The optional imported mesh is private geometry with replacement materials; it does not port the reference game's textures, screen, animation, behavior, or code.
- Recording uses a dedicated Unity `Camera` and private 1280×720 `RenderTexture`, not a screenshot of the full game window. Frames are JPEGs with timestamps, written as a bounded clip. The current source documents a 60 FPS target, but actual cadence is lower when capture/encoding cannot keep up; missed frames are not duplicated. Audio capture is disabled.
- The current project documents limits of 1–20 seconds, at most 1,200 frames, 128 MiB per clip and 100 discovered clips per save. Clip metadata is save-scoped; file writes use temporary files/atomic replacement, validate IDs and clean up only the affected recording on failure. These are source-level design facts; verify the exact current implementation before relying on them after updates.
- The runtime has a host-only session guard and a join-time shutdown path. A later code review added a connected-client-count check because relying only on local ownership was insufficient. Do not infer that this proves all multiplayer transitions safe; remote play is unsupported.
- Scoring is an original configurable event model, not a port of Content Warning balance or code. Events are stored with clip metadata and sampled separately from video frames; brief events may be missed. Static inspection of the reference game's serialized scoring asset was incomplete and some extracted candidate values were explicitly unconfirmed, so they must not be presented as authoritative balance data.
- Lethal Company’s ordinary camera/TV lifecycle and materials can overwrite or conflict with custom display state. A separate marked display/controller with cloned materials and owned render targets is safer than changing shared materials or globally patching every TV. A physical camera screen/TV is not currently implemented.

## Build steps

From `mods/lethal-company-mod/`, with the user's game and BepInEx already installed:

```powershell
dotnet build -c Release "-p:LethalCompanyDir=D:\SteamLibrary\steamapps\common\Lethal Company" "-p:ModOutputDir=$env:LOCALAPPDATA\ContentCompany-build"
dotnet run --project tests/ClipTests.csproj
```

The project also accepts `GameDir` as an alias for `LethalCompanyDir`. Copy only the built `ContentCompany.dll` into the user's `BepInEx/plugins/` directory, and only while the game is closed. Check and back up the target save before launching. The repository README lists F6 preview, F7 record, F8 local upload/payout, F9 playback, F10 clip selection, and F11 enlarged viewer; confirm controls against the build being tested.

For a fresh test, launch through Steam, choose LAN → Local-only and explicitly confirm the intended save slot from the fresh plugin log. A previous direct executable launch failed to initialize the expected Steam transport and produced socket recovery errors; a Steam launch succeeded in a later run. Never use F5's diagnostic pickup helper as proof of normal station pickup.

## Verification

- Historical prototype run: a private Local-only session recorded and played back real JPEG footage. A later camera-feed run recorded 135 frames over 3.704 seconds at a measured average 36.5 FPS (1280×720; about 8.39 MB JPEG payload), and playback displayed the frames in game. This is evidence for that historical build/run only, not the current source or a stable 60 FPS rate.
- Earlier journal entries also record successful ordinary pickup/drop, a short recording, local playback and once-only solo payout in particular builds. Other runs exposed false-positive pickup messaging, incorrect/mismatched save selection, socket startup failures, and camera pose/visibility issues. Do not combine these runs into a claim that the current candidate passes acceptance.
- The 2026-10-13 reconciliation reported 18 clip unit tests passing and a successful Release build with zero warnings/errors. Later source changes and the current candidate require fresh checks; no tests were run while preparing this note.
- Current acceptance remains incomplete: the latest journal records an `Avatar is null` exception in the hand-pose visual's `LateUpdate`, uncertain current DLL/source correspondence, and incomplete fresh-run checks. Camera pose, pickup attribution, complete stop/drop/death/reload behavior, current-source recording/playback, payout recovery, audio, physical TV, co-op and 60 FPS are not all verified.

## Gotchas

1. **The plugin appears to initialize and then disappears. Cause:** the bootstrap `BaseUnityPlugin` object was observed being destroyed during startup. **Fix:** keep Harmony installation in the bootstrap and attach the persistent runtime from a live local-player update path; verify lifecycle in a fresh log.
2. **The first local-host launch loops on socket recovery. Cause:** one observed direct-executable launch logged Facepunch transport disabled; this suggests missing Steam launch context, though it is not proof of the only cause. **Fix:** launch through Steam and verify the fresh session diagnostic before testing gameplay.
3. **A pickup helper reports success but the camera is not actually held. Cause:** a message/key path is not proof of the game's held state; camera pickup depends on the normal hit/collider/ownership path. **Fix:** require the held-state log/HUD and a deliberate ordinary E pickup with a visible Grab prompt; do not count a helper or belt Equip prompt as acceptance.
4. **A run appears to pass but verifies the wrong campaign. Cause:** menu selection and existing open sessions have previously resulted in File1 instead of the intended File3. **Fix:** verify the save name in a fresh runtime log before interpreting results; stop if it differs.
5. **A test seems to start but no capture is produced. Cause:** recording requires the camera to be genuinely held, and earlier attempts pressed controls while it was still on the floor. **Fix:** verify held state first, then test a short clip and confirm frame count, file, playback and logs independently.
6. **The handheld mesh does not line up with the hand or capture view. Cause:** the visual transform, inherited item/collider and independent recording camera are separate coordinate/state paths. **Fix:** adjust only the visual anchor/pose and verify in game; don't treat a configured offset or successful build as visual proof.
7. **A nominal 60 FPS setting produces less. Cause:** synchronous GPU readback/JPEG encoding can miss deadlines. **Fix:** report measured frame count, duration and average FPS; don't synthesize duplicate frames or relax size/duration limits to make a test appear successful.
8. **Removing the plugin does not restore vanilla progression. Cause:** quota/deadline changes are persisted in the campaign save. **Fix:** back up before testing and use a dedicated campaign; DLL rollback and save restoration are separate operations.

## Assets

No assets are distributed from Content Warning. The owner's optional mesh import writes a private geometry file outside the repository and uses replacement materials. Extracted assets, game files and decompilations must remain outside the repository and published package.

## Open questions

- Fix or guard the current null-avatar hand-pose exception, then repeat the baseline on the intended Local-only save with a known candidate DLL hash.
- Verify current-source ordinary pickup, camera framing/pose, bounded clip save/reload, playback and failure/cleanup paths in game.
- Complete bounded writer/capture and lifecycle tests; decide separately whether video encoding and audio are in scope. Stable 720p60 and game-audio capture are not established.
- A physical display/TV, robust save-crash recovery and any cooperative transfer/scoring/ledger are future work; multiplayer is not supported.
- Keep reference-game scoring values and event semantics explicitly unconfirmed until independently validated; do not copy its code, serializers or assets.
