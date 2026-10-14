# Triad Wars (PC Closed Beta) — Teardown Documentation

**Game:** Triad Wars (Sleeping Dogs universe F2P, cancelled)  
**Platform:** PC (Windows 64-bit)  
**Developer:** United Front Games  
**Publisher:** Square Enix  
**Year:** 2015–2016 (client files dated Dec 2015–Jan 2016; beta shut down 2016, never released)  
**Format:** 7z archive (`TW.7z`, 6.86 GB, LZMA:26 BCJ2 solid)

---

## 1. Game Engine

**Engine:** United Front Games proprietary engine (Sleeping Dogs lineage — `.big`/`.bix` archive pairs)  
- **Middleware (confirmed from file listing):**
  - **Wwise** (Audiokinetic) — `.pck` sound banks ×2
  - **NVIDIA GameWorks** — `GFSDK_NVDOF_LIB.win64.dll` (Depth of Field) + `GFSDK_SSAO.win64.dll` (HBAO+ ambient occlusion)
  - **DirectX 11** (`d3dcompiler_46.dll`)
  - **libcurl + OpenSSL** (`libcurl.dll`, `libeay32.dll`, `ssleay32.dll`) — online services
- **Executables:** `TriadWars.exe` (64-bit) + `TextureScriberPC64.exe` (texture build tool)
- **Container:** 125 `.big` archives + 125 `.bix` indexes (Sleeping Dogs format family)
- **Shaders:** `shaders.perm.bin` + `Shaders.temp.bin` (47 MB, precompiled)
- **Physics:** Unconfirmed from listing (Havok probable — Sleeping Dogs used Havok; exe strings not scanned, archive unextracted)

**Evidence from dump:**
- 125 `.big`/`.bix` pairs (`Animation`, `Characters0–5` + `HD` variants, `Game`, `GameHD0–21`, `GameSD*`)
- `HK Options`, `DisplaySettings.xml`, `TW AutoSave` (beta client config)
- BCJ2 x86 filter confirms native 64-bit Windows executables

---

## 2. File Formats

| Format | Count | Description |
|---|---|---|
| `.big` / `.bix` | 125 / 125 | Game archives + indexes (United Front) |
| `.pck` | 2 | Wwise sound banks |
| `.dll` | 6 | GameWorks, DX compiler, curl/OpenSSL |
| `.exe` | 2 | Game + texture tool |
| `.rdb` / `.dat` / `.bin` / `.xml` | 1 / 3 / 2 / 1 | Database, data, shaders, settings |

---

## 3. Key Technical Details

- **Cancelled F2P experiment** — open-world Hong Kong action set in the Sleeping Dogs universe; closed beta 2015, shut down before launch
- **HD/SD archive split** (`GameHD*` vs `GameSD*`) — scalability tiers in the same client
- **GameWorks integration** dates it firmly to the 2014–2016 NVIDIA middleware wave
- Archive **not extracted** (6.8 GB solid LZMA) — strings-level middleware audit (Havok/Bink/Scaleform) pending extraction

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Triad Wars\TW.7z`*  
*Engine: United Front Games proprietary (Sleeping Dogs lineage), United Front Games 2015–16*