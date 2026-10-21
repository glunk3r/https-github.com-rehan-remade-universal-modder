# Metro 2033 (2010) crash fix: m2033fix

A 9 KB `dinput8.dll` for the **original Metro 2033** (Steam 43110, `metro2033.exe` 1.0.0.1). It fixes a
vanilla crash that hits about **25–35 s after start**. The crash shows up as an access violation at
`0x84F72A` (sometimes `0x84F53C`), followed by "Previous launch was unsuccessful. Would you like to start in
safe mode?" on the next start. The DLL also lets the game save the mouse-smoothing option.

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

## The bug
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
| P2 | `0x84F6CB` | same pattern, call `E8 86 C9 BB FF` → `90`s | Keeps the charmap alive at shutdown. **Not proven to be needed:** no exit crash has been traced to it. | **off** |
| P3 | `0x9F371B` (`.data`) | `00` → `01` | Sets the save flag (`0x01000000`) on the `mouse_inertion` cvar object at `0x9F3710`, so the game writes mouse smoothing to `user.cfg` like other options. The object's vtable and name are checked first. | on |

Nothing else is hooked. There are no detours, IAT hooks or D3D/Steam/input hooks. `DirectInput8Create`,
the game's only import from dinput8, is forwarded unchanged to the system DLL.

## How it works
1. **`DllMain`** only records the DLL folder. At that point the loader lock is held and `.text` is still
   encrypted. MetroDeveloper 1.2.2, a `dinput8.dll` proxy too, hangs this build forever at this stage.
2. **The game's first `DirectInput8Create` call** (main thread, about 2 s after start, long before the
   language switch) does the rest:
   1. loads `GetSystemDirectoryW()\dinput8.dll` by full path;
   2. checks the exe: base `0x400000`, SizeOfImage `0xB64000`, TimeDateStamp `0x4C7775B7`;
   3. compares the exact bytes at each site;
   4. applies each enabled patch independently with VirtualProtect, write and FlushInstructionCache;
   5. writes `m2033fix.log`;
   6. forwards the call.
3. **On any mismatch** the patch is skipped with `SKIP … found …` in the log, and the game runs vanilla.

## Build
You need [Zig](https://ziglang.org/) (0.13+; 0.17.0 was used) on PATH.
```
powershell -ExecutionPolicy Bypass -File build.ps1      # -> build\dinput8.dll
```
- The build compiles with the Windows headers, then links with `-nostdlib`.
- `src/dinput8.def` exports the undecorated `DirectInput8Create`.
- The result imports only KERNEL32.

## Install
1. Close the game, then run `powershell -ExecutionPolicy Bypass -File install.ps1`.
   - It finds the Steam install, or you can pass `-Game "<install folder>"`.
   - If another `dinput8.dll` is there (MetroDeveloper), it stops. With `-Replace` it renames that one to
     `dinput8.dll.off`.
   - It copies `build\dinput8.dll`, plus `m2033fix.ini.txt` as `m2033fix.ini` (only if there is none
     yet).
   - To install by hand, copy those two files the same way.
2. Start the game. `m2033fix.log` next to the exe should show `P1 … OK`, `P2 … disabled in ini` and
   `P3 … OK`.

## Uninstall
`powershell -ExecutionPolicy Bypass -File uninstall.ps1 -Game "<install folder>"`, or delete `dinput8.dll`
and `m2033fix.ini`.
- A `dinput8.dll.off` is renamed back.
- `user.cfg` may keep a `mouse_inertion` line (P3). Vanilla runs it and drops it at the next save, which
  is harmless.

## Settings (`m2033fix.ini`)
| Key | Default | Meaning |
|---|---|---|
| `[fix] lang_switch_race` | `1` | P1 |
| `[fix] exit_charmap_free` | `0` | P2 (unproven; leave off unless an exit crash proves it) |
| `[fix] save_mouse_inertion` | `1` | P3 |
| `[log] enabled` | `1` | Writes `m2033fix.log` once at startup |

`mouse_inertion` is the mouse smoothing factor: default 0.9, range 0.01–1. The game reads `user.cfg` from
**Steam Cloud first** (`<Steam>\userdata\<id>\43110\remote\user.cfg`), so edit that copy. FOV is
`sick_fov` (saved; same value as `r_base_fov`, default 45).

## Verification
Same PC and settings, 10 Steam launches each, 130 s per launch, closed by PID:

| | Crashes | Notes |
|---|---|---|
| Without the DLL | **5/10** at 26–28 s | 4× `0x84F72A` (read `0xC`), 1× `0x84F53C` (write `0x0`); same worker chain in every dump |
| With the DLL (P1+P3) | **0/10** | No dumps; the charmap pointer went old → new directly in every run |

Fisher exact, one-sided: p = 0.016.
- **Menu exits with the DLL:** 4 in total. All were clean (no WER event), with no safe-mode prompt on the
  next start, and the game saved `mouse_inertion` itself.
- **Not tested:** other builds (Redux, GOG, retail), long play sessions beyond about 10 minutes, and
  changing the language from the options menu.

## Known limits
- Only `metro2033.exe` 1.0.0.1 (Steam) is supported; anything else stays vanilla.
- It can't be used together with MetroDeveloper, since both are `dinput8.dll`. MetroDeveloper 1.2.2 hung
  this build at startup anyway.
- P1 leaks one charmap object per language switch.

## Credits
- [tsnest/MetroTools](https://github.com/tsnest/MetroTools): reference for the VFI/UPK archive format used
  during the investigation.
- [tsnest/MetroDeveloper](https://github.com/tsnest/MetroDeveloper): the community engine mod for the
  series. It uses the same `dinput8.dll` load path, and its settings documented the dev console and
  config cvars.
- Ghidra, Frida, capstone, minidump (Python), Zig.
- **AI disclosure:** the investigation, code and tests were done by Claude Code (Opus 5.5) with and for
  wh1tem0nst3r, who reviewed the design before the DLL was built and ran the in-game exits.
