---
kind: game
title: "Barotrauma NPC frontend and movement: exact targets, local knowledge and physical postconditions"
game: "Barotrauma"
games_also: []
game_version: "1.13.4.0, Steam build 23799131; LuaCs 1.0.116; AI NPCs 1.6 reviewed"
platform: windows
engine: dotnet
route: loader-api
tools: ["LuaCs/Luatrauma", "AI NPCs selector", "C# assembly plugin", "Mono.Cecil", "offline Lua fixtures"]
anti_cheat: "Disposable operator-controlled local multiplayer servers only"
status: in-progress
agents: ["Codex (GPT-6)"]
humans: ["jkjkj2805"]
date: 2026-10-13
links: ["https://steamcommunity.com/sharedfiles/filedetails/?id=3074046183", "https://github.com/evilfactory/LuaCsForBarotrauma", "https://github.com/FakeFishGames/Barotrauma"]
tags: [npc, frontend, native-ai, knowledge, visibility, postconditions, idempotency]
---

# Barotrauma NPC frontend and movement: exact targets, local knowledge and physical postconditions

> A privately permitted AI NPCs frontend selected a native conversation target while one external Core owned reasoning and memory. Separate controlled acceptance proved one NPC reply with recipient-scoped sight and one existing AI crewmember's native walk to an exact compartment. Conversation, movement and creative narrative success are different claims. The private frontend and bridge are not publicly distributed by this note.

## Setup

The accepted target was Windows Barotrauma 1.13.4.0, Steam build 23799131 and LuaCs 1.0.116 at runtime revision `0d380afcd1`. The reviewed AI NPCs package was Workshop 3074046183 version 1.6, credited to **RubbingMyAxe**. Its documented targeted chat syntax was `!firstname message` / `!lastname message`.

The operator reported author permission for private modification/sharing; that is not an independently established public redistribution license. Obtain appropriate permission before reusing or shipping third-party selector code. Credit FakeFish/Undertow, LuaCs/Luatrauma maintainers and the [AI NPCs author](https://steamcommunity.com/sharedfiles/filedetails/?id=3074046183). No third-party Lua or private package is included here.

## Route and why

The frontend keeps interaction and target selection; it does not host another planner, provider, prompt builder or memory store. The private package structurally omits stock provider classes, autonomous reactions, independent history/embeddings and order processing. Turning features off in a broad stock loader would be weaker than excluding the unused implementations entirely.

The existing Core conversation route produces plain text. The server revalidates the same exact objects before calling native speech. Movement is a separate guarded Executor capability, disabled by default; conversational prose never directly becomes an order.

## How the game works (what we had to learn)

### Addressing is more than a name

The retained selector uses native eligibility/hearing checks and ranked first/last-name matching. Literal comparison avoids Lua pattern interpretation; tied best candidates fail closed. Exact `Client`, speaker `Character` and target `Character` objects pass through `ILuaCsHook.Call`/`Add` using the bounded `randur.frontend.input` hook. The bridge must not resolve a new target later by display name, job or roster position.

The host's `DirectConversationAddress` combines authenticated participant, current connection, speaker actor/body, target actor/body, world/epoch and expiry. Generation does not reserve the NPC indefinitely: native and host checks repeat before presentation. A transport ACK or queued message is not player-visible delivery.

### Server truth is not NPC knowledge

`RecipientPerceptionV2` binds sight to the exact current actor/body and scene. In the reviewed native implementation, `ISpatialEntity.CheckVisibility` contributes facing and physics occlusion. Same-Hull membership is a candidate filter only. Range was bounded at 600 native units, with windows treated as occluding. The query's shared scratch state was reviewed and restored; removed bodies or absent colliders were rejected before spatial getters.

The model sees self state/location, speaker presentation, an explicitly unverified player claim and positive current observations with bounded-coverage qualifiers. It does not receive the full private scene, remote equipment, missions, bank, hidden health, other NPC speech, GM plans or stock conversation history. Omitting an object does not prove absence. Native-positive sight is current-only, not permanent NPC memory. An NPC-generated assertion remains attributed speech, not newly authoritative world truth.

### Native locomotion is not teleportation

The guarded hand was `barotrauma.npc_move_to_compartment.v1`, capability version `baro6a.1`. It supports one exact existing AI crew body and a referenced current destination Hull. It uses `AIObjectiveGoTo` and the existing `AIObjectiveManager.AddObjective` on the game thread, preserving normal pathfinding, doors, ladders and hazard priorities. It does not set position, force a custom route or translate text room names into coordinates.

An existing same-type objective or conflicting order causes rejection: `AddObjective` can replace a same-type objective, so blindly injecting a new one is not neutral. Current player control, death/incapacity/stun, wrong crew/submarine, unsafe Hulls, stale body/info, missing explicit arm or expired command also reject. Core preflight is repeated against current game objects at native dispatch.

Creation or native completion of a GoTo objective is not exact arrival. SUCCESS needs a later committed Scene revision proving the same body/info in the exact destination Hull, matched to the terminal native receipt. Native distance completion elsewhere is insufficient. Acknowledgement loss or epoch replacement produces failure/uncertainty, with no automatic retry and no rollback of the path already walked.

## Build steps

This is a reproduction plan for independently authorized implementation, not an installer for the private fork.

1. Review the exact AI NPCs version and license/permission. Retain only the needed targeting frontend, or implement equivalent original targeting logic.
2. Pass native object identity once across a bounded hook, then bind the entire address to current authenticated control and epoch. Reject ambiguity before model generation.
3. Start with self/player-claim context. Add sight only after reviewing the installed visibility and physics dependencies; test a real remote canary's exclusion without banning its generic type name.
4. Revalidate address, contributing visible objects and their current Hulls before native speech; keep generated-but-not-presented and presented outcomes distinct.
5. For movement, advertise one narrowly typed guarded hand and require exact evidence, explicit scope arm and approval. Let native AI handle locomotion.
6. Test an accepted-but-stalled objective, completion in another Hull, lost ACK, same-name different body, changed epoch and duplicate execution. Require Scene evidence for success.

### Movement oracle in compact form

The following is explanatory pseudocode for the already described contract, not an implementation of the private bridge. `submit` means the reviewed native AI objective path, not a public RPC:

```text
Before submit:
  require exact current body/info, safe Hull, approval and live scope
  reject player control or conflicting objective/order
  admit one execution identity; submit native GoTo once
After submit:
  require a matching terminal receipt and a newer committed Scene
  if same body AND same info AND exact destination Hull: SUCCESS
  if scope is lost or the outcome is not verified: report uncertainty
  never resubmit merely because ACK or objective flags are missing
```

For the negative oracle, keep the NPC and command fixed but observe it in another Hull: objective completion or proximity must still not satisfy exact arrival. Then replay the execution identity and count native submissions; a duplicate result is not a second movement. No new movement was performed for this example.

## Verification

**LIVE-PROVEN conversation:** one authenticated local targeted message traversed frontend, exact address, Core generation, native same-NPC presentation and a correlated receipt; the human confirmed the response. Later acceptance captured 11 native sight checks with four positive and seven negative results, and a filtered reply. A private remote canary was absent from model messages despite an independently visible local object of the same generic type. This is evidence-specific filtering, not a word blacklist.

**LIVE-PROVEN movement:** one approved existing AI crewmember walked into an exact destination through the real Core Executor and bridge. Exact Scene arrival established SUCCESS even while the native objective's Completed/Abandoned flags were both false. Repeating the same execution identity returned duplicate suppression with one command and one native submission. No autonomous Creator/model chose that movement; the controlled intent was an engineering fixture. Human visual confirmation of the walk was not recorded.

**TEST-PROVEN:** offline Lua fixtures exercised target ambiguity and literal matching; Core/native-wire fixtures covered stale addresses, forbidden context, physical-arrival requirements, forged receipts, pre-dispatch rejections and durable Executor deduplication. Fake provider/native fixtures prove integration, not independent live creativity.

**UNKNOWN:** persistent NPC identity/memory across reload, all hearing/radio/voice cases, other bot enhancement combinations and a meaningful autonomous strategic Creator-to-movement story. A natural live Creator test instead honestly returned missing capability for an unavailable physical effect; dispatch count was zero.

## Gotchas

1. **Ordinary addressed chat never reaches the host.** **Cause:** a client-side rewrite hook was mistaken for the server ingress actually receiving multiplayer chat. **Fix:** trace the exact `chatMessage` path and the native hook; prove input, target and correlation before spending on generation.
2. **The NPC knows remote machinery.** **Cause:** a private full scene or same-room relation was treated as perception. **Fix:** project only recipient-specific native-positive sight with current evidence and coverage qualifiers.
3. **An order silently replaces the NPC's normal work.** **Cause:** same-type objective replacement or forced-order interaction. **Fix:** reject conflicting objectives/orders rather than borrowing stronger priorities.
4. **The move is accepted but falsely reported successful.** **Cause:** ACK, objective creation or approximate distance completion was used as the postcondition. **Fix:** require exact same-body destination-Hull evidence from the committed Scene.
5. **A lost ACK creates a second movement.** **Cause:** generic transport retry resent a non-reversible command. **Fix:** durable Core execution identity plus epoch-local replay defense; uncertain actions do not retry automatically.

## Assets

No third-party selector source, private dialogue, player aliases, account identifiers, target refs or game assets are distributed. All behavior is described in original prose.

## Open questions

The documented private permission does not establish public release rights. Conversation knowledge, mechanical locomotion and interesting campaign agency need separate acceptance. No new model or game call was made while preparing this note.

Related field notes: [scope and continuity](server-observation-identity-and-gap-safe-continuity.md); [item callback and Scene oracle](item-spawn-callback-scene-oracle-and-proof-boundaries.md).
