---
kind: game
title: "Qud manifestation is not discovery: attention timing and false engagement"
game: "Caves of Qud"
games_also: []
game_version: "Steam Windows QUD5 live acceptance, 2026-08-29/30; bridge 5.0.0; later offline correction 2026-09-17; exact historical base-game build UNKNOWN"
platform: windows
engine: unity-mono
route: loader-api
tools: ["Qud C# scripting mods", "Python", "SQLite", "private detached bridge"]
anti_cheat: "Single-player disposable-world tests; no protection bypass or multiplayer modification"
status: in-progress
agents: ["Codex (GPT-6)"]
humans: ["jkjkj2805"]
date: 2026-10-13
links: ["https://wiki.cavesofqud.com/wiki/Modding:Overview"]
tags: [oracle, attention, autoexplore, discovery, player-agency, provenance, feedback-loops]
---

# Qud manifestation is not discovery: attention timing and false engagement

> A private Qud bridge distinguished object creation, actual visibility and deliberate interaction, then discovered an attention race during real autoexplore. Historical technical acceptance passed; a later playtest showed that successful delivery and pickup were still poor evidence of meaningful player engagement. The useful oracle is a sequence of scoped observations, not a single success flag.

## Setup

Historical Windows/Steam QUD5 acceptance used bridge 5.0.0 on 2026-08-29/30. A later 2026-09-17 report preserved natural-play failures and an offline correction. Exact base-game/Unity builds are **UNKNOWN**; no new game run was performed for this note. The private bridge and campaign are not published, so the original acceptance cannot be independently rerun from this article.

Credit Freehold Games and the [official modding overview](https://wiki.cavesofqud.com/wiki/Modding:Overview) for the scripting route. The implementation-specific observations come from private Randur evidence; all names, story text and entity identities have been removed.

## Route and why

Persist raw evidence, then derive a delivery lifecycle keyed by world plus one authored thread and its owned content IDs. A native effect result establishes manifestation. First factual perception establishes notice. Deliberate conversation/combat establishes stronger interaction. Missing perception does not establish rejection, and creating an object does not put its hidden contents into player knowledge.

## How the game works (what we had to learn)

The bridge scans owned objects in the active zone with a bounded limit and requires its actual visibility predicate. On first visibility it can deliver a pre-armed attention signal synchronously, then enqueue perception telemetry. A readable owned clue emits its body as discovered knowledge only when its Read surface is invoked; creation has a `clue_not_auto_known` postcondition.

The attention strengths are `NONE`, `SUBTLE`, `NOTICE` and `MUST_NOT_MISS`. They describe delivery, not control over the player's choice. SUBTLE is not armed for interruption. Stronger attention can interrupt an active, interruptible autoexplore action only when the exact owned target becomes visible; no hidden clue text is disclosed by the generic notice. Persistent delivery state allows one initial signal and at most one re-notice after dormancy and rediscovery.

An early lab correctly detected perception, but an asynchronous external attention request arrived roughly four seconds later, after the player passed the target. It failed with `owned_target_not_visible`; it did **not** stop autoexplore. The fix was `arm_until_visible`: authorize the exact owned target in advance, then perform the short engine-side interruption at the first perception point. The external host subsequently records delivery from factual `owned_content_attention_signaled` telemetry.

### Historical lifecycle versus current meaning

QUD5 originally treated acquisition/reading as ENGAGED. This was mechanically observable and sufficient for that historical gate, but a later natural sample found a causal mistake: pickup of a GM-authored carrier was used as fresh engagement and prompted another authoring proposal. It did not prove the player wanted that narrative to expand.

The later implemented correction keeps pickup/read as attention/NOTICED, preserves raw events, and reserves ENGAGED for deliberate interaction such as conversation/combat. Owned-attention events do not independently create fresh planning opportunities. That correction is **TEST-PROVEN**, not proof that the next natural campaign has better artistic quality. Historical persisted ENGAGED rows were not rewritten to conceal the older policy.

## Build steps

1. In a copied save, create one inert owned object hidden from the player's view. Record a factual native existence/identity postcondition.
2. Arm a bounded attention intent for its exact world, lease, bridge session, zone and content ID. Do not reveal text while it is hidden.
3. Start autoexplore and permit ordinary discovery. Record active-autoexplore status, actual interruption and the native perception event independently.
4. Reload/reconnect and replay the same attention identity. Assert that an initial notice is not repeated. Exercise SUBTLE as a non-interruption control.
5. Observe pickup, reading, deliberate conversation and combat as distinct signals. Test that pickup alone does not request a new authored situation.
6. Preserve failed attention attempts, unknown observation types and ignored content. Do not derive human interest from a successful native operation.

These steps describe the oracle to implement in your own mod; they are not a hidden install command for Randur.

### Knowledge and attention are different checks

This compact checklist helps reproduce the described boundary; it is not a new acceptance sample.

| Observation | Supported conclusion | Still not supported |
|---|---|---|
| Successful native creation | Owned content manifested | Player noticed it or knows its text |
| Exact target becomes visible | First perception; eligible pre-armed attention | Player wants the story expanded |
| Read surface invoked | That readable content becomes discovered knowledge | Unrevealed hidden circumstances become known |
| Passive pickup of authored carrier | Preserve factual acquisition and authored origin | Independent narrative demand |

When reproducing the timing race, distinguish an attention arm from delivery: only the subsequent factual attention signal proves interruption. An unobserved target must not be treated as a rejected opportunity.

## Verification

| Claim | Evidence class and limit |
| --- | --- |
| Same owned NPC survives restart and is perceived/conversed with | LIVE-PROVEN historical QUD5 record; unchanged owned identity, separate perception and conversation events |
| Strong attention interrupts active autoexplore; SUBTLE does not; bounded redelivery | LIVE-PROVEN historical accepted gate; early failed race is retained as negative evidence |
| Natural authored clue is acquired/read after successful native realization | LIVE-PROVEN historical; raw factual result separately asserts clue text is not auto-known |
| Perception arriving before hook projection is buffered; restart replays without duplicate notice | TEST-PROVEN existing offline tests |
| Pickup/read no longer imply strong narrative engagement | TEST-PROVEN later correction; improved natural-play quality UNKNOWN |
| Interesting long-running autonomous narrative | UNKNOWN; technical execution and discovery do not establish it |

The September natural-play report explicitly found weak information-only payoffs despite successful manifestations. Do not reuse older green transport gates as a creative quality certificate.

## Gotchas

1. **Symptoms: real perception, no autoexplore stop.** **Cause:** the external control round trip loses the visibility window. **Fix:** pre-arm one bounded exact-target instruction and execute synchronously at native visibility, retaining factual delivery telemetry.
2. **Symptoms: successful result advances to NOTICED without player evidence.** **Cause:** existence and perception were collapsed. **Fix:** require distinct source events and scoped owned IDs for every transition.
3. **Symptoms: reading a book spawns another narrative beat.** **Cause:** the mod's own delivery generated pickup/read evidence, which was mistaken for independently expressed player interest. **Fix:** preserve authored provenance; treat passive acquisition as attention and require an additional intentional interaction or world consequence for fresh authoring.
4. **Symptoms: hidden plan reaches a help response.** **Cause:** external knowledge of an object was mistaken for player-known contents. **Fix:** filter by the actual recipient's knowledge and discovery events. Capability success does not lift that filter.

## Assets

No game screenshots, private transcripts, authored campaign copy, extracted code or save objects are distributed.

## Open questions

The shared [oracle field note](https://github.com/rehan-remade/universal-modder/blob/main/knowledge/techniques/oracles-how-agents-know-a-mod-works.md) explains repeatable mechanical checks and why a fake host is insufficient. This case adds a narrower causal warning: an oracle can be live and technically correct, yet measure an intervention's own side effect rather than independent player agency. In any external-director mod, keep **authored origin → manifestation → discovery → deliberate response** separate so the output does not become its own evidence of demand.

This is a cross-game engineering hypothesis derived from Qud's observed feedback failure, not an experimentally proven rule for every game.

Related field notes: [native save/reload postconditions](bounded-actions-postconditions-and-save-reload-dedup.md); [cross-game causal review](../../techniques/authored-effects-are-not-player-agency-evidence.md).
