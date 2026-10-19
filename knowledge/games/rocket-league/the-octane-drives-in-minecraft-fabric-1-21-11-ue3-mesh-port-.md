---
kind: game
title: 'The Octane drives in Minecraft (Fabric 1.21.11): UE3 mesh port, client-authoritative vehicle and RL physics'
game: Rocket League
games_also:
- Minecraft
game_version: 'Rocket League (Epic build, 2026-10): UE3 packages Ver 868/32, Engine 10897; Minecraft 1.21.11, Fabric Loader 0.19.5'
platform: windows
engine: unreal
route: reimplementation
tools:
- umodel (UE Viewer build 1590, -game=rocketleague)
- Fabric Loom 1.18.4 / Gradle 9.7.1 / JDK 25
- JUnit 5 (headless physics oracle)
anti_cheat: EasyAntiCheat
status: working
agents:
- 'opencode (big-pickle)'
humans:
- Jack
date: '2026-10-19'
links:
- https://wiki.rlbot.org/v5/botmaking/useful-game-values/
- https://rl.source.gs/physics/
- https://wiki.rlbot.org/v5/botmaking/jumping-physics/
tags:
- minecraft
- fabric
- unreal
- ue3
- umodel
- psk
- vehicle
- physics
---
# The Octane drives in Minecraft (Fabric 1.21.11): UE3 mesh port, client-authoritative vehicle and RL physics

> The Rocket League Octane, ported into Minecraft Java 1.21.11 as a Fabric entity: its real mesh and
> albedo converted out of the user's own install with umodel, rendered through a custom
> vertex-emitting renderer, and driven with Rocket League's measured physics (throttle curve, 2300
> uu/s boost cap, jump/dodge, 3 s boost tank). Rocket League is **never launched or hooked**
> (EasyAntiCheat); only its cooked packages are read offline. Verified in a real client by an
> automated test that drives, boosts, jumps, and screenshots the car.

## Setup
- Rocket League from Epic, `C:\Program Files\Epic Games\rocketleague`, EasyAntiCheat present. Offline
  only: the `.upk` packages in `TAGame\CookedPCConsole` were read with UE Viewer (umodel) build 1590.
  `-game=rocketleague` is required; auto-detect dies with a "bad allocation" on the name table. The
  mesh package is `Body_Octane_SF.upk` (Ver 868, Engine 10897).
- Host: Minecraft 1.21.11, Fabric Loader 0.19.5, Fabric API 0.141.6+1.21.11, Mojang official
  mappings, `splitEnvironmentSourceSets()`.
- Toolchain gotcha: Loom 1.18 **requires Gradle on JDK 25** even though the compile target is Java 21.
- Node fakes used by the AI-agent CLI (scan/backup/kb) are not part of the mod.

## Route and why
- **reimplementation** (pattern "port the content"). Rocket League runs EasyAntiCheat, so injecting
  or hooking is off the table; a passthrough/bridge was rejected for the same reason. The guest is
  read offline only.
- GeckoLib was tried and dropped: 5.4.5 for 1.21.11 parses a `poly_mesh` but does not render
  arbitrary triangle meshes. The working path is a plain `EntityRenderer` that emits the mesh itself.

## How the game works (what we had to learn)
- Rocket League is Unreal Engine 3; assets are standard cooked `.upk` packages (magic `C1 83 2A 9E`)
  with bulk texture mips in shared `Textures*.tfc`. umodel reads both.
- umodel exports the SkeletalMesh as a PSK: points, wedges (point + UV), triangles, bones, and
  per-triangle material indices. The Octane body is 20697 vertices / 28478 triangles across 2
  materials; the material *names* come back generic (`material_0`), which matters below.
- Textures: `Body_Octane_Bevel_RGB` (albedo, 1024x1024) and `Body_Octane_Bevel_N` (normal map).
- Rocket League units are Unreal units: **1 uu = 1 cm**, physics at 120 Hz. The Octane hitbox is
  ~118x84x36 uu, which is why the exported mesh is only ~1.4 blocks long - that is correct, RL cars
  are small.
- Movement is **client-authoritative**. The rider's client simulates the vehicle and sends
  `ServerboundMoveVehiclePacket`; the server's `ServerGamePacketListenerImpl.handleMoveVehicle`
  simply applies the reported position, and only when `rootVehicle.getControllingPassenger()` is the
  player and the vehicle is the one they last mounted. This is the single most important fact for a
  rideable Fabric entity: do not also simulate it on the server.
- Vanilla vehicle input reaches the server as a `Input` record (`forward/backward/left/right/jump/
  shift/sprint`) via `ServerboundPlayerInputPacket` -> `ServerPlayer.getLastClientInput()`, but for a
  client-authoritative car that hook is not needed.
- 1.21.11 render pipeline: `EntityRenderer<T, S>` with `submit(S, PoseStack, SubmitNodeCollector,
  CameraRenderState)`; custom meshes go through
  `SubmitNodeCollector.submitCustomGeometry(PoseStack, RenderType, (pose, vertexConsumer) -> ...)`.
  Render types moved to `net.minecraft.client.renderer.rendertype.RenderTypes`
  (`entityCutoutNoCull(Identifier)`). `EntityRenderState` has **no yaw**, so carry it yourself.

## Build steps
1. Extract the mesh and albedo, offline, into a private dir (never into the repo):
   `umodel -game=rocketleague -notex export ... Body_Octane_SF.upk`, then the textures by name (see
   the gotchas on `-notex` and one-name-per-line).
2. `scripts/octane_export.py` reads the PSK + albedo and writes a compact `octane.bin` (positions,
   normals, UVs, indices, material ids), an RGBA albedo PNG, and `octane.json`, into
   `<devInstance>\config\octane\`.
3. The Fabric mod registers `octane:octane` and a client `EntityRenderer` that loads `octane.bin`,
   makes a `DynamicTexture` from the PNG, and emits triangles via `submitCustomGeometry`.
4. `scripts/octane_audio.py` synthesises engine/boost/jump Ogg Vorbis (no game audio shipped).
5. Physics lives in `OctanePhysics` (pure Java, RL units) and is sub-stepped at 120 Hz inside the
   20 Hz entity tick. `gradlew test` runs the headless oracle; `gradlew runClient -Pautotest` runs the
   in-game oracle.

## Verification
- Slice 1 (render): summon the car in front of the player on a flat world, screenshot with and
  without it. `octane_with.png` has a coherent albedo-orange blob (3748 px); `octane_without.png` is
  0; the diff isolates a 5170 px blob.
- Slice 2/3 (drive): hold forward then forward+left, then boost, then jump.
  `boost speed=2300.000 uu/s tank=0.183` (the RL cap), `jump apex=236.484 uu`, and the drive
  screenshot/diff isolate the moving car.
- Slice 3 (physics): `gradlew test` - 6 headless checks: throttle-only top speed 1410 uu/s, boosted
  top speed 2300 uu/s, a full tank lasts 3.0 s, jump apex matches an independent RLBot
  impulse/hold/gravity integration within 5%, a parked car cannot yaw, a double jump gains height.
- NOT verified: multiple simultaneous riders, cheats/anti-cheat interaction (out of scope), and the
  normal map (see limits).

## Gotchas
1. **The car is invisible with the correct texture and geometry loaded.** The real cause was two
   different things stacked. First, the albedo PNG was saved as **RGB**: with a cutout render type a
   zero alpha channel discards every fragment. **Fix:** export the albedo as **RGBA** (alpha 255).
2. **Still invisible after fixing the texture.** **Cause:** `submitCustomGeometry` stores the
   `PoseStack` you pass and draws the geometry **later** (it is deferred), so wrapping the submit in
   `pose.pushPose(); pose.mulPose(...); ...; pose.popPose()` corrupts the stored pose before it is
   used and the vertices land wrong/off-screen. **Fix:** hand the dispatcher's pose over untouched
   and bake any rotation into the vertex positions and normals yourself. (An earlier note claimed
   `CustomFeatureRenderer$Storage.add` snapshots the pose so push/rotate/pop is safe - it is not.)
3. **The car does not render at all until it is on screen.** **Cause:** `submit` is frustum-culled,
   so the mesh only loads on the first frame the entity is visible, and `Screenshot.grab` is async -
   a screenshot taken the same tick the camera turns to the car can capture a frame without it.
   **Fix:** aim the camera at the car every tick and settle several ticks before capturing.
4. **Physically-correct handling feels wrong / jump too high.** **Cause:** RL physics run at 120 Hz;
   integrating at Minecraft's 20 Hz inflates a jump (293 uu vs 232). **Fix:** sub-step the model at
   120 Hz inside the entity tick.
5. **The car slides/floats and the boost never engages.** **Cause:** self-contradictory movement.
   Because vehicles are client-authoritative, simulating on both sides fights the server's applied
   position. **Fix:** simulate on the client while ridden (`getControllingPassenger() instanceof
   Player`), and on the server only when parked.
6. **The in-client oracle reads zeros for speed/jump.** **Cause:** the test held a reference to the
   *server* entity while the physics runs on the *client* entity (and an even earlier version kept a
   stale reference to a killed entity). **Fix:** resolve the client-side entity (near `mc.player`)
   and null the reference between test phases.
7. **umodel crashes exporting the mesh with textures**, on a referenced `Startup.upk` texture.
   **Fix:** export the mesh with `-notex`, then the textures by name. Never pass two object names on
   one umodel command line - the extra names are read as packages.
8. **GeckoLib ignores your mesh.** It parses `poly_mesh` and renders nothing. Use the vanilla
   custom-geometry path instead.
9. **Audio:** RL's audio is Wwise `.bnk`/`.wem`, not UE sound packages, and decoding it needs extra
   tooling - and you should not ship it. **Fix:** synthesise the engine/boost/jump yourself and play
   looping instances whose pitch tracks speed. (There is no `ffmpeg`/`vgmstream` on a bare Windows
   box; `uv pip install soundfile` gives an Ogg Vorbis writer.)

## Assets
- Mesh + albedo converted from the user's own install (not shipped). Normal map extracted but unused
  (the vanilla entity pipeline has no normal-map input).
- Engine/boost/jump audio **synthesised** with numpy + `soundfile` (`scripts/octane_audio.py`).
- Boost jets are vanilla flame particles; the boost meter is a Fabric `HudElement`.

## Cost and time
- One long agent session. No API spend (no fal key configured; audio synthesised locally).

## Open questions
- Apply the normal map (needs Iris/a shader) and the second material (umodel returns unnamed
  materials and only one albedo was exported).
- Independent wheel spin (the wheels are baked into the body mesh).
- Port a non-default skin from another `.upk`; add RL dodge/air-roll tuning as separate curves.
