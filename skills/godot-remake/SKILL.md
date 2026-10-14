---
name: godot-remake
description: Rebuild a game in Godot 4 from a written spec and prove every slice works by running it. Covers acceptance checks tied to spec claims, headless scenario tests with edge-case matrices, contact-sheet captures, a live bridge that lets the agent inspect and drive the running game, asset variants with an in-game picker, dirty-vs-clean asset measurement, a clean-room leak scan and reviewer pass, and a browser build friends can join. Use when building or verifying a remake slice, e.g. "build the jump from SPEC.md", "is the movement slice done", "compare our sprites to the original", "let me play the remake with a friend".
---

# Godot remake: build from the spec, prove by running

A slice is done when its checks pass **at the current revision** and the game boots, not when the code
reads right. `um remake` keeps those facts separate and on disk, so they survive restarts and other agents.

```bash
um remake init remakes/<game>                 # Godot project + gd_remake addon + acceptance.json (idempotent; re-run to update the addon)
um remake check remakes/<game> [--slice movement]
um remake status remakes/<game>               # per slice: implemented / checks pass / integrated / played
```

## 1. Spec claims become checks
Every claim in `SPEC.md` that the remake must reproduce gets an entry in `acceptance.json`:
```json
{"game": "<game>", "boot_frames": 120, "checks": [
  {"id": "jump.apex", "slice": "movement", "spec": "SPEC.md#jump", "claim": "Jump apex 2.4 m +-0.05",
   "scenario": "res://tests/scenarios/jump.gd", "required": true}
]}
```
- One check per claim with a number or a rule. Copy the tolerance from the evidence, not from what passes.
- `"scenario": null` is a manual check (feel, look): it never auto-passes and is listed until a human
  confirms it in play.
- Write the checks **before** the slice's code, from SPEC.md alone.

### What SPEC.md must pin down (methods from DevilutionX, The Force Engine, fallout2-ce, openage)
- **One mechanic per file** (`mechanics/<name>.md`) with sources and a **Quirks** section; every quirk
  becomes a case in `cases()`.
- **Evidence level per claim**: `static` (read in the decompile, `fn:<addr>`), `observed` (debugger
  experiment, `exp:<id>`), `golden` (output captured from the original, e.g. seed -> generated level),
  `unverified`. Prefer `golden` for anything a player can measure; a golden table becomes a check that
  diffs the remake's output line by line.
- **Timing**: the original tick rate and its rounding (TFE runs Dark Forces at 145 Hz), what runs per
  tick vs per frame. Set Godot's physics rate to match instead of converting numbers to 60 Hz.
- **RNG**: algorithm, constants, seed source, call order. Reproduce it exactly and add a known-value
  check (the value after 10000 draws), including the original's own bugs.
- **Citations are pinned**: decompile evidence as `<exe sha256 prefix>:<addr>`, observed/golden evidence
  with the experiment or run id and the git SHA it ran at. "The latest run" is not a citation.
- **Open questions**: a divergence you can't explain from evidence goes here and to the human. Never
  close it with a fudge constant tuned until the check passes (PortPS5's "if it needs a hack, stop").
- **Original bugs**: faithful by default. Each deviation is a named flag in the claim (`fix_flag:`),
  off by default; acceptance checks run with all flags off. An unflagged deviation is a review finding.

## 2. Scenarios: one mechanic, every edge case
A scenario builds a tiny world, drives input and asserts. `cases()` is the edge-case matrix: walk the
SPEC's edge cases (zero, max, boundary values, simultaneous inputs, slopes, frame-1 input, network loss)
and keep only those that can really happen.
```gdscript
extends "res://addons/gd_remake/scenario.gd"   # see "Scenario base" below

func cases() -> Array[Dictionary]:
    return [{"name": "flat"}, {"name": "held_jump", "hold": 20}, {"name": "on_slope", "slope": 30.0}]

func run() -> void:
    var p := spawn("res://player/player.tscn")
    p.position = Vector2.ZERO
    press(&"jump")
    await frames(params.get("hold", 2))
    release(&"jump")
    var apex := 0.0
    for i in 90:
        await frames(1)
        apex = maxf(apex, -p.position.y / 100.0)
    metric("apex_m", apex)
    expect_near(apex, 2.4, 0.05, "jump apex")
```
Helpers: `frames(n)`, `seconds(t)`, `press/release/tap(action)`, `expect`, `expect_near`, `expect_eq`,
`metric`, `spawn(scene)`, `params`. Scenarios run headless and in sequence; engine `SCRIPT ERROR` lines
during a case turn it into `error`, so a pass means the case ran clean.
Each case gets `um remake check --timeout` seconds (30 by default). A case whose length real time decides
(separate processes playing a live session) declares its own deadline with `func time_limit_s() -> float`;
size it from what the case waits for, never as headroom for a slow test.

**Contact sheet** (the visual edge-case report): every case of one scenario side by side, labelled,
failures marked red, in one PNG. Look at it once; it shows clipping, z-order, wrong scale and broken
animation that numbers miss.
```bash
um remake grid remakes/<game> tests/scenarios/jump.gd --out /tmp/jump.png --cell 480x270 --at 2
```
Grid cases run at once and share input, so give grids their own input-free scenario (see below).

### Clean-room split: spec writer and implementer are different agents
For each mechanic, the agent that read the decompile writes `SPEC.md` + `acceptance.json` + fixtures and
stops. A **fresh** agent with no conversation history implements it from those files only, told not to
read `dirty/`, the reference room or prior code for that module. Record it in
`docs/provenance/<module>.md`: inputs given, what replaced what, and the limits (procedural isolation on
one machine; says nothing about model training data). Constants not measured from the original are
marked "policy, not measured". (iw4l replaced a module this way after a similarity report.)

### Engine vs content
Generic systems (`src/core/`: movement, combat, AI, netcode) contain no level names, asset ids or
per-level branches. Per-level behaviour is data (`data/levels/<id>.tres|json`) under a named mechanism
key, listed with its reason in `docs/overrides.md`. A special case in core is a review finding.

## 3. Status is four facts, never one
`um remake status` reports per slice, and never merges them:
- **implemented**: every check has a scenario file;
- **checks pass**: every required check passed at the current revision (older results are `stale`);
- **integrated**: the main scene boots headless for `boot_frames` with no engine errors;
- **played**: `um remake played remakes/<game> --capture clip.mp4` recorded a real play capture at this
  revision (`showcase-video` / `um win` to record).
Report exactly those facts. "Checks pass" is not "played"; a worker finishing is not a pass. Verdicts are
computed by `um remake`, never typed by an agent.
- **Prove the run before reading the result.** A scenario asserts its own preconditions first (subject
  spawned, on floor, in frame, input reached it), with failures named "precondition: ...". A failed
  precondition means the run proves nothing: fix the setup, don't read the verdict. A reported bug is
  closed only by reproducing it at the reported spot and showing it clean there and in one neighbouring
  state; green unrelated checks are not evidence.
- **Checks only grow.** Never delete a check or case, loosen a tolerance or flip `required` without a
  line in SPEC.md saying why, citing evidence. Every confirmed bug gets a failing-first case.
- **Probe scenarios are temporary.** Throwaway debug scenarios are deleted before handoff; only
  scenarios tied to `acceptance.json` stay.
The revision hashes the project (not `.md`, `.godot/`, `.import`), so any code or asset change makes old
results stale.

## 4. Live bridge: look inside the running game
```bash
um remake run remakes/<game> --bridge 47800 [--headless] [--scene res://levels/one.tscn]   # prints PID
um remake bridge 47800 tree path=/root depth=3
um remake bridge 47800 get path=/root/Main/Player prop=velocity
um remake bridge 47800 set path=/root/Main/Player prop=position value=[100,200]
um remake bridge 47800 action action=jump pressed=true
um remake bridge 47800 frames n=30
um remake bridge 47800 eval expr="get_node('Main/Player').is_on_floor()"
um remake bridge 47800 screenshot path=S:/tmp/now.png       # windowed runs only
um remake bridge 47800 quit
```
Use it to answer "what is the state right now" with numbers instead of guessing from screenshots, and to
reproduce a bug before writing its scenario. The bridge listens on 127.0.0.1 only and only when started
with `--gd-bridge`; exported builds without that argument never open it. Stop the game with `quit` or
`um win kill <pid>`.

## 5. Asset variants: three answers, pick in game
For each asset brief, make **three** candidates that differ on **one** axis (silhouette, palette weight,
detail density, timing, loudness), named for what they are (`chunky`, `lean`, `ornate`, never `a/b/c`).
Put them in `variants/<slot>/<name>.<ext>` and load the slot in game code:
```gdscript
$Sprite2D.texture = Variants.load("hero")         # or: Variants.bind($Sprite2D, "texture", "hero")
```
In game, **F7** cycles slots and **F8** cycles that slot's variants; `--variant hero=lean` pins one on the
command line (scenarios and grids too). Judge them in the real scene, with real neighbours, then measure
(step 6). Promote the winner, which deletes the losers:
```bash
um remake variants list remakes/<game>
um remake variants promote remakes/<game> hero lean   # -> assets/hero.png; Variants.load("hero") keeps working
```

## 6. Match by measurement
`um remake measure` gives the same numbers for original and remake: image size, opaque bounds, palette,
luminance; audio duration, peak, loudness; glTF tris, bounds, bones, animation lengths.
```bash
um remake measure dirty/<game>/raw --root dirty/<game>/raw --out dirty/<game>/manifest.json
um remake compare <game> [--tol 0.1]   # -> dirty/<game>/compare/index.html (dirty room only)
```
`remakes/<game>/assets.json` maps each clean asset to its brief and the dirty manifest id it is measured
against (`[{"path": "assets/hero.png", "brief": "hero", "ref": "chars/hero_idle.png", "generator":
"fal-ai/...", "settings": {...}}]`). The compare page shows reference and remake side by side with deltas
flagged past tolerance. It references dirty files, so it lives in the dirty room and is never shipped.
Matching means the numbers and the feel agree, not the pixels.

## 7. Clean-room gate: leak scan + reviewer
Before calling a slice done, and before anything leaves the machine:
```bash
um remake leak <game>    # exit 1 on: byte-identical files, near-duplicate images, code sharing decompile shingles, links into dirty/
```
Then a **reviewer** pass, ideally a different model from the one that built the slice, following
`references/review.md`: every claim maps to a passing check, tuning numbers in code match SPEC.md, no
check was loosened to pass, no dirty material crossed over. The reviewer reports; it doesn't fix.

## 8. Play it together (browser)
```bash
um remake serve remakes/<game> --with-server   # web export + local server + room link for a friend on the LAN
um remake serve remakes/<game> --with-server --https   # friends on OTHER machines: Godot web needs a secure context (https), wss relayed on /ws
```
Web builds can't use ENet: networked remakes use `GdNet.server(port)` / `GdNet.client(host, port)`
(WebSocket, works on desktop and web) and read `GdNet.url_param("room")` / `GdNet.url_param("server")`
from the link. The headless server is the authority, as in `multiplayer-remake`.

## 9. Handoff
Long work is split across sessions and agents. Each task keeps an append-only folder
`remakes/<game>/.work/<task>/` (gitignored) of numbered reports `<N>-<name>-<SUFFIX>.md`:
- `FINAL`: done, nobody's move; `PART`: another agent continues; `READY`: the human must play or decide.
  When unsure, pick the suffix that keeps the work on the agent's side.
- Never rewrite an old report; correct it in the next one. Every report has **What was not done** and
  says whether the cause or only the symptom was fixed.
- A fresh agent picking up a stuck task restates the problem from the latest report before touching code.

## 10. Record and improve the instructions
At the end of a session, add to the field note (`share-field-notes`) what the checks caught and what they
missed. If a check or a step here was wrong or missing, propose the exact edit to this skill or SOUL.md as
a diff for the human to approve; never apply it unasked.

## Scenario base
- Write scenarios as `extends "res://addons/gd_remake/scenario.gd"`. It works on a project that was never
  opened in the editor. `extends GdScenario` needs Godot's class cache; `um remake check` imports first,
  so it works there, but the path form never breaks. Same for the net helper:
  `const GdNet = preload("res://addons/gd_remake/net.gd")`.
- `frames(n)` returns after n full physics steps, so physics numbers are exact (30 frames of 980 px/s²
  free fall at 60 Hz = 490 px/s).
- Any `ERROR`/`SCRIPT ERROR` logged during a case makes it `error`; a crash or `quit()` mid-case still
  leaves a result marked `error`, never a silent pass.
- Each case gets a fresh scenario node and released inputs. `--case <name>` runs one case.
- Grid runs share one `Input`, so grid scenarios must not `press()`: build the state directly (spawn at
  the edge, set the velocity) and let it play. Errors in a grid run can't be tied to a cell and mark all
  cells. Grids need a window (no `--headless`).

## Never
- Mark a slice done from a diff, a compile, or a worker's word.
- Loosen a tolerance or delete a case to make a check pass; fix the code or correct SPEC.md with evidence.
- Put dirty files, decompiled code, or the compare page into the remake.
