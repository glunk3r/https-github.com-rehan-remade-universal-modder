---
kind: game
title: 'ActRaiser (SNES): the title-screen cherub becomes a golden star (sprite/tile hack), and the sprite char base proved numerically'
game: ActRaiser
games_also: []
game_version: 'ActRaiser (USA) [!], No-Intro, 1 MiB LoROM, no copier header, SHA-256 b8055844825653210d252d29a2229f9a3e7e512004e83940620173c57d8723f0'
platform: emulator
engine: unknown
route: data
tools: ["Ghidra 12.1.4 + a 65816 processor extension", "RetroArch 1.21.0 (snes9x_libretro core)", "RetroArch network command interface", "um win launch / um win drive / um win shot", "Python 3 + Pillow"]
anti_cheat: none
status: working
agents:
- Big Pickle (big-pickle)
humans: [etproductions]
date: '2026-10-15'
links: []
tags: ["snes", "rom-hack", "ips", "sprites", "oam", "vram", "4bpp", "cgram", "lorom", "65816", "reverse-engineering", "emulator"]
---
# ActRaiser (SNES): the title-screen cherub becomes a golden star (sprite/tile hack), and the sprite char base proved numerically

ActRaiser's title screen draws a small animated cherub as OAM sprite #6: a 16x16
two-frame flip-book whose tiles sit **uncompressed** in the ROM, so a byte edit is a
VRAM edit. I rewrote its eight tiles as a four-point golden star and shipped a
335-byte IPS. It draws in a real emulator (29 of 29 usable captures) where the
pristine ROM always shows the cherub. The reusable part is not the star: it is how to
pin a sprite's **character base** numerically instead of by eye, and the three traps
that made the obvious approaches lie. Companions: the same game's palette note
(`title-palette-rb-swap.md`) for the screen-script interpreter and the LoROM/checksum
basics, and the KB's technique note on oracles (in the universal-modder repo, outside
this workspace).

## Setup
- ROM: **ActRaiser (USA) [!]**, 1 MiB LoROM, no copier header, SHA-256
  `b80558…23f0` (front matter). Same dump as the palette note.
- **RetroArch 1.21.0**, core `snes9x_libretro` (bundled snes9x 1.63), Windows.
- **RetroArch's network command interface** — the single most useful tool here.
  Enable it (`network_cmd_enable = "true"`, `network_cmd_port = <port>`) and speak
  plain TCP:
  - `SCREENSHOT` — takes a **native** 256x224 PNG, 1:1 pixels, and returns the path;
  - `READ_CORE_RAM <addr> <len>` — the address is a **WRAM offset, parsed as hex**:
    `READ_CORE_RAM 380 100` reads `$7E:0380` (verified byte-identical against a
    savestate), so WRAM can be sampled live. Format it in hex — a `%d`-formatted
    `896` for `$380` reads a different address and returns plausible garbage
    (Gotcha 6);
  - `LOAD_STATE_SLOT <n>`, `GET_STATUS` (flaky, retry).
  Input still goes through the window: `um win drive --proc retroarch.exe focus
  "key 0x0D"` (RetroArch maps keyboard Enter to RetroPad Start, and `Y`/`A`/`B`/`X`
  to `a`/`x`/`z`/`s`). Never send `0x1B` — that is `input_exit_emulator`.
- **Savestates as the oracle.** A RetroArch `.state` (RASTATE `s9xsnp:0012`) carries
  the whole PPU, so CGRAM, OAM and VRAM can be read *without* running the game and
  without a single scaled screenshot. Chunk sizes in order: `VRA=65536 RAM=131072
  PPU=2652 SRA=524288 FIL=32768 SND=66560`; inside the PPU chunk, `CGDATA` is at
  offset `0x41` (256 little-endian BGR555 words) and `OAMData` at `0x7D3` (544
  bytes = 512 low table + 32 high table).
- Python 3 + Pillow for every pixel comparison. This agent cannot look at an image,
  so every check is numeric: colour histograms, ASCII cells, region equality.

## Route and why
**Data.** The sprite's tiles are stored uncompressed and are copied to VRAM verbatim
by the screen's own script, so no code patch and no loader are involved — rewrite the
tiles in a copy of the ROM and recompute the header checksum. Shipped as an IPS
because ROM hacks travel as patches, never as the ROM.

Why the title sprite as the second hack: it is the smallest unit that exercises the
**sprite** path end to end (OAM entry, character base, 4bpp tile format, OBJ palette,
16x16 tile layout), and unlike the earlier palette swap it has an independent numeric
proof available — the character base can be *derived* from the pixels rather than
guessed.

Two oracles again, deliberately: a Python model of the sprite path (decode OAM ->
decode 4bpp tiles -> composite the cell) and the live emulator. The model can be wrong
in the same direction as the edit; the emulator cannot.

## How the game works (what we had to learn)
**Sprite character block.** The title screen's sprite tiles are uploaded verbatim by
its own screen record: `UploadVram dest=$2000 words <- source 06:8000` — VRAM word
`$2000` is byte `$4000`, and the source pointer is a flat file offset `0x68000`. So
**file `0x68000`–`0x6BFFF` is VRAM byte `$4000`–`$7FFF`, 1:1**. Comparing a
savestate's VRAM chunk against the ROM confirms it exactly, which is why editing the
file is editing VRAM — a fact worth *checking* on each screen rather than assuming.

**Character base.** A sprite's tile index is an offset into the selected character
block, so every tile address depends on where the block was uploaded. Here the base
is VRAM byte `$4000` (word `$2000`, OBSEL name-base 2, name-select 0). Tile *N* is
therefore at file `0x68000 + N * 32`.

**OAM.** 128 entries of 4 bytes (`x`, `y`, tile index, attribute) plus a 32-byte high
table (x bit 8 and the size bits). Attribute bits: 0 = tile bit 8, 1–3 = **palette
0–7**, 4–5 = priority, 6 = h-flip, 7 = v-flip. The title screen's sprite #6 is 16x16,
palette 0, at pixel (120, 104).

**16x16 is four 8x8 tiles**, not one: `t`, `t+1`, `t+16`, `t+17`. This is the
single most useful layout fact for authoring, and the reason one must think in
tile-quadruples.

**4bpp tile format.** 32 bytes per 8x8 tile, interleaved bitplanes: bytes 0–15 hold
planes 0 and 1 (one byte per row each, plane 0 first), bytes 16–31 hold planes 2 and
3. The pixel value is `p0 | p1<<1 | p2<<2 | p3<<3`, i.e. a palette index 0–15, with 0
transparent.

**The sprite is a two-frame animation.** It alternates its OAM tile index every tick
and bobs one pixel: tile `$000` at (120, 103), or tile `$002` at (120, 104). So the
full target is eight tiles — `$000 $001 $010 $011` at file
`0x68000 0x68020 0x68200 0x68220`, and `$002 $003 $012 $013` at
`0x68040 0x68060 0x68240 0x68260`. Six of my nine savestates happened to be frozen on
`$002` and only two on `$000` — see Gotcha 2.

**CGRAM is rewritten every vblank.** The game re-uploads its sprite palette on every
vblank (`VBlank_CgramAnim`, bank `$02`), indexed by `frame & 2`. So CGRAM read at any
instant is one write behind the screen you are looking at, and a live CGRAM dump will
not match a screenshot. Recover the palette *from the screenshot* and test the
index→shade **function**; do not compare raw 5-bit words across the two.

## Build steps
1. Decode the target from a savestate: read the PPU chunk, walk `OAMData` at `0x7D3`
   in 4-byte entries, and take the sprite's x, y, tile, attribute, size and palette.
- Confirm the character base numerically (next section) — do not take it from a
  disassembly read, and do not trust a plausible-looking guess.
- Author the replacement as 8x8 palette-index grids, then encode 4bpp.
- Patch **every animation frame's** tiles into a *copy* of the ROM at
  `0x68000 + N*32`.
- Recompute the SNES header checksum at `0x7FDC`/`0x7FDE`.
- Emit an IPS containing only the bytes that differ: 16 records, 247 bytes here
  (243 pixels of tile data + the 4 checksum bytes).
- Verify with the model, then with the emulator, then re-apply the IPS to a fresh
  dump with a **separate** implementation and diff the result against the build.

## Verification
- **The character base, proved numerically — the part worth copying.** Decode the
  sprite's tiles for each candidate base and, for every pixel, look up the colour at
  its palette index *in the emulator screenshot*. A correct base is a *function*:
  every pixel sharing an index must share a colour. Scoring **consistency** gives
  **1.000** at byte `$4000` and **0.22** at `$3000`. No disassembly, no guessing, and
  it does not care what the palette is.
- **The same score works on any screen, with no known palette and no register.** Run
  palette-free — treat the screenshot as the colour oracle and crop each sprite to its
  own width/height — on a paused booted state on the action stage's first screen: **1.000**
  at byte `$4000` and **0.357** for the next-best base (`base_check.py`). Its screen id was
  questioned in between (the corrected bullet below); the savestate's own `$18/$19` reads
  `01/01`, so that split is a clean identification on a real screen. A screen's base is
  recoverable from one paused state + screenshot pair on a screen built from 8x8
  sprites, with no known palette. The OBSEL register is not needed for that — and on
  this ROM it is not in the savestate's PPU chunk at all, so it could not be read back
  that way even if it were wanted.
- **Decode round-trip.** The 4bpp codec round-trips 200/200 generated tiles; decoding
  the *pristine* ROM's tiles and compositing sprite #6's cell reproduces the
  emulator's own frame with **0 of 1674 pixels** differing.
- **Prediction, then emulator.** The verifier predicted the patched cell's colour
  histogram — `#E7A600` x52, `#FFE700` x36, `#FFFFFF` x12 — and the emulator produced
  exactly that, shade for shade, with the cell's 16 rows matching the authored art
  row for row.
- **Emulator.** A 40-capture burst on the booted patched ROM gave 29 usable captures:
  **29 star, 0 cherub**. The same burst on the pristine ROM never showed the star.
- **Scope.** 247 bytes differ, in 16 runs: 4 checksum bytes plus 243 inside the
  sprite's own tiles. No code, no other art, no palette.
- **The sweep, measured 2026-10-17.** The gap this closes was a screen that draws from
  whatever is already in VRAM instead of re-uploading the block. Sixteen candidate
  records were booted with the patched request and scored from four live 256x224
  captures per ROM, 1.3 s apart (`emu_stage_leak.py`):
  - **Star — the controls.** All six ACT views `(00,01)`..`(00,06)` and the title
    `(00,07)`. On the ACT views every sample from the second on gains gold and loses
    exactly the pristine ROM's skin pixels; the title reports in all four (skin
    88 -> 0, gold 20 -> 88).
  - **No star.** The first action screen of all seven stages, `(01,01)`..`(07,01)`
    (`(07,01)` answers live `$18/$19` = `(7,2)`), plus the sub-screens `(01,02)` and
    `(02,02)`: **zero pixels of the star's palette in either ROM, in every sample.**
    `(01,01)`, `(03,01)`, `(04,01)` and `(07,01)` are pixel-identical across the two
    ROMs; where a stage does differ (`(02,01)` ~1.1-1.4 k px, `(05,01)` 5.6 k px,
    `(06,01)` 7.3-8.7 k px) the motion is its own animation, present in both ROMs, and
    still not one gold pixel.
  Each of those stage screens draws sprite `#11` on tile `$11`, one of the eight edited
  tiles: identical pixels from an *edited* tile mean the tile in VRAM is not the mod's
  block. The stage loaded its own over the slot, so nothing is inherited — on a
  sub-screen either.
  Each of those stage screens draws sprite `#11` on tile `$11`, one of the eight edited
  tiles: identical pixels from an *edited* tile mean the tile in VRAM is not the mod's
  block. The stage loaded its own over the slot, so nothing is inherited — on a
  sub-screen either.
- **The overwrite, read from code (2026-10-17) — why the sweep cannot miss a screen.**
  The same question was then answered statically, and the answer closes the sweep rather
  than just explaining it. `FindRefs 078000` (the 24-bit address of file `$038000`)
  returns **exactly one** reference: `02bcac  LDA !>$0x78000,X` in `FUN_02bc9e`.
  `FindCalls 02bc9e` returns exactly one caller: `008366  JSL !>$0x02bc9e` in
  `Game_State_Update`, on the branch taken only when `$18 != 0` and `$18 != 8`. And
  `find_upload_loops.py` — the same question asked without Ghidra, by scanning all 1 MiB
  for `LDA long,X` followed by a VMDATA or VMADD write — finds **three** copy loops, all
  three inside that one routine. So the sweep's per-screen verdict is not an artefact of
  which screens were tried: exactly one code path can refill the slot, it belongs to
  `$18 != 0`, and its source is a fixed address rather than anything the record table
  chooses. Headless commands used (`README.md` has the full line):
  `-postScript FindRefs 078000`, `-postScript FindCalls 02bc9e`,
  `-postScript DisasmList 02bc80 0xa0 038000 0x100`.
  Menus *reached by playing*, audio and real hardware stayed out of scope.

## Where the star appears (leak inventory 2026-10-15; slot mechanism 2026-10-16; action stages, sub-screens and the loader 2026-10-17)

A 4 KiB character block with seven uploaders is not automatically a title-only edit,
so the scope was *measured* rather than argued:

- **Statically, the uploaders of *that* block are countable.** Records
  `(00,01)`..`(00,07)` each `UploadVram` the **same** 16 KiB block from file `$068000`
  to VRAM word `$2000`, and `(00,08)` then overwrites 8 KiB of it from `$02CE7F`, with
  no other record re-uploading `$068000`. So the candidate screens come out of the
  record table, without playing. (Record scripts are not the whole story — see the
  slot bullet below.)
- **Each candidate was booted, not guessed.** RESET's boot request is one immediate
  word naming the record's minor id (`A2 07 00` at file `0x49`). Patching that operand
  and booting makes the game run that record *through its own init path* — script,
  upload, handler — so pristine and patched renders are directly comparable. This is
  the only sound way to see it: loading a savestate cannot, because a frozen state's
  VRAM already contains its own tiles and the test would read its own precondition.
- **Result.** The star is drawn on **all six overworld ACT views**, `(00,01)`..`(00,06)`
  (40-52 px per stable frame at `x=131..139 y=115..126`), and on none of the
  neighbouring screens: `(00,08)` cutscene (all frames pixel-identical), `(00,09)`
  overworld, `(00,00)` boot/logo screen (the screen RESET's own `State_Init (00,00)`
  paints while the title request is pending; `md5 c0d965ae56` for every frame in
  *both* ROMs). Each of those six, plus the title `(00,07)`, was then re-booted
  individually in the 2026-10-17 sweep and shows the star. So the leak is real: the
  title and the hub share one sprite block, and the six ACT views load it. **Terminology
  check** (`TRANSITIONS.md` §2, §6): `$18=00` is the overworld hub, so
  `(00,01)`..`(00,06)` are the ACT *views*; the action stages proper are `(01,*)`..
  `(07,*)`, and all seven of those are measured below — see the last bullet.
- **The bound, stated statically — and what it does *not* cover.** The star's tiles sit in a shared character slot (VRAM word `$2000`, byte
  `$4000`). Replaying all 61 records' declared ops (`slot_writers.py`) says only
  these touch byte `$4000`-`$5FFF` at all: `(00,01)`..`(00,07)` upload the `$068000`
  block into it, `(00,08)` overwrites its first 8 KiB from `$02CE7F`, and
  `(00,00)`/`(00,09)` use the plane variant, which writes the *odd* byte of every word
  `$0000`-`$3FFF` and so destroys the tiles there too. **The other 51 records never
  write the slot — including every action stage, `(01,*)`..`(07,*)`.** So a screen
  *can* inherit whatever the previous screen left in the slot; the six ACT views leak
  only because they load `$068000` there and draw from it. **But the record table is not
  the whole story:** `FUN_02bc9e` (`$02:BC9E`) copies 8 KiB of ROM file `$038000` into
  word `$2000` on *every* screen change onto a screen with `$18 != 0`, and no record
  declares it (the loader bullet below reads that code). So "51 records never write the
  slot" means their *records* do not rewrite it — not that the slot survives on those
  screens.
- **"`(01,01)` refills the slot" — right about the effect, wrong about the mechanism; and
  my first retraction of it was wrong too (both 2026-10-17).** The original reading was
  that the action stage's first screen re-uploads the slot from `$038000`. It does — but
  not through its record script, and the state it was measured on *was* `(1,1)`:
  - the savestate's own `$18/$19` is **`01/01`** — the game says it is on screen `(1,1)`.
    The first retraction argued the label was wrong because `identify_state.py` scores
    every record below 0.14 against that state; that inference was backwards. The scorer
    replays *record* ops, and in-stage screens do not get their VRAM from record ops, so
    a low score means "not a hub screen", not "mislabelled". `identify_state.py` now
    prints the state's own `$18/$19` beside the scores.
  - the slot (VRAM byte `$4000`-`$5FFF`, 8192 B) equals **ROM file `$038000` for 97%** of
    its bytes, and a *cold* boot of `(1,1)` has only `(00,00)`'s plane (`$058300`)
    underneath, so that upload is the stage's own, not an inheritance.
  - record `$01/$01` is not the uploader, and neither is any other record: every record's
    operand bytes were searched for the little-endian pointer `$038000` — across *all*
    ops, not just `UploadVram` — and it appears **nowhere**. The loader is code, and it
    spells the pointer exactly once, as the LoROM address `$07:8000`:
    `02bcac  LDA !>$0x78000,X` in `FUN_02bc9e` (`$02:BC9E`). The loader bullet below reads
    the whole dispatch out of the ROM.
  What the record walk still says stands: record `$01/$01`'s declared ops write words
  `$0000/$1000/$3000/$4000/$5000` and never word `$2000`.
- **The loader, found and read (2026-10-17) — this is the entire leak mechanism.**
  Screen changes go through `State_Transition` (`$00:8241`), which returns immediately
  unless the requested-id flag `$1a` is set, moves `$1a`/`$1b` into `$18`/`$19`, clears
  `$1a`, and only then calls `Game_State_Update` (`$00:8325`). So everything below runs
  **once per screen change**, never per frame. `Game_State_Update` dispatches on the id:
  - `$18 == 8` (the ending) — no loader at all.
  - `$18 | $19 == 0` (the boot paint) — no loader.
  - `$18 != 0` (in-stage) — `FUN_02bc9e` (`$02:BC9E`) copies 8 KiB from the LoROM address
    `$07:8000` (file `$038000`) into **word `$2000`** (byte `$4000`), the star's own slot:
    `LDX #$2000` / `STX $2116`, then `02bcac  LDA !>$0x78000,X` / `STA $2118` for 4096
    words. This is the one path that refills the slot.
  - `$18 == 0`, `$19 = 1..6` (the six ACT views) — `FUN_038053` (`$03:8053`) copies its
    8 KiB into **word `$6000`** (byte `$C000`), *not* the slot, so the record's `$068000`
    block — star included — survives there.
  - `$18 == 0`, `$19` outside `1..6` — `FUN_038053` returns before its copy
    (`LDA $19` / `AND #$ff` / `DEC A` / `CMP #$6` / `BCC`), so the title (`$19 = 7`), the
    cutscene (`$19 = 8`) and the overworld (`$19 = 9`, which takes its own `$028134` path
    instead) all keep exactly what their record left in the slot — which is the star for
    the title, and for the other two the block their own record uploads.
  Besides the 8 KiB, `FUN_02bc9e` is two more literal loops: 48 colours from `$07:D040`
  (file `$03D040`) to `CGADD $C0`, and 256 B from `$06:A400` (file `$032400`) +
  `(id-1)*128` to word `$2D40`, where `id` is the low byte of `$02AC` (the current stage
  id; `0` is read as `6`). Those two are the routine's only per-stage inputs — **the
  sprite block itself is one shared bank for every stage, so there is no per-stage sprite
  bank to look for.** `find_upload_loops.py` sweeps all 1 MiB for this shape (`LDA
  long,X` followed by a VMDATA/VMADD write) and finds **exactly three** loops, all of them
  inside `FUN_02bc9e`: every other upload in the game goes through a table operand or a
  register pair, which is why scanning the record table for the pointer came up empty.
  The one loose end this explains is the savestate's 97% match: the game has a per-frame
  tile patcher (`Tile_PatchPlanes` `$02:ACE5`, `VBlank_VramPatch` `$02:AEBB`,
  `VBlank_VramPatch5800` `$02:AEEB`) that rewrites some of those tiles as things animate,
  so a *paused* slot is never expected to be a byte-for-byte image of the ROM block.
- **A tile index inside the block's range proves nothing on its own.** An earlier version
  of this bullet read `(1,1)`'s paused state, saw OAM tile `$11` (an edited tile) pointing
  into base `$4000`, and concluded the screen drew the mod's block. An index only says
  which VRAM slot a sprite reads; whether that slot holds the mod's bytes is a separate
  question. The sharp version of the test is the one used above: a sprite on an edited
  tile that renders **identical pixels in both ROMs** proves the slot is *not* the mod's
  block. Follow the source, and let the frame diff settle it.
- **Metric that works.** Whole-frame diffs are useless here — the stages animate, and
  even two captures of the *pristine* title differ by thousands of px. Count instead
  the pixels that are **cherub skin** in the pristine frame and **star gold** in the
  patched frame; that isolates the swap without knowing where the sprite is
  (`leak_report.py`). Cherub skin `#FFD7AD`/`#D6AE84`/`#A57952`, star gold
  `#E7A600`/`#FFE700`.
- **Caveat, now closed by experiment (2026-10-17).** These screens were entered
  through the patched boot request, not by playing, so the leftover-VRAM case — a screen
  that keeps the block in VRAM without re-uploading it — had to be tested rather than
  argued. The full sweep is the first Verification bullet above; in short, booting both
  ROMs into the first action screen of every stage `(1,1)`..`(7,1)` and the sub-screens
  `(1,2)`, `(2,2)` gives **no pixel of the star's palette in either ROM, in any of four
  samples per screen**, where all six ACT views and the title do show it. Frames come out
  pixel-identical across ROMs on `(1,1)`, `(3,1)`, `(4,1)` and `(7,1)`, and the
  differences elsewhere track each stage's own animation between the two boots. Each
  stage screen tested puts sprite `#11` on tile `$11`, one of the eight edited tiles.
  Identical pixels from an edited tile mean the tile in VRAM is not the modded block: the
  stage's own upload (`$038000`, above) has already replaced it. The star therefore
  cannot be inherited by an action stage, whatever its ACT view left in the slot.

## Gotchas
1. **The patched ROM looked frozen while the pristine ROM animated.** The capture
   script used the `F8` screenshot **hotkey**; when window focus failed the hotkey did
   nothing and the script then re-copied the *newest pre-existing PNG* — 11 times.
   Every "frame" was the same stale image. **Cause:** window-hotkey capture has no way
   to report failure, so a stale file is indistinguishable from a fresh one. **Fix:**
   capture with RetroArch's `SCREENSHOT` **network command**: it either returns a
   freshly written file or an error. Never build an unattended verdict on a hotkey.
2. **Rewriting only one animation frame makes the sprite flicker.** A capture burst
   showed roughly 50/50 star/cherub even though there is exactly one sprite and one
   tile set. **Cause:** the sprite is a two-frame flip-book (`$002` <-> `$000`), so the
   untouched frame keeps drawing the cherub — and *six of my nine savestates* were
   frozen on `$002`, so the second frame never appeared in my oracle. **Fix:** rewrite
   every frame's tiles; enumerate frames from live captures or several savestates, not
   from one state.
3. **A colour-based search for the character base found the wrong base.** An earlier
   pass scored candidate bases by how close the decoded colours were to a palette it
   had guessed, and "won" at word `$3000` (byte `$6000`) with a weak 0.577 — wrong.
   **Cause:** it was comparing against CGRAM read one write behind the frame (see
   Gotcha 5), so the target palette was itself mis-phased. **Fix:** score
   *consistency* (all pixels sharing an index share one colour) against the palette
   recovered from the screenshot, and cross-check against the address the screen's own
   record uploads to. The right answer then scores 1.000 and the wrong one 0.22.
4. **Emulator screenshots are resampled, so pixel and colour equality both fail.**
   Window captures come out at the scaled size (e.g. 897x672) because the SNES 8:7 ->
   4:3 correction is a non-integer horizontal scale (~3.5) and the GPU bilinearly
   blends neighbours; 21 of 28 observed colours sat off the 5-bit lattice.
   `-c`/`--appendconfig` with `video_smooth="false"` and `video_scale_integer="true"`
   were both ignored by this install. **Fix:** use the network `SCREENSHOT` command,
   which returns the native 256x224 framebuffer with 1:1 pixels — geometry becomes
   exact and comparisons become meaningful. Note it is still the *emulator's* RGB
   conversion, so compare colours within one capture pipeline (or compare the
   index -> shade mapping) rather than asserting absolute 5-bit values.
5. **Live CGRAM disagrees with the screenshot you just took.** The sprite palette is
   re-uploaded every vblank and indexed by `frame & 2`. **Cause:** the register read
   and the capture are different phases of the same animation. **Fix:** recover the
   palette from the screenshot, or work from a savestate, and verify the *function*
   from index to shade, never raw CGRAM words against raw pixels.
6. **Live WRAM reads came back as garbage — a mis-addressed read, not a mid-copy
   race.** The `$7E:0380` OAM shadow matched the PPU OAM inside a savestate, but the
   same bytes read live over the network interface were nonsense, so "the shadow OAM is
   not a safe oracle" looked like the answer. **Cause:** `READ_CORE_RAM` parses its
   address argument as **hex**, while the helper building the command formatted it with
   `%d`; a decimal-looking `896` for `$380` is read as `$896`, a *different* address
   whose contents look exactly like noise. **Fix:** format addresses in hex. Proved by
   reading both live on one paused frame: `READ_CORE_RAM 380 256` equals `RAM[0x380]`
   (256/256) and `READ_CORE_RAM 896 256` equals `RAM[0x896]`. The shadow OAM is a fine
   live oracle. Lesson: when an oracle only ever *fails* instead of erroring, print the
   request arguments before doubting the window it reads.
7. **Whole-frame diffing is meaningless on this screen.** Two captures of the *same
   pristine* ROM differ by 3,500–4,600 pixels. **Cause:** the lower half of the title
   screen is an animated sky. **Fix:** compare the sprite's 16x16 cell (or the tiles
   themselves). Concretely: pristine-vs-pristine changes 9–133 pixels *inside* the
   cell (the sprite's own flap), pristine-vs-patched 158–173. If a whole-frame diff is
   your only check, a real change is lost in the noise.
8. **The capture harness can pause itself, and then every capture agrees.** A whole
   pass of patched captures came back uniform/identical while the pristine ROM
   animated. **Cause:** the emulator's own config sets `pause_nonactive`, and the
   launcher never focuses the window, so the core was paused from its first frame and
   every "frame" was the same stale surface — a *paused* capture pipeline cannot
   report that it is paused. **Fix:** launch with an `--appendconfig` that turns
   `pause_nonactive` off and points saves/states at a scratch directory, then validate
   the harness against a screen you already have a reference for. Never edit the
   user's own config to do it.

## Assets
Hand-authored, in Python, as a 16x16 grid of palette indices: a four-point sparkle of
100 opaque pixels using **only indices the original sprite already used** — 14 dark
gold (52 px), 15 yellow (36 px), 5 white (12 px) — so no palette edit was needed and
CGRAM is untouched. No generative models and no image files; nothing to attribute.
Building the art from indices rather than RGB is what makes "reuse the existing
palette" a property you can check instead of hope for.

## Cost and time
Two sessions. Most of it went to the two-frame discovery (Gotcha 2) and to replacing
a capture path that could silently lie (Gotcha 1) with one that cannot.

## Open questions
- **Other screens sharing the tiles — settled 2026-10-15; mechanism, action stages and
  sub-screens 2026-10-17.** Records `(00,01)`..`(00,07)` all upload the same block, so the
  answer had to be measured: the star draws on the title and on all six overworld ACT
  views, and on none of the cutscene, overworld or boot-logo records. See "Where the star
  appears". `slot_writers.py` gives the record-side bound without playing — only
  `(00,00)`, `(00,08)` and `(00,09)` also write the slot, and 51 of 61 records never do.
  **The leftover-VRAM case is now measured closed:** both ROMs booted into the first
  action screen of all seven stages (`(1,1)`..`(7,1)`) and two sub-screens (`(1,2)`,
  `(2,2)`), live `$18/$19` reported each time, gives zero star-palette pixels in either
  ROM — while a sprite on those screens sits on an edited tile, so the stage's own 8 KiB
  `$038000` upload has already replaced the block. **The loader is found and read
  (2026-10-17):** `FUN_02bc9e` (`$02:BC9E`), reached once per screen change from
  `Game_State_Update` (`$00:8366`) only when `$18 != 0`, spells the pointer as the LoROM
  address `$07:8000` (one `LDA !>$0x78000,X`, file `$038000`). The block is *shared* by
  every stage, so "which sprite bank each stage loads" has no per-stage answer for the
  slot — the routine's only per-stage inputs are a 256-byte chunk (file `$032400` +
  `CGADD $C0`). **Open: the hub's per-view 8 KiB source (partly answered 2026-10-18).**
  Live probes: `(01,01)` has `$02AC = 00` and its shadow OAM draws tiles 212..215, i.e.
  the id-0 slice of that chunk really is the one on screen. ACT-view WRAM `$7F:0000`-
  `$7F:1FFF` (the buffer `FUN_038053` copies to word `$6000`) is view-dependent: 64
  structured bytes, 288/8192 zero, 156 distinct values, matching no ROM offset as a
  straight *or* byte-swapped 32-byte prefix (longest prefix < 33/8192) — and 8192/8192
  zeros at `(01,01)`. So the hub's page is assembled into `$7F:0000` at runtime from
  per-view pieces rather than copied from one ROM block; the routine feeding it is not
  yet pinned down. **Per-stage inputs settled (2026-10-18):** the id-0 chunk is file
  `$032400` (256 B -> word `$2D40`, first 8 words `FF00 BF52 FF07 BF5D BF5C FF59 FF1B
  FE56`), and the 48 colours are one fixed table at file `$03D040` -> `CGADD $C0` (first
  12 words `0180 1080 437F 3EDA 01F7 012D 7F59 7AB3 71ED 4D08 02FF 3486`), the same for
  every stage. Neither loosens this mod's scope: on
- **Two records upload through a plane, not an address.** `UploadVram` with `b3 = $FF`
  ignores the address operand: it writes the source into the odd byte of each VRAM word
  from word 0. `(00,00)` and `(00,09)` use it. If either screen ever needs to be traced,
  the odd-byte layout is the thing to remember.
- The emulator's RGB conversion is not a plain 5-bit expansion, so exact colours
  should be treated as per-pipeline. A capture taken through a different core or
  frontend may differ in the low bit or two without anything being wrong.
- Animation frames were enumerated by hand, from savestates and bursts. A general
  "list every tile index this sprite uses over N seconds" probe would have caught the
  second frame immediately and is the obvious next tool.
- Sprites are now modelled well enough to be replaced; *moving* or adding one (OAM
  allocation, the sprite's own animation script) is untouched territory.
