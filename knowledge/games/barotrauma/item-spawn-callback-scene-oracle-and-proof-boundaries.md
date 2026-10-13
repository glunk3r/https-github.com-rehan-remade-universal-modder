---
kind: game
title: "Barotrauma item placement: native spawn callback plus later Scene is the oracle"
game: "Barotrauma"
games_also: []
game_version: "1.13.4.0, Steam build 23799131; LuaCs 1.0.116; isolated storage-instrumented dedicated copy"
platform: windows
engine: dotnet
route: loader-api
tools: ["LuaCs/Luatrauma", "C# EntitySpawner queue", "Mono.Cecil", "Core Executor", "headless dedicated fixture"]
anti_cheat: "Owned isolated local dedicated server; no external clients, anti-cheat or ownership bypass"
status: in-progress
agents: ["Codex (GPT-6)"]
humans: ["jkjkj2805"]
date: 2026-10-13
links: ["https://github.com/FakeFishGames/Barotrauma", "https://github.com/evilfactory/LuaCsForBarotrauma", "https://github.com/rehan-remade/universal-modder/blob/main/knowledge/techniques/oracles-how-agents-know-a-mod-works.md"]
tags: [entity-spawn, postcondition, identity, headless, isolation, idempotency, proof-boundaries]
---

# Barotrauma item placement: native spawn callback plus later Scene is the oracle

> A default-off private adapter placed one empty vanilla metal crate through the existing Core Executor and native spawn queue. An isolated headless game proved the exact callback identity in later Scene revisions and suppressed a duplicate command. That is real native mechanical proof, not an autonomous story, player-visible delivery or a publicly available item-creation mod.

## Setup

Native API review was pinned to Barotrauma/DedicatedServer 1.13.4.0 with LuaCs 1.0.116 on Windows; the original game identification was Steam build 23799131. The candidate was compiled against reviewed installed/publicized references and statically inspected with Mono.Cecil. The observation wire remained `baro6bobs1.1`; the new bounded capability had its own `baroitem1.1` ABI.

Only disposable independent regular-file copies, a private profile/cache/save and an isolated Core database were used. The installed native DLL, accepted bridge/config and real saves were untouched. This retrospective note contains no game files, binary patches or private implementation source. Credit Barotrauma and LuaCs/Luatrauma maintainers for the native runtime and loader, and Universal Modder's oracle taxonomy for separating headless and client proof.

## Route and why

Use the actual game's spawn queue rather than direct `Item` construction or a second module-owned executor. A tool-blind Creator describes the desired effect; the existing Core Executor checks the legal capability's honest effect and exact current evidence. A generic request for a story object does not mean an empty crate is adequate.

The hand was `barotrauma.place_item_in_compartment.v1`, disabled by default, guarded, approval-required, non-reversible and `safe_retry=false`. Its only allowlisted prefab was `metalcrate`, with a canonical effective-definition fingerprint. It supplied no cargo, text, ownership, reward, mission, provenance or hidden history. The fixture cannot be used as an exact substitute when those properties are essential.

## How the game works (what we had to learn)

The reviewed overload was `EntitySpawner.AddItemToSpawnQueue(ItemPrefab, Vector2 position, Submarine sub, float? condition, int? quality, Action<Item> onSpawned)`. Its positions are submarine-local: pairing `Hull.Position` with the exact `Hull.Submarine` matters. The reviewed native path creates the item, emits the spawn network event and then calls the callback with that exact item. A server network-event call does not prove an authenticated client received or rendered it.

The native hand takes an exact current destination Hull, not a free-text room or external coordinates. Dispatch requires current world/session/epoch, transport generation, nonce/correlation, eight-second admission expiry, explicit arm, the pinned prefab and a dry/fire-free main-submarine Hull. The conservative destination predicate also required at least 200 by 120 local units and no item/body within 100 units of the center. Current native legality is advertised as at most 16 exact Hull refs and rechecked at dispatch.

The bounded Scene's partial semantic-device list cannot itself prove an unobstructed room center. This was demonstrated by a genuine native rejection. The solution was current native legality advertisement, not weakening the clearance guard or treating missing items as an empty floor.

The callback identity is retained as a runtime object token. The existing bounded Scene prioritizes created refs, so the newly created exact object can later be observed. SUCCESS requires a newer committed Scene containing that same new item in the exact destination Hull, matching native correlation and empty-container evidence. Queue acceptance, a similarly named pre-existing item or a forged receipt cannot satisfy it.

Later `current_observations` keep the exact item, current Hull, literal custody and source links. Created-empty is a historical creation fact; current contents and ownership remain UNKNOWN. Absence from a partial Scene does not prove destruction. A lost epoch/GAP clears current binding; the item is never rebound by name or prefab in a new world.

## Build steps

The bridge/harness is private; these are requirements for independently implementing the same bounded experiment.

1. Review the installed queue overload and replication/callback order; pin the exact effective prefab definition and avoid mutating observation getters.
2. Isolate native profile/cache/save and host database. Inspect the actual storage bootstrap before launching, not only configured savepath or environment overrides.
3. Advertise exact current safe destinations from native checks; pass only immutable typed commands to the update thread. Keep reflection expressions, console RPC and arbitrary prefabs out of the action surface.
4. Submit one native queue entry and retain its callback object. Preserve typed execution/attempt/correlation identity through native receipt and later Scene commit.
5. Make the Core ActionResult depend on the exact later Scene postcondition. Distinguish zero-dispatch rejection from an attempted but unverified/uncertain spawn.
6. Reissue only the same Executor identity to test duplicate suppression, not a second native command. Then inspect at least two later same-scope observations of the same item.
7. Stop only owned processes and compare protected install/config/save hashes before and after. Test client visibility separately under a new bounded authorization.

### A three-stage placement checklist

This checklist restates the oracle in a form an independent bridge author can instrument. It is not a new API or another spawn result.

| Stage | Record/check | Insufficient substitute |
|---|---|---|
| Admission | Current safe exact Hull, scope, prefab fingerprint and execution identity | A room name or an apparently empty partial Scene |
| Native callback | The exact newly created item and correlation | Queue acceptance or any item with the same prefab |
| Later Scene | Newer committed observation of that same item in the exact Hull, matching receipt and empty-container evidence | A callback alone or a client screenshot of a different crate |

Count queue submissions as well as objects when replaying the execution identity. Treat client replication, discovery and pickup as separate future gates; this headless oracle cannot establish them.

## Verification

**LIVE-PROVEN mechanical headless fixture:** one real Core dispatch and one native spawn produced a successful exact ActionResult. The callback item appeared in Scene revision 4 and remained the same exact identity at revisions 5 and 6. The repeated Executor identity returned duplicate suppression; command/native counts stayed one. No authenticated player, provider generation or autonomous Creator selection was used.

**LIVE-PROVEN negative boundary:** a center obstruction caused native rejection with zero creation calls, no execution and no uncertainty. An earlier Scene-revision race also rejected before creation. These failures are useful oracle evidence, not successful placement.

**TEST-PROVEN:** focused real-Core/mock-native tests covered exact identity persistence, durable deduplication, illegal destinations/prefabs, queue-only receipts, pre-existing items, forged correlation, epoch/GAP loss and no retry. Static verification covered the exact native overload, sole queue submission site, definition fingerprint and callback ordering. Tests and IL checks do not establish client rendering.

**Isolation qualification:** environment APPDATA overrides did not relocate every native storage location. The reviewed `SaveUtil` static bootstrap used Windows KnownFolder directly and could touch Workshop cache during startup. Exactly two storage-root instruction substitutions were made only in authorized private lab copies; all other 27,558 method bodies remained unchanged, original copies were retained and actual relocated cache creation was checked. This is a storage-instrumented native stand, not proof that an untouched dedicated startup is harmless to a real profile, and not an installed-game modification. No protection bypass or game code is published.

**UNKNOWN/NOT PROVEN:** client-visible replication, player discovery, pickup, current contents/ownership, meaningful non-fixture prefabs, cross-restart identity and an interesting autonomous Creator-to-Executor-to-game-to-next-Creator story. Synthetic situation fixtures and valid planned intent must not be reported as such a live story. The crate cannot retroactively manifest an unrelated earlier model idea.

## Gotchas

1. **A private savepath still touches the real Workshop cache.** **Cause:** native bootstrap uses Windows KnownFolder independently of the configured savepath. **Fix:** review all storage roots and prove isolation before launch; the recorded stand used separately authorized scratch-only relocation, not silent edits to installed game files.
2. **Scene changes during ACK delivery reject a safe destination.** **Cause:** unconditional equality to an older source revision confuses unrelated updates with lost scope. **Fix:** admit a positive, non-future source within bounded expiry, while rechecking every actual destination and scope guard; still require later exact Scene proof.
3. **A room is chosen from incomplete device observations.** **Cause:** partial Scene coverage was treated as center clearance. **Fix:** have native current legality attest exact destinations, and repeat its predicate at dispatch.
4. **The queue call is mistaken for manifestation.** **Cause:** implementation reports acceptance rather than world state. **Fix:** capture exact callback identity and require it in a later committed Scene before ActionResult SUCCESS.
5. **Mechanical PASS is sold as narrative success.** **Cause:** a valid effect, a saved plan and a synthetic continuation are conflated. **Fix:** report technical execution, client/knowledge evidence and human creative quality separately; the latter can remain unproven.

## Assets

The experiment used a vanilla prefab from the operator's own installation. No prefab XML, game binary, extracted asset, private campaign context or entity identifier is distributed.

## Open questions

A client-visible bounded acceptance is still needed, followed by a separately judged useful autonomous manifestation and continuation. No new game, model or paid service was run while preparing this note.

Related field notes: [NPC movement postconditions](private-npc-frontend-and-native-movement-postconditions.md); [effect versus engagement evidence](../../techniques/authored-effects-are-not-player-agency-evidence.md).
