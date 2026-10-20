---
kind: game
title: "bnd2 containers and the Renderable vertex format in Burnout Paradise (vehicle geometry swap not finished)"
game: "Burnout Paradise"
games_also: ["Burnout Paradise Remastered"]
game_version: "Burnout Paradise: The Ultimate Box, PC/Steam — vehicle bundle VEH_PEUS4B2_GR.BIN, 1,379,237 bytes, 194 resources"
platform: windows
engine: unknown
route: asset-only
tools: ["Python 3 (struct, zlib)", "Blender 5.0", "community Burnout Paradise bnd2 Blender addon", "custom bnd2 unpacker/repacker"]
anti_cheat: "none — offline single-player only, never launched with an online session"
status: abandoned
agents: ["OpenCode (DeepSeek V4.1 Flash Free)"]
humans: ["@GeoffreyMba"]
date: 2026-10-20
links: []
tags: [bnd2, renderable, vertex-format, bundle-container, reverse-engineering, vehicle, criterion, zlib, round-trip]
---

# bnd2 containers and the Renderable vertex format in Burnout Paradise

> I reversed the `bnd2` bundle container and the `Renderable` resource layout in Burnout Paradise far
> enough to unpack a stock vehicle bundle and repack it **byte-identically** (582/582 resources across the
> files tested), and to read the vehicle's vertex and index data out into a normal 3D format. I did **not**
> finish the swap: a hand-built `Renderable` payload never produced a bundle the game would accept, so no
> mod ever ran in-game. Everything below is either verified by round-trip or marked as unverified. The
> container work is solid; the `Renderable` writer is where it stops.

## Setup

- **Game:** Burnout Paradise: The Ultimate Box, PC/Steam. Both TUB and Remastered ship the same `bnd2`
  container (Remastered is a later re-export with the same magic and header layout), so the container
  findings apply to both. All numbers below come from TUB.
- **Bundle examined:** a car's graphics bundle, `VEH_PEUS4B2_GR.BIN` — 1,379,237 bytes, 194 resources,
  15 `Renderable` resources, and a `GraphicsSpec` describing 27 parts. `PEUS4B2` is the internal vehicle
  code; the same layout held for the other car bundles I opened.
- **Tools:** Python 3 with only `struct` and `zlib`; a community Blender addon that imports Burnout
  Paradise bundles into Blender 5.0 (useful for eyeballing geometry, not for the format work); a custom
  unpacker/repacker written from scratch.
- **Nothing installed into the game folder.** All work was on copied bundles. The original bundle is the
  only source of truth and must be re-extracted from the install before any retry.

## Route and why

`asset-only`, because the goal was to replace one car's mesh with another car's mesh, not to change code.
The alternatives and why I skipped them:

- **Loader/hook route (`native-hook`)** — could intercept the mesh upload, but Burnout Paradise has no
  supported mod loader and you would be reimplementing resource lookup. Way more surface area than editing
  a file the game already reads.
- **`decomp-recomp`** — there is no decompilation of this engine and the tooling investment dwarfs the task.
- **`data`** — the vehicle roster and handling live in separate data files; that changes *which* car you
  drive, not what it looks like. Not the goal, but it is the easier mod if someone just wants a different
  car.

Asset-only is correct: the game loads bundles from disk, so a valid bundle with different geometry should
just work. "Should" is the whole problem — see Gotcha 2.

## How the game works (what we had to learn)

### Container: `bnd2`

Every `.BIN`, `.BNDL`, `.BUNDLE`, `.DAT` and `.HM` begins with the ASCII magic `62 6E 64 32` (`bnd2`),
so the extension tells you nothing about the contents. Assets are addressed internally by `gamedb://`
virtual path plus a numeric ID, and the internal project name is `burnout5`; this note is about the bytes.

- Header is **0x30 bytes**: magic, a version/flags pair, total length, an entry count and the offset of
  the entry table. A **global flags word** decides whether the data area is zlib-compressed (bit `0x1`).
- The entry table has a fixed **stride of 0x40 bytes** per resource and sits inside the same file.
- Each entry starts with the resource's **8-byte ID**, then **three parallel size/offset triples**. A
  resource can have up to three portions (the ones I saw used at most two: a "main" portion and a
  "graphics" portion). For each portion there is an uncompressed length, an on-disk length, and an offset
  into the data area.
- The **high nibble of the on-disk length carries the alignment**; the low 28 bits are the length. Mask
  with `0x0FFFFFFF` before comparing lengths, or every size check is wrong.
- After the triples come the **resource type**, an **import count**, and the **import table** pointer.
  `0x0C` is `Renderable`, `0x2A` is `RwMaterial`, `0x0E` is `TextureState`, and the `GraphicsSpec` type is
  `0x10006`.
- Compression is plain **zlib**, not the raw deflate some RenderWare-derived engines use. `zlib.decompress`
  works directly on the on-disk bytes.

The exact byte offsets of the three triples inside the 0x40 entry are recorded in the code I wrote but I
would not publish them as gospel — I read them back correctly in every file I tested, and the round-trip
proves self-consistency, not that I named the fields right.

### `GraphicsSpec`: 27 parts, 15 unique geometries

The car's `GraphicsSpec` resource lists **27 parts** that reference `Renderable` resources by their
**CRC32-derived 8-byte IDs**. Only **15** distinct `Renderable` resources back those 27 parts — the rest
are material variants that reuse the same mesh. This matters: if you write 27 meshes you have written 12
duplicates, and the game loads both copies.

### `Renderable`: two portions

A `Renderable` is split into a **main portion** and a **graphics portion**, each independently compressed.

**Main portion:**

- Starts with an **AABB**: centre `(x, y, z)` and a radius as four floats at offset 0.
- At **0x10**: `version` and `num_meshes` as two `u16`s.
- At **0x14**: a pointer to the mesh table.
- **Mesh records are 0x60 bytes each** and reference the vertex buffer, the index buffer and the material.

**Graphics portion:**

- A **`u16` index buffer first**, then the **interleaved vertex buffer**.
- **Vertex stride is 56 bytes:**
  `position(3×f32) + normal(3×f32) + uv0(2×f32) + uv1(2×f32) + tangent(4×f32)`.
- Vertex descriptor attribute type codes: **`0x01` position, `0x03` normal, `0x05` UV, `0x0F` tangent**.
  `0x05` appears twice (uv0 and uv1) at different offsets in the descriptor.

### Coordinate and UV conversion

Geometry authored in a conventional right-handed setup (a GTA V model in my case) has to be rotated into
Burnout's convention, or the car arrives on its side:

- position/normal: `(x, y, z) → (-z, x, y)`
- tangent: same rotation on xyz, keep `w`
- UV: `(u, v) → (u, 1 - v)`

## Build steps

1. Copy the target vehicle's graphics bundle out of the game install. **Keep an untouched copy** — there is
   no other source of truth.
2. Unpack with a `bnd2` reader: parse the 0x30 header, walk `entry_count` entries at `0x40` stride, and for
   each portion `zlib.decompress` the slice `[data_offset + offset : + on_disk_length]`.
3. Dump each resource to `Type/ID.dat` so you can see the 15 `Renderable`s and the `GraphicsSpec` next to
   each other.
4. Repack **without changing anything** and compare hashes. This is the step that tells you whether your
   reader and writer agree with the game's file format. Do not skip it; everything downstream depends on it.
5. Only then attempt a payload change.

## Verification

- **Verified:** unpack → repack → **byte-identical output for 582 of 582 resources** across the bundles
  tested. This means the header, the entry table, the size triples, the alignment nibbles, the compression
  and the offsets are all understood well enough to reproduce the file exactly.
- **Verified:** the vertex stride, attribute codes and coordinate conversion were checked by parsing a stock
  `Renderable`, converting it to a normal mesh, and looking at the result — the car is upright and correctly
  proportioned with the conversion applied, and rotated/inside-out without it.
- **Verified:** the 27-parts-to-15-renderables ratio, by parsing the `GraphicsSpec` reference list.
- **NOT verified:** that any hand-built `Renderable` loads. No generated bundle was ever accepted by the
  game. This is the honest verdict on the whole exercise — the format reading is right, the writer is not.
- **NOT verified:** texture replacement. DXT5 extraction worked; DXT1 extraction was partial and re-encoding
  was never attempted.

The round-trip being clean is precisely why the failure is interesting: a perfect container rebuild proves
nothing about whether the payload is a valid asset.

## Gotchas

1. **The packer died with `OSError: [Errno 22] Invalid argument` the moment a bundle had resources with
   imports. Symptom:** `seek()` to an absurd offset during repack, only on files whose entries had a
   non-zero import count. **Cause:** the import-offset fixup loop used the **resource index** as the index
   into the import area, instead of the resource's **own import index**. With 194 resources and single-digit
   imports per resource, `resource_index × 0x10` walks off the end of the file. **Fix:** read the import
   count and import offset **per entry**, then iterate only that entry's imports. Two different loops that
   look identical when every entry has zero imports.
2. **Every "final" build script silently degenerated into `shutil.copy2(original, output)`.** Three separate
   rewrites of the writer ended this way — the code below the debug print was never reached, and the output
   file looked plausible because it *was* a working bundle. **Cause:** the writer was written in one pass
   with a fallback that "temporarily" copied the original, and each iteration kept the fallback. **Fix:**
   make the writer **fail loudly** and add a hard guard: `assert md5(output) != md5(original)`. A build that
   produces the input is not a build.
3. **A byte-perfect container rebuild still gave a game-invalid asset.** **Symptom:** repacked bundle
   round-trips cleanly, but substituting a modified `Renderable` payload changed nothing in-game or crashed
   the loader. **Cause:** container validity and payload validity are independent. The mesh table pointer,
   the AABB, and the per-mesh record fields all have to be internally consistent with the new buffer sizes;
   my first writer copied the original header and only swapped the buffers, so the pointers described the
   old layout. **Fix:** recompute the AABB from the new positions and rewrite the mesh table and its
   pointer to describe the new buffers. I got this far and stopped.
4. **Recompressing everything at zlib level 9 is fine — but only if you rewrite every offset.** Changing the
   compression level changes every on-disk length, which changes every offset after it. **Symptom:** the
   game reads garbage after the first resource. **Cause:** offsets copied from the original entry table.
   **Fix:** never carry an offset across a rebuild; compute the data area layout first, then write entries
   pointing into it. This is also why stuffing a big texture back in at a different size breaks neighbours.
5. **Skipping the coordinate conversion "to save a step" makes the car appear rotated or inside-out**, which
   reads as a broken mesh rather than a broken transform. **Cause:** handedness/up-axis mismatch.
   **Fix:** `(x, y, z) → (-z, x, y)` and flip V in the UVs. Check this before suspecting the vertex writer.
6. **Do not assume the 27 `GraphicsSpec` parts are 27 meshes.** Writing 27 copies triples the file and
   duplicates geometry. **Fix:** group parts by `Renderable` ID first; there are 15.

## Assets

None shipped. The replacement geometry was a car model from an unrelated title, used only as a test payload;
it is not distributable and is not included anywhere in this repository or its history.

## Cost and time

Several long sessions, all local compute. The format work converged quickly; the writer did not converge at
all. Reasonable estimate: 70% of the time went into the `Renderable` writer, which never worked.

## Open questions

- **Does the mesh table pointer need to stay below some size, or be relative rather than absolute?** I
  assumed absolute offsets within the main portion and never confirmed it, because I never got a payload the
  loader accepted.
- **What exactly does the game validate?** The loader may check the AABB against the vertex data, the
  `num_meshes` count against the table, or the index buffer length against a field in the mesh record. Any
  of these would reject a structurally plausible file.
- **Is there a per-`Renderable` checksum anywhere?** None found in the entry table, but nothing was tested
  against a working modified asset, so absence of evidence is weak here.
- **DXT1 re-encoding.** Not attempted. DXT5 read back cleanly.
- **The next move, if someone picks this up:** do not write a writer yet. First take a stock bundle, change
  **one float** in a stock `Renderable`'s AABB, repack at byte level with the container code above, and see
  whether the game accepts it. That single experiment separates "my container is wrong" from "my mesh writer
  is wrong", and it is the step that was skipped here.
