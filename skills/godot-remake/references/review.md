# Reviewer pass (clean-room + spec conformance)

Run by an agent that did **not** build the slice, ideally on a different model. Input: the remake folder,
`SPEC.md`, `acceptance.json`, `um remake status` and `um remake leak` output. Output: a findings list.
The reviewer does not edit code, specs or checks.

## Spec conformance
- Every claim in the slice's SPEC.md sections with a number or a rule has an `acceptance.json` check.
  List claims without one.
- Every check's tolerance matches the evidence in SPEC.md (not wider). Compare against the check's git
  history: a tolerance widened, a case removed or a `required: false` flipped right before it passed is a
  finding.
- Tuning constants in code (speeds, timers, damage, gravity) equal the SPEC.md values, or the deviation is
  written in SPEC.md with a reason.
- Every behaviour that differs from the original is a named fix flag in SPEC.md, off by default. A
  silent fix (an original bug quietly not reproduced) is a finding.
- Scenarios assert the claim itself (an apex height, a cooldown in frames), not a proxy that always holds.
- `um remake status` shows checks pass and integrated at the **current** revision. Stale counts as no.

- No level/asset special cases in `src/core/`; overrides are data listed in `docs/overrides.md`.
- No check deleted, case removed or tolerance loosened without a SPEC.md line citing evidence.
- Evidence citations are pinned (`<exe sha>:<addr>`, experiment/run id + git SHA).

## Clean room
- `um remake leak <game>` exits 0. Read every hit it reports even if someone marked it "fine".
- No file in the remake was copied, re-exported, traced or renamed from `dirty/`; `assets.json` lists a
  generator or "hand-made" for every asset, and no generator setting points at a dirty file (no img2img,
  style or voice reference from originals).
- No code reads like a translation of decompiled functions: same odd constants in the same order, same
  quirky control flow, decompiler-style names (`FUN_`, `param_1`, `uVar3`) or comments with addresses.
  Shared numbers from SPEC.md are fine; shared structure is not.
- Each module has `docs/provenance/<module>.md`, and its implementer was not the agent that read the
  decompile.
- Nothing under the remake references `dirty/` paths (scripts, `.tscn` ext_resources, export presets).

## Report
One line per finding: file or check id, what is wrong, the evidence (line, value, command output).
"No findings" plus the list of what was checked is a complete report.
