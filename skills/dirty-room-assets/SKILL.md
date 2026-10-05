---
name: dirty-room-assets
description: Extract as much of the original game's content as possible - models, textures, sprites, animations, SFX, music, VFX, UI - into a private dirty-room reference library, measure it, and turn it into clean-room briefs so new assets match the original's style, proportions, timing and sound without copying it. Use before generating any asset for a remake, e.g. "pull everything out of <game> so we can match it", "make our sword swing feel like theirs", "what does their explosion VFX consist of".
---

# Dirty room -> clean room (assets)

Two rooms, one direction of flow:
- **Dirty room** (`dirty/<game>/`, local only, never committed or shipped): the original files, extracted
  and decompiled. You may look at, play, measure and compare against anything here.
- **Clean room** (`remakes/<game>/`): only original work. It receives **briefs and measurements**, never
  the original files. The rule that keeps the remake clean: **no original asset is ever an input to a
  generator or a copy** - no img2img, style-transfer, voice/audio cloning, tracing or re-export of an
  original. Text briefs, measured numbers and side-by-side human/agent review are fine.

## 1. Extract (dirty room)
Pull everything, organised by type under `dirty/<game>/raw/<type>/`. Per engine:
- **Unity:** AssetRipper (full project export, incl. animations), UABEA, UnityPy (`asset-pipeline` notes
  on memory).
- **Unreal:** FModel (meshes, textures, anims, sounds, Niagara/Cascade), UAssetGUI for data tables; UE5
  needs the right AES key only if the user's own install exposes it - never crack encryption.
- **Godot:** gdsdecomp (GDRE Tools).
- **Source / id / custom:** Crowbar, QuickBMS with a matching script, the `reverse-engineering` skill for
  unknown formats (prove each format with a round trip).
- **Audio:** vgmstream for game codecs; Wwise/FMOD banks via their community extractors.
- **Anything rendered:** RenderDoc frame captures (offline mode only - never on an anti-cheat client) for
  meshes, materials and VFX particle setups that don't extract cleanly.
Keep the extraction log (tool, version, command, counts) in `dirty/<game>/EXTRACT.md`.

## 2. Measure -> `dirty/<game>/manifest.json`
One entry per asset that matters to the remake, with numbers a generator or animator can hit:
- **Models:** tri count, bounds/scale in metres, pivot, bone count & hierarchy, LODs, material slots.
- **Textures/sprites:** resolution, texel density, palette (top colours), frame count, sheet layout.
- **Animations:** duration, frame rate, root motion, key poses and contact frames, event timings
  (hit frame, footsteps), loop points.
- **SFX/music:** duration, loudness (LUFS), peak, frequency character, layers, loop points, triggers.
- **VFX:** emitters, particle counts, lifetimes, colours over life, timing relative to the event.
- **UI:** layout grid, font metrics, colours, icon sizes.
Use contact sheets (`um sprite`, Blender renders) to review whole sets at once.

## 3. Brief (the hand-off)
Write `remakes/<game>/ASSET_BRIEFS.md`: one brief per asset or family - purpose, the measured targets from
the manifest, the style in words (shape language, palette ranges, material feel, timing feel), and what
must differ. This file is the only thing that crosses from dirty to clean.

## 4. Produce and match (clean room)
Generate or build new assets from the briefs (`fal-assets`, `asset-pipeline`, Blender), then compare
against the dirty reference **by measurement**: proportions, durations, frame timings, loudness, palette
distance. Iterate until the numbers match and the side-by-side reads as the same game feel - not the same
pixels. Record each asset's brief, generator and settings in `remakes/<game>/ASSETS.md` (provenance).

## Never
Commit, publish or ship anything from `dirty/`. Feed an original file to a generator. Re-export an
original under a new name. Download game files you don't own.
