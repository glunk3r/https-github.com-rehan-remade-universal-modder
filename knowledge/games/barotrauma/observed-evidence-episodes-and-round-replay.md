---
kind: game
title: "Barotrauma evidence Eyes: preserve unknowns and replay only what a GM knew"
game: "Barotrauma"
games_also: []
game_version: "1.13.4.0, Steam build 23799131; LuaCs 1.0.116"
platform: windows
engine: dotnet
route: loader-api
tools: ["LuaCs/Luatrauma", "C# assembly plugin", "Python EventStore projections", "offline replay"]
anti_cheat: "Operator-controlled local multiplayer observations only"
status: in-progress
agents: ["Codex (GPT-6)"]
humans: ["jkjkj2805"]
date: 2026-10-13
links: ["https://github.com/FakeFishGames/Barotrauma", "https://github.com/evilfactory/LuaCsForBarotrauma", "https://github.com/rehan-remade/universal-modder/blob/main/knowledge/techniques/oracles-how-agents-know-a-mod-works.md"]
tags: [observation, evidence, unknown, provenance, replay, context-budget, knowledge-fences]
---

# Barotrauma evidence Eyes: preserve unknowns and replay only what a GM knew

> A private server observer collected campaign, sparse scene, gameplay and resource evidence into one external EventStore. Offline replay reconstructed historical decision cutoffs and bounded actor episodes without inventing missing actions or knowledge. Real recording proves the source observations; offline proof establishes extraction and request-budget behavior. Neither proves that an AI produces an interesting campaign.

## Setup

Accepted observations came from Windows Barotrauma/DedicatedServer 1.13.4.0, Steam build 23799131, LuaCs 1.0.116 (`0d380afcd1`). The observation wire remained protocol 1; the rich resource/continuity profile advertised `baro6bobs1.1`. The capture bridge, host projections and accepted corpus are private, not downloadable public training data. Do not request or publish campaign logs to reproduce these principles.

Credit: Barotrauma by FakeFish/Undertow, LuaCs/Luatrauma by its maintainers, and Universal Modder's [oracle taxonomy](https://github.com/rehan-remade/universal-modder/blob/main/knowledge/techniques/oracles-how-agents-know-a-mod-works.md) for distinguishing source, replay and real-world checks.

## Route and why

Capture facts through the authoritative game's own types. Keep one raw evidence store and rebuildable game-specific projections. Scene extraction and interpretation belong to the game adapter; generic selection and memory stay in the host. The DTO is evidence, not a prompt, and observations must not silently become player knowledge.

## How the game works (what we had to learn)

The four observer surfaces answer different questions:

| Surface | Observed facts | Invalid shortcuts |
|---|---|---|
| Campaign | Current/selected map state, offered/selected/active missions, bank, reputation, pending/stored upgrades | Offered means selected; selected means active; disappearance means mission completion |
| Scene | Submarine/Hull/door structure, exact character/Hull relations, dead flags, bounded semantic devices and literal containment | Missing from a partial set means absent or destroyed; same room means visible |
| Gameplay | Explicit state transitions, paired native damage relations, observed inventory-parent changes | Damage point means shot; damage plus later death means fatal cause; parent change means intent or ownership |
| Resources | Definition/scope/count/condition evidence, equipment/site/salvage facts, selected recipe feasibility | Object count means operating hours; failed recipe feasibility means no finished supplies |

Character death requires an observed false-to-true dead transition for the same known body. Disappearance or disconnect is insufficient. A paired damage hook can establish attacker-to-target damage; it does not automatically identify a later fatal blow. Similarly an item upsert proves entry into an observed set, not that a player spawned it. Inventory custody establishes literal parent relations, not acquisition motives or lawful ownership.

Beacon `Level.LevelData.IsBeaconActive` supports a bounded flag observation. Continuous false-to-true snapshots at the same site can support activation; an already-true bootstrap cannot prove who activated it or when. Dedicated boss-victory, whole-station destruction and item opening/unsealing semantics were not provided by the reviewed observer. Do not infer specific events from generic telemetry coverage.

Each block carries complete/partial/unavailable status. Raw envelopes commit before current projections become visible. Semantic observations retain their exact direct refs and transitive source closure, making them rebuildable. A derived summary is useful indexing, not a substitute evidence authority.

An observed episode links only the same exact body plus compatible `CharacterInfo` inside one world/epoch/round. A scene revision hole, removal, future dependency, foreign scope or intersecting recorded GAP breaks admission. Two independent sequences may share a presentation batch without gaining a causal relationship. Unknown motive, affiliation, weapon, death cause and recipient knowledge remain explicit.

## Build steps

The private corpus is not distributed. To reproduce with one's own observer and consented campaign:

1. Capture bounded campaign/scene/gameplay/resource frames on the game thread; give each immutable envelope namespace, epoch, sequence and capture time.
2. Commit raw evidence before semantic projection. Keep explicit completeness and avoid death, completion or destruction inference from absence.
3. Record gaps with last verified and first fully fresh observations. Loading is an unknown interval even if no TCP socket changed.
4. Freeze rich checkpoints with exact source closure. For historical evaluation create separate BEFORE, SCENE READY and AFTER files. AFTER must never enter the historical BEFORE request.
5. Reconstruct final pre-departure mission choices from the latest admitted committed state, not merely the last checkpoint; late selections can occur between checkpoint and loading.
6. Admit bounded episodes only with fact-level evidence and scope/identity continuity. Keep recipient filtering unchanged.
7. Measure the entire serialized model request, including prompt, user JSON, schema, aliases, escaping and provider envelope. Source-text token savings alone are not the gate.

### Two independent cutoff gates

An independently written replay can use this explanatory filter; the names are notation, not the private DTO/API:

```text
admit a fact only when:
  capture_time <= historical_time_cutoff
  AND ingestion_position <= historical_ingestion_cutoff
  AND every source dependency also passes both cutoffs
  AND world, epoch, identity and gap continuity are proved
then apply the existing recipient knowledge filter
```

For context selection, serialize the entire baseline and candidate requests with the same serializer. Reject growth or lost protected facts/provenance and restore the baseline; comparing only episode prose is insufficient. A useful negative pair is an observed dead flag with an unknown cause: the death remains, while a proposed killer or motive must not enter as history. The filter/example adds no new historical evidence.

## Verification

**LIVE-PROVEN observations:** accepted natural recording showed repeated outpost/voyage boundaries, device/environment changes, custody/salvage facts, deaths and upgrade states. Those are sampled observations, not a complete trace of player intent or a claim of observed boss victory, beacon activation or station destruction.

**TEST-PROVEN historical replay:** three voyage rounds, four outpost phases and six explicit loading GAPs were reconstructed offline from accepted evidence. BEFOREs admitted only facts before both time and ingestion cutoff; dependency closure rejected hidden future leakage. Mission outcomes and causes of gap-spanning money/reputation changes remained unknown.

**TEST-PROVEN offline shadow selection:** all 15 accepted natural cases were compared under existing complete-request limits. In the eligible episode case, two abstract tactical summaries were replaced by two independent bounded episodes, with all other selected facts/citations preserved. Each corresponding full envelope became 19 characters and 27 wire bytes smaller (six estimated tokens, not provider usage). Another candidate grew by 367 characters, so the full-envelope veto restored its original request. The dangerous case preserved its full original context.

Priority protection includes HIGH/CRITICAL pressure, ESCALATING trend, unresolved danger, other demonstrated urgency and insufficient assessment. Missing/wholly unknown urgency preserves the original tactical context. A calm-looking last-eight summary cannot erase a richer warning. No observed urgency is not a proof of safety. Competitive urgent-episode behavior also had synthetic fixture tests; the natural dangerous scene did not supply a competing admitted episode.

**CODE-ONLY/UNKNOWN:** the accepted shadow selector was not promoted to production in that stage. Later production history support used a different explicitly bounded path: at most 8,192 ingestion positions and six epochs in the same native instance, with capped cards/episodes. It is not guaranteed whole-campaign memory or the zero-growth shadow policy. No live/provider creative-quality benefit follows from either technical gate.

## Gotchas

1. **The archive contains rich history but the GM sees only generic pressure.** **Cause:** a last-eight selection window and crew-only importance filtering removed earlier actor relations. **Fix:** reconstruct bounded evidence-backed episodes before generic selection, preserving scope and exact provenance.
2. **A missing crafting ingredient becomes an urgent fuel crisis.** **Cause:** recipe feasibility was conflated with finished-item stock. **Fix:** keep count, capacity, scope coverage and feasibility distinct; unknown material coverage is not zero.
3. **Deaths become a faction consequence.** **Cause:** temporal proximity and location faction were used as causal/affiliation joins. **Fix:** preserve independent observations and explicit unknowns unless the relevant relationship itself was observed.
4. **The next-round baseline leaks into preparation.** **Cause:** a replay mixed AFTER or SCENE READY into BEFORE. **Fix:** fence every fact and dependency by its historical cutoff, not only the outer envelope.
5. **A shorter narrative still creates a bigger request.** **Cause:** citations, alias enums, schema and escaping also consume bytes. **Fix:** veto on the complete serialized envelope and restore the exact original request.

## Assets

No original campaign histories, transcripts, names, event IDs, screenshots or game assets accompany this note. Examples describe semantic categories only.

## Open questions

Cross-native-instance actor continuity, a live activation witness, full campaign duration coverage, production zero-growth episode selection and improved creative outcomes remain separate acceptance tasks. This retrospective preparation ran no game or model.

Related field notes: [server identity and GAP](server-observation-identity-and-gap-safe-continuity.md); [authored effects versus player agency](../../techniques/authored-effects-are-not-player-agency-evidence.md).
