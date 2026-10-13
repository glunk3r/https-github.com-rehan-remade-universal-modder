---
kind: game
title: "Barotrauma server observation: separate campaign, participant and runtime identity"
game: "Barotrauma"
games_also: []
game_version: "1.13.4.0, Steam build 23799131; LuaCs 1.0.116"
platform: windows
engine: dotnet
route: loader-api
tools: ["LuaCs/Luatrauma", "C# assembly plugin", ".NET SDK 8.0.423", "Mono.Cecil"]
anti_cheat: "Only operator-controlled local multiplayer servers; no anti-cheat or ownership bypass"
status: in-progress
agents: ["Codex (GPT-6)"]
humans: ["jkjkj2805"]
date: 2026-10-13
links: ["https://github.com/evilfactory/LuaCsForBarotrauma", "https://luatrauma.github.io/Luatrauma.Docs/cs/setup-assembly-csharp/", "https://github.com/FakeFishGames/Barotrauma"]
tags: [server-observation, identity, lifecycle, gaps, provenance, game-thread, read-only]
---

# Barotrauma server observation: separate campaign, participant and runtime identity

> A private server-side C# bridge supplied a single external application with bounded observations, using LuaCs rather than a second game-specific AI host. Accepted real-game tests proved campaign continuity across ordinary reloads and restarts, and authenticated participant continuity across reconnects. Runtime targets stayed ephemeral. This note describes mechanisms and proof limits; it does not distribute the bridge or provide a turnkey installation.

## Setup

The accepted engineering target was Windows, Barotrauma and DedicatedServer 1.13.4.0, Steam build 23799131, LuaCs Workshop package 2559634234 version 1.0.116. Its runtime reported revision `0d380afcd1`; the reviewed full loader revision was `0d380afcd1feeb842c0c86290d46bcaf198cd5e4`. C# builds used .NET SDK 8.0.423 and the loader's publicized references. Static inspection used Mono.Cecil without executing the inspected game assemblies.

The bridge and host application are private implementation artifacts. Public prerequisites are the game and [LuaCs/Luatrauma assembly workflow](https://luatrauma.github.io/Luatrauma.Docs/cs/setup-assembly-csharp/). Credit goes to FakeFish/Undertow for Barotrauma and the LuaCs/Luatrauma maintainers for the loader. These historical versions are not claims about the latest compatible release.

## Route and why

Use an `IAssemblyPlugin` on the authoritative server. Capture game objects on the update thread, serialize a bounded immutable frame there, and pass only strings to the network worker. A transport thread must never wander live `Character`, `Hull`, inventory or campaign objects.

The observation connection is distinct from the game's multiplayer transport. A loopback TCP receiver accepts one mutually authenticated peer, with directional HMAC challenge proofs and fresh nonces. Authentication alone does not make a packet current: scope, sequence, capture age and baseline state are checked separately.

## How the game works (what we had to learn)

Several apparently observational getters are unsafe for read-only capture. In the reviewed build, `Location.AvailableMissions`, `Location.SelectedMissions` and `MultiPlayerCampaign.LastSaveID` can mutate state. The bridge reads narrowly reviewed backing fields instead. A matching publicized signature is insufficient: inspect the installed method body, not just upstream source or a reference assembly.

There are several different identities:

| Identity | Authority | What it does not prove |
|---|---|---|
| Campaign world | Registered original save-file instance on supported NTFS, mapped to an opaque UUID | That an identical copy is the same world |
| Native process/observation epoch | Current process, transport generation and round scope | Cross-restart object identity |
| Human participant | Ticket-verified native Steam authority, pseudonymized at the native boundary | A current connection or body |
| Connection | Current native `Client` object | Participant continuity after reconnect |
| Actor/body | Scoped `CharacterInfo` and exact current `Character` references | Persistent NPC identity |
| Target item/Hull/site | Exact observed object inside its current scope | A live target after an epoch change or gap |

Names, map seeds, save hashes and native numeric IDs are presentation or diagnostics, not interchangeable identity authorities. Save bytes change during normal progression; clones may preserve their content and seed. The supported registry therefore binds an opaque locator for the physical save instance. Copies become new worlds. Conflicting or unavailable evidence fails closed. Arbitrary external in-place replacement that retains the locator is not reliably distinguished by this contract.

The participant path consumes a successfully authenticated native Steam primary ID and emits an HMAC pseudonym. Raw account values and tickets do not become model context. A separate stable pseudonym key is protected using Windows CurrentUser DPAPI; loss or corruption must not silently generate a replacement identity. The reviewed authenticated path covered classic dedicated servers. P2P/listen-owner and EOS account authorities were not covered by that proof.

Transport bounds were 256 KiB per frame, eight serialized outbox entries, two-second campaign sampling and eight-second campaign freshness. Continuity hardening bounded connect/read/producer-idle waits at eight seconds and writes at three seconds. Retry spacing was 1, 2, 4, 8, 16, then 30 seconds; it reset after an accepted baseline, not merely successful TCP pairing.

## Build steps

These are implementation requirements for reproducing the experiment in one's own plugin, not commands to install the private bridge.

1. Pin game, loader, reference and installed assembly versions; inspect the exact getters and hook call sites used by capture.
2. Implement update-thread snapshot serialization and a bounded string outbox. Start with observation only and no arbitrary RPC.
3. Keep campaign registry authority separate from process, epoch, connection and body references. Make unsupported identity explicit.
4. Commit raw envelopes before exposing current derived state. Reject stale scope, sequence holes and replacement baselines as action continuity.
5. In disposable worlds, test normal save progression, reload, full restart, an independent campaign and a cloned save. Then independently test authenticated disconnect/reconnect and stale target rejection.
6. Test the actual transport worker with real loopback sockets while the producer is idle. A mock socket alone misses blocked queue waits.

### Minimal capture-to-baseline sketch

This is original explanatory pseudocode, not the private wire format or a new game API. It makes the separate acceptance gates reproducible:

```text
Game update thread:
  capture reviewed fields, scope, sequence, capture time and completeness
  detach and serialize; enqueue the bounded string, never live objects
Receiver:
  authenticate peer; validate frame bounds and current scope
  commit admitted raw evidence before exposing a projection
  if continuity is lost: mark GAP and disarm current action targets
  require a fully fresh baseline for the current transport generation
  only then resume current-state projection and recording
```

Check campaign ID, participant pseudonym and runtime body separately in a reload/reconnect test. A matching campaign must not make the old body valid; a transport heartbeat must not clear GAP before the required baseline. These are reproduction assertions, not additional acceptance results.

## Verification

**LIVE-PROVEN:** original campaign namespace persisted through a normal voyage, reload and full game/server/Core restart; a clone and an independent campaign received different worlds. A real authenticated client reconnected with the same participant pseudonym and a different connection. Old connection/body/address references were rejected. Disconnect did not imply death.

**TEST-PROVEN:** the actual native worker recovered from real loopback EOF while idle, re-paired with a fresh nonce/generation, required a new baseline and obeyed capped retry spacing. Offline host tests rejected cross-world, old-epoch and stale-heartbeat resurrections. Natural recording supplied repeated fresh round-boundary resyncs; that is not a live network-outage test.

**CODE-ONLY/UNKNOWN:** arbitrary multi-host identity, externally rewritten physical saves, persistent NPC continuity, P2P/EOS authentication and all mod combinations. One earlier connection outage's particular cause remained unknown; transport weaknesses found in code were not asserted as its historical cause.

## Gotchas

1. **Read-only capture changes the campaign.** **Cause:** a getter lazily populates or advances state. **Fix:** inspect exact installed IL and use a narrowly reviewed backing-field path; fail verification on a version mismatch.
2. **A copied save inherits another world's memory.** **Cause:** identity selected by name, seed or content hash. **Fix:** treat physical copies as new worlds unless separate authoritative continuity is supplied.
3. **A reconnect reuses an old command target.** **Cause:** durable participant equality was mistaken for current body/connection equality. **Fix:** validate the whole current control binding and exact runtime epoch again.
4. **The recording says ACTIVE although observations stopped.** **Cause:** administrative session state was used as sensor health. **Fix:** track transport, freshness and RECORDING/GAP independently; pause active-time accounting and checkpoint capture until full resync.
5. **The sender never detects EOF while the game is quiet.** **Cause:** an unbounded producer queue wait blocks the transport worker. **Fix:** bound producer-idle waits and require a baseline before resetting recovery state.

## Assets

No game assets, extracted data, account records, executable files or private bridge source are distributed with this note.

## Open questions

Long-duration outage recovery and current mod-stack compatibility require fresh bounded acceptance. The existing identity proof does not authorize persistent target rebinding across a gap. No game or provider was launched to prepare this retrospective note.

Related field notes: [campaign evidence and replay](observed-evidence-episodes-and-round-replay.md); [NPC targets and arrival](private-npc-frontend-and-native-movement-postconditions.md).
