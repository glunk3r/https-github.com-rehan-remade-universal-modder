# Track Racing Pursuit (PC) — Teardown Documentation

**Game:** Track Racing Pursuit  
**Platform:** PC (Windows)  
**Developer:** Unknown (Unity game)  
**Publisher:** Unknown  
**Year:** Unknown (modern Unity)  
**Engine:** **Unity** (2020.x or 2021.x based on MonoBleedingEdge)

---

## 1. Game Engine

**Engine:** **Unity** (2020.3 LTS or 2021.x)  
- **Middleware:** 
  - **Unity Engine** (core)
  - **PhysX** (via Unity Physics - `UnityEngine.PhysicsModule.dll`)
  - **Amplify Motion** (motion blur - `AmplifyMotion.dll`)
  - **Photon** (multiplayer - `Photon3Unity3D.dll`, `websocket-sharp.dll`)
  - **Google Mobile Ads** (ads - `GoogleMobileAds*.dll`)
  - **Unity Services** (analytics, core - `Unity.Services*.dll`)
  - **TextMeshPro** (UI text - `Unity.TextMeshPro.dll`)
  - **Timeline** (cinematics - `UnityEngine.Timeline.dll`)
  - **AI Navigation** (navmesh - `Unity.AI.Navigation.dll`)
  - **Vehicle Physics** (Unity Vehicle Physics package - `UnityEngine.VehiclesModule.dll`)
  - **Newtonsoft.Json** (JSON - `Newtonsoft.Json.dll`)
  - **Ionic.Zip** (ZIP handling - `Ionic.Zip.dll`)
  - **NSpeex** (audio codec - `NSpeex.dll`)
- **Executable:** `TrackRacing Pursuit.exe` (not in dump, but Data folder present)
- **Graphics:** DirectX 11/12 (D3D12Core.dll present)
- **Scripting:** **C#** (Mono/IL2CPP - `MonoBleedingEdge` folder present)
- **Physics:** Unity PhysX + Vehicle Physics package

**Evidence from dump:**
- `UnityPlayer.dll` - Unity runtime
- `UnityCrashHandler64.exe` - Unity crash handler
- `MonoBleedingEdge/` - Mono runtime (IL2CPP backend)
- `TrackRacing Pursuit_Data/` - Unity Data folder
- `Managed/` - C# assemblies (100+ DLLs)
- `level0-3` - Scene data
- `resources.assets`, `sharedassets0-3.assets` - Asset bundles
- `D3D12/D3D12Core.dll` - DirectX 12 support
- `Plugins/x86_64/libonigwrap.dll` - Oniguruma regex wrapper

---

## 2. File Formats

| Format | Description |
|---|---|
| `.assets` | Unity asset bundle (serialized assets) |
| `.resS` | Unity resource file (split resources) |
| `.resource` | Unity resource index |
| `.dll` | C# assembly (Mono/IL2CPP) |
| `.so` / `.dll` (Plugins) | Native plugins |
| `.json` | JSON data (RuntimeInitializeOnLoads, ScriptingAssemblies) |
| `.bin` | Binary data (globalgamemanagers) |

---

## 3. Asset Structure

```
Track Racing Pursuit/
├── TrackRacing Pursuit.exe          # Main executable (missing)
├── UnityPlayer.dll                  # Unity runtime
├── UnityCrashHandler64.exe          # Crash handler
├── dstorage.dll / dstoragecore.dll  # DirectStorage (Windows 11)
├── D3D12/
│   └── D3D12Core.dll                # DirectX 12
├── MonoBleedingEdge/                # Mono runtime (IL2CPP)
│   ├── EmbedRuntime/
│   │   ├── mono-2.0-bdwgc.dll
│   │   └── MonoPosixHelper.dll
│   └── etc/mono/                    # Mono config
└── TrackRacing Pursuit_Data/
    ├── boot.config                  # Boot configuration
    ├── globalgamemanagers           # Global managers
    ├── globalgamemanagers.assets
    ├── level0-3                     # Scenes
    ├── resources.assets             # Main assets
    ├── resources.assets.resS
    ├── resources.resource
    ├── sharedassets0-3.assets       # Shared assets
    ├── sharedassets0-3.assets.resS
    ├── sharedassets0-3.resource
    ├── RuntimeInitializeOnLoads.json
    ├── ScriptingAssemblies.json
    ├── app.info                     # App info
    ├── Managed/                     # C# assemblies (100+)
    │   ├── Assembly-CSharp.dll      # Game code
    │   ├── Assembly-CSharp-firstpass.dll
    │   ├── AmplifyMotion.dll
    │   ├── Photon3Unity3D.dll
    │   ├── GoogleMobileAds*.dll
    │   ├── Unity.Services*.dll
    │   ├── Unity.TextMeshPro.dll
    │   ├── UnityEngine.VehiclesModule.dll
    │   ├── Newtonsoft.Json.dll
    │   ├── Ionic.Zip.dll
    │   ├── NSpeex.dll
    │   └── websocket-sharp.dll
    ├── Plugins/
    │   └── x86_64/
    │       └── libonigwrap.dll
    ├── Resources/
    │   ├── unity default resources
    │   └── unity_builtin_extra
    └── StreamingAssets/
        └── UnityServicesProjectConfiguration.json
```

---

## 4. Key Technical Details

- **Unity Vehicle Physics** - `UnityEngine.VehiclesModule.dll` indicates official Unity vehicle package
- **Photon Multiplayer** - `Photon3Unity3D.dll` + `websocket-sharp.dll` for real-time multiplayer
- **Google Mobile Ads** - AdMob integration (mobile-style monetization on PC?)
- **Unity Services** - Analytics, Remote Config, Cloud Save
- **DirectX 12** - `D3D12Core.dll` for modern rendering
- **DirectStorage** - `dstorage.dll` for fast asset loading (Windows 11)
- **IL2CPP** - `MonoBleedingEdge` folder indicates IL2CPP scripting backend
- **Amplify Motion** - High-quality motion blur effect

---

## 5. Documentation Notes

- **Modern Unity** - 2020.3 LTS or 2021.x
- **PC game with mobile SDKs** - Google Mobile Ads unusual on PC
- **Multiplayer focus** - Photon + WebSocket for online racing
- **Vehicle physics package** - Official Unity vehicle system
- **No executable in dump** - Only Data folder extracted

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Track Racing Pursuit\`*  
*Engine: Unity (2020.3/2021.x), Unknown Developer*