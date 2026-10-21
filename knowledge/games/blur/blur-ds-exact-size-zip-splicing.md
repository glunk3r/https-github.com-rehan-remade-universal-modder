---
kind: game
title: "Exact-size zip splicing for Blur DS texture edits, and the deflate wall that stopped a car model swap"
game: "Blur"
games_also: []
game_version: "Blur DS beta, Europe, unreleased; 64 MB NDS ROM, title BLUR, game code BBRP, maker code 36"
platform: console
engine: unknown
route: asset-only
tools: ["Python 3 (struct, zlib)", "melonDS 1.1", "COLLADA .dae mesh round-trip"]
anti_cheat: "none — unreleased offline beta"
status: in-progress
agents: ["OpenCode (DeepSeek V4.1 Flash Free)"]
humans: ["@GeoffreyMba"]
date: 2026-10-21
links: []
tags: [nds, zip, deflate, exact-size, splicing, texture, palette, firebrand, octane, blur, rom-patching]
---

# Exact-size zip splicing for Blur DS texture edits, and the deflate wall that stopped a car model swap

> Blur DS keeps every asset in a plain `vfs.zip` sitting at a fixed offset inside a 64 MB NDS ROM, so
> anything that changes an entry's compressed size shifts every offset after it. I wrote car-texture edits
> into unused palette space and spliced the resulting deflate streams back at **exactly** their original
> lengths, producing a ROM with the zip byte-size unchanged and all 3,146 entries intact. The same
> exact-size constraint is what killed the car model swap: rebuilt meshes compress 25–30% worse, and the
> small LODs cannot be squeezed back to their original length. The texture ROM is structurally verified;
> **it was never confirmed booting in-game**, so treat it as unverified. Status `in-progress`.

## Setup

- **Game:** Blur (DS), Europe beta, unreleased — the DS counterpart to the 2010 console title. 64 MB
  (67,108,864-byte) NDS ROM, title `BLUR`, game code `BBRP`, maker code `36`.
- **Engine:** Firebrand Octane, the same pipeline as TrackMania DS / Turbo DS and GRID DS — `vfs.zip`
  container, `.n` models in the Turbo-DS short-extension style, NitroSDK 2D formats, Lua 5.1 bytecode.
- **Container:** `vfs.zip`, **24,658,789 bytes, 3,146 entries**, stored in the ROM at `0x021C4800` and
  ending at `0x03948B65`.
- **Tools:** Python 3 with `struct` and `zlib` only; melonDS 1.1 to launch; COLLADA `.dae` export for
  mesh comparison.

## Route and why

`asset-only`, because the goal was a content change on an offline beta with a plain-file container.

- **`data`** would have changed the car roster or stats, not the visuals — easier, but not the goal.
- **`native-hook` / loader** means patching ARM9 on a retail NDS ROM with no loader ecosystem. Far more
  risk than the task justified, and it fails the moment anything re-reads the cartridge image.
- **`decomp-recomp`** — no decompilation of this engine exists.

Asset-only is the right call *provided* you can write into the ROM without moving anything. That
constraint turned out to be the whole project.

## How the game works (what we had to learn)

### The container is a stock zip at a fixed offset

`vfs.zip` is a normal, uncompressed-container Deflate zip: local headers, compressed streams, then a
central directory and end-of-central-directory record. Because the whole archive sits at one fixed ROM
offset, **any change to any entry's compressed size shifts every byte after it** and invalidates the
central directory's offsets. On a 64 MB cartridge image that is not a problem you can paper over with a
rebuild — it is the problem.

The workable consequence: if you can produce a new Deflate stream of **exactly** the old `csize`, the
archive's layout is untouched, and you only have to overwrite those bytes in the ROM.

### Car meshes and their LOD ladder

Cars live under `Graphics/Cars/<car code>/<variant>/`, each with an eight-file LOD ladder:
`lod0`, `lod1`, `lod1net`, `lod2`, `lod3`, `lod3net`, `lod4`, `lod4net`. There are 24 car directories, so
24 `lod0` targets — and the small LODs are the ones that matter for the size problem.

`.n` files carry GX-style primitives (tri-strips, triangles, quads) and palette-indexed textures. Two
palette groups showed up repeatedly, a body palette (`custom_pl`) and a reflection palette (`envmap_pl`).

### Free palette pairs are the writable real estate

A car's texel data is palette-indexed. Some palette index pairs are **never referenced by that mesh's
UVs** — dead entries. Writing into the texel regions those pairs cover changes the image without
touching anything the model actually samples. That is the trick that makes a texture edit possible under
an exact-size budget: you are changing bytes that the original compressor already had to encode, in a
region whose colour statistics you can keep close to the original.

In practice the patch pass located a rectangular site per car, wrote a label into it in a single flat
colour, and then recorded four numbers: how many blocks changed, how many bytes changed, whether anything
inside the site was invalid, and **whether anything outside the site changed at all**.

### The exact-size splice

For each patched `.n`:

1. Recompress the modified file.
2. Tune the stream until its length equals the original entry's `csize` exactly.
3. Overwrite that entry's stream in a copy of `vfs.zip`.
4. Recompute nothing — the central directory CRCs are per *uncompressed* data, so they still have to be
   updated, but every offset stays valid because no length moved.

Every spliced entry in the log reports `stream exact`, which is the invariant that matters.

## Build steps

1. Extract the ROM and locate `vfs.zip` (offset and length above).
2. Inventory entries and record each entry's `csize` — that number is your hard budget.
3. For a texture edit, find palette pairs the mesh never references, pick a texel site, write into it.
4. Recompress and force the stream to the original `csize`.
5. Splice the streams into a copy of `vfs.zip`; assert the archive length is unchanged.
6. Overwrite only the zip region in the ROM image.

## Verification

**Structurally verified:**

- `testzip`: **ALL OK** on the rebuilt archive.
- Per-entry round-trip CRC for all 24 spliced entries.
- Central directory CRC records re-verified.
- **Archive size identical**: 24,658,789 bytes before and after.
- **ROM writes stayed inside the archive**: 1,614,744 bytes changed, all within the zip range.
- **Geometry untouched**: exported `.dae` for original vs patched car is identical apart from the
  exporter's `<created>`/`<modified>` timestamps — 391 lines each, 4 differing lines, all timestamps.
- Texture-patch pass: **24/24 cars** patched, each with `verify_changed_outside: 0`.

**Not verified:**

- **The modded ROM was never confirmed running.** No screenshot, no emulator log, no in-game observation —
  the pipeline ends at a written ROM and an MD5. Everything above proves the file is structurally sound,
  not that the game accepts it.
- Whether the patched texels are actually invisible on the car. Free palette pairs are *unreferenced by
  the mesh*, which is a strong argument, but it was never confirmed on screen.

Original ROM MD5 `B8D258ED8F761D08C1DE857CCBB27402`; patched `37E9309E32985D55E6FDCF25BCB22E28`.

## Gotchas

1. **The model swap died on the small LODs, not on the big one.** **Symptom:** rebuilt meshes fitted,
   encoded and validated cleanly, but could not be compressed back to the original length.
   **Cause:** the rebuilt data is roughly **25–30% less compressible** than the original, because the
   original exporter's mesh quantization is something Deflate exploits and a naive rebuild is not.
   **Measured gap:** `lod0` came in **174 bytes under** target (a near hit); `lod1` ~3.5% over;
   `lod1net` ~5% over; `lod2` ~12% over; **`lod3` and `lod3net` ~29% over**; `lod4`/`lod4net` ~18% over.
   **Fix:** none found. The big LOD is achievable; the small ones are the wall. If you retry, the move is
   to reproduce the original quantization rather than to find a better compressor.
2. **`19/24` on the first texture pass, `24/24` on the second. Symptom:** five cars failed with
   `no free palette pair`. **Cause:** some meshes reference every palette pair in their body palette.
   **Fix:** widen the search to a cross-palette region (the reflection palette) instead of only the body
   palette. Budget the writable area per car rather than assuming it exists.
3. **A single byte of size drift invalidates the whole archive.** **Symptom:** anything that recompresses
   an entry normally makes the game's reads land on garbage after that point. **Cause:** every central
   directory offset is relative to the archive start, so a longer stream moves all of them.
   **Fix:** treat `csize` as immutable and assert it before writing, per entry.
4. **"It recompressed fine" is not verification.** **Symptom:** a stream that decompresses correctly but
   is the wrong length looks healthy in isolation. **Cause:** correctness and length are separate
   properties. **Fix:** check both, per entry, and assert the archive length is unchanged as a whole.
5. **Exported-mesh diffs lie about timestamps.** **Symptom:** comparing original vs patched `.dae` reports
   four changed lines and looks like geometry drift. **Cause:** the exporter stamps `<created>` and
   `<modified>` per run. **Fix:** ignore those two elements when hashing or diffing, or normalise them
   first — otherwise you cannot tell "geometry is identical" from "geometry moved slightly".
6. **Package name collisions bite on a 24 MB archive with 3,146 entries.** Keep the modified archive and
   the ROM copy distinct until the splice is verified; an in-place rewrite with a bad entry is not
   recoverable without the original image.

## Assets

None shipped. The replacement car model used as a test payload came from an unrelated commercial title
and is not redistributable; no game files, extracted textures or ROM images are included here.

## Cost and time

Several sessions. The texture-patch path converged in two passes; the model-swap path consumed most of the
effort and ended without a working result.

## Open questions

- **Does the patched ROM actually boot?** This is the single missing check and it is cheap: load it in
  melonDS and look at a car. Until then the texture work is structurally sound and unproven.
- **Are free palette pairs genuinely invisible?** Unreferenced-by-UV is a strong signal, not a guarantee;
  a mip or a second UV set could still sample them.
- **Can the model swap be made size-exact?** Only by matching the original quantization, not by improving
  Deflate. Measure the original's quantization first, then fit to that — not the other way round.
- **Where is the practical ceiling?** If `lod3` needs 29% more bytes than exist, sub-lod3 mesh replacement
  may simply be off the table for this engine, and the realistic target is `lod0`/`lod1` only.
