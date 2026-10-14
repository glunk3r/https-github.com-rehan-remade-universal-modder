# Track Racing Online (Android) — Teardown Documentation

**Game:** Track Racing Online  
**Platform:** Android  
**Developer:** Unknown (package: `com.tm.race`)  
**Publisher:** Unknown  
**Year:** Unknown (modern Android)  
**Format:** APK (Android Package) + split APKs

---

## 1. Game Engine

**Engine:** **Unity** (likely)  
- **Middleware:** 
  - **Unity Engine** (standard Android game engine)
  - **Google Play Services** (ads, analytics, multiplayer)
- **Format:** APK (Android Package) + split APKs (config.arm64_v8a.apk)
- **Architecture:** ARM64 (arm64-v8a)
- **Graphics:** OpenGL ES 3.x / Vulkan
- **Scripting:** C# (Unity) / IL2CPP (likely)
- **Physics:** Unity Physics (PhysX backend)

**Evidence from dump:**
- `com.tm.race.apk` - Main APK (53.6MB)
- `config.arm64_v8a.apk` - Split APK for ARM64 native libs (27MB)
- `manifest.json` - Bundle manifest

---

## 2. File Formats

| Format | Description |
|---|---|
| `.apk` | Android Package (ZIP-based) |
| `.so` | Shared library (native code, ARM64) |
| `.dex` | Dalvik bytecode (Java/Kotlin) |
| `.bin` / `.dat` | Unity asset bundles |
| `.resS` | Unity resource files |
| `.assets` | Unity asset bundles |

---

## 3. Asset Structure (Expected APK Contents)

```
com.tm.race.apk/
├── AndroidManifest.xml        # App manifest
├── classes.dex                # Java/Kotlin bytecode
├── lib/
│   └── arm64-v8a/
│       ├── libunity.so        # Unity runtime
│       ├── libil2cpp.so       # IL2CPP runtime
│       └── libmain.so         # Game code
├── assets/
│   ├── bin/Data/              # Unity data
│   │   ├── managed/           # C# assemblies
│   │   ├── resources.assets   # Unity assets
│   │   ├── sharedassets*.assets
│   │   └── level*.unity3d     # Scene data
│   └── StreamingAssets/       # Raw assets
└── res/                       # Android resources
```

**Split APK (config.arm64_v8a.apk):**
```
config.arm64_v8a.apk/
└── lib/arm64-v8a/
    ├── libunity.so
    ├── libil2cpp.so
    └── (other native libs)
```

---

## 4. Key Technical Details

- **Package name:** `com.tm.race` (TM = TrackMania? Or generic "Track Master"?)
- **Split APKs** - Android App Bundle format (dynamic delivery)
- **ARM64 only** - Modern 64-bit only (no ARM32)
- **Unity standard** - Typical Unity Android structure
- **Online multiplayer** - "Online" in title suggests networking

---

## 5. Documentation Notes

- **Unknown developer** - Package name doesn't match major studios
- **TrackMania-like?** - "TM" could reference TrackMania
- **Modern Android** - App Bundle format, ARM64 only
- **Unity IL2CPP** - Likely (standard for modern Unity Android)
- **Requires APK analysis** - Need to extract and inspect

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Track Racing Online\`*  
*Engine: Unity (Android), Unknown Developer*