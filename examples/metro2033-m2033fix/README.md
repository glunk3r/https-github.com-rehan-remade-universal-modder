# Metro 2033 (2010) crash fix: m2033fix

A 13 KB `dinput8.dll` for the **original Metro 2033** (Steam 43110, `metro2033.exe` 1.0.0.1). It fixes a
vanilla crash that hits about **25–35 s after start**. The crash shows up as an access violation at
`0x84F72A` (sometimes `0x84F53C`), followed by "Previous launch was unsuccessful. Would you like to start in
safe mode?" on the next start.

Version 0.2 also brings over two things the DRM-free GOG release fixes in the same exe build:
- a display-mode list that holds 1024 modes instead of 512;
- a V-Sync option that actually works under DX11.

- **The game is untouched.** The exe, its SteamStub DRM and the archives are not modified. All changes
  live in the game's memory. They are made after SteamStub has decrypted the code itself, and only when the
  exact expected bytes are found.
- **No loader is needed.** Windows loads `dinput8.dll` from the game folder. The DLL imports only
  `kernel32.dll`, uses no CRT, and does nothing in `DllMain`.
- **Easy to roll back.** Each fix is a switch in `m2033fix.ini`, and deleting the DLL gives back the
  vanilla game.

Tested on: Windows 11, Steam build of `metro2033.exe` 1.0.0.1 (PE timestamp `0x4C7775B7`), RTX 3050 Ti
laptop (hybrid with an AMD iGPU), DX11, fullscreen 1920×1080, Russian text. Field note:
`knowledge/games/metro-2033/original-metro-2033-steamstub-exe-vfi-upk-archives-quicklz-a.md`.

## The bug (P1)
- About 25 s after start, the main thread switches the text language (`FUN_0085B090`). It does three
  things in order:
  1. sets the global charmap pointer `DAT_00A14F88` to NULL;
  2. frees the old charmap (`0x40C060`, which also zeroes its size);
  3. stores the new one.
- Meanwhile a worker thread lays out UI text. Its chain is `0x7A40C3 → FUN_00846E10 → FUN_00846010 →
  FUN_008456E0 → FUN_0084F6E0`, and `FUN_0084F6E0` converts UTF-16 to the game's charmap encoding.
- That conversion re-reads the global for every character. If the switch lands in the middle, the worker
  dereferences NULL+0xC and the game dies. The crash was confirmed by call-validated stack scans of 5
  minidumps.
- The switch happens on every start, whatever the Steam language. A faster GPU changes the timing, and on
  the test laptop vanilla crashed in **5 of 10** starts.

## What it changes (complete list)
| Id | Address | Bytes | Effect | Default |
|---|---|---|---|---|
| P1 | `0x85B0A8` | `C7 05 88 4F A1 00 00 00 00 00 E8 A9 0F BB FF` → 15× `90` | The NULL store and the free disappear. The new charmap is installed by the existing single aligned store at `0x85B0C2`, so the global is never NULL, and the old table stays valid for a thread still reading it. It leaks one table of a few KB per language switch (one per start). | on |
| P4 | `0x7A1F1A`, `0x7A1F3F`, `0x7A1F4F`, `0x7A1F77` | `B8 40 38 00 00` → `B8 80 70 00 00`; `8D 95 C0 C7 FF FF` → `8D 95 80 8F FF FF`; `C7 45 FC 00 02 00 00` → `C7 45 FC 00 04 00 00`; `8D 8D C0 C7 FF FF` → `8D 8D 80 8F FF FF` | `FUN_007A1F17` reads `IDXGIOutput::GetDisplayModeList` into a stack buffer of 512 modes. This raises the stack frame, both buffer references and the capacity to 1024, byte for byte as the GOG build does. All four parts are applied, or none. With 512 modes or fewer nothing changes. | on |
| P5 | `0x7A1733`, `0x7A1D71` | `53 53 57 FF D1` and `53 55 FF 50 20` → `E9 rel32` to a stub in this DLL | Both per-frame `IDXGISwapChain::Present` calls pass `SyncInterval = 0` whatever `r_vsync` says. The stubs push `r_vsync ? 1 : 0` (bit `0x10` of `0x9F2820`), call `Present`, and jump back. Each 5-byte jump is written with one `cmpxchg8b`. The `r_vsync` registration code is checked first. With `r_vsync off` the frames are the same as vanilla. | on |

Nothing else is hooked. There are no IAT hooks and no Steam or input hooks. P5's two jumps are the only
detours, and they sit at the game's own `Present` call sites. `DirectInput8Create`, the game's only import
from dinput8, is forwarded unchanged to the system DLL.

**Dropped in 0.2:**
- **P2** kept the charmap alive at shutdown. No exit crash was ever traced to it.
- **P3** set the save flag of the `mouse_inertion` cvar. It was a convenience, not a fix, and the option
  isn't in the original config at all.

**Deliberately not ported from GOG:**
- GOG's 120 FPS busy-wait limiter: in gameplay this laptop stays below `target_fps`, so the vanilla
  `Sleep` limiter never runs.
- The loader input checks (not fully traced).
- The "unsupported graphics card" popups.

## How it works
1. **`DllMain`** only records the DLL folder. At that point the loader lock is held and `.text` is still
   encrypted. MetroDeveloper 1.2.2, a `dinput8.dll` proxy too, hangs this build forever at this stage.
2. **The game's first `DirectInput8Create` call** (main thread, about 2 s after start) does the rest. This
   is long before the language switch, the display-mode query (about 4 s) and the first `Present`.
   1. loads `GetSystemDirectoryW()\dinput8.dll` by full path;
   2. checks the exe: base `0x400000`, SizeOfImage `0xB64000`, TimeDateStamp `0x4C7775B7`;
   3. compares the exact bytes at each site;
   4. applies each enabled patch independently with VirtualProtect, write and FlushInstructionCache;
   5. writes `m2033fix.log`;
   6. forwards the call.
3. **On any mismatch** the patch is skipped with `SKIP … found …` in the log, and the game runs vanilla.
4. **Rebasing:** P5's stubs return through variables that the DLL's relocations fix up. The test system
   loaded the DLL away from its preferred base, and the return path worked.

## Build
You need [Zig](https://ziglang.org/) (0.13+; 0.17.0 was used) on PATH.
```
powershell -ExecutionPolicy Bypass -File build.ps1      # -> build\dinput8.dll
```
- The build compiles with the Windows headers, then links with `-nostdlib`.
- `src/dinput8.def` exports the undecorated `DirectInput8Create`.
- The result imports only KERNEL32.
- The P5 stubs are a top-level `__asm__` block in `src/m2033fix.c`.

## Install
1. Close the game, then run `powershell -ExecutionPolicy Bypass -File install.ps1`.
   - It finds the Steam install, or you can pass `-Game "<install folder>"`.
   - If another `dinput8.dll` is there (MetroDeveloper), it stops. With `-Replace` it renames that one to
     `dinput8.dll.off`.
   - It copies `build\dinput8.dll`, plus `m2033fix.ini.txt` as `m2033fix.ini` (only if there is none
     yet).
   - To install by hand, copy those two files the same way.
2. Start the game. `m2033fix.log` next to the exe should start with `m2033fix 0.2-pre (P4, P5)` and show
   `P1 … OK`, four `P4 display_modes_1024 … OK` lines and `P5 vsync_follow_cvar` `A … OK` / `B … OK`.

**Upgrading from 0.1:**
- `install.ps1` replaces the DLL but keeps your `m2033fix.ini`.
- 0.2 ignores the old keys (`exit_charmap_free`, `save_mouse_inertion`).
- The new keys default to on when they are missing.
- A `mouse_inertion` line that 0.1 got saved into `user.cfg` is dropped by the game at the next settings
  save.

## Uninstall
`powershell -ExecutionPolicy Bypass -File uninstall.ps1 -Game "<install folder>"`, or delete `dinput8.dll`
and `m2033fix.ini`. A `dinput8.dll.off` is renamed back.

## Settings (`m2033fix.ini`)
| Key | Default | Meaning |
|---|---|---|
| `[fix] lang_switch_race` | `1` | P1 |
| `[fix] display_modes_1024` | `1` | P4 |
| `[fix] vsync_follow_cvar` | `1` | P5. V-Sync itself is still the game's option: `r_vsync on`/`off` in `user.cfg` or the options menu. |
| `[log] enabled` | `1` | Writes `m2033fix.log` once at startup |

The game reads `user.cfg` from **Steam Cloud first** (`<Steam>\userdata\<id>\43110\remote\user.cfg`), so
edit that copy. FOV is `sick_fov` (saved; same value as `r_base_fov`, default 45).

## Verification
Same PC and settings, Steam launches of 130 s each, closed by PID:

| Build | Runs | Crashes | Notes |
|---|---|---|---|
| Without the DLL | 10 | **5/10** at 26–28 s | 4× `0x84F72A` (read `0xC`), 1× `0x84F53C` (write `0x0`); same worker chain in every dump |
| 0.1 (P1 + P3) | 10 | **0/10** | No dumps; the charmap pointer went old → new directly in every run |
| 0.2 test build, `r_vsync on` | 10 | **0/10** | P5 A/B OK in every log |
| 0.2 (this source), `r_vsync off` | 10 | **0/10** | No dumps; P1, P4 ×4, P5 A/B OK in every log |

Without the DLL vs 0.1: Fisher exact, one-sided, p = 0.016.

**P5:** a Frida hook on `dxgi.dll`'s `Present` (not on game code) read the SyncInterval of the frames.
- With `r_vsync off` it saw `SyncInterval = 0`; with `r_vsync on`, 1 from the first frame.
- Setting the `r_vsync` bit in a running game switched it to 1 within the same session.
- Vanilla passes 0 in all of these cases, and PresentMon agrees.

**P4:** all four writes apply (log `OK`) and the game starts and runs normally. This laptop has only 62
display modes, so the more-than-512 case was not reproduced.

**Not tested:**
- the visible effect of V-Sync (none on this hybrid-GPU laptop);
- P4 with more than 512 modes (4K, high refresh, DSR);
- the options-menu V-Sync toggle (the bit was set directly, as the menu setter does);
- other builds (Redux, retail), long play sessions beyond about 10 minutes, and changing the language from
  the options menu.

The GOG build is not supported. Its exe has no SteamStub section (SizeOfImage `0xB0C000`), so the identity
check fails and it stays vanilla. It already ships its own equivalents of P4 and P5.

## Known limits
- Only `metro2033.exe` 1.0.0.1 (Steam) is supported; anything else stays vanilla.
- It can't be used together with MetroDeveloper, since both are `dinput8.dll`. MetroDeveloper 1.2.2 hung
  this build at startup anyway.
- P1 leaks one charmap object per language switch.
- With P5 and `r_vsync on`, the frame rate is capped at the display's refresh rate.

## Credits
- [tsnest/MetroTools](https://github.com/tsnest/MetroTools): reference for the VFI/UPK archive format used
  during the investigation.
- [tsnest/MetroDeveloper](https://github.com/tsnest/MetroDeveloper): the community engine mod for the
  series. It uses the same `dinput8.dll` load path, and its settings documented the dev console and
  config cvars.
- The GOG release of the same exe build was the reference for P4 and P5.
- Ghidra, Frida, capstone, minidump (Python), PresentMon, Zig.
- **AI disclosure:** the investigation, code and tests were done by Claude Code (Opus 5.5) with and for
  wh1tem0nst3r. wh1tem0nst3r reviewed each design before the DLL was built, chose P5's stub variant and
  ran the in-game exits.
