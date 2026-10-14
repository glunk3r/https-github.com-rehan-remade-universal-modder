# Metal Gear Solid V: Ground Zeroes (PC) — Teardown Documentation

**Game:** Metal Gear Solid V: Ground Zeroes  
**Platform:** PC (Windows, Steam AppID 311340)  
**Developer:** Kojima Productions (verified: `KJP` ×4 in exe)  
**Publisher:** Konami  
**Year:** 2014 (console) / Steam release (AppID 311340)  
**Engine:** FOX Engine (verified)

---

## 1. Game Engine

**Engine:** FOX Engine (verified: `FOX` ×7 — `F_SID_DECL`, `symbols.txt`, `__FOX_PRIORITY0-4`, mission/event opcodes `ELIMINATE_RAT/CROW`, `CREATE_FOX_MARK`, `DEMO_START/END`)  
- **Middleware (verified via binary evidence):**
  - **Steamworks** (`SteamAPI_Init`, `steam_api64.dll`, AppID 311340)
  - **Lua entities** (`Lua Entity`, `Lua Core Entity` in engine type registry — FOX entity scripting)
- **Executable:** `MgsGroundZeroes.exe` (33,477,200 bytes, unpacked)
- **Container:** `.g0s` opaque archives (`data_00.g0s` 225 MB, `data_01.g0s` 1.1 GB, `data_02.g0s` 1.6 GB — no magic, encrypted/compressed)
- **Assets:** `.ftex` (FOX textures, ×208 refs in exe)
- **Scripting:** Lua (entity system)

**Falsified:** `hk` ×89 / `Nx` ×304 = x86 opcode-byte noise (single letters in disassembly), NOT Havok/PhysX. `CRI` ×4 = `desCRIption`/`subsCRIbe` substrings, not CRIWARE. `fmod` ×2 = CRT math. No Bink, Wwise, FMOD, Miles, Oodle, Denuvo, SecuROM, D3DX, PhysX strings.

**Evidence from dump:**
- `version_info.txt` (`ESRB_Eng`, `ver 1.005 euna_en`), `steam_appid.txt` (311340), `_Redist/`, uninstaller

---

## 2. Key Technical Details

- **FOX data discipline**: everything behind opaque `.g0s`; textures referenced as `.ftex`; symbol-hash assert macros (`FOX_STRHASH_VER`) compiled in
- **No licensed physics/audio middleware evidenced** — FOX carries its own systems + Lua entities + Steam; audio/video codec specifics unconfirmed (no Bink/Wwise/FMOD/CRI traces)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Metal Gear Solid V - Ground Zeroes\`*  
*Engine: FOX Engine, Kojima Productions 2014*