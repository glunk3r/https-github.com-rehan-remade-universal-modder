# Pursuit Force: Extreme Justice (USA) — Teardown Documentation

Game: Pursuit Force: Extreme Justice (USA), PSP, UCUS98640 (same as PF1), Bigbig Studios 2007 (`Game03` engine, `PursuitForce2` module).
Source dump: `C:\Users\gmbad\Downloads\teardown\Pursuit Force - Extreme Justice (USA) (En,Fr,Es)\`

## 1. Game engine

Proprietary in-house Bigbig Studios engine (`Game03` lineage) — direct evolution of Pursuit Force 1.
Built on Sony PSP SDK — no licensed middleware.

Evidence (from `PSP_GAME\SYSDIR\BOOT.BIN`, decrypted ELF32LE MIPS):
- `*** Copyright (c) 2005 Bigbig Studios ***` (carried over), `c:/Workdir/PursuitForce2/...`, `PursuitForce2` module name
- Same 22 SCE imports as PF1 + `sceNet/sceNetAdhoc/sceWlanDrv` for AdHoc multiplayer
- Zero hits for Unreal/RenderWare/Havok/PhysX/PhyreEngine/Gamebryo/FMOD/Wwise/Bink/Scaleform
- `Bullet*` hits are game objects, not Bullet Physics. `fmodf` is C math.

## 2. Disc layout

```
UMD_DATA.BIN (48B): UCUS-98640|...|0001|G
PSP_GAME/
  PARAM.SFO (472B): DISC_ID=UCUS98640, TITLE=Pursuit Force: Extreme Justice, v1.00, PSP_SYSTEM_VER=5.55
  ICON0.PNG (30KB, 144x80), PIC1.PNG (241KB, 480x272), ICON1.PMF (358KB, PSMF0012), SND0.AT3 (85KB)
  SYSDIR/
    EBOOT.BIN (3,179,248B, ~PSP encrypted, tag PursuitForce2)
    BOOT.BIN  (3,178,901B, decrypted ELF; 347B = crypt-header stripped)
    UPDATE/: EBOOT.BIN (~PSP/updater 5.2MB), DATA.BIN (PSAR FW 18.4MB), PARAM.SFO (MSTKUPDATE ver 5.55)
  USRDIR/
    MAIN.PAK (1,404,203,584B, 1508 files) — all game data
```

## 3. Executable (BOOT.BIN)

- ELF32LE MIPS (`e_machine=8`), `e_type=0xFFA0` (SCE PSP), `entry=0x001D63F8`
- 2x PT_LOAD: text 2,531,348B `R-X`; data/bss 3,156B file / 195,796B mem `RW-`
- 62 sections: `.text` 2.4MB, `.rel.text` SCE-reloc ~500KB, `.rodata` ~100KB, `.data` ~60KB, `.bss` ~133KB
- 22+ SDK imports (PF1 set + `sceNet/sceNetAdhoc/sceWlanDrv` for AdHoc multiplayer)
- Engine ID: `*** Copyright (c) 2005 Bigbig Studios ***`, `c:/Workdir/PursuitForce2/...`, `PursuitForce2` module name
- Handlers: `Character/Physics/GamePhysics/Vehicle/Mission/Object/Trigger/Particle/CutScene/SceneSetter/SceGuSignal` + `GameAudio/Vehicle_Audio_Handler`, `GameMode_Handler`, `Net*` for AdHoc
- Asset formats: same `psp*` family (`.pspptx`, `.pspp3d`, `.psppve`, `.pspppprt`, `.psppfnt`, `.chpsp`, `.anp`, `.pph`, `.pob`, `.inp`, `.stf`, `.msp`, `.VAG`, `.vib`, `.vdb`) + `.VIB/.VDB` speech banks

## 4. PAK container (MAIN.PAK)

```
0x00: 02 50 41 4B        (version 2, "PAK")
0x04: u32LE file count   (1508)
0x08: u32LE hdrsize      (78300 = name table bytes)
0x0C: build path         "c:\\workdir\\pursuitforce2\\game\\pakfile creation\\" + "\r"
0x80: index, 16B/entry LE: data_off | size | unk=0x0012F94C | name_off
      index_end = 0x80 + 16*n = 0x5EC0
      name table = [index_end, index_end+hdrsize), NUL/double-NUL padded names
      data_start = align2048(index_end+hdrsize); blobs run to EOF
      Verified: off[n+1]==align2048(off+size), off%2048==0, max(off+size)==filesize.
```

- 1508 entries, 1001 unique names in table, 962 non-zero files extracted
- All names under `Data_PSP\...` (music, speech, surfaces, plus full asset tree)

## 5. Extracted Assets (`EXTRACTED\`)

- `Data_PSP\Audio\Music\*.at3` (44+): gang themes (Cons/Raid/Synd/Viper/War), Menu/Win/Lose, Cop
- `Data_PSP\Chains\Act*\Speech\*.VIB/.VDB` (multi-lang EN/FR/SP): mission speech banks
- `Data_PSP\Surfaces.INP` — physics surface definitions
- Full asset tree expected: `.pspptx` (textures), `.pspp3d` (models), `.chpsp` (characters), `.psppve` (vehicles), `.pspppprt` (particles), `.psppfnt` (fonts), `.pspp3d` (weapons), `.pspchunk` (levels), `.VIB/.VDB` (SFX/speech), `.inp/.dat/.stf` configs

## 6. Movies / Modules / Updater

- No separate MOVIES folder (movies likely embedded in MAIN.PAK or streamed)
- `modules_psp/psmf.prx` (7.4KB) — only module bundled
- `UPDATE/`: FW 5.55 updater (`MSTKUPDATE`, `PSAR` 18.4MB), matches game's `PSP_SYSTEM_VER=5.55`

## 7. Engine verdict

**Same Bigbig `Game03` proprietary engine** as Pursuit Force 1, evolved:
- Added AdHoc multiplayer (`sceNetAdhoc`, `sceWlanDrv`)
- Larger PAK (1.3GB vs 1.2GB), 1508 vs 1626 files
- Mission "Chains" system with multi-lang speech banks
- Same asset pipeline (`.psp*` formats), same SDK, same handlers
- No licensed middleware anywhere

This file serves as the persistent record.