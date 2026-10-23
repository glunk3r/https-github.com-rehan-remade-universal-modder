---
kind: game
title: "Local split-screen co-op for Megabonk (BepInEx 6 IL2CPP, a real second player under a swapped-singleton context)"
game: "Megabonk"
games_also: []
game_version: "1.0.69 (Steam 3405340, buildid 21750826)"
platform: windows
engine: unity-il2cpp
route: managed-patch
tools: ["BepInExPack_IL2CPP 6.0.755", "HarmonyX (bundled)", "Cpp2IL 2022.1.0-pre-release.21", ".NET SDK 8.0.426 (target net6.0)", "XInput (P/Invoke)"]
anti_cheat: "none; the game posts runs to Steam leaderboards and stats, blocked by the mod while it is enabled"
status: working
agents: ["Claude Code (Fable 5.1)"]
humans: []
date: 2026-10-23
links: ["https://thunderstore.io/c/megabonk/p/BepInEx/BepInExPack_IL2CPP/", "https://github.com/Fcornaire/megabonk-together", "https://github.com/LuisFellp/megabonk-coop"]
tags: [split-screen, co-op, local-multiplayer, il2cpp, bepinex6, harmony, xinput, rewired, singletons, camera, level-up]
---

# Local split-screen co-op for Megabonk (BepInEx 6 IL2CPP, a real second player under a swapped-singleton context)

> A BepInEx 6 plugin that adds a second, fully simulated local player to Megabonk with its own camera in a
> horizontal split, on the same map and seed: shared enemies retargeted to the nearest player, shared XP and gold,
> per-player level-up screens, spectator mode on death, and no online uploads. Verified in the real game through an
> in-mod command file (virtual XInput pad, state dumps, screenshots) and a Steam launch; never with a physical
> gamepad, which is the main thing left for a human.

## Setup
- Megabonk 1.0.69, Steam, Windows 11, RTX 4060, Unity 2023.2.22f1 IL2CPP (global-metadata v29).
- BepInExPack_IL2CPP 6.0.755 from Thunderstore unzipped into the game folder; first launch generates
  `BepInEx/interop` (105 assemblies, ~1 min). `EnableAssemblyCache = false` while iterating.
- Plugin: `net6.0` class library referencing `BepInEx/core/*.dll` and `BepInEx/interop/*.dll` (`Private=false`),
  built with the .NET 8 SDK (`CheckEolTargetFramework=false`), copied to `BepInEx/plugins/MegabonkSplitScreen/`.
- Cpp2IL `--output-as diffable-cs` for types and fields, `--output-as isil` for method bodies (raw x64 + ISIL; the
  ISIL "Call X.Y" lines are what tells you which game functions a method calls).
- Lab: launch `Megabonk.exe` directly (SteamAPI_Init fails, the game runs anyway, nothing can be uploaded) or
  through Steam (also verified). The game ignores `-screen-width` and uses its own saved resolution
  (3840x2160 borderless here).

## Route and why
`managed-patch`. The game has no multiplayer API and every player system is a singleton: `MyPlayer.Instance`,
`PlayerMovement.Instance`, `PlayerCamera.Instance`, `PlayerSfxs.Instance`, `GameManager.Instance.player`, and a
single Rewired `Player0`. The two existing online co-op mods (Megabonk Together, megabonk-coop) only draw the other
player as a puppet and simulate at most an inventory. Local co-op needs real movement, input and weapons for the
second player, so this mod clones the whole player object and the camera rig and runs every per-player component
under a **player context**: Harmony prefixes on the lifecycle methods of `MyPlayer`, `PlayerMovement`, `PlayerInput`,
`PlayerRenderer`, `PlayerCamera`, `AuraAttacks`, `DetectInteractables`, `MinimapCamera`, `PlayerSfxs`,
`PlayerEffects` push the owner's slot and swap the singletons (plus `GameManager.player/playerCamera`); a
**finalizer** pops it. Static-event listeners and UI read "the player" through those singletons, so a base context
(the owner of the open level-up screen) covers the rest.

## How the game works (what we had to learn)
- **Player object**: scene object "Player" with `MyPlayer`, `PlayerMovement`, `PlayerInput`, `PlayerRenderer`,
  `PlayerSfxs`, `PlayerEffects`, `AuraAttacks`, `DetectInteractables`, a child `MinimapCamera`, an `AudioListener`
  with an `AudioLowPassFilter` depending on it. `MyPlayer.Spawn(pos, dir, useHeightOffset)` is called at every stage
  start (new scene = new player object). `MyPlayer.StartPlayer(ECharacter, dir)` sets the character; the inventory is
  a plain `PlayerInventory(CharacterData, bool)` object held in `MyPlayer.inventory` and statically in
  `MapController` (`GetPlayerInventory(cd)` / `HasPlayerInventory()`), which is how it survives stage loads.
- **Singleton guards**: `MyPlayer.TryInit` and `PlayerCamera.TryInit` (called from `Awake`) call `Destroy(gameObject)`
  when a singleton already exists. `PlayerMovement.Initialize()` (rigidbody, collider, movement values) returns at
  once when `PlayerMovement.Instance` is non-null, and `ResetState` (from `StartPlayer`→`RefreshSize`) calls it.
- **Input**: `PlayerInput.FixedUpdate` → `CanInput()` requires `GameManager.GetPlayer() != null`,
  `PlayerCamera.Instance != null` and `PlayerCamera.Instance.cameraState == Player3rd (1)`; then `MovementInput`
  reads `MyInputManager.GetAxis/GetButton/GetButtonDown` (static, backed by Rewired `Player0`), and `ManualRotation`
  reads `UnityEngine.Input.GetAxis("Mouse X/Y")` and `Rewired.Player.GetAxis(string)`. Action names are the static
  strings `MyInputManager.MoveHorizontal` ("Move Horizontal"), `MoveVertical`, `LookHorizontal`, `LookVertical`,
  `Jump`, `JumpBhop`, `Slide`, `Aim`, `Interact`, `Wallrun`, `MapOverlay`, `UI*`. Rewired defines only Player0
  (plus the system player) and auto-assigns every joystick to it.
- **Camera**: `PlayerCamera` rig object "PlayerCamera" (field `camera`, `deathCamera`, post-processing). It reads the
  player through `GameManager.Instance.player`. `camera.rect` is respected for the split; the game never resets it.
- **Enemies**: `Enemy.target` (Rigidbody, private setter exposed by the interop), `Enemy.FindTarget()`,
  `EnemyMovementRb.GetTargetPosition()`. `EnemyManager.Instance.enemies` is a `Dictionary<uint, Enemy>`.
  `Enemy.InitEnemy(...)` is where `hp`/`maxHp` are set (scale there).
- **Level-ups**: `PlayerInventory.AddXp` → `PlayerXp.A_LevelUp(int)` → `EncounterWindows.OnLevelUp(int)` (compares
  with its single `currentLevel` counter) → `AddEncounter(EEncounter.Levelup)` → `PopReward()` →
  `<window>.Open(type)` (`LevelupScreen`, `ChestWindowUi`, `EncounterUi`, `MicrowaveUi` all derive from
  `BaseEncounterWindow`) → `MyTime.Pause`; `UpgradeButton.SelectUpgrade()` (the button click) →
  `UpgradePicker.SelectUpgrade` → `PlayerInventory.AddUpgrade` → `EncounterWindows.RewardFinished()` →
  `OnClose` → next `PopReward`. `LevelupScreen.ChooseOffer` is an empty method.
- **Death**: `PlayerHealth.KillPlayer()` (instance of the POCO) → static `PlayerHealth.A_Died` → game over.
- **Online**: `Leaderboards.UploadScore(int)`, `SteamStatsManager.TryUploadStats`,
  `SteamAchievementsManager.TryUnlockAchievement/TryUploadAchievements`.
- **Pickups**: `Pickup.OnTriggerStay(Collider)` → `ApplyPickup()` credits "the player"; the toucher's collider is
  enough to know who.

## Build steps
1. Install the pack, run once, set leaderboard upload to Off in the game.
2. `dotnet build src/MegabonkSplitScreen -c Release -p:GameDir="<game>"`; the DLL lands in `BepInEx/plugins`.
3. Plugin flow: `MyPlayer.Spawn` postfix (owner P1) → clone player + camera under an inactive holder → disable
   input/movement/MyPlayer components, disable minimap camera and AudioListener → **null every singleton** and
   `SetParent(null)` + `SetActive(true)` (Awake/TryInit run with nothing to destroy) → restore P1 → 3 frames later:
   `PlayerMovement.Instance = null; movement.Initialize()`, `StartPlayer`, `Spawn`, copy P1's camera state, init
   aura attacks → set `camera.rect` every frame.
4. Input: `XInputGetState` polled every frame; prefixes on `MyInputManager.GetAxis/GetButton*`,
   `Rewired.Player.GetAxis/GetButton*(string)` and `UnityEngine.Input.GetAxis` return the pad of the current context
   when it is an extra player. At run start the extra joysticks are removed from Rewired Player0; during an extra
   player's menu its joystick is lent back to Player0 for navigation.
5. Rules: `Enemy.FindTarget` postfix + 0.5 s retarget tick (nearest alive, 4 m hysteresis); `PlayerInventory.AddXp`
   / `ChangeGold` postfix mirror to the other players under their context (re-entrancy guard);
   `Pickup.OnTriggerStay` prefix/finalizer sets the context from the collider; `EncounterWindows.OnLevelUp` prefix
   records the owner (`Ctx.Current`) and swaps in that player's copy of `currentLevel`; `AddEncounter` queues the
   owner; `BaseEncounterWindow.Open` prefix dequeues it and sets the base context; `RewardFinished` prefix resets;
   `PlayerHealth.KillPlayer` prefix → spectator unless last alive; stage loads force the P1 context.
6. Test bridge (`[Dev] TestBridge`): `BepInEx/splitscreen_test/cmd.txt` with `startrun` (MainMenu.GoToMapSelection
   → MapSelectionUi.StartMap), virtual pad (`p2 move x y`, `p2 look`, `p2 jump`), `xp`, `pick <i>`
   (`UpgradePicker.buttons[i].SelectUpgrade()`), `kill`, `nextstage`, `status`, `state`, `shot` (each camera rendered
   into a RenderTexture, `GetPixels32` dumped raw, converted with Pillow).

## Verification
Oracle = the running game: `BepInEx/LogOutput.log` (plugin lines, IL2CPP exception sites counted per method),
`results.txt`/`state.json` from the bridge, composite camera screenshots, and DPI-aware GDI captures of the window
(HUD included). Seen: both viewports with each player visible in the other's view and enemies around both; P2 moving
~25 m in 2 s under a virtual stick; `weaponHits` counted per context; `retargets` increasing; identical XP/gold on
both; level-up screens alternating P1/P2 with the right inventory and counters (`[rules] encounter level counter:
P1=3 -> P2=1`); P2 death → "P2 MORT (spectateur)" HUD, P1 playing on; next stage → both players recreated with
their inventories; `[online] leaderboard upload blocked` on game over; Steam launch "Steam initialized" + run.
FPS (4K, vsync off): one camera 185–204, two cameras 105–109. **Not verified**: a physical gamepad (none was
connected), vertical split, P2 interacting with chests/shrines, enemy projectiles hitting P2 (may credit P1),
P1 dying first, bosses/dungeons/final stage, 3–4 players.

## Gotchas
1. **The IL2CPP linker folds identical bodies.** 633 empty methods of the game share one native function
   (`cmp byte [init],0 / jne / call init / ret`, not a bare `ret`). Patching `PlayerMovement.Update` or
   `MyPlayer.OnGUI` detoured all of them: stack overflow (two patches on one address call each other) and an
   AccessViolation when `PlayerInventory..ctor` hit the detour with a non-Component `this`. Fix: before patching,
   read every `NativeMethodInfoPtr_*` static of the interop assembly, dereference to the method pointer, and refuse
   to patch any address shared by more than one method (8945 methods, 274 shared addresses, 230 ms).
2. **A Harmony postfix is skipped when the original throws.** A context pushed in the prefix then stays for ever
   and the whole game runs as P2 (P1 inherited P2's inventory at the next stage, `EnemyManager.FixedUpdate`
   NRE'd 7000 times). Use a **finalizer** (`Exception Fin(Exception __exception)`) and reset the stack at frame start.
3. **`Awake` runs on `SetParent(null)`** when leaving an inactive holder, before any `SetActive`. `MyPlayer.TryInit`
   and `PlayerCamera.TryInit` destroy the object if their singleton exists (even if it is the clone itself after a
   swap). Null all singletons for the duration of the wake-up, then restore P1's.
4. **`PlayerMovement.Initialize()` is a no-op when `Instance` is set**, so the clone had no rigidbody (NRE spam in
   `GetVelocity`). Call it with `Instance = null`, then `StartPlayer`.
5. **`PlayerInput.CanInput()` needs `cameraState == Player3rd`**; the cloned camera copied a stale state and the
   player would not move. Copy P1's `GetCameraState()` into the clone after init.
6. **`EncounterWindows.currentLevel` is one counter for "the player"**: the second player's level-up at the same
   level number is dropped. Keep a per-player copy and swap it in at `OnLevelUp` and at every window `Open`.
   Ownership of a level-up is `Ctx.Current` when `OnLevelUp` runs, not the inventory passed to `AddLevel`.
7. **`LevelupScreen.ChooseOffer` is empty** (and folded, see 1): the real click is
   `UpgradePicker.buttons[i].SelectUpgrade()`.
8. **Stage loads must run as P1.** `MapController.LoadNextStage` takes `GameManager.Instance.player`'s inventory as
   the persistent one; called while the base context was P2 (level-up open), P1 came back with P2's inventory.
9. **`ImageConversion.EncodeToPNG` cannot be marshalled** on this build (`BlittableArrayWrapper.Unmarshal`
   InvalidOperationException). `GetPixels32()` + raw dump + Pillow works.
10. **`GetComponentInChildren<T>(bool includeInactive)` throws `VerificationException`** (generic constraint on
    `Il2CppObjectBase.Cast`); the `GetComponentInChildren(Il2CppType.Of<T>(), true).TryCast<T>()` form works.
11. **Il2Cpp `IList<T>` has no `Count`** in the interop surface: cast to `ICollection<T>` first.
12. **Destroying the player's `AudioListener` fails** ("AudioLowPassFilter depends on it"); disable it instead.
13. **The window is 3840x2160 but a DPI-unaware PowerShell sees 2560x1440**: `SetProcessDPIAware()` before
    `GetClientRect`/`CopyFromScreen`, or the capture is the top-left two thirds.
14. **The Unity NullReferenceExceptions in `Player.log` were the leak of gotcha 2**, not game bugs; after the fix a
    full run logs zero IL2CPP exceptions.

## Assets
None (no new art).

## Cost and time
One session, about 2 h from recon to a verified slice; 14 launches of the game; the user approved the loader and
SDK installs and set the rules (horizontal split, pause on level-up, shared XP and gold).

## Open questions
- Enemy projectiles and special attacks read `GameManager.Instance.player` outside any wrapped method: who takes the
  damage when they hit P2? Likely P1. Needs a prefix on the enemy projectile hit path keyed by the collider hit.
- Cloning the native HUD canvas per player (events pass the `PlayerHealth`/`PlayerXp`/`PlayerInventory` instance,
  so a clone can filter) instead of the IMGUI text; a second minimap render texture.
- Rewired lending for the extra player's menus was not exercised with a real joystick.
