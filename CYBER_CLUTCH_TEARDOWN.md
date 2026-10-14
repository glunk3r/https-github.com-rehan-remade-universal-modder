# Cyber Clutch: Hot Import Nights (PC) — Teardown Documentation

**Game:** Cyber Clutch: Hot Import Nights  
**Platform:** PC (Windows 64-bit, Steam AppID 1939920)  
**Developer:** Unknown  
**Publisher:** Unknown  
**Year:** 2025 (build date Aug 13, 2025, #2224)  
**Engine:** **Unreal Engine 4.27** (verified)

---

## 1. Game Engine

**Engine:** **Unreal Engine 4.27** (verified: `4.27` ×283 in shipping exe, zero hits for any other 4.2x)  
- **Middleware (all verified via binary/DLL evidence):**
  - **PhysX 3** (`PhysX3_x64.dll` + cooking/foundation/PVD; `PhysX` ×113 in exe)
  - **APEX + NvCloth** (`APEX_Clothing/Legacy`, `NvCloth_x64.dll`)
  - **Chaos Cloth** (`ChaosClothWeightedValue` strings — 4.26+ cloth alongside PhysX)
  - **Oodle** (×42 — IoStore compression)
  - **Epic Online Services** (`EOSSDK-Win64-Shipping.dll`, 18 MB)
  - **Steamworks v151** (`steam_api64.dll`, AppID 1939920, depots 228989/228990/1939921/1939922)
  - **CEF3** (Chromium Embedded — `libcef.dll`, locale paks; `UnrealCEFSubProcess.exe`)
  - **XAudio2 + Ogg/Vorbis** (`xaudio2_9redist.dll`, `libvorbis`, `libogg`)
  - **NVIDIA Aftermath + GeForceNOW SDK** (crash dumps + cloud gaming)
  - **OpenImageDenoise + TBB** (Intel denoiser for ray tracing)
  - **AWS CloudWatch plugin** (telemetry), **d3dcompiler 43/47**
- **Executables:** `HotImportNights.exe` (227 KB bootstrap, zero middleware strings) + `HotImportNights-Win64-Shipping.exe` (87 MB, unpacked)
- **Container:** IoStore (`.ucas` 5.9 GB + `.utoc`) + legacy `.pak` (105 MB) — UE 4.26+ packaging
- **Scripting:** None (C++/Blueprints)
- **Physics:** PhysX 3 (vehicles) + Chaos Cloth (no Havok/FMOD/Wwise/Bink/EAC/Denuvo strings)
- **DRM:** None found (no Denuvo/EAC; Steamworks only + emulator configs present in dump)

**Evidence from dump:**
- `Engine/Binaries/ThirdParty/` full middleware DLL set (VS2015 toolchain = UE4 era)
- `Build.json`: master build, `HotImportNights_Package_Any`, BuildPC2, #2224
- `steam_settings/` emulator configs (Goldberg-style crack artifacts, not game tech)
- `HotImportNights/Content/Paks/` + `Movies/`, `Engine/Content/`

---

## 2. File Formats

| Format | Description |
|---|---|
| `.ucas` / `.utoc` | IoStore containers (UE 4.26+) |
| `.pak` | Legacy Unreal package |
| `.dll` (ThirdParty) | Middleware (PhysX/APEX/CEF/EOS/Steam) |
| `.json` / `.ini` / `.txt` | Build manifests, Steam configs |

---

## 3. Key Technical Details

- **UE 4.27 pinned** by string frequency (283 vs 0) — late-4.x stack: IoStore + Oodle + Chaos Cloth + PhysX coexistence
- **Arcade street-racing** (Hot Import Nights branding) on AAA-pattern UE4 tech: EOS + Steamworks dual online, GameWorks diagnostics, cloud-gaming SDK
- Developer/publisher unconfirmed (no strings, store page unfetchable at teardown time)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Cyber Clutch Hot Import Nights\CyberClutchHotImportNights10\`*  
*Engine: Unreal Engine 4.27 — Steam AppID 1939920 (https://store.steampowered.com/app/1939920/)*