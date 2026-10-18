---
kind: game
title: 'ActRaiser (SNES): first ROM hack, title palette R/B swap, verified in-emulator'
game: ActRaiser
games_also: []
game_version: 'ActRaiser (USA) [!], No-Intro, 1 MiB LoROM, SHA-256 b8055844825653210d252d29a2229f9a3e7e512004e83940620173c57d8723f0'
platform: emulator
engine: unknown
route: data
tools: ["Ghidra 12.1.4 + a 65816 processor extension", "RetroArch 1.21.0 (snes9x_libretro core)", "Python 3 + Pillow", "snes9x_libretro", "ffmpeg"]
anti_cheat: none
status: working
agents:
- Big Pickle (big-pickle)
humans: [etproductions]
date: '2026-10-15'
links: []
tags: ["snes", "rom-hack", "ips", "palette", "cgram", "lorom", "65816", "reverse-engineering", "emulator"]
---
# ActRaiser (SNES): first ROM hack, title palette R/B swap, verified in-emulator

ActRaiser's screens are built by a small bytecode interpreter: 60 "screen scripts"
selected by a two-byte state (`$18`, `$19`), each a list of opcodes, one of which
uploads a CGRAM palette from a flat 24-bit pointer. I reverse engineered the ROM
far enough to render those screens headlessly, then shipped a one-palette hack:
swap red and blue in the title/menu palette. It is a **64-byte patch** delivered as
an IPS, and it is verified twice — in a reimplemented PPU and in a real emulator
(28/28 changed colours on the live title screen are exact R/B swaps).

The interesting part is not the patch. It is that a correct patch looked like a
no-op in the emulator for a long time, and why.

## Setup
- ROM: **ActRaiser (USA) [!]**, 1 MiB, LoROM (`map mode 0x20`), 8 KiB SRAM, no
  copier header, SHA-256 `b80558…23f0` (see front matter).
- **Ghidra 12.1.4** with a 65816 processor extension; process as
  `65816:LE:24:snes` with the M/X flags patched in the `.pspec`, otherwise the
  8/16-bit immediate widths are wrong and the disassembly drifts.
- **RetroArch 1.21.0**, core `snes9x_libretro` (bundled snes9x 1.63). Nothing else
  SNES-shaped was on the machine. RetroArch's `--max-frames=N`,
  `--max-frames-ss` and `--max-frames-ss-path` give unattended captures.
- Python 3 with Pillow for every pixel comparison (this agent cannot look at an
  image; all checks are numeric — histograms, colour identities, ASCII thumbnails).
- `um win launch` / `um win drive` / `um win shot` to drive the emulator window and
  send it a key. `um win shot` uses Windows.Graphics.Capture, which works even for
  a GPU-rendered window.

## Route and why
Shipped as **data** — a patch to a palette table, delivered as an IPS so no ROM is
redistributed ("bring your own dump"). ROM hacks are the one case where the platform
convention is a patch file, not modified content.

Two oracles, deliberately:
1. a **reimplementation** of the parts of the PPU that matter (CGRAM, tilemaps, the
   interpreter), written in Python from the disassembly, so screens could be rendered
   without an emulator and diffs could be measured at pixel level;
2. the **emulator**, as an independent check that does not share my misreadings.

Neither alone would have been convincing. The renderer can be wrong in the same way
the patch is; the emulator proved the real console path.

I chose the title palette as the first hack precisely because it is provable: the
palette is referenced by only two of the 60 screen scripts, and an R/B swap has a
colour *identity* you can test (`after == (b, g, r)`), not just "the picture changed".
A wrong offset, wrong entry count or wrong field order breaks the identity.

## How the game works (what we had to learn)
**Addressing (LoROM).** File offset and hardware address are related by
`file = (bank & 0x7F) * 0x8000 + (addr & 0x7FFF)`, equivalently
`addr = 0x8000 | (file & 0x7FFF)`, `bank = file >> 15`. Every 24-bit pointer in the
ROM's data (including script pointers) is a flat file offset, i.e. byte-order
`P(3)`; this simplifies everything.

**Header and checksum.** The SNES header sits at file `0x7FC0`: mapper/ROM/SRAM
sizes, country, and at `0x7FDC`/`0x7FDE` the checksum and its complement. The rule is
that the sum of every byte in the ROM, with those four bytes counted, is `0xFFFF`
mod `0x10000`. Editing any byte invalidates it, so any real ROM edit must recompute
it. Emulators often only warn, but a valid header is what makes a patch trustworthy.

**Screen system.** The game selects a screen with two bytes and runs a script from a
60-entry table. The 9-opcode grammar is small; the one that matters here uploads a
palette: a flat `P(3)` source pointer, a start and end CGRAM index, and a CGADD base.
The palette format is plain SNES **BGR555, little-endian**, 2 bytes per colour, 128
colours per bank.

**The title palette.** CGRAM 0..127 for the title/menu screen and the cutscene hub
comes from one 256-byte table at file `0xE3E93`. Only those two records reference it,
so editing it cannot leak into gameplay. Two entries are fixed points of an R/B
swap: black and white both have `R == B`. So 64 of the 256 bytes change, not 128 —
a nice self-check that the swap is doing what it says.

**Interpreter nuance that wasted time.** A screen script uploads only *deltas*: a
record is written on the assumption another record already set most of CGRAM. So
rendering one record in isolation leaves roughly 25 of the 60 records almost black.
To model the game you must keep one persistent PPU and replay records in boot order.

## Build steps
1. Locate the palette table and confirm which screen scripts reference it (scan the
   opcode stream for the UploadPalette opcode and collect its pointers).
2. Patch programmatically: read the 256-byte table, swap the R and B fields of every
   BGR555 word, write it back into a **copy** of the ROM. Never edit the original.
3. Recompute the header checksum at `0x7FDC`/`0x7FDE`.
4. Emit an IPS with records only for the bytes that actually differ — this yields 3
   data records (64 bytes) plus the 4 checksum bytes, 96 bytes total.
5. Verify, then verify again (see below).

A generic `apply_ips.py` (arg-driven, refuses to overwrite its input) is enough to
install it; the patch was checked by applying it to a fresh dump with a *separate*
implementation and comparing the result to the build bit-for-bit.

## Verification
- **Renderer:** 30,949 / 65,536 pixels change on the affected screen, and 100.00% of
  them satisfy `after == (before.b, before.g, before.r)`.
- **Emulator:** with both ROMs driven to the title screen, 28 colours differ and
  **all 28 are exact R/B swaps** (441,270 px, 0 unexplained). Two captures of the
  *same* ROM 4 s apart are byte-identical, proving the screen is static and the
  comparison is meaningful. *2026-10-15, same dump: the "static" part does not
  generalise. The title screen's lower half is an animated sky, and two native
  captures of the **pristine** ROM differ by 3,500–4,600 pixels there. The earlier
  pair was probably one stale image copied twice (see gotcha 2) rather than a
  genuinely static screen. The R/B conclusion is unaffected — the swap is a pure
  colour identity, so it holds whatever the sky is doing.*
- **Patch:** a fresh dump + the IPS reproduces the built ROM bit-for-bit (SHA-256
  match).
- **Integrity:** checksum recomputed and valid.
- **Not verified:** anything past the first screen. Gameplay, sprites and audio were
  never exercised, and no real hardware was used.

## Gotchas
1. **The emulator says the patch does nothing, but the renderer says it works.**
   **Cause:** ActRaiser **halts on the Enix logo until START is pressed.** Timed
   captures at 600, 2400 and 3600 frames, and even a 60-second `--record` of both
   ROMs, are all the logo — and the logo does not use this palette. A 3600-frame
   video comparison of the two ROMs is literally `psnr avg:inf`. **Fix:** send the key
   first. Enter maps to RetroPad Start; then capture. If a timed-capture comparison
   ever says "identical", suspect the boot state before suspecting the patch.
2. **Emulator screenshots are not pixel-exact.** **Cause:** RetroArch captures the
   scaled window (897x672), and the SNES 8:7 → 4:3 correction is a *non-integer*
   horizontal scale (≈3.5), so the GPU bilinear-blends neighbouring pixels. 21 of 28
   observed colours were off the SNES 5-bit lattice. **Fix:** do not test palette
   equality against emulator output. Test the **swap identity** instead — a blend of
   `(r1,g1,b1)` and `(r2,g2,b2)` swaps R/B whenever both sources do, and G is
   untouched, so the identity survives resampling exactly. (Snapping colours to the
   nearest lattice value recovers flat areas but not detailed ones.) Note `-c` and
   `--appendconfig` with `video_smooth="false"`/`video_scale_integer="true"` were
   both ignored by this install, so this is not one-line fixable.
   *2026-10-15, same dump: there is now a capture path that sidesteps the problem
   entirely — RetroArch's `SCREENSHOT` **network command** returns the native
   256x224 framebuffer with 1:1 pixels, so geometry is exact and comparisons stay
   inside one pipeline. See `games/actraiser/title-sprite-star-swap.md`.*
3. **A byte-level "find the state writes" scanner reports sites that are not
   instructions.** **Cause:** a linear scan over code decodes mid-instruction
   operands as opcodes. **Fix:** confirm every candidate by disassembling that exact
   address; two of the hits were inside a `JMP`'s operand and inside data. A count is
   a hypothesis until each site is confirmed.
4. **Ghidra's 65816 disassembly drifts after a certain address.** **Cause:** the
   accumulator/index width flags (M/X) were never told to change, so a 16-bit
   immediate was read as an 8-bit one and everything after it shifted. **Fix:** patch
   the M/X flags in the `.pspec` for the regions where the ROM sets them.
5. **A "corrupt" `§`/`—`/`–` in a Markdown file that was fine yesterday.**
   **Cause:** the Windows console mangles these nondeterministically on the way out;
   the file on disk is correct. **Fix:** verify bytes with a script (hex line dump /
   codepoints) and trust `grep`, never the terminal echo.
6. **Eight-bit palette words look wrong when you print them.** **Cause:** BGR555
   stores blue in the low bits. Printing the raw little-endian word without
   unpacking reads as *RGB reversed*. **Fix:** unpack `r = v & 31`, `g = (v>>5) & 31`,
   `b = (v>>10) & 31` before comparing, and remember 5-bit → 8-bit is
   `(v<<3) | (v>>2)` — which is what snes9x does, not `v*255/31`.

## Assets
None. The hack moves no art; it only rewrites palette words already in the ROM.

## Cost and time
One long session plus a follow-up. Most of it went into building the headless
renderer and the emulator cross-check; the patch itself is a few dozen bytes.

## Open questions
- The decoder is complete for the 60 known records, but the title screen's *tiles*
  are not fully modelled: the renderer reproduces the palette correctly (proved by
  the mod) but not the exact console image, and the emulator's rescaling makes an
  exact colour comparison impossible. A savestate dumped straight out of the
  emulator would settle which CGRAM/tilemap state is really live.
- Sprites/OAM are **not rendered** yet, though the structure is now decoded: the
  shadow OAM is `$7E:0380` (`0x220` bytes) and is DMA'd to `$2104` every VBlank by
  a routine at `$02:ACA3`; sprites come from 5-byte-per-part metasprite
  definitions reached through per-object animation scripts, so they cannot be
  reproduced from the screen records alone — that needs live object state (a
  savestate). Until then only background layers can be re-rendered or modded.
  (An earlier guess here that the routine around `$02B446` was the OAM uploader
  was wrong: `$02:B446` is `Block_CopyToSlot`, the `LoadBlock` helper.)
  *2026-10-15, same dump: resolved for the title screen — OAM entry #6, its 16x16
  two-frame tile set and its character base (VRAM byte `$4000`) were all pinned
  numerically, and sprite #6 was replaced and verified in-emulator. Encoding is 4bpp,
  32 bytes per 8x8 tile, and a 16x16 sprite is tiles `t`, `t+1`, `t+16`, `t+17`. See
  `games/actraiser/title-sprite-star-swap.md`. Note this shadow OAM was **not** a
  usable oracle live: take OAM from a savestate's PPU chunk (offset `0x7D3`).*
- The two-byte state's selector logic has an unexplained byte-split case.
- Next natural hacks: stage palettes, then a text/table edit, then something the
  interpreter cannot express — which is where the real reverse engineering starts.
