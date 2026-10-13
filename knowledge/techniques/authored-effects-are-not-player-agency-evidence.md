---
kind: technique
title: "A live oracle can still misattribute agency: authored effects versus player response"
status: in-progress
agents: ["Codex (GPT-6)"]
humans: ["jkjkj2805"]
date: 2026-10-13
links: []
tags: [oracle, causal-provenance, game-bridge, postconditions, idempotency, knowledge, player-agency]
---

# A live oracle can still misattribute agency: authored effects versus player response

> A screenshot or event can be current, correctly scoped, and mechanically accurate while supporting the wrong causal conclusion. An external game director may create a clue, observe its pickup, and mistakenly treat that side effect as evidence that the player wants another story beat. Preserve the origin and meaning of observations so a successful intervention does not manufacture its own demand.

## When to use it

Use this check in any mod that observes the player and proposes new world effects in response: AI directors, adaptive encounters, narrative tools, or agent-controlled test bridges. It extends [the general oracle method](https://github.com/rehan-remade/universal-modder/blob/main/knowledge/techniques/oracles-how-agents-know-a-mod-works.md) and [mod-side command-file automation](https://github.com/rehan-remade/universal-modder/blob/main/knowledge/techniques/driving-a-game-from-a-mod-side-command-file-lab-profile-wake.md); it does not replace their liveness, main-thread, isolated-profile or duplicate-command checks.

## How

Keep a causal chain of separately proven steps:

`authoring intent → bounded dispatch receipt → observed effect → recipient discovery → deliberate response`

1. **Receipt identity:** bind the command to the exact world, runtime/session attachment, applicable epoch/lease and location. Keep a stable action identity plus a fingerprint of its bounded arguments. A repeated ID with changed arguments is a conflict; a timeout is not a new permission to execute.
2. **Native postcondition:** after dispatch, inspect the actual owned object or changed native value. Record accepted, performed, certain/uncertain and each postcondition separately. An API acknowledgement alone cannot prove an effect.
3. **Object-to-receipt link:** persist an owned content identity derived from that action, or a native state ledger when no object is created. Do not join by display name, mere temporal proximity, or a reused native ID outside its scope. Missing objects do not automatically authorize recreation.
4. **Authored origin:** carry the intervention's origin into later perception/acquisition events. Preserve raw observations; classify their meaning in a rebuildable projection. Picking up a director-created carrier can prove attention without proving independent player investment.
5. **Knowledge:** discovery of an object is not discovery of its hidden contents. Keep world truth, current observation, recipient-known information and hidden authoring commitments distinct. A help/advice path must not inherit unrevealed plans from the director.
6. **Discontinuity:** after an epoch change, rewind, unknown observation gap or replacement of the world attachment, require fresh attestation. Historical evidence may remain useful history; it is not a live target or a causal bridge across an unproven gap.
7. **Trigger meaning:** let independently evidenced deliberate interaction or world consequences justify follow-up. Do not promote every owned-carrier pickup to fresh demand, and do not infer disinterest from absence of perception. WAIT/ignore remains a valid outcome.

Apply these fields at the existing observation/execution boundary. This does not require a second planner, new memory system, or an LLM that classifies engagement.

### Minimal counterfactual review card

Hold the same factual observation constant while reviewing its origin and supported meaning. This is an explanatory checklist, not a new experiment or a universal game policy.

| Evidence | Keep in history/knowledge as applicable | Fresh authoring demand? |
|---|---|---|
| Passive pickup of a director-created carrier | Yes; retain authored-origin link | Not from pickup alone |
| No perception of a created carrier | Historical creation only; do not grant hidden knowledge | No inferred rejection |
| Deliberate interaction or independent consequence | Yes; retain its own source | Eligible for assessment, not compulsory authoring |
| Repeat of one execution identity | Original factual receipt | No duplicate effect or fresh event |

If a source is missing or crosses an unproved world/epoch/gap boundary, keep the causal link UNKNOWN rather than joining by name or time. This leaves deliberate player refusal and WAIT available.

## Verification

The Qud case behind this note is documented in [manifestation/discovery and attention](../games/caves-of-qud/manifestation-discovery-and-attention-oracles.md) and [native postconditions/replay suppression](../games/caves-of-qud/bounded-actions-postconditions-and-save-reload-dedup.md). Historical private real-game evidence showed mechanical manifestation, perception and a self-propagating proposal after acquisition of an authored carrier. It did **not** show a second manifested carrier from that specific proposal.

The later suppression of owned passive-attention triggers is offline-test-proven. Better natural-play quality after that change remains UNKNOWN. General usefulness in other games is an engineering hypothesis; it has not been experimentally established across all games.

For a minimal negative oracle, hold the observed pickup constant and change only its authored-origin classification. It must still remain in raw history and recipient knowledge, while passive pickup alone must not create a new authoring opportunity. A deliberate conversation or independently observed consequence should still be eligible. Separately replay an exact command and assert no new object, delta or event; changed fingerprint, stale epoch and missing target must fail closed.

## Gotchas

1. **The oracle is alive, so every inferred conclusion is accepted.** **Cause:** liveness checks validate freshness, not causal interpretation. **Fix:** name the narrow claim each observation supports: exists, visible, acquired, read, deliberately pursued, or unresolved.
2. **The model's output becomes evidence for its next output.** **Cause:** authored origin is lost between execution and observation. **Fix:** retain the action/content join and interpret owned passive interaction conservatively without erasing it.
3. **A restart resurrects deleted content.** **Cause:** a retry sees local absence but ignores a persistent success ledger. **Fix:** reconcile the original receipt; uncertain local absence is not permission to repeat the effect.
4. **Old events reveal future knowledge after reload.** **Cause:** world identity was used without timeline ancestry. **Fix:** filter current context by provable lineage; keep raw history for forensic inspection.

Related field notes: [Barotrauma headless item oracle](../games/barotrauma/item-spawn-callback-scene-oracle-and-proof-boundaries.md); [DS2 render lifetime and proof limits](../games/dark-souls-ii/visible-arsenal-six-slot-cosmetics.md).
