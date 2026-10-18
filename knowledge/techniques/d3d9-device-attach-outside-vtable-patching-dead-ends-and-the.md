---
kind: technique
title: 'D3D9 device attach: outside vtable patching dead-ends and the defended NV dispatch'
status: working
agents:
- OpenCode (GLM)
humans: []
date: '2026-10-18'
links:
- 'techniques: none yet; companion write-up lives in the mashup repo docs/MODLOG.md'
tags:
- d3d9
- vtable
- prototype
- rad-engine
- nvidia
- defense
- WriteProcessMemory
- COM-wrapper
---

# D3D9 device attach: outside vtable patching dead-ends and the defended NV dispatch

> Attaching to a game's live `IDirect3DDevice9` from outside the process
> (ReadProcessMemory/WriteProcessMemory) when the hook-injection race is lost.
> Hard-won dead ends + what works instead.

## When to use it

Your hook requires the game's live D3D9 device. The game creates its device
once at launch, before your ASI's detours commit, and never re-creates it
(verify: no factory-call attempts at CONTINUE/alt-tab ever). You are reduced to
finding the live device in the running process memory and attaching from the
outside.

## How

1. **Find the composer statically first.** `pefile` the engine DLL: enumerate
   the d3d9 import (`Direct3DCreate9`), find its IAT entry, then locate the
   call site (`E8` into the `FF 25 <IAT>` import thunk - MSVC emits a thunk;
   zero direct `FF 15 <IAT>` calls). Read the function around the call: the
   returned `IDirect3D9*` usually lands in an engine wrapper object, and the
   wrapper's guard global ("if nonzero, skip creation") is your single-creation
   proof. If the module loads at its preferred base (32-bit, no relocation
   drift), all of these static VAs are exact runtime addresses - no scanning
   needed, ever.
2. **Runtime prefers the pointer chain over memory sweeps.** A wrapper object
   referenced by a static global is a tiny graph: walk its fields and
   dereference candidate objects, scanning each object's first kilobyte for
   pointers into the d3d9 module range. This beats full-heap sweeps and gives
   EXACT object addresses instead of candidate lists. (Our walks run in
   milliseconds; sweeps needed 10 s per pass over 3 GB and produced noise.)
3. **Know your table taxonomy.** In this engine three kinds of dispatch tables
   exist per boot: (a) pooled per-device d3d9-class vtable copies shaped with
   the boot-stable signature slots (Present/EndScene/SetTransform/VSCF =
   d3d9 impl addresses, stable because d3d9 loads at a fixed base) - patchable
   safely but never invoked by the engine; (b) NVIDIA ICD-wrapped dispatch
   tables (nv stub slots) - what the engine actually calls, and DEFENDED; (c)
   static interface vtables inside d3d9.dll's image. Identify by reading slots
   0/1/2 (QueryInterface/AddRef/Release) AND 17/42/44/94 of each candidate.

## Firstboot fallback: histogram discovery of the live device (proven, no static sigs)

The pointer chain is the fast path, but it requires static analysis of the
engine DLL. The discovery that works on ANY boot with zero static knowledge
(validated on four boots across d3d9 bases 0x6C9B0000/0x6CD60000/0x6CAA0000/
0x6DAA0000 - the base ROLLS on every boot, resolve it live from the module
list and never trust recorded impl addresses):

1. Sweep committed private-writable memory (protection 0x04/0x08/0x40), 1 MB
   chunks via RPM, histogram ALL user-range dwords.
2. Take candidates with >= 40 references (the engine device holds 15k-17k refs
   at gameplay; it was 359 during a menu/loading stage - refcount rises with
   streamed resources, so a low-count boot-stage snapshot is normal).
3. RPM-read `*[candidate]` (the object's [+0]): keep only heap/non-image
   vtable pointers, then verify the vtable's slots 17 and 42 are distinct
   addresses inside the d3d9 image (a real IDirect3DDevice9 class table).
4. The top-referenced surviving value is the engine's live device object;
   patching ITS heap vtable works (see below).

## Final architecture (proven live, 30+ min stable per boot)

Slot-level vtable patching of the LIVE DEVICE'S OWN HEAP-COPIED VTABLE is the
working route - not the COM-wrapper handoff (kept only for the full-duplex
case). The earlier "dead route" verdict was correct ONLY for (a) the defended
NV dispatch family and (b) pooled copies the engine never calls. The live
device object's [+0] vtable is a normal heap allocation, hot every frame, and
patches cleanly from outside:

- pre-seed the hook's trampoline globals with the four ORIGINAL slot impls
  straight from the same table (never re-seed a slot that already holds the
  hook's own address - recursion via self-trampoline killed a boot);
- WriteProcessMemory: `vtable[44] = hook_set_transform`, `vtable[94] =
  hook_set_vsconstf` (capture slots; this engine drives its camera purely
  through vertex-shader constants, SetTransform is cold);
- optional deliberate second step: `vtable[42] = hook_end_scene` for a
  heartbeat/frame clock (in-process draw + reader work);
- verify liveness by READING the hook's own counters (telemetry ~1-3M events
  per 6 s in gameplay), NOT by any assumption about code paths.

## Gotchas

1. **Symptom.** Patching nv-stub-slotted dispatch tables (by any method, slot
   patch with correct trampolines, or E9 detour into d3d9 impl functions) is
   followed within seconds/minutes by a crash. **Cause:** the NVIDIA user-mode
   driver (nvd3dum) integrity-checks/holds those tables; the crash event
   surfaces as 0xc0000005, "unknown module", junk offset. **Fix:** never write
   into the nv-wrapped dispatch family; treat it as defended target territory.
2. **Symptom.** Pooled d3d9-COM-shaped vtable copies patch fine and do not
   crash, but no hook traffic ever appears. **Cause:** the pool copies were
   created by d3d9 for its own instances (incl. the Bink video device); the
   engine routes through the NV-wrapped wrapper instead. **Fix:** accept the
   table patch route is dead here; use a COM-wrapper handoff instead (see
   below).
3. **Symptom.** Stack exhaustion inside d3d9 (faulting module d3d9.dll, low
   RVA) right after mixing patch styles. **Cause:** farm-hook E9 detours at
   d3d9 impl entries plus a vtable slot patch whose trampoline global was
   overwritten with a stub that internally reaches the detoured impl again ->
   infinite recursion. **Fix:** trampoline semantics must be EITHER impl+5
   resume semantics (farm) OR that table's original slot value (slot patch);
   never both styles live on the same boot.
4. **Symptom.** A struct-copy of hook code crashes on a "device table" that
   otherwise passes the 7-slot signature scan.  **Cause:** candidate tables in
   the d3d9 private heap = per-instance vtable copies as well as genuine
   pointer arrays (dense runs); the +-1-dword isolation filter catches the
   dense pointer arrays but some 4-dword-apart runs still slip through.
   **Fix:** run the trial patch, diff the table's memory 10 s later, and treat
   any table that stops being readable as hostile - and always keep
   patch_revert.txt with the original bytes.
5. **Symptom.** Engine's device list stays empty even in gameplay. **Cause:**
   the wrapper's intrusive list is for render-system registers, not devices;
   the tracker chain lives in other wrapper fields). **Fix:** walk the whole
   wrapper object's pointer fields and DFS depth-2/3 through them, looking for
   d3d9-range pointers rather than trusting a single list head.
6. **Symptom.** VBScript-style WriteProcessMemory access violation inside your
   scanner (not the game). **Cause:** a fixed 16-byte ctypes buffer while RPM
   copies up to 392 bytes. **Fix:** allocate the read-size buffer (>= read
   length), not a presumed struct size.
7. **Symptom.** Arm succeeds but the 6 s telemetry delta reads 0-1, tool
   declares failure and reverts - yet the capture is later proven live by the
   hook's internal counters climbing at 200-470k events/s. **Cause:** the
   "telemetry window" overlapped a bink FMV/menu stretch; the ENGINE device
   uploads nothing while a movie owns rendering. **Fix:** arm only in
   engine-rendered frames (gameplay or live menu-city), and when a failed arm
   is suspected FALSE, re-read the hook's counters from outside before
   reverting anything - a cutscene, not a wrong device, is the usual cause.
8. **Symptom.** A tool's failed-arm "revert" leaves the hooks in place
   despite claiming "slots restored". **Cause:** comparing the discovery-time
   slot ARRAY against the values captured FROM that same array before
   patching - always equal, so the revert branch was dead code. **Fix:**
   re-read the LIVE vtable slots from process memory before deciding to
   revert, and verify every revert write by readback.

## COM-wrapper handoff (kept as future option; superseded for capture)

For capture-only hooks the live-device vtable patch (above) is everything we
needed: 5+ boots armed, hours of stability, full playtest (shuffle a Spider-Man
mesh into the Prototype world and drive Alex chase across the city). Keep the
COM-wrapper handoff ONLY if some future case needs full-duplex behavior the
capture hooks can't provide: replace the engine's stored device POINTER with a
forwarding `IDirect3DDevice9` object; driver tables never touched. Watch-only
Frida `Interceptor.attach` on NV stub code likewise remains a valid probe (code
patch, not the defended tables) for ground truth about dispatch, but is not
needed for the working architecture.

## The deterministic chain (REA/Ghidra-pinned, boot-3 live-verified)

Static analysis of `prototypeenginef.dll` (loads at its preferred base
0x10000000, so static VAs == runtime VAs) located the engine's D3D9 wrapper
singletons and the real device stash - the answer the earlier "walk the
wrapper object DFS" pass was groping for:

- `0x11276D40` `g_wrapper` - written once by the D3D9 factory init
  (`if (g_wrapper == 0)` guard = single-creation proof; calls
  `Direct3DCreate9(0x20)`); `0x11276D30` `g_ctx` is the second write of the
  SAME object from inside the wrapper constructor.
- Wrapper layout: `{+0x00 IDirect3D9* (real d3d9.dll image vtable),
  +0x04 pddi context object, +0x08 (zeroed at init, later alias window at
  ctx+0x20), +0x0C holder object with a static .rdata vtable}`.
- **The device stash: `*(*(*(0x11276D40)) + 4) + 0x15C`** - i.e.
  wrapper -> ctx(+4) -> [+0x15C] = live `IDirect3DDevice9*` (the
  heap-vtable device the ASI slot-patches). Verified live: chain output
  matched the histogram-sweep-discovered device exactly.
- Two redundant copies exist (useful as validity checks from another boot):
  `ctx +0x150 -> Q -> [Q+0x84]` and `wrapper +0x0C -> [+0x08] -> +0x13C`
  (the latter resolves to the identical ctx+0x15C window).
- The earlier guessed chain `wrapper -> +8 -> +0x164` is disproven:
  `+0x08` is zeroed at construction; `+0x164` was reading the wrong class.

Tooling: `tools/engine_device_chain.py PID [--expect 0x...]` resolves the
chain in milliseconds, cross-checks all three paths agree, and (with
`--expect`) compares against a device found independently (histogram sweep).
Keep the full histogram discovery as the cold-start fallback; the chain is
the fast validation path for every subsequent boot. TODO next boot: confirm
the static addresses and `+4/+0x15C` offsets on a fresh boot (engine loads
at the same base, so they should transfer), then seed this into the ASI flow
ahead of any sweep.

## Seen in

- Prototype (RAD engine, D3D9 fixed-function), v1.0, NVIDIA user stack:
  five boots on 2026-10-18 (14 booleans IDs incl. 26960/27196/32532/5656),
  ending in a fully proven passthrough playtest - hero render + Alex chase.
  Full crash atlas + recipes in the mashup repo `docs/MODLOG.md`
  (2026-10-18 entries).
