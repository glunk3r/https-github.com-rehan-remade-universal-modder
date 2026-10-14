# 007 Legends (PC) — Teardown Documentation

**Game:** 007 Legends  
**Platform:** PC (Windows, Steam + emu configs in dump)  
**Developer:** Eurocom (verified: `Eurocom` ×2, `EngineXT` ×6, `X:\EngineXT\Code\...` build paths)  
**Publisher:** Activision  
**Year:** 2012 (`Bond2012PC.exe`)  
**Engine:** Eurocom EngineX (verified)

---

## 1. Game Engine

**Engine:** Eurocom EngineX (verified: `EngineXT requires at least PixelShader/VertexShader 3.0`, `X:\EngineXT\Code\Network\DemonWare\...`)  
- **Middleware (verified via binary/DLL evidence):**
  - **Bink Video** (`Bink` ×28 + `binkw32.dll`; `EXMovieDecoderBink::StartupMovie()`)
  - **XAudio** (`OXAudioManager`, faction bark system: `XAudioManager: Unknown faction (%s) defaulting to Bond/MI6!`)
  - **DemonWare** (online/networking: `bdCore/bdHashMap`, `bdRemoteTaskManager`, `bdNet->Start()`, bdFacebook/bdTwitter social)
  - **Steamworks** (`Steam` ×93: `EXContentEnumerateDownloadedItemsParamsSteam`, marketplace UI params + `steam_api.dll`)
  - **DirectX 9** (`D3DX` ×1; Shader Model 3.0 floor)
- **Executable:** `Bond2012PC.exe` (14,818,088 bytes) + `Bond2012PC.ex_` (19 KB, compressed backup?)
- **Audio archives:** `EUROSOUND_<REGION>.000` + `.BIN` pairs + `EUROSOUND_<REGION>_STR.000` streamed banks (COM 409 MB / COM_STR 1.18 GB; per-language FRE/GER/RUS/USA)
- **Container:** `filelist.000`–`.003` (2.1/2.1/2.1/0.68 GB split archives) + `FILELIST.BIN`
- **Support DLLs:** `PCGamePadDB.dll`, `PCXMLParser.dll`
- **Physics:** Unconfirmed (no Havok/PhysX strings)

**Falsified:** `Nx` ×131 / `Lua` ×9 = x86 opcode-byte noise. `CRI` ×3 = ASN.1/DemonWare substrings. `fmod` ×2 = CRT math. `Ogg` ×1 = noise. No RenderWare/Havok/PhysX/FMOD/Miles/Unreal/Unity/Denuvo/SecuROM.

**Evidence from dump:**
- `DATA/`, `DOWNLOAD/`, `UPDATE/` dirs; `FlawlessWidescreen/` (third-party mod); `steam_emu.ini` (emulator config — crack artifact)
- `_Cheat Codes.txt`, `_Language Picker.bat`, `__How To Play!!.txt` (scene extras)

---

## 2. Key Technical Details

- EngineX identified by its own shader-floor asserts + `X:\EngineXT` build paths — Eurocom's last bond game before closure
- DemonWare (Activision online stack) + Steam params + faction-aware XAudio barks = full online/multiplayer audio pipeline

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\007 Legends\Bond2012PC.exe`*  
*Engine: Eurocom EngineX, Eurocom 2012*