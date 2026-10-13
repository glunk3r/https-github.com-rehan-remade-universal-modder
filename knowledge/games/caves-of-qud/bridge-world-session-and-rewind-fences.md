---
kind: game
title: "A detached Qud bridge: world, session, and rewind are different identities"
game: "Caves of Qud"
games_also: []
game_version: "Steam Windows acceptance, 2026-08-29 to 2026-08-31; exact historical game build UNKNOWN; private bridge 5.0.0/6.0.0"
platform: windows
engine: unity-mono
route: loader-api
tools: ["Qud C# scripting mods", ".NET netstandard2.1 / C# 9", "Python", "SQLite", "Mono.Cecil (historical inspection)"]
anti_cheat: "Single-player disposable-world tests; no protection bypass or multiplayer modification"
status: in-progress
agents: ["Codex (GPT-6)"]
humans: ["jkjkj2805"]
date: 2026-10-13
links: ["https://wiki.cavesofqud.com/wiki/Modding:Overview"]
tags: [bridge, game-thread, world-identity, save-load, rewind, evidence, stale-actions]
---

# A detached Qud bridge: world, session, and rewind are different identities

> A private Randur bridge connects a scripted Qud mod to an external Python host without sending live game objects across threads. Historical real-game runs proved reconnection and save/reload continuity; later offline tests proved stronger timeline and evidence fences. This is an implementation field note, not a publicly downloadable bridge or a claim of compatibility with every Qud build.

## Setup

The accepted Windows/Steam runs used private bridge versions 5.0.0 and 6.0.0. The bridge project targets `netstandard2.1`, C# 9, and references the owner's installed `Assembly-CSharp.dll` and `Newtonsoft.Json.dll`. The exact historical game/Unity and compiler tool versions were not retained in the acceptance summary: **UNKNOWN**, not "latest". Test fixture version strings are not installed-game evidence.

Qud's [official modding overview](https://wiki.cavesofqud.com/wiki/Modding:Overview) describes its C# scripting-mod route. Credit Freehold Games and the Qud wiki contributors for that route; credit the private Randur implementation for the bridge-specific contracts here. No game assemblies or decompiled source accompany this note.

## Route and why

Use Qud's scripting hooks and inspect an owned installation's actual managed interfaces before implementing a bridge. A transport thread exchanges bounded data transfer objects; it must never dereference a Qud `GameObject`. Game access is posted to the `SynchronizationContext` captured by `CallAfterGameLoaded`. The private implementation captures on a roughly 500 ms cadence and executes at most one queued capability per capture.

This avoids a second simulated world on the external side and avoids guessing that thread-safe JSON serialization makes native game access thread-safe.

## How the game works (what we had to learn)

Keep these identities independent:

| Identity | Meaning | Must not be used as |
| --- | --- | --- |
| `XRLGame.GameID` | Authoritative save/world identifier; normal reload retains it | Player name or transport session |
| Bridge session UUID | Current runtime peer/session | Durable world or timeline ancestry |
| Binding generation | Current external host's lease on this attachment | Session ID or automatic memory reset |
| Runtime timeline generation | In-process replacement/rewind fence | Universally durable save-lineage proof |
| Native object ID | Scoped observed target | Eternal identity inferred from display name |

The private snapshot includes availability, sequence, game version, GameID, turns, time ticks, zone, player object ID and position, and timeline generation. An unavailable snapshot is explicit; the last known world is not fabricated into an available player.

`ObserveTimeline` detects same-GameID replacement of the `XRLGame` object or a decrease in `Turns`, increments a generation, and drops queued writes. The host separately stores durable branch ancestry using comparable `(Turns, TimeTicks)` observations. Raw events remain immutable; current-context retrieval excludes abandoned future branches.

**Detection limit:** a cross-process restore at exactly the last stored complete position, with no stronger lineage token, can be indistinguishable from a normal restart. This remains UNKNOWN. A reused display name supplies no missing lineage evidence.

## Build steps

These are reproduction requirements for your own bridge, not commands to install unpublished Randur code:

1. Enable scripting mods in a copied test profile and reference assemblies from your legally owned installation; record their version and hashes privately.
2. Capture the post-load game-thread context. Publish only detached immutable snapshots to a loopback transport.
3. Require an available GameID/player/zone before binding. Separate the world namespace, bridge session, binding generation, and timeline generation in every request and observation.
4. Disarm on disconnect, unavailable world, changed bridge session, rebind, or epoch change. Cancel old queued requests before admitting a new world.
5. Test save reload, lower-turn rewind, and world switching independently. Assert both "new work reaches the new scope" and "old work cannot reach it".

### Reload versus rewind check card

Use separate columns in an independent diagnostic trace rather than one overloaded ID. This is a reproduction checklist, not new recorded output.

| Controlled change | Identity/context check | Write admission |
|---|---|---|
| Normal reload | Compare GameID; inspect new bridge session and binding | Require fresh binding and explicit rearm |
| Same-world lower-turn restore | Detect timeline replacement/regression; exclude abandoned future facts | Drop old queued work; require current scope |
| Switch to another save/world | Resolve the new GameID namespace independently | Reject the previous world's requests |
| Exact-position cross-process restore | Report indistinguishable lineage as UNKNOWN | Never infer ancestry from a display name |

The external history may retain old raw events. What changes after a proven fork is eligibility for current context, not the historical record itself.

## Verification

- **LIVE-PROVEN, historical:** one controlled save/reload preserved GameID, changed bridge session, and required explicit rearming; owned content remained. Earlier restart reconstructed the same owned content without duplication.
- **TEST-PROVEN, existing offline tests:** superseded connections and older sequences cannot overwrite state; cross-world pending commands cancel; new bridge session disarms; same-world turn regression excludes abandoned-future context; benign rebind does not erase legitimate durable knowledge.
- **CODE-ONLY for today's installation:** the currently inspected thread, capture and native epoch paths were not rerun for this note.
- **UNKNOWN:** exact historical base-game build, every mod combination, and indistinguishable same-position cross-process restores.

## Gotchas

1. **Symptoms: raw events exist but the model gets no targets.** **Cause:** a binding-generation label was accidentally copied into the canonical session field; strict lookups correctly rejected it. **Fix:** propagate the real bridge/Core session unchanged and carry binding generation separately. Do not weaken scope validation to hide the mismatch.
2. **Symptoms: paused menus look disconnected.** **Cause:** game-thread capture pauses while transport repeats the latest snapshot. **Fix:** accept an identical sequence only when the entire snapshot is identical; allow liveness and pending detached delivery, but do not ingest it as new telemetry. Same-sequence conflicting content must fail closed.
3. **Symptoms: old knowledge survives a rewind.** **Cause:** save identity was mistaken for timeline identity. **Fix:** preserve immutable history with branch membership and query only provable current ancestry. Unknown-position legacy facts fail closed after a fork.
4. **Symptoms: target identity looks valid forever.** **Cause:** display names or native IDs were used without current scope/location attestation. **Fix:** revalidate world, session, binding, timeline, player, and current target; history is not a live object handle.

## Assets

No art, audio, game assets, save files, private campaign text, or extracted code are included.

## Open questions

A public minimal bridge would make the exact transport contract independently executable. Until then, readers can reproduce the listed native/thread/identity checks with their own scripted mod, but cannot independently rerun the private historical acceptance. Technical continuity does not prove a compelling autonomous GM.

Related field notes: [save/reload and native deduplication](bounded-actions-postconditions-and-save-reload-dedup.md); [manifestation and discovery](manifestation-discovery-and-attention-oracles.md).
