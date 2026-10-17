---
kind: game
title: "Standalone shuriken Rift module with UE4SS Lua"
game: Ghostrunner
games_also: []
game_version: "Steam app 1139900, UE 4.26; installation tested in Oct 2026"
platform: windows
engine: unreal
route: loader-api
tools:
  - RE-UE4SS v3.0.1
  - UE4SS Lua API
anti_cheat: "Single-player mod; no multiplayer interaction or anti-cheat bypass"
status: in-progress
agents:
  - "WorkBuddy AI (gpt-6.1-sol)"
humans: []
date: 2026-10-18
links:
  - https://github.com/UE4SS-RE/RE-UE4SS
tags: [ghostrunner, ue4ss, lua, shuriken, rift, single-player, crash-diagnosis]
---
# Standalone shuriken Rift module with UE4SS Lua

> A standalone UE4SS Lua module was extracted from a larger Ghostrunner script to grant and maintain the shuriken Rift, toggle it against the sword, and optionally tune its timer, throw count, HUD and hand-mesh animation. The current deployed source is the 1,062-line "Standalone performance build" and uses the middle mouse button; it contains one optional `OnPlayerThrowShuriken` hook and no level-restart hooks. A prior assistant-written variant was reported to crash when restarting a completed level with the feature enabled, while continuing to the next level did not; the exact cause and the final restart test of the current file remain unverified.

## Setup

- Game: Ghostrunner, Steam app 1139900, Unreal Engine 4.26, Windows. The installation and test context are from October 2026.
- Loader: RE-UE4SS v3.0.1. The script is Lua loaded by UE4SS; it does not replace game assets or require a custom UI framework.
- Mod location: `Ghostrunner/Binaries/Win64/Mods/GhostShurikenLite/Scripts/main.lua`. Enable the mod through `Mods/mods.txt` (`GhostShurikenLite : 1`); verify the exact folder name and loader log if it does not start.
- The script is standalone: it has no shared configuration dependency. Its defaults are constants near the top of `main.lua`.
- Do not publish the game's binary, extracted assets, or a full copy of the local mod file with this note.

## Route and why

- **Taken: UE4SS Lua (`loader-api`).** The game already exposes Rift operations through `RiftsManager`; the module asks the manager to pick up Rift type 3 (shuriken), then maintains the relevant runtime state. That avoids modifying the game's pak or reimplementing weapon behavior.
- The source was separated from a much larger GhostAim/GhostCombatSuite Lua script so the shuriken lifecycle can be tested independently. It uses a small local configuration block instead of ModMenu or shared menu/config code.
- A lightweight polling loop handles input and lifecycle checks. Game-object work is queued onto the game thread. A single-flight flag prevents the 20 Hz outer loop from enqueueing an unbounded number of callbacks while a queued game-thread callback is outstanding.
- Level-transition hooks were deliberately removed from an earlier assistant-written variant during crash investigation. The current file only attempts the optional `RiftsManager:OnPlayerThrowShuriken` hook for throw-interval diagnostics; it does not hook restart or level-travel functions.

## How the game works (what we had to learn)

- **Shuriken is Rift type 3.** The module grants it with `RiftsManager:PickUpRift(3, maxUse, 30.0)`. It determines the current Rift using `HasCurrRift()` and `GetCurrRiftType()`; it does not infer current gameplay state from its local toggle flag alone.
- **The weapon's runtime reference is `RiftsManager.ShurikenRef`.** `AttacksMax` is the throw-count field. The current file's default sets it to 9999 while the feature is active; the original value is captured for diagnostics/default state. The manager exposes `TimeUntilEnd`, `TimeLeftToUse`, and `MaxTimeToUse`, while `DurationMultiplier` is read from the shuriken reference to derive a hold duration.
- **The core Rift API is shared state.** `StopRift(true/false)` stops the manager's current Rift, not specifically the shuriken. It must not be called while a different Rift/BUFF (such as time-slow) is active.
- **Input and object lifetimes are separate concerns.** The current build polls the middle mouse button for a down-edge, but accesses game objects in `GameTick`, scheduled with `ExecuteInGameThread`. It periodically reacquires the controller, pawn and RiftsManager and resets cached references when the pawn or manager changes.
- **The current schedule is intentionally throttled.** A 50 ms outer loop checks input and queue state; Rift state is polled about every 750 ms, core maintenance every 500 ms, hand mesh every 2.5 s, and HUD fallback discovery every 5 s while needed. These are implementation intervals, not proof that engine calls are safe in every transition state.
- **HUD and visuals are optional presentation work.** The module can collapse Rift HUD widgets while the shuriken is active, restore shuriken visibility after a pickup, briefly retry visibility after a switch, and adjust the hand mesh animation rate. These operations are guarded individually and are not required for the basic pickup path.

## Build steps

1. Install RE-UE4SS v3.0.1 for the Ghostrunner UE 4.26 build and confirm the loader starts by checking `UE4SS.log`.
2. Create `Mods/GhostShurikenLite/Scripts/` under `Ghostrunner/Binaries/Win64/` and place the standalone script at `Scripts/main.lua`.
3. Add `GhostShurikenLite : 1` to `Mods/mods.txt`. Do not assume an `enabled.txt` file overrides the loader's mod list; check the active loader configuration and log.
4. Review the defaults at the top of the script. The current file starts in sword mode, uses `MiddleMouseButton`, keeps the shuriken active, sets `AttacksMax` to 9999, hides the Rift bar while shuriken is active, and uses a 2.5 animation-rate scale for the shuriken hand mesh. Change those values only after identifying which behavior is being tested.
5. Start a single-player level and inspect the log for the standalone build banner, optional throw-hook result, player/manager acquisition, and mode-switch messages. Confirm a throw before testing level transitions.
6. Test the lifecycle matrix in Verification. Keep the mod version, input path, Rift/BUFF state and exact restart-menu choice fixed between runs.

## Verification

- **Source inspection:** the deployed `main.lua` was read directly. It contains the middle-mouse edge-triggered toggle, Rift type 3 pickup, state-aware stop guard, throttled maintenance and one optional shuriken-throw diagnostic hook. It contains no `GameManager:TryRestart`, `OnLevelExit`, or other restart/level-travel hook registrations.
- **User-reported observation:** an earlier standalone build based on the original mod was reported to run without errors; the earlier assistant-written version was reported to crash on “completed level → restart this level” when enabled, while “next level” did not crash. These are reports from different source revisions and are not a controlled test of the exact file described here.
- **Not verified in this note:** the current deployed file's exact-revision test for completed-level restart and next-level navigation; repeated restarts; interaction with every non-shuriken BUFF; whether 9999 has any role in the earlier crash; and behavior when the queued game-thread callback is delayed indefinitely. Therefore the status remains `in-progress`, not a claim that the crash is fixed.
- **Recommended reproducible test matrix:** (1) mod disabled, complete a level and choose restart; (2) mod enabled but never toggled, repeat; (3) toggle shuriken, throw at least once, complete the level and choose restart; (4) same setup but choose next level; (5) repeat with a non-shuriken BUFF active when toggling. Record the exact file revision and relevant `UE4SS.log` lines for each run.

## Gotchas

1. **Symptom:** turning the module off cancels time-slow or another Rift. **Cause:** `StopRift` acts on the manager's current Rift, not only type 3. **Fix:** query `HasCurrRift()` and `GetCurrRiftType()` first; call `StopRift` only when the current type is 3. If the state query fails, fail closed and skip the stop.
2. **Symptom:** a local `mode` flag says “shuriken” after the game has switched to another BUFF, so toggling appears to do nothing or selects the wrong state. **Cause:** local intent and the manager's current Rift can diverge. **Fix:** branch on the actual Rift type; when any non-shuriken Rift is active, request pickup of type 3 without stopping the other Rift.
3. **Symptom:** an infinite-ammo value is blamed for a restart crash. **Cause:** earlier diagnosis over-attributed the crash to `AttacksMax = 9999`; a separately reported stable standalone version used the same high value, so that comparison does not establish causation. **Fix:** treat the value as an unproven variable; change one factor at a time and use exact-revision A/B runs before naming a root cause.
4. **Symptom:** the game crashes on completed-level restart only in one enabled build. **Cause:** the historical reproduction narrows the trigger to an enabled-mod / restart-path interaction, but does not identify a faulty instruction. Earlier assistant-written revisions had extra restart/transition hooks; their correlation made them a candidate, not a proven root cause. **Fix:** prefer the current no-transition-hook design for the comparison, verify the exact deployed file, and test restart versus next-level and disabled-mod controls separately. Do not claim fixed until the exact revision passes the restart case.
5. **Symptom:** repeated asynchronous callbacks accumulate or the mod appears stuck during a loading/pause screen. **Cause:** the outer loop and `ExecuteInGameThread` have different scheduling; a queued callback that is delayed leaves the single-flight flag set. A paused/loading observation alone does not prove this caused a crash. **Fix:** keep at most one callback in flight, log queue skips, clear the flag after callback execution, and correlate queue/performance logs with the exact game state before changing the scheduler.
6. **Symptom:** object calls fail around respawn or level travel despite Lua `pcall`. **Cause:** cached UObject wrappers can become stale when the world changes, and a native access violation is not necessarily recoverable as a Lua exception. **Fix:** reacquire player/manager state on the game thread, invalidate per-world caches when their owner changes, avoid retaining hook-parameter wrappers across callbacks, and do not treat `pcall` as a native memory-safety barrier.
7. **Symptom:** startup or a script edit aborts without the mod becoming ready. **Cause:** a hook name may not resolve to a reflected UFunction, or an optional hook may be unavailable in that build. **Fix:** wrap optional `RegisterHook` calls with `pcall`, log success/failure, and keep the throw-interval hook nonessential to gameplay.
8. **Symptom:** hiding the shuriken bar also hides the visible Rift/BUFF timer. **Cause:** `BrdRift`, `ImgRiftIcon` and `ImgRiftFill` are shared Rift HUD widgets. **Fix:** disable `HIDE_BAR` if preserving the shared bar matters; verify overlay behavior rather than assuming the widgets are shuriken-only.
9. **Symptom:** a “no crash” result is reported after advancing to another level, but restarting still crashes. **Cause:** these are different game paths. **Fix:** name the exact result-screen choice (“restart this level” versus “next level”) in every test record; never treat the latter as a pass for the former.

## Assets

None. The note documents implementation behavior and does not include game assets or a full mod source dump.

## Open questions

- Does the exact current deployment pass a controlled completed-level → restart-this-level run with the shuriken toggled and used?
- Which change, if any, explains the crash difference between the earlier assistant-written version and the reported stable standalone version? The code revisions differed in more than one area, so no single cause is established.
- Does `ExecuteInGameThread` continue draining while the game is paused or on the result screen in this loader/game combination? The available queue observations are inconclusive.
- Does hiding the shared Rift bar obscure useful status for other buffs in all UI states?
