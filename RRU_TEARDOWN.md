# Ridge Racer Unbounded (PC) — Teardown Documentation

**Game:** Ridge Racer Unbounded (RRU)  
**Platform:** PC (Windows, Steam)  
**Developer:** Bugbear Entertainment  
**Publisher:** Namco Bandai Games  
**Year:** 2012  
**Engine:** ROMU Engine (Bugbear Entertainment)

---

## 1. Game Engine

**Engine:** ROMU Engine (Bugbear Entertainment) — verified: `bugbear.DataProvider` + `.\src\bflash\` paths in `RRU.exe`  
- **Middleware (all verified via binary strings in unpacked `RRU.exe`):**
  - **Scaleform GFx** — UI (2,090 `Scaleform::` hits, D3D9 HAL; 82 `.gfx` files)
  - **CRI ADX** — audio (`CRI ADX Decoder/PCx86 Ver.1.00.08 Build:Dec 20 2010`)
  - **Vorbis** — audio codec
  - **Quazal (RendezVous)** — online networking (360 hits: `Network.Quazal`, `Network.UGCManager`)
  - **Steamworks** (`steam_api.dll`, `Network.Steam` strings)
  - **XAudio2 + XMA** — audio output (`Invalid XAudio2 API call`, `Hardware XMA decoder error`)
  - **DirectX 9** (`D3DX*` strings, Scaleform D3D9 renderer)
- **Executable:** `RRU.exe` (12.8 MB, unpacked — 8 PE sections)
- **Container:** 3 extensionless data parts (`00__ridge_racer__` 0.5 MB, `01___unbounded___` 1.47 GB, `02____update_____` 2.75 MB) via Bugbear DataProvider
- **Scripting:** None found (C++ only)
- **Physics:** In-house (no Havok/PhysX/Bink/Miles strings; destruction-focused custom physics)

**Evidence from dump:**
- `bugbear.DataProvider` + `.\src\bflash\BGFxFileOpener.cpp` build paths
- 82 `.gfx` Scaleform movies (`Data\Menu\` — Main, Ingame, HUD_AS3, Overlay, PreRace/Result screens)
- `installscript.vdf` (Steam), `steam_api.dll` + `steam_api.ini`
- Full DirectX Redist (143 `.cab`) ships with the game

---

## 2. File Formats

| Format | Description |
|---|---|
| Extensionless parts | Bugbear DataProvider chunks (`00__`, `01___`, `02____`) |
| `.gfx` | Scaleform GFx UI movies (SWF-derived) |
| `.adx` | CRI ADX audio (inside data parts) |

---

## 3. Asset Structure

```
RRU/
├── RRU.exe                      # Unpacked, 8 sections
├── 00__ridge_racer__            # Data part (0.5 MB)
├── 01___unbounded___            # Data part (1.47 GB)
├── 02____update_____            # Update part (2.75 MB)
├── steam_api.dll / steam_api.ini
├── installscript.vdf
├── Data/
│   └── Menu/                    # 82 .gfx (Main, Ingame, HUD_AS3, Overlay, ...)
└── Redist/                      # DirectX (143 .cab) + vcredist_x86
```

---

## 4. Key Technical Details

- **Bugbear's destruction-racing tech** (FlatOut heritage) reskinned as Ridge Racer — city creator + domination modes
- **Scaleform D3D9 UI** across menus, HUD, overlays
- **Quazal online** (Ubisoft middleware inside a Namco-published title — via Bugbear's network layer)
- **No Bink/Havok/FMOD** — notably lean licensed stack for a 2012 AAA racer

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\RRU\`*  
*Engine: ROMU Engine, Bugbear Entertainment 2012 — https://www.pcgamingwiki.com/wiki/Engine:ROMU_Engine*