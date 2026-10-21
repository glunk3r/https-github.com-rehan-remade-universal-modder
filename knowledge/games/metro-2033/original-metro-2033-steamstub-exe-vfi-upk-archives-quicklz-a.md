---
kind: game
title: 'Original Metro 2033: SteamStub exe, VFI/UPK archives, QuickLZ and the crc32-keyed scripts.bin'
game: Metro 2033
games_also: []
game_version: 'Original 2010 Steam build (app 43110), metro2033.exe 1.0.0.1, PE timestamp 2010-08-27'
platform: windows
engine: 4A Engine
route: native-hook
tools: ["Python 3 + pefile (static PE/RTTI/strings)", "own VFI/UPK lister + pure-Python QuickLZ 1.5 L3 decoder", "MetroTools source (format reference)", "MetroDeveloper 1.2.2 (hangs this build)", "Ghidra 12.1.4 on a read-only memory image", "Frida 17.24.3", "capstone + minidump (Python)", "Zig 0.17.0 (x86-windows-gnu, no CRT)"]
anti_cheat: "none (single-player). The exe is SteamStub-wrapped; it was not unpacked or patched."
status: working
agents:
- Claude Code (Opus 5.5)
humans: ["wh1tem0nst3r"]
date: '2026-10-21'
links:
  - "https://github.com/tsnest/MetroTools"
  - "https://github.com/tsnest/MetroDeveloper"
  - "https://github.com/tsnest/MetroDeveloper/releases"
tags: [steamstub, rtti, vfi, vfs0, upk, quicklz, scripts-bin, crc32, level-bin, cvars, metrodeveloper]
---
# Original Metro 2033: SteamStub exe, VFI/UPK archives, QuickLZ and the crc32-keyed scripts.bin

This is a static, read-only reverse of the 2010 Steam release. The exe's code section is SteamStub-encrypted
on disk, so the engine was mapped from RTTI and strings, which are not encrypted. The archives were decoded
fully, patch packs included.
- The pure-Python extractor reproduces an earlier, independent extraction byte for byte.
- `content\scripts.bin` turned out to be a crc32-keyed bundle of config files; 90 of its 277 names were
  recovered.
- A dynamic pass then read the running process, read-only. It recovered the cvar table and the config
  loader, and found that the installed MetroDeveloper hangs this build (Gotchas 8–11).
- A 9 KB `dinput8.dll` proxy (m2033fix, kernel32 only) patches two things in memory after SteamStub has
  decrypted the code, and nothing else:
  - a vanilla race that crashed half of all starts on an RTX laptop;
  - the save flag of `mouse_inertion`.
  - Verified with an A/B soak (Gotcha 14).

## Setup
- **Install:** Steam app 43110 (a secondary Steam library), Windows 11.
- **Exe:** `metro2033.exe` 1.0.0.1, PE32 i386, VS2005 runtime (MSVCR80), PhysX 2.8 (PhysXLoader),
  d3dx9_42, D3D11 path present. The PDB path string is `x:\bin_x86\metro2033.pdb`.
- **Loader:** MetroDeveloper 1.2.2 was installed: a single `dinput8.dll` + `MetroDeveloper.ini`.
  Since 1.2.1 there is no separate `.asi` file. The game imports `DirectInput8Create`, which is why the
  proxy loads. It hangs this build (Gotcha 8) and was disabled.
- **Tooling:**
  - static part: Python 3.14 via `uv`, `pefile`;
  - dynamic part: Ghidra 12.1.4 on a read-only memory image (raw blob at `0x400000`), Frida, capstone,
    minidump;
  - the fix: Zig 0.17.0.
- **Hardware:** RTX 3050 Ti laptop with an AMD iGPU; the game was forced to the dGPU.
- **Benchmark exe:** the separate `metro2033benchmark.exe` is a .NET app. Ignore it when choosing a
  route.

## Route and why
The investigation started on the data route. Gameplay lives in data (`scripts.bin`, `level.bin`), and
most option changes need only `user.cfg` (Gotchas 9–13).
- **The crash fix had to be native.** The bug is a race in engine code, so it is fixed by a byte patch in
  memory from a `dinput8.dll` proxy (`examples/metro2033-m2033fix`).
- **The community loader wasn't usable.** MetroDeveloper 1.2.2 hangs this build (Gotcha 8).
- **Unpacking the exe:** not done. SteamStub counts as DRM under the toolkit's safety rules. The code was
  read from a read-only memory image of the running game, and the patch is applied only after the stub
  has decrypted `.text` itself.

## How the game works (what we had to learn)
- **SteamStub:**
  - The entry point is in a `.bind` section, and `.text` (about 5.3 MB) has Shannon entropy 8.0, so a
    disassembler on the file shows noise.
  - `.rdata`/`.data` are plain. They yield 1,622 MSVC RTTI type names (`.?AV...@@`) and about 45k ASCII
    strings.
- **Engine map from RTTI:**
  - `visual` (renderer/models, ~300 classes).
  - `vs` (~300): visual-scripting blocks, i.e. `action_*`, `trigger_*`, `entity_*`, logic gates,
    `drezina_*` (handcar), `kulemet_*` (mounted gun).
  - `as`: animation state graph with blenders and transitions.
  - `vfs`: package registry and pack readers.
  - `uskeleton`, `umainmenu`, AI classes (`commander`, `cover`, `speech`).
- **Leftover multiplayer:** `network_client`/`network_server`, RakNet interfaces, a `-server -map %s`
  argument and messages such as "only server can change levels".
- **Console:** about 325 cvar names in strings (`g_*`, `r_*`, `ph_*`, `s_*`, `dbg_*`), e.g. `g_god`,
  `g_unlimitedammo`, `g_player_speed_scale`, `ph_gravity`, `r_base_fov`. The console itself needs
  MetroDeveloper.
- **Launch arguments in strings:** `-editor`, `-map`, `-save`, `-cfg`, `-test`, `-trace`, `-logflush`,
  `-nogpu`, `-force_physx`, `-openautomate`. Their behaviour is untested.
- **`content.vfi`:**
  - It is a stream of `(u32 id, u32 size)` chunks. Id `0xFFFFFFFF` is the header (u32 version 0 +
    16-byte GUID).
  - Every other chunk is one pack. Sub-chunk 0 holds the pack's file name and size. Sub-chunk 1 holds the
    file records: u32 key, offset, size, packed size, name length, then the name XOR-ed with the key's low
    byte.
  - 46,165 entries across `content.vfs0`, `textures.vfs0/1`, 7 `sounds*.vfs0` and `videos.vfs0`.
- **`content.upk0..3` (patch archives):**
  - Chunk 0 is the blob, chunk 1 the TOC (same record layout), chunk 2 four unknown bytes, chunk 3 the
    GUID.
  - **TOC offsets are absolute in the `.upk` file.**
  - upk1 carries the patched `scripts.bin`, `anims.bin`, all 9 `.lng` files, every `level.bin` /
    `level.add.bin`, and the whole `l08_market_launch` level. upk0 is one texture; upk2/upk3 hold only
    `scripts.bin`.
  - The patch order upk0 < upk1 < upk2 < upk3 is assumed from the names, not proven.
- **Compression:** QuickLZ 1.5.0, level 3, `QLZ_STREAMING_BUFFER 0x20000`.
  - Packets sit back to back. Each has a 1-byte flag (bit 0 = compressed, bit 1 = 9-byte header), then
    packed and unpacked sizes.
  - Back-references can reach into earlier packets, so decode all packets into one contiguous buffer.
  - Entries whose packed size equals their size are stored raw.
- **`level.bin`:** the magic `levl`, then u32 unpacked size, then a QuickLZ stream. Example:
  `l02_exhibition` unpacks from 384,197 to 1,467,910 bytes. It contains entities and script data.
- **`content\scripts.bin`:**
  - A sequence of `(u32 key, u32 size, body)` records that tile the file exactly (277 records in the
    patched copy).
  - **key = crc32 (zlib) of the lowercase path `content\scripts\<name>.bin`.**
  - Recovered names include `gamedata`, `game_materials`, `hud_manager`, `mainmenu`, `environments`,
    `color_anim_lib`, `speech_manager`, `dynamic\human\human`, `dynamic\monsters\<m>\<m>`, `fonts_<lang>`
    (9 languages), and one record per level `lNN_<name>`.
  - Bodies carry no field names (positional, per class), so editing values needs the class layouts.

## Build steps
1. `python vfi_list.py "<game dir>" files.tsv` lists every entry with its pack, offset and sizes.
2. `python vfi_extract.py "<game dir>" <out dir> <substring>...` extracts matching entries, applying the
   upk patches in order.
3. Brute-force `scripts.bin` names as `crc32("content\\scripts\\" + candidate + ".bin")`. Draw candidates
   from archive path components, exe strings and the strings inside `scripts.bin`, under folders such as
   `dynamic\<cat>\<name>\<name>`.
- The scripts are not in the KB. Their layout above is enough to rewrite them in about 150 lines of
  Python.
- Keep the output outside the game folder and the repo.

**Crash-fix proxy (m2033fix).**
- Source, build, install and uninstall scripts: `examples/metro2033-m2033fix` (README has the full patch
  list and test tables).
- Build:
  1. Compile with headers: `zig cc -target x86-windows-gnu -O2 -c m2033fix.c`.
  2. Link without the CRT: `zig cc ... -shared -nostdlib -Wl,--entry=DllMain@12 m2033fix.o dinput8.def -lkernel32`.
     `-nostdlib` drops the Windows headers too, hence the two steps.
  3. Provide your own `memcpy`/`memset`/`strlen` and avoid 64-bit division.
  4. The `.def` is required, otherwise the export is `DirectInput8Create@20`.
- Behaviour:
  - `DllMain` only records the module path.
  - The first `DirectInput8Create` loads `GetSystemDirectoryW()\dinput8.dll`, checks the exe (base
    0x400000, SizeOfImage 0xB64000, TimeDateStamp 0x4C7775B7) and the exact bytes at each site, applies
    the patches, logs them, then forwards the call.
  - If anything mismatches, the proxy stays a pure pass-through.
- Rollback: delete `dinput8.dll`.

## Verification
- **Decoder:** checked against an independent earlier extraction of `l02_exhibition` (`level.portals`,
  `level.environment`); the files are byte-identical. Every unpacked size matches the TOC.
- **`scripts.bin`:** the record walk ends exactly at EOF. Name matches are crc32 hits, so they are
  certain once found.
- **Not verified:**
  - anything at runtime: loose-file override, cvars, launch arguments;
  - the upk priority order;
  - the record body schema.

## Gotchas
1. **Disassembly of `metro2033.exe` is garbage.** **Cause:** SteamStub; `.text` is encrypted and the
   entry point is in `.bind`. **Fix:** use RTTI/strings statically. For code, inspect the running
   process read-only. Don't run unpackers on the exe.
2. **`um scan` says ".NET application".** **Cause:** it scores `metro2033benchmark.exe`, the managed
   benchmark launcher. **Fix:** the game is native x86; use the native/data routes.
3. **`um scan` says "loaders: none".** **Cause:** MetroDeveloper is just a `dinput8.dll` + ini, which the
   scan doesn't know. **Fix:** look for `MetroDeveloper.ini` in the game root.
4. **UPK entries decompress into nonsense or index errors.** **Cause:** TOC offsets were treated as
   relative to the blob chunk. **Fix:** they are absolute file offsets.
5. **QuickLZ decode fails after the first packet.** **Cause:** the streaming buffer (0x20000) lets
   matches point into earlier packets. **Fix:** decode into one growing buffer, not per packet.
6. **`scripts.bin` keys don't match crc32 of bare names.** **Fix:** hash the full lowercase path with
   the `content\scripts\` prefix and the `.bin` suffix.
7. **No `uengine.log` although `[log] enabled = yes`.** **Cause:** the game simply hasn't been launched
   since MetroDeveloper was installed. Expect the log next to the exe after the first run; the game
   needs write access there. (Later, see 8: on this build the loader itself hangs.)
8. **The game sits windowless forever with MetroDeveloper 1.2.2 installed.** **Cause:** a WOW64
   thread-stack snapshot shows the main thread sleeping inside the `dinput8.dll` proxy's init. Steam is
   not yet initialised at that point, `steamclient.dll` never loads, and `uengine.log` stays at 0 bytes.
   **Fix:** rename `dinput8.dll` away, and vanilla shows its `_uengine_` window in about 5 s. Retry with a
   newer MetroDeveloper or report it upstream.
9. **Edits to `%LOCALAPPDATA%\4A Games\Metro 2033\user.cfg` are ignored.** **Cause:** `config_load` reads
   the **Steam Cloud** copy first (`SteamRemoteStorage` FileRead). It falls back to the local file, then
   to the archives. **Fix:** edit `<Steam>\userdata\<id>\43110\remote\user.cfg`.
   - Every line is executed as a console command with no filter.
   - So cvars the game never saves still apply, e.g. `r_base_fov` (default 45, range 1–90) and
     `mouse_inertion` (mouse smoothing, default 0.9). Both were verified by reading them from memory.
10. **Windowed 1280x720 opens as a blurry 1024x576 client area.** **Cause:** the exe is not DPI-aware, and
    Windows scales it at 125%. **Fix (untested):** the per-exe compatibility option "High DPI scaling
    override: Application".
11. **Cvar table.** The cvars are static objects in `.data`, typed by vtable: float, int, flag bit, enum,
    and commands.
    - Float layout: `{vtable, name, flags, ?, *value, min, max}`.
    - Flag bit `0x01000000` marks a cvar that is written back to user.cfg.
    - The console singleton registers a cvar through vtable+8 and executes a line through vtable+0x1c.
    - About 250 cvars are recoverable by scanning `.data` of a memory image for (vtable, name) pairs.

12. **FOV set with `r_base_fov` disappears after a session.** **Cause:** `sick_fov` (a "motion sickness"
    option) and `r_base_fov` share one value, at `0x9f2824`. Only `sick_fov` carries the save flag.
    **Fix:** write `sick_fov <deg>` instead.
    - The game keeps it across a menu exit (verified).
    - It travels with Steam Cloud, so every PC on the account gets the same FOV.
    - 60 felt too wide on a 16:9 laptop panel.
13. **`mouse_inertion 0.01` works (players reported crisp aiming) but is gone after a menu exit.**
    **Cause:** on exit the game rewrites user.cfg with only flagged cvars, and `mouse_inertion` has no
    flag.
    - The mouse code (`0x726260`) uses `k = sick_mouse + (1 - sick_mouse) * mouse_inertion` (defaults 0
      and 0.9). So the saved `sick_mouse` can only add smoothing and is no substitute.
    - **Fix options:**
      - re-apply the line before each launch, e.g. a Steam launch-option wrapper;
      - from a runtime patch, set the cvar's save flag (`flags |= 0x01000000` on the object at
        `0x9f3710`), so the game saves it itself.

14. **Random access violation about 25–35 s after start, or at exit (`c0000005` reading `0xC` at
    `0x84F72A`), then "Previous launch was unsuccessful. Start in safe mode?" on the next start.**
    **Cause:** a race in the text-language switch.
    - `FUN_0085B090` nulls the charmap global `DAT_00A14F88` and frees it before installing the new one.
    - Meanwhile another thread converts text with `FUN_0084F6E0`, which re-reads that global for every
      character.
    - The switch happens on **every** start at about 24–27 s, even when the Steam game language matches
      `lang_text`. An earlier guess that matching the languages avoids it was wrong: the charmap pointer
      still changed once per start in all 20 soak runs.
    - The crashing thread is always a late worker thread. A call-validated stack scan of 5 dumps shows
      `0x85EDA2 → 0x7A40C3 → FUN_00846E10 → FUN_00846010 → FUN_008456E0 → FUN_0084F6E0`.
    - One dump hit the same race at `0x84F53C` instead (a write to 0 via `FUN_00846E10 → 0x84F510`).
    - A faster dGPU makes it more frequent, and the delay Frida adds hides it.
    - **Fix (in-memory patch, exe untouched):** NOP the 15 bytes `C7 05 88 4F A1 00 00 00 00 00 E8 A9 0F
      BB FF` at `0x85B0A8`.
      - The global is then replaced by one aligned store at `0x85B0C2` and is never NULL.
      - The old table is leaked (a few KB once per start), so readers holding it stay valid.
    - **Measured:** 10×130 s Steam launches with the patch gave 0 crashes; without it, 5/10 crashed at
      26–28 s (Fisher p = 0.016). Menu exits with the patch were clean, and the next start showed no
      safe-mode prompt.
15. **Where the saves are.** `user.cfg` is in Steam Cloud (`remote\`). The campaign saves (`lNN_*.player`,
    `auto_save`) are Steam Auto-Cloud files under `Documents\4A Games\Metro 2033`. If OneDrive redirects
    Documents, they are under the OneDrive copy.
    - `um scan` and the first recon missed them.
    - `user.cfg`'s `xbox_state_data (...)()` line is game state the game rewrites itself; it went empty
      after an accidental new-mission start, so back it up before any session that starts missions.
16. **A proxy that does work in `DllMain` hangs this build** (see 8). A `dinput8.dll` proxy is reliable if it
    defers everything to the game's first `DirectInput8Create` call: on the main thread, about 2–4 s
    after start, with `.text` already decrypted by SteamStub.

## Open questions
- Does `unlock_content_folder` let a loose `content\scripts\<name>.bin` override the record inside
  `scripts.bin`, or only loose files that exist as real archive entries?
- What are the class layouts of `scripts.bin` record bodies? The next step is to find the reader in the
  running process (read-only debugger) via xrefs to the `content\scripts.bin` string.
- 187 unnamed `scripts.bin` records remain, mostly visual-script sequences and hand/weapon setups.
- What is the 4-byte UPK chunk 2? Is the upk order really numeric?
