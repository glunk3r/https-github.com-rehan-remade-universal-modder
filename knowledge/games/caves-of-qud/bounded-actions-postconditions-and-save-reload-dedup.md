---
kind: game
title: "Bounded Qud actions: native postconditions and save-reload deduplication"
game: "Caves of Qud"
games_also: []
game_version: "Steam Windows controlled acceptance, 2026-08-31; exact historical game build UNKNOWN; private bridge 6.0.0"
platform: windows
engine: unity-mono
route: loader-api
tools: ["Qud C# scripting mods", ".NET netstandard2.1 / C# 9", "Mono.Cecil (historical inspection)", "Python", "SQLite"]
anti_cheat: "Single-player disposable-world tests; no protection bypass or multiplayer modification"
status: in-progress
agents: ["Codex (GPT-6)"]
humans: ["jkjkj2805"]
date: 2026-10-13
links: ["https://wiki.cavesofqud.com/wiki/Modding:Overview"]
tags: [capabilities, executor, postconditions, idempotency, save-load, parts, effects, quests]
---

# Bounded Qud actions: native postconditions and save-reload deduplication

> A private bridge exposed a curated action catalog to an external Executor, with native revalidation and factual postconditions. A controlled disposable-world run tested seven new action families, one real save/reload, and replay suppression. This proves bounded mechanical effects in that historical setup; it does not prove general quest generation, compelling GM judgment, or present-build compatibility.

## Setup

Historical acceptance was on 2026-08-31, Windows/Steam, bridge 6.0.0. The native project targets `netstandard2.1` and C# 9 against the owner's installed managed assemblies. The exact historical game/Unity build and inspection-tool version are **UNKNOWN**. The private bridge is not distributed with this note; reproduction requires implementing these contracts yourself or obtaining the bridge separately.

Credit Freehold Games, the [official Qud modding documentation](https://wiki.cavesofqud.com/wiki/Modding:Overview), Mono.Cecil's maintainers for managed-interface inspection, and Randur's private integration for the bounded bridge implementation. No proprietary method body is reproduced.

## Route and why

Keep authoring intent separate from execution. The authoring role stays tool-blind; an Executor sees only allowlisted semantic capabilities. Qud owns native legality, game-thread execution, and postcondition observation. Neither a model's JSON nor an accepted network request is evidence that an effect happened.

The historical catalog had 13 bounded capabilities, including story NPC/item/clue, local encounters, inert props and attention. The controlled gate specifically exercised these additions:

| Capability | Native mechanism inspected | Historical controlled postcondition |
| --- | --- | --- |
| `introduce_dialogue_npc` | Owned serializable `IPart`; `BeginConversationEvent` | One non-hostile NPC with the authored dialogue surface; same NPC after reload |
| `create_unique_reward_item` | Precompiled `IPart`, equip/unequip events, `StatShifter` | One item; exactly +1 equipped modifier, removed on unequip; repeated after reload |
| `apply_temporary_stat_effect` | Serializable `Effect`, `ApplyEffect`, duration, `StatShifter` | One bounded +1 defensive modifier; remaining duration after reload; eventual expiry |
| `apply_permanent_stat_delta` | `Statistic.AddShift` and exact stored shift identity | Exactly +1 base attribute; persisted; replay did not reapply |
| `modify_faction_reputation` | Installed `Factions` lookup, `PlayerReputation.Get/Modify` | One +25 delta for an existing faction; persisted; replay did not reapply |
| `create_owned_side_quest` | Initialized native `Quest`/`QuestStep` and registry | Exactly one optional owned one-step quest; persistent identity |
| `advance_owned_side_quest` | Exact owned quest/objective state | Only that owned objective finished; visible journal state; replay did not repeat |
| Expanded `create_local_encounter` | Allowlisted blueprints, `Brain`/faction disposition | Two neutral actors, safe distance, expected owned member count |

The table names private capability IDs, not a public Qud network API. Skills, new mutations, cybernetic installation and arbitrary generated C# were not exposed by this gate.

## How the game works (what we had to learn)

`GameObjectFactory.Factory.CreateObject` and `Cell.AddObject` support ordinary creation, but safe placement and ownership are additional responsibilities. A created name is presentation; serialized owner/world/action/content properties establish provenance.

The bridge uses stable action IDs and semantic payload fingerprints. Existing matching objects reconstruct a result rather than being created again. A persistent game-state tombstone also records the successful action. If all its objects are gone or outside the bounded observation scope, absence does not authorize resurrection: reconciliation is required. Reusing an ID with changed arguments is an idempotency conflict.

State-changing capabilities need their own durable ledger because there may be no new object to inspect. Permanent attribute changes additionally retain their exact shift identity; temporary effects serialize action and story metadata; quests carry owner/action/key properties.

Precompiled parts/effects serialize data only. Sockets, queues, external host services and live request objects remain transient. Keeping the mod enabled while the external host is offline is supported; removing the mod that defines a saved CLR type is **not** claimed to be lossless.

## Build steps

1. Work on a copied disposable save. Inspect the installed blueprint registry and the exact API signatures; do not publish the assemblies or a decompiler dump.
2. Implement one narrow capability with typed scalar arguments, allowlists and explicit bounds. No arbitrary blueprint/reflection/console passthrough.
3. Arm only the current world/session/lease. Include action ID, fingerprint, expected zone, runtime generation, expected turn, and expiry.
4. On the game thread, validate before mutation, perform the one effect, then re-observe native state. Return accepted/performed/uncertain and named postconditions separately.
5. Save and reload once. Rebind and explicitly rearm. Verify the same owned identity or native value before replaying the exact original action identity.
6. Replay; verify zero duplicate objects and zero reapplied deltas. Test changed payload under the same ID and missing-object reconciliation as negative cases.

### Save/reload and dedup verification matrix

For one independently implemented capability, record both an object count and the relevant native value/shift identity. These are expected oracle checks, not additional live results. Rebind and rearm after reload; do not resend an expired transport packet merely because its semantic action ID is durable.

| Step | Expected check |
|---|---|
| First legal action | One owned effect; factual native postconditions, not ACK alone |
| Exact semantic replay | Same action ID and fingerprint; no new object or reapplied delta |
| Save, reload, fresh arm | Same serialized owned identity or exact stored native value |
| Same action identity after reload | Reconstruct/reconcile the existing result; zero extra effect |
| Same ID, changed semantic payload | Idempotency conflict before mutation |
| Recorded success but object missing | Reconciliation required; do not resurrect it from absence |

For a permanent modifier, count the exact stored shift, not just the displayed final attribute: unrelated changes can hide a duplicate. For an item, compare serialized ownership/action identity rather than its localized name.

## Verification

- **LIVE-PROVEN, controlled historical gate:** the listed effects, one save/reload, bounded modifiers, optional owned quest progress, literal localized dialogue, and exact replay suppression. The private acceptance record includes human-visible checks; not every reload condition was independently re-read from raw telemetry during preparation of this note.
- **Raw evidence spot-check:** saved factual `action.result` envelopes independently retain successful uniqueness, placement, modifier, ledger, quest and encounter postconditions. Failed/uncertain quest attempts also remain; they were not erased to make the final gate green.
- **TEST-PROVEN:** an existing mocked-bridge test routes a typed command through Core Executor to factual EventStore evidence and returns the same result on duplicate execution. Other tests cover arming and stale scope. Mocked native postconditions are transport proof, not independent game physics proof.
- **CODE-ONLY/current compatibility:** inspected native ledgers, allowlists and postcondition code were not rerun in a game for this note.
- **UNKNOWN:** all future builds, other genotype/mod combinations, mod removal recovery, general multi-step quests or dialogue trees, and creative quality of autonomous high-commitment use.

## Gotchas

1. **Symptoms: native quest exists but the host times out.** **Cause:** `StartQuest`/`FinishQuestStep` UI can wait synchronously for acknowledgement after changing state. **Fix:** the controlled implementation registers fully initialized owned state and emits normal typed events without a blocking modal. Inspect native state before deciding whether retry is safe; timeout is not proof of no effect.
2. **Symptoms: owned NPC speaks unrelated merchant dialogue.** **Cause:** its blueprint inherits a vanilla `ConversationScript`. **Fix:** remove that inherited surface for new owned NPCs and intercept `BeginConversationEvent` in the serialized owned part. The existing saved NPC was verified after reload as well.
3. **Symptoms: a duplicate still changes the attribute.** **Cause:** an external request ledger alone does not survive every reconnect/reload route. **Fix:** persist the action identity in native game state and validate the exact stored shift or object identity before any mutation.
4. **Symptoms: serialization looks safe but removal of the mod breaks behavior.** **Cause:** saved objects reference custom CLR parts/effects. **Fix:** keep those types available; external-host absence and mod absence are different tests.

## Assets

No generated assets, game binaries, save data, private narrative text or original authored item/NPC names are included.

## Open questions

The historical controlled mechanical gate is closed, while a publicly repeatable bridge and current-build retest remain unavailable. An `exact` realization means the physical effect matches the requested goal; it is not a review of whether the goal is interesting.

Related field notes: [world/session/rewind fences](bridge-world-session-and-rewind-fences.md); [causal interpretation of authored effects](../../techniques/authored-effects-are-not-player-agency-evidence.md).
