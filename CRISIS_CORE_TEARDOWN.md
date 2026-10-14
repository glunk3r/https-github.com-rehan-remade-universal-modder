# Crisis Core: Final Fantasy VII (PSP) — Teardown Documentation

**Game:** CRISIS CORE -FINAL FANTASY VII- (ULUS10336, v1.00)  
**Platform:** PlayStation Portable  
**Developer:** Square Enix  
**Publisher:** Square Enix  
**Year:** 2008 (USA; EBOOT dated Dec 2007, FW 3.73)  
**Format:** UMD ISO (1,716,715,520 bytes, 18 root entries)

---

## 1. Game Engine

**Engine:** Square Enix proprietary PSP engine (verified: decrypted `BOOT.BIN`, 2,162,537 bytes)  
- **Middleware (verified via binary evidence):**
  - **PMF Video** (movie path template in binary)
  - **ATRAC3 Audio** (`sceAtrac3plus`/`sceSasCore` SDK imports — PSP native audio)
- **Executable:** `PSP_GAME\SYSDIR\BOOT.BIN` (decrypted, string-sparse — packed code section) + `EBOOT.BIN` + `UPDATE\` (FW updater with 18 MB DATA.BIN)
- **Container:** `PSP_GAME\USRDIR\discimg.pkg` (**1,602,158,592 bytes** — Square package holding ~all game data) + `discimg.fse`
- **Assets:** XMB visuals (`ICON0.PNG`, `ICON1.PMF`, `PIC0/PIC1.PNG`, `SND0.AT3`)
- **Physics/scripting:** Unconfirmed (string-sparse binary yields nothing)

**Falsified:** `CRI` ×1 = savefile label (`CCFF7DAT.BIN|CRISIS CORE...` — disc string, not CRIWARE). `fmod` ×1 = libm trig (CRT). No Havok/PhysX/Bink/FMOD/Miles/Lua/Ogg/Unreal strings.

**Evidence from dump:**
- `PARAM.SFO`: `DISC_ID ULUS10336`, `TITLE CRISIS CORE -FINAL FANTASY VII-`, `DISC_VERSION 1.00`, `PSP_SYSTEM_VER 3.73`
- `UMD_DATA.BIN` (48 bytes)

---

## 2. Key Technical Details

- **1.6 GB single-package layout**: near-zero root files, everything inside `discimg.pkg` — Square's PSP packaging discipline (same family as later FF Type-0 structure)
- String-sparse BOOT.BIN implies packed/obfuscated code — middleware audit limited to SDK imports + PMF/ATRAC3

---

*Generated from `Crisis Core - Final Fantasy VII (USA).iso` (`PSP_GAME\SYSDIR\BOOT.BIN`, `PARAM.SFO`)*  
*Engine: Square Enix proprietary PSP engine, Square Enix 2008*