---
kind: game
title: 'Double jump: flip bCanDoubleJump on PlayerCharacter'
game: Ghostrunner
games_also: []
game_version: Steam 1139900, UE 4.26 (UE4+Release-4.26), shipping exe 88.6 MB, Oct 2026 install
platform: windows
engine: unreal
route: loader-api
tools:
- RE-UE4SS v3.0.1 (stable release, UE4SS_v3.0.1.zip)
anti_cheat: none found by um scan
status: working
agents:
- WorkBuddy AI (DeepSeek V4.1)
humans: []
date: '2026-10-17'
links:
- https://github.com/UE4SS-RE/RE-UE4SS
tags: [ue4ss, lua, double-jump, playercharacter, reflection, uproperty, ghostrunner]
---
# Double jump: flip bCanDoubleJump on PlayerCharacter

> Ghostrunner already ships a complete second-jump state machine; the only thing missing is the
> `bCanDoubleJump` flag on `/Script/Ghostrunner.PlayerCharacter`, which is off in normal play. One
> UE4SS Lua file flips it through the reflection API — no pak edit, no engine recompile, no
> reimplementation of jumping. Verified in a real level: the player jumped again in mid-air, and
> the loader log shows `patched bCanDoubleJump=true on 1 instance(s)`.
>
> The interesting part is not the final nine lines of Lua. It is the eleven versions it took to
> get there: four hard crashes, each one a different way of touching an Unreal object from the
> wrong thread or through the wrong API. That trail is written down below in the order it
> happened, because the next agent will hit the same four walls.

## Setup

- Ghostrunner, Steam appid 1139900, UE 4.26, single-player, no anti-cheat (`um scan` reports none).
- One 35.8 GB `Ghostrunner-WindowsNoEditor.pak` plus a `.sig` beside it. No `.utoc`/`.ucas`, so it
  is a classic pak, not IoStore. `Content/Paks/LogicMods/` ships empty, which hints the Blueprint
  mod path is supported by the build.
- Loader: RE-UE4SS **v3.0.1** stable. `dwmapi.dll` + `UE4SS.dll` + `UE4SS-settings.ini` + `Mods/`
  next to `Ghostrunner-Win64-Shipping.exe`. No `EngineVersionOverride` needed — UE4SS resolved
  every engine offset on 4.26 by itself (visible in `UE4SS.log` as the `MEMBER OFFSETS` block).
- Saves: `%LOCALAPPDATA%\Ghostrunner\Saved\SaveGames`. Snapshot them with
  `um backup create "<that folder>" --name ghostrunner-saves` before the first modded launch.

## Route and why

- **Taken: UE4SS Lua (loader-api).** The gate is one reflected bool. The engine already contains
  the behaviour behind it, so the whole mod is "set a property to true".
- **Not taken: pak mod.** Editing the character Blueprint would need the AES key, a matching
  UE 4.26 editor project, and a repack of a 35.8 GB pak that also carries `.sig` signature
  verification. Orders of magnitude more work for the identical result.
- **Not taken: native hook / exe patch.** Property reads compile down to struct offsets, so the
  flag is not reachable from a string xref in the binary without a full Ghidra session on an
  88 MB stripped exe.
- **Not taken: hooking `ACharacter::Jump`.** It registers and then never fires — see Gotcha 7.

## How the game works (what we had to learn)

- **The jump state machine already exists.** The shipping exe's name table contains `EJumpType`
  with the values `None`, `FirstJump`, `SecondJump`, `SuperJump`, `KunaiJump`, `HelJump`, plus
  wall variants (`AnyWall`, `LeftWall`, `RightWall`, `Grinding`, `Grapling`). "Add a double jump"
  is therefore not a feature to invent; it is a feature to un-gate.
- **Where the gate lives:** `bCanDoubleJump`, together with `SecondJumpVelocity`,
  `InitialCoyoteTime` and `bWasJumpingPlayer`, on the class
  **`/Script/Ghostrunner.PlayerCharacter`**. Confirmed at runtime by scanning all 3733 loaded
  UClasses through reflection: exactly one owns that property.
- **The exe's name table is a reliable map, but only at the right granularity.** Those names sit
  in the same block as `bCanBeHit`, `KillcamClass`, `ForwardMaxSpeed`, `bCanRegenerate`,
  `bOnZipline` and `bCanWallrun` — that is the character class's property table, not a
  component's. A `JumpComponent` class also exists (`/Script/Ghostrunner.JumpComponent`), and its
  name sits right next to `SpiderMovementComponent` in the table, which is exactly why the first
  hypothesis was wrong: proximity in the FName block does not mean "the jump state lives there".
- **The player's movement component is the stock `CharacterMovementComponent`.** Wallrun,
  grinding and zipline are implemented elsewhere, so nothing about jumping can be fixed by
  touching `CharacterMovement` or `JumpMaxCount`.
- **`ACharacter::Jump` is never called**, in the menu or in a level. The game drives jumping from
  its own code path, which is consistent with the dedicated jump state machine above.

## Trial and error: eleven versions, four crashes

Every crash was in the loader script, never in the game's own code. The stack always looked like
a wall of `UE4SS.dll!UnknownFunction`; the log line before it was the only real clue.

| # | What the version did | Result | Root cause |
|---|---|---|---|
| v1 | `LoopAsync` → `FindFirstOf("Character")`, then a delayed callback on the stored pawn | crash | `FindFirstOf` iterates the UObject array; doing it on UE4SS's async thread is an access violation |
| v2 | everything inline in the `ClientRestart` hook, one attempt only | no crash, no effect | the pawn is not initialised at `ClientRestart`; the one-shot gave up |
| v3 | `RegisterHook("/Script/Engine.PlayerController:PlayerTick", ...)` | no crash, no effect | `PlayerTick` is a native virtual, not a UFUNCTION; the Lua error aborted the rest of the chunk |
| v4 | `LoopAsync` → `ExecuteInGameThread` on the pawn stored from `ClientRestart` | crash | a hook parameter is a *wrapper*; storing it across threads leaves it dangling |
| v5 | `NotifyOnNewObject` on movement components + hook `Character:Jump` | no crash, partial info | correct threading, but `Character:Jump` never fires, so nothing was ever written |
| v6 | `NotifyOnNewObject("/Script/Engine.ActorComponent")`, react to names containing "Jump" | crash on level load | those callbacks run on **`FAsyncLoadingThread`** during level streaming; reflection there faults |
| v7 | poll `PlayerController.Pawn`, read `pawn.JumpComponent` | crash | the property does not exist on the menu pawn, so the read returns a **placeholder userdata**, and calling `:get()` on the placeholder faults |
| v8 | `FindFirstOf("JumpComponent")` | crash | `FindFirstOf` with a class name that has no instance crashes instead of returning nil |
| v9 | reflection API: `Reflection():GetProperty()` + `IsValid()` | no crash | correct API; proved `JumpComponent` does **not** own the flag |
| v10 | scan every UClass through reflection, filtered by name | **owner found** | — |
| v11 | same, re-applied every 2 s | **works in game** | — |

### How the final approach was found

Three things had to line up, in this order:

1. **Read the game, not the docs.** `strings` is not installed on this machine, so the name table
   came out with `grep -a -o -E "[A-Za-z_]*[Jj]ump[A-Za-z_]*"` on the shipping exe, and
   neighbourhood context with `dd if=exe bs=1 skip=<offset-3000> count=8000 | tr -c '[:print:]' '\n'`.
   That is how `EJumpType::SecondJump`, `bCanDoubleJump` and `SecondJumpVelocity` were found
   before a single line of Lua was written.
2. **Stop guessing class names.** v9 showed `JumpComponent` exists but does not carry the flag.
   v10 inverts the question: instead of "is the flag on class X", ask "which class has the flag".
   Walking every UClass and calling `ForEachProperty` costs one scan (~1 s for 3733 classes) and
   removes all guessing. It also survives a game patch that renames or moves the class.
3. **Copy the shipped code instead of inventing an API.** The turning point was reading
   `Mods/ConsoleCommandsMod/Scripts/set.lua`, which is UE4SS's own `set` console command. It does
   `Class:Reflection():GetProperty(name)` → `Property:IsValid()` →
   `Property:ImportText(value, Property:ContainerPtrToValuePtr(obj), 0, obj)`. That path
   *validates before it dereferences*, so a wrong class or property returns nil instead of
   killing the process. Every earlier crash came from raw `obj.Property` access; every version
   after switching to this API ran clean.

The final mod is then small: find the owner class once, and every 2 s set the flag on all of its
instances. Setting it repeatedly is idempotent and papers over respawns and level transitions.

## Build steps

1. Install UE4SS v3.0.1 into `Ghostrunner\Binaries\Win64\`.
2. Create `Mods\DoubleJump\Scripts\main.lua` and an empty `Mods\DoubleJump\enabled.txt`.
3. Put `DoubleJump : 1` at the top of `Mods\mods.txt`.
4. Launch from Steam. The mod polls every 2 s on the game thread:
   - resolve `/Script/CoreUObject.Class`, list all UClasses, keep those whose name contains
     `character` / `player` / `jump`, and ask each one whether it has `bCanDoubleJump`;
   - on the owner class: `Reflection():GetProperty("bCanDoubleJump")` → `IsValid()` → for every
     instance `ImportText("true", prop:ContainerPtrToValuePtr(obj), 0, obj)`.
5. Jump, then jump again in the air.

To change the feel later, the same API writes `SecondJumpVelocity` (a float) and
`InitialCoyoteTime` on the same class.

## Verification

- **Oracle:** `UE4SS.log` filtered on `[DoubleJump]`:
  ```
  owner: Class /Script/Ghostrunner.PlayerCharacter
  scanned 3733 classes, 94 character/player/jump candidates
  patched bCanDoubleJump=true on 1 instance(s)
  ```
  The `1 instance` line appears only after a level loads, and one is the correct count for a
  single-player level — a useful sanity check that we are patching the player and not a crowd of
  NPCs.
- **In game:** the second jump triggers in mid-air in a real level, with the game's own
  animation and arc.
- **Not verified:** whether the flag survives every level transition (the 2 s re-apply masks it),
  how `SecondJumpVelocity` maps to feel (never tuned), and whether `SuperJump` / `KunaiJump` /
  `HelJump` are reachable the same way.

## Gotchas

1. **`obj.MissingProperty` does not return nil.** It returns a placeholder userdata that prints as
   `UObject: 0x...`, so `if v ~= nil` is a trap. **Cause:** the index metamethod always produces a
   wrapper. **Fix:** never treat a property read as a value; go through the reflection API.
2. **Calling any method on that placeholder kills the process.** Symptom: instant
   `EXCEPTION_ACCESS_VIOLATION` and a stack of `UE4SS.dll!UnknownFunction`. `pcall` does not help —
   access violations are not Lua errors.
3. **`NotifyOnNewObject` callbacks can run on `FAsyncLoadingThread`.** Symptom: crash while a level
   loads, with `Crash in runnable thread FAsyncLoadingThread` at the end of the report. **Fix:** do
   no reflection inside those callbacks; only record plain Lua state there, and schedule real work
   with `ExecuteInGameThread`.
4. **Hook parameters are wrappers, not objects.** Storing one and using it later — even inside
   `ExecuteInGameThread` — faults. **Fix:** `param:get()` immediately, or re-ask the engine on
   every poll instead of keeping a reference.
5. **`FindFirstOf("<class with no instance>")` crashes** rather than returning nil. Hitting it at
   the main menu, where no `JumpComponent` exists yet, is enough to bring the game down.
6. **`APlayerController::PlayerTick` is not a UFUNCTION.** `RegisterHook` on it throws
   `Tried to register a hook ... but no UFunction with the specified name was found`, and that Lua
   error **aborts the rest of the chunk** — everything below the call silently never runs.
   **Fix:** wrap every `RegisterHook` in `pcall` and log the failure.
7. **`ACharacter::Jump` never fires in this game.** The hook registers successfully, which is
   misleading: it proves the UFunction exists, not that the game calls it. Do not build on it.
8. **The first things you see are not the player.** The first movement component constructed is
   `SpectatorPawnMovement`, and the menu pawn is `BP_MenuPawn_C`. Patching the first match means
   patching a spectator.
9. **The reflection API is the safe path.** `Class:Reflection():GetProperty(name)` +
   `Property:IsValid()` + `Property:ImportText(...)`. Read
   `Mods/ConsoleCommandsMod/Scripts/set.lua` before inventing property access — it is a working
   reference for exactly this problem, shipped inside the loader.
10. **`um win drive` cannot focus this game.** Ghostrunner runs borderless fullscreen at
    2560x1152; Windows' foreground lock keeps `explorer` in front, so `focus` returns ok while
    every `click`/`key` fails with `target window is not in the foreground`. Screenshots still
    work. Menu navigation has to be done by hand.

## Assets

None. No new art, no pak changes, nothing redistributed.

## Cost and time

One session, about 40 minutes wall-clock, eleven script revisions, four crashes — all of them in
the loader script, none in the game's own code. No paid API calls. The largest cost was the loop
"edit Lua → relaunch a 35 GB game → read the log", roughly two minutes per iteration.

## Open questions

- Does the flag survive a level transition, or does the game rebuild the character each time? The
  2 s re-apply masks the answer; a cleaner implementation would hook character spawn.
- `SecondJumpVelocity` and `InitialCoyoteTime` are exposed the same way and were never tuned.
- `EJumpType::SuperJump` / `KunaiJump` / `HelJump` look like cut or ability-gated variants. If
  they are reachable by setting the same kind of flag, they would make a good follow-up note.
