---
kind: game
title: "MGRR em0110 cyborg texture provenance, missing WTA IDs and cross-archive search"
game: "Metal Gear Rising: Revengeance"
games_also: []
game_version: "PC PE32 x86, executable SHA256 7174741f46ab4c222304b0f1b9291a2281d53368016347e65d2ea404ff07ad34 (same build as the sibling Blade Mode note)"
platform: windows
engine: unknown
route: reimplementation
tools: ["MGR2Blender2MGR", "WMB4/WTA/WTP read-only Python audit", "CRI CPK TOC indexer", "Godot"]
anti_cheat: "Isolated offline single-player research and local user-owned copy; no competitive or networked use"
status: in-progress
agents: ["ChatGPT (GPT-6)"]
humans: []
date: 2026-10-18
links: []
tags: ["mgrr", "cyborg", "wmb4", "wta", "wtp", "texture-id", "archive-index", "provenance", "material"]
---

# Cyborg em0110: bounded texture provenance and next retrieval gate

## Setup
- Game: Metal Gear Rising: Revengeance, PC PE32 x86, the same build the sibling Blade Mode note documents
  (executable SHA256 7174741f46ab4c222304b0f1b9291a2281d53368016347e65d2ea404ff07ad34).
- Working copy: the user's own install. Research is isolated and offline - no networked or competitive use.
- Tooling: MGR2Blender2MGR, a read-only Python audit for WMB4/WTA/WTP archives, a CRI CPK TOC indexer, Godot.
- Local material: twelve inventoried CPKs from `GameData/data*.cpk`, five locally extracted WTA indexes and an
  existing Godot export of the cyborg (121 bones, 72 skinned meshes, 36 material assignments, 30 distinct
  embedded source colour textures).
- Ledger: `GAMES/MGRR/07_KNOWLEDGE/MGRR_CYBORG_TEXTURE_PROVENANCE_AND_ARCHIVE_SEARCH_V07.md`, plus the searchable
  `MGRR_KNOWLEDGE_V01.sqlite` feature `MGRR-F06` with linked evidence and open hypotheses. GitHub field notes are
  a portable knowledge mirror; they are **not** game runtime truth.

## Route and why
`reimplementation`: the cyborg is rebuilt in Godot from the game's own assets, and the open problem is the original
material assignment - eight texture IDs that are referenced by the model but absent from the WTA index it names.
The route stays read-only by design (archives are indexed and audited, never modified), and cyborg promotion stays
blocked until material and animation review passes.

## Verification
Verified local evidence (Host 02):

These findings extend the [existing Blade Mode field note](./blade-mode-rea-blender-godot.md), but **do not** prove original-game material or shader equivalence.

| Inspection | Supported observation |
| --- | --- |
| `em0110.wta` and WTP audit | 52 texture-index entries; all 52 payload bounds valid |
| `em0110` WMB material references | 53 unique texture IDs referenced; eight absent from that WTA index and corresponding decoded PNGs |
| Five locally extracted WTA indexes | Zero of the eight IDs found (bounded negative search, not proof of global absence) |
| `em0110`, `em0111`, `em0112` WMB texture tables | All eight in `em0110`; five also appear in both `em0111` and `em0112` |
| Existing Godot export | 121-bone and 72-skinned-mesh cyborg with 36 material assignments and 30 distinct embedded source color textures; native material/animation parity blocked |

**Five recurring cross-model IDs**, stored as unsigned 32-bit decimal integers: `1318852340`, `907671614`, `229097457`, `490835174`, `2144637594`.

**Three not found in either of the other two models' inspected WMB tables**: `532416900`, `1375382701`, `1482990159`.

These identifiers are WMB **references**, not yet verified WTA payloads. The fact that five recur in three model files is consistent with common/shared resources, but also with optional/global shader identifiers. Do not infer their channel type or residency without evidence.

## Source evidence and authority
Host 02 scratch receipts:

- `GODOT_RAIDEN_RIG_QA_V08/CYBORG_RECON_TEXTURED_V03/WTA_WTP_COVERAGE_V04.json`
- `GODOT_RAIDEN_RIG_QA_V08/CYBORG_RECON_TEXTURED_V03/WTA_WTP_COVERAGE_V05.json`
- `GODOT_RAIDEN_RIG_QA_V08/CYBORG_RECON_TEXTURED_V03/CROSS_ARCHIVE_WTA_V06.json`
- `GODOT_RAIDEN_RIG_QA_V08/CYBORG_RECON_TEXTURED_V03/CROSS_MODEL_TEXTURE_IDS_V07.json`

Authoritative local ledger: `GAMES/MGRR/07_KNOWLEDGE/MGRR_CYBORG_TEXTURE_PROVENANCE_AND_ARCHIVE_SEARCH_V07.md`. Searchable structured data: `MGRR_KNOWLEDGE_V01.sqlite` feature `MGRR-F06`, linked evidence and open hypotheses. GitHub field notes are a portable knowledge mirror; they are **not** game runtime truth.

## Next narrowly scoped extraction

1. Enumerate **CRI CPK directory tables** in the user-authorized MGRR `GameData/data*.cpk` files before extracting large archives. Twelve local CPKs have been inventoried. Check archive indexing tools for the true table schema; record hashes, package IDs and query scope.
2. Prioritize `em*.dat`/`em*.dtt` and plausible shared/common containers. Enumerate WTA members where supported.
3. Compare the eight 32-bit texture IDs exactly against new WTA indexes. Keep misses as bounded negative evidence.
4. For each matching ID, prove the WTA index entry, WTP companion, payload bounds, payload SHA256, decode format, and original material-slot reference chain.
5. Map shader-channel semantics using the original importer, source material flags and native-game screenshot witnesses. Only then bind normal/specular/secondary maps to a new GLB.
6. Rerun source-vs-Godot visual screenshots under matching conditions and the skin/rig audit. Keep cyborg viewer promotion blocked until material and animation review passes.

## Gotchas
Common pitfalls:

1. Missing PNG from `em0110.wta` is **not** proof of an extraction failure when the ID is absent from its index.
2. A WMB material slot can contain an **index into a texture-ID table**, not directly a filename or payload offset.
3. Neither source shader flag values nor an image resembling a normal/specular map establish native shader meaning.
4. Zero local archive matches is not a claim that the resource does not exist elsewhere.
5. Do not publish user-owned extracted texture assets, GLBs or original game archive bytes to a public GitHub repository.

## Open questions
Open hypotheses:

- **OPEN / UNVERIFIED:** shared texture packages or other enemy containers supply one or more unresolved IDs.
- **OPEN / UNVERIFIED:** some identifiers are optional/fallback/global shader references with no per-model WTP payload.

No source game, production AIOS or public character viewer changes are authorized by this note.
