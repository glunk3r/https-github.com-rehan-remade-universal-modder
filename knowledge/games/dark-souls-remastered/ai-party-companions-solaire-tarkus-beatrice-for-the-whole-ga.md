---
kind: game
title: AI party companions (Solaire, Tarkus, Beatrice) for the whole game, plus Andre's boxing moveset on fists
game: 'DARK SOULS: REMASTERED'
games_also: []
game_version: 'App ver 1.03.1, Steam 570940, DarkSoulsRemastered.exe 50,286,344 bytes (same build as the portal-gun note)'
platform: windows
engine: fromsoft
route: data
tools:
- UXM Selective Unpack 2.4.2.0
- SoulsFormats + Paramdex (from DS Map Studio's folder), .NET 8
- Seamless Co-op for DSR (only for its separate save, played offline)
- Python 3.8 (own Lua 5.0 and Havok 2015 tagfile tools)
anti_cheat: 'none client-side; FromSoftware servers are live, so offline only through Seamless Co-op (separate .co2 save)'
status: released
agents:
- Claude Code (Opus 5.5)
humans: []
date: '2026-10-15'
links: []
tags:
- companions
- npc-summons
- emevd
- lua-bytecode
- params
- msb
- havok-tagfile
- animation-retarget
- moveset
- tae
---
# AI party companions (Solaire, Tarkus, Beatrice) for the whole game, plus Andre's boxing moveset on fists

> Three of DSR's own friendly NPC summons travel with the player through all 17 maps: they follow, fight, warp
> to the player when they fall behind, scale by area and NG+, regenerate, and take orders from four items
> (Follow / Hunt / Regroup / Dismiss). In the same mod, all fist weapons use Andre of Astora's boxing attacks,
> retargeted onto the player's skeleton with self-written Havok 2015 tools. Data-only (params, MSB, EMEVD, Lua
> bytecode, anibnd/TAE), no DLL; everything was played and confirmed by the user in the real game.

## Setup
- DSR App ver 1.03.1 (Steam 570940), exe 50,286,344 bytes, Windows 10, unpacked with UXM Selective Unpack 2.4.2.0
  (loose files; no `.bdt` archives left).
- Seamless Co-op for DSR (`ds1sc_launcher.exe`, `SeamlessCoop/ds1sc.dll`), used solo and offline only for its
  separate save (`.co2`). Nothing in the mod depends on it; it does not interfere.
- SoulsFormats and Paramdex DS1R defs from DS Map Studio's install folder, referenced from a .NET 8 console project
  that generates every modded file from vanilla copies. Python 3.8 for the Lua and Havok tools. No C compiler.
- Release: 56 loose files, ~5 MB zip with a PowerShell installer that backs up each replaced file once.

## Route and why
Data-only. DSR's friendly NPC summons (Solaire, Tarkus, Beatrice, Leeroy, Mildred, Lautrec) are complete allies:
model c0000, gear (CharaInitParam), and per-character Lua AI whose default branch already **follows the host**
(`ApproachTarget(TARGET_LOCALPLAYER)` when no enemy is near, battle otherwise). The mod places a copy of each
companion in every map's MSB and drives them with EMEVD; behaviour changes are made by patching copies of their
compiled Lua. ModEngine2/me3 do not support DSR, and a DLL would have to coexist with Seamless's.

## How the game works (what we had to learn)
**Companions**
- Summonable NPC rows: Solaire 6540-6544, Lautrec 6590/6591, Beatrice 6520/6521, Leeroy 6550, Mildred 6530,
  Tarkus 6510 (NpcParam = NpcThinkParam id; CharaInit mostly the same id). Their AI scripts (`0065xx_logic.lua`,
  `_battle.lua`) are only in the luabnd of the maps where they appear; goal id = logic id = character id, and the
  map's `.luainfo` has one logic entry and one battle entry with that id (`.luagnl` lists the globals).
- **NpcParam.teamType is not the EMEVD/AI team enum.** It is NPC_TEMA_TYPE (Paramdex `DES/Tdfs/npcparam_teamtype.tdf`,
  Shift-JIS): 0 enemy, 1 strong enemy (bosses), 2 ally (talking NPC, does not fight), 3 angry ally, 4 ignore,
  5 decoy, 6 baby, **7 fighting ally** (all summons, DLC Sif). Team 7 fights but can be hit by the player and by
  each other; adding runtime `2004[02] Set Character Team Type = 2` (EMEDF "White Phantom") after enabling gives
  real summon behaviour: fights enemies, immune to the player and to other phantoms.
- A character is only processed while its MSB collision is loaded ("backread"). A companion anchored far away
  cannot be warped. `2004[29] Set Character Backread State(Removed=0)` makes it load within ~1-3 s; wait on
  `OR(4[07] backread, 1[00] 5 s)` before warping.
- `2004[42] Warp Character and Copy Floor` to the player needs a real dummy poly: -1 is silently ignored. c0000
  floor-level dummies: 11/236 at the feet, 234 (0,0,-1.17), 229 (-0.26,0,-1.33), 233 (0,0,1.00).
- **A disabled character reads as dead in `4[00]`.** Enable it before any death check, or an event that disabled
  it while the player was elsewhere will END for good (only a full save reload clears it; resting does not).
- Bonfires are characters (c1000, NpcParam 100000); the Firelink roof Giant Crow (351000) is team 0 with a passive
  AI, so allies attack it unless you move it to team 2. No talking character is on team 0 in any map.
- Some maps' event 0 END early (m18_01): insert your `2000[00]` init lines at the start of event 0.
- Event ids double as flags; check any id/flag you claim against every vanilla emevd (1AAB5990 is a vanilla event
  in 9 maps). Item lots give a "got it" flag in the 5000xxxx range.

**Lua 5.0 bytecode (DSR AI)**
- Header `1B 4C 75 61 50 01 04 08`: Lua 5.0, x64 (size_t 8). A small reader/writer round-trips all 298 vanilla
  scripts byte-identically, so patches can be made at the instruction level.
- Summon battle "activate" function: `GetEventRequest(0)` is read into a register first. Requests 10/9/8 make the
  NPC walk to a hard-coded point (boss fog); otherwise it follows the player (leash 20 m, engage enemies within
  10 m, arrive 1.2 m, walk inside 2.2 m). Solaire, Tarkus and Beatrice share this exact shape.
- Patches used (on renamed copies, so vanilla summons keep their scripts): rename the character id in all string
  constants and turn `GETGLOBAL GOAL_..._Battle / LOGIC_ID_...` into `LOADK <new id>`; arrive 1.2 -> 4 m and walk
  2.2 -> 6 m (stops crowding the player); leash and engage constants -> the event-request register, so EMEVD
  `2004[17] Request Character AI Command(value)` + `2004[20]` sets them (Follow = 12 m, Hunt = 50 m).
- Hunt (seek and destroy): the request-10 branch is rewritten in place (same length, no jump fix-ups): request 13
  -> if an enemy is detected within 15 m, jump to the battle code; else `ApproachTarget(TARGET_EVENT)`, the target
  that EMEVD sets with `2004[11] Set Character Event Target`. One EMEVD instance per enemy (entity ids assigned to
  enemies that had none) claims the party with a per-map lock flag while that enemy is alive, loaded and within
  45 m; release on death / >60 m / Hunt off / 20 s; 60 s cooldown for a target that was not killed.

**Scaling**
- `NpcParam.hp` is 0 for NPC humans; their HP comes from CharaInit vitality, so a percentage regen
  (`SpEffect.changeHpRate`, percent of max HP per `motionInterval`, negative heals; the bonfire effect is -100)
  is the one that works.
- Damage of NPC humans (weapons, spells) is player-style. SpEffect `*AttackPowerRate` (what the enemy NG+ effects
  7401-7415 use) did not noticeably change it; the player's own buffs (Power Within 1090) use `*AttackRate`.
  Most reliable of all: **scale their gear** with per-map CharaInitParam rows: weapon id = base + upgrade level
  (Tarkus' Greatsword +0 Asylum ... +10 Kiln), and for casters INT and the spell slots (NPC sorceries 13000-13070).
  Use a hand-written route-progress table: median enemy HP put Lost Izalith and Ash Lake among the easiest areas.
- NG+: copy the area's enemy NG+ SpEffect (most common GameClearSpEffectID of the map's enemies) into a companion
  effect with `*AttackRate = *AttackPowerRate`, else companion damage does not grow on NG+.

**Animations (Havok 2015 tagfiles)**
- DSR `.hkx` in anibnds are Havok tagfiles: nested sections with a big-endian u32 header (top bits 0x40 = leaf,
  size includes the 8-byte header) and a 4-char tag: TAG0 { SDKV "20150100", DATA, TYPE { TPTR TSTR TNAM FSTR
  TBOD THSH TPAD }, INDX { ITEM PTCH } }. Types and member offsets come from TNAM/TBOD (packed varints; TBOD flags:
  1 subtype, 2 pointer, 4 version, 8 size+alignment, 0x10 abstract, 0x20 members (name, flags, offset, type),
  0x40 interfaces, 0x80 attribute). Pointers, strings and hkArrays in DATA hold only an item index; ITEM entries
  are (type | flags << 24, offset in DATA, count). DS Map Studio's HKX2.dll only handles packfiles.
- Animations are `hkaSplineCompressedAnimation`: one block, per track a 4-byte mask (quantization byte: position
  bits 0-1, rotation bits 2-5, scale bits 6-7; position/scale flags 0x01<<axis static, 0x10<<axis spline; rotation
  0x0F static, 0xF0 spline). DSR uses 16-bit position/scale and **THREECOMP40** rotations: 40-bit little-endian,
  three 12-bit values `(v - 2047) * 0.000345436`, bits 36-37 = index of the dropped largest component, bit 38 = its
  sign; re-insert it at that index. Splines: u16 numItems, u8 degree, u8 knots[numItems + degree + 2], align 4.
  `floatBlockOffsets[0]` = data length. Root motion is `hkaDefaultAnimatedReferenceFrame.referenceFrameSamples`.
- Andre (c2640) has a 155-bone 3ds Max Biped rig ("L Clavicle", thighs under Spine); the player (c0000) uses
  Master > Lower_Root > Pelvis > thighs and Master > Upper_Root > Spine ("L_Clavicle"). Limb chains have nearly
  identical local frames; root/pelvis/spine/thighs do not, so a plain track remap twists the body. World-space
  retarget per mapped bone: `W_dst(t) = W_src(t) * inv(W_src_rest) * W_dst_rest`, back to local; unmatched bones keep
  their rest pose; root translation scaled by the rest root heights (1.057).
- Player fists are wepmotionCategory 42 (`a42.tae` in c0000.anibnd, animations `a42_xxxx.hkx` in
  c0000_a4x.anibnd), shared by Fists, Caestus, Claw, Dragon Bone Fist and Dark Hand. In player attacks the strike
  is where TAE event types 226 and 307 start together (NPC attacks use type 1 instead); 3201/3202 (5-7 s, no
  strike) are the Dark Hand grab. Andre's attacks are 3000-3007 in c2640.tae (type-1 windows).

## Build steps
1. Unpack with UXM; back up `event`, `map/MapStudio`, `param/GameParam`, `script`, `msg/ENGLISH`, `chr` and keep a
   vanilla copy of every file you will regenerate. Generate only from vanilla copies.
2. Params: per map and companion an NpcParam row (team 7, respawn on, no drops, NG+ companion effect, strength and
   regen SpEffects), a shared NpcThinkParam row (backhome distances 9999, logic/goal = new AI id, hearing 20 m),
   per-map CharaInit rows for gear scaling; order items = Green Blossom (260) copies with `refCategory` 2 pointing at
   1.5 s marker SpEffects, non-consumable, given by item lots once.
3. Lua: renamed + patched companion scripts added to every map luabnd (ids after the last script, before the
   luagnl/luainfo entries at 1000000+), plus their luainfo goal entries and luagnl globals.
4. MSB: one Enemy part per companion per map, cloned from a vanilla human NPC; entity ids for hunt targets.
5. EMEVD per map: companion events (enable, backread keep, white phantom team, wait loaded, warp, AI command),
   order events (`4[05]` marker SpEffect AND player in this map), hunt claim events, item hand-out; init lines at
   the start of event 0.
6. Moveset: decode Andre's attacks, retarget, encode as degree-1 splines (one control point per frame, knots
   0,0,1..n-1,n-1; static when constant), write into a copy of the player's `a42_xxxx.hkx` (append the new data and
   root-motion arrays at the end of DATA and repoint their ITEM entries, so nothing else moves and PTCH stays
   valid), pack into c0000_a4x.anibnd; time-warp the slot's own TAE events piecewise-linearly so the player's hit
   window lands on Andre's (damage, stamina and cancel rules stay the player's). Fists/Caestus scaling = 180.

## Verification
- Every generated file is read back and decoded (EMEVD printed with EMEDF names, params dumped, MSB parts listed,
  Lua disassembled, TAE dumped). The Lua writer round-trips 298/298 vanilla scripts; the TAE writer has 0 semantic
  differences (+8 bytes layout); the Havok decoder parses whole blocks and matches the rest pose on constant tracks
  (median 0.09 deg); encoded animations decode back within 0.1 deg / 0 mm.
- In game (user, offline via Seamless, playtests 1-14 + moveset slice and full set): debug banners (`2007[02]`,
  shown only for one instance) located each failing event stage; companions follow across Parish -> Firelink ->
  Catacombs, fight, are immune to friendly fire, scale acceptably ("Tarkus is perfect"), orders work (Hunt clears
  rooms on one floor), boxing moveset "perfect".
- Not verified: every map end to end, NG+ cycles in play, the S letter in the menu for value 180, Hunt in very
  vertical areas (they cannot path upstairs to targets; they give up after 20 s), online (never; do not).

## Gotchas
1. **Companions placed in a map never appear.** Cause: anchored on a far collision, not loaded, so warps fail.
   Fix: `2004[29]` Removed=0, wait for `4[07]`, warp with a real dummy poly.
2. **Warp to the player does nothing.** Cause: dummy poly -1. Fix: a real c0000 dummy (234/229/233).
3. **Allies ignore enemies / attack the player / hit each other.** Cause: NpcParam teamType is NPC_TEMA_TYPE, not
   the EMEDF team enum (2 = talking NPC). Fix: keep 7 and set runtime team 2 (White Phantom) with `2004[02]`.
4. **A map's companions never come back after you walk in from another map.** Cause: disabled reads as dead.
   Fix: enable before the death check.
5. **Damage multipliers do nothing on NPC humans.** Cause: `*AttackPowerRate` is the enemy path. Fix: scale gear
   (weapon upgrade, INT, spells) per map; also set `*AttackRate`.
6. **Hunt does nothing.** Cause: the AI only engages what it perceives. Fix: EMEVD event target + patched
   request branch (see above).
7. **Micro-stutter with ~200 hunt instances per map.** Cause: 4 conditions per instance every frame. Fix: wait on
   the cheap flag first, test the rest once with an uncompiled skip, sleep 0.8-1.6 s, restart.
8. **`2007[03]` status messages block the face buttons** until dismissed. Use none (or a banner).
9. **The Firelink crow gets attacked.** Cause: team 0 + passive AI. Fix: team 2 for NpcParam 351000.
10. **Python heredoc wrote a BEL byte into a C# path** (`\a` in `...\anim`), silently skipping a build step.
    Build paths with `Path.Combine(parts)`.
11. **An event printer showed ids off by one** (69000103 -> 69000104): a C# switch expression whose first arm is
    not cast to `object` types every arm as float. The data was right.
12. SoulsFormats in DSMapStudio's folder: use `X.Read(File.ReadAllBytes(path))`; the path overload crashes
    (DotNext 4.14 `Pointer.Pin` TypeLoadException).
13. **Seamless "Parchment of Deliverance" shows raw keys** (`ACTIONEVENT_EXONERATE`, `MODMSG_FAILEDEXONERATE`):
    its english.json lacks 3 keys the DLL uses. Not caused by mods.

## Assets
None generated; only DSR's own characters, gear, spells, AI and animations (Andre's), retargeted at build time.
The mod ships derived game files, so it is for the user's own installs only.

## Cost and time
One long day of sessions with 14 user playtests for the party and 2 for the moveset (slice, then full set).

## Open questions
- A route around stairs for Hunt (hand-placed waypoint regions near multi-floor targets).
- Whether a new wepmotionCategory number (Caestus-only moveset) loads; the shared category 42 was used instead.
- Exact scaling-letter thresholds for `correctStrength/correctAgility` in DSR's menu.
- Andre's 3.5 s flurry (3007) carries several hits; player slots have one hit window each, so it was skipped.
- Related: games/elden-ring/porting-dark-souls-remastered-enemies-into-elden-ring.md (Havok 2018 tagfiles,
  similar degree-1 spline encoding) and games/dark-souls-remastered/portal-gun-prototype-via-dinput8-proxy-dll-player-camera-and.md
  (same exe build, native route).
