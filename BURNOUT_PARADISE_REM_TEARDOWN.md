# Burnout Paradise Remastered (PC) — Teardown Documentation

**Game:** Burnout Paradise Remastered  
**Platform:** PC (Windows, Origin/EA App)  
**Developer:** Criterion Games (original) / Stellar Entertainment (remaster)  
**Publisher:** Electronic Arts  
**Year:** 2018 (original 2008)  
**Engine:** RenderWare (Criterion Games / Stellar Entertainment) — per PCGamingWiki engine listing (https://www.pcgamingwiki.com/wiki/Engine:RenderWare)

---

## 1. Game Engine

**Engine:** RenderWare (Criterion Games / Stellar Entertainment) — per PCGamingWiki engine listing  
- **Middleware (verified via binary/DLL evidence):**
  - **Lua** (×12: `LuaCode`, `TypeLib`, `LuaCodeResourceType` + `LUA/` script dir)
  - **EA WebKit** (`EAWebKit` ×2 + `EAWEBKIT/` dir — UI)
  - **XAudio2** (`XAudio` ×2; `Ogg`/`Vorbis` ×1 each, codec unconfirmed)
  - **Origin SDK** (`Origin` ×712 — integration + EULA; `origin_emu.dll` + `rune.ini` in dump = RUNE crack artifacts, not game tech)
  - **DirectX 11** (`d3dcompiler_47.dll`; `GPGPU/`, `POSTFX/`, `SHADERS.BNDL`)
- **Executable:** `BurnoutPR.exe` (130,604,032 bytes, unpacked) + `dbdata.dll` (12 MB)
- **Internal codename:** **B5** (`B5ComponentUnity`, `B5MenuItem`, `B5HudMessage` — Burnout 5 = Paradise)
- **Save/profile:** `AutoLogin.BurnoutParadiseSave`, `config.ini`
- **Physics:** In-house (no Havok/PhysX strings; Paradise's crash physics are custom)
- **Scripting:** Lua (gameplay/UI logic)

**Falsified:** `Denuvo` ×20 = Polish EA-legal EULA text mentioning Denuvo (`ochrony ... technologii Denuvo`) — NOT active protection evidence. `Unity` ×1 = `B5ComponentUnity` (codename, not the engine). `Ego`/`Neon`/`Speed` hits are substring noise (`JunkyardNeon` location, `GetPlayerSpeed` vars).

**Evidence from dump:**
- `EA_Criterion_Logo`, `Criterion Games|Burnout Paradise Remastered`, `NEW_LOADING_01.BIN`
- 400+ `TRK_UNIT*_GR.BNDL` track chunks, `GLOBALBACKDROPS.BNDL` (92 MB), `WORLDTEX0-3.BIN` (137–180 MB each), `WORLDCOL.BIN` (14 MB), `GLOBALTEXTUREDICTIONARY.BIN`, `GLOBALMODELDICTIONARY.BIN`, `GLOBALPROPS.BIN` (23 MB)
- `CAMERAS`/`FLAPTHUD`/`PARTICLES`/`PLAYBACKREGISTRY`/`RWACFEATUREREGISTRY` `.BUNDLE`s, `HUDMESSAGES.HM`, `POPUPS.PUP`, `AI.DAT`, `DISTRICTS.DAT`, `TRIGGERS.DAT`, `PROGRESSION.DAT`
- Dirs: `LUA/`, `SOUND/`, `GUIAPT/`, `GUIIMAGES/`, `LANGUAGE/`, `ENGINES/`, `ENVIRONMENTSETTINGS/`, `POSTFX/`, `GPGPU/`, `PROPS/`, `Core/`, `DOWNLOADED/`

---

## 2. File Formats

| Format | Description |
|---|---|
| `.BNDL` | Track/world chunks (`TRK_UNIT*`, backdrops, traffic, progression) |
| `.BUNDLE` | Cameras, HUD, particles, feature registry |
| `.BIN` | Texture/model dictionaries, world textures/collision, loading screens |
| `.DAT` | AI, districts, progression, street data, triggers |
| `.HM` / `.HMSC` / `.PUP` | HUD messages / sequences / popups |

---

## 3. Key Technical Details

- **RenderWare engine** (Criterion/Stellar, per PCGW listing) alongside in-house Criterion systems: Lua gameplay scripting, EA WebKit UI, XAudio2 audio, Origin online. Note: the literal `RenderWare` string is absent from the 130 MB shipping exe — the RW runtime here leaves no name traces (renamed/statically-integrated fork); engine attribution follows the PCGW listing, not the strings audit.
- **Lua-driven gameplay** with EA WebKit UI — unusual licensed-light stack for a 2008 AAA racer, carried into the 2018 remaster unchanged
- **Origin-era DRM stack** (no SecuROM/SolidShield remnants in strings)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Burnout Paradise Remastered\`*  
*Engine: Criterion in-house post-RenderWare, Criterion Games 2008 / Stellar Entertainment 2018*