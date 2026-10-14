# Detonation Racing (iOS) — Teardown Documentation

**Game:** Detonation Racing  
**Platform:** iOS (iPhone/iPad)  
**Developer:** Electric Square Ltd  
**Publisher:** Electric Square Ltd (Apple Arcade)  
**Year:** 2021 (v1.2, build 178904; App Store item 1477484840)  
**Engine:** **Unity** (IL2CPP)

---

## 1. Game Engine

**Engine:** **Unity** (modern, IL2CPP scripting backend)  
- **Middleware:**
  - **Unity Engine** (verified: `UnityFramework.framework`, 93 MB)
  - **Game Center** (`gameCenterEnabled` in iTunesMetadata.plist)
- **Bundle ID:** `com.electricsquare.luna-testflight`
- **Executable:** `Detonation Racing` (70 KB thin launcher; code in UnityFramework)
- **Graphics:** Metal / OpenGL ES (Unity iOS player)
- **Scripting:** **C#** (IL2CPP — `ScriptingAssemblies.json` present)
- **Physics:** Unity PhysX (built-in)

**Evidence from dump:**
- `Payload/Detonation Racing.app/Frameworks/UnityFramework.framework/UnityFramework` (93 MB)
- `Data/` with `globalgamemanagers`, `level0–41` (42 levels), `sharedassets0–41`, `resources.assets` + `.resS` splits
- `Data/Managed/`, `Data/RuntimeInitializeOnLoads.json`, `Data/ScriptingAssemblies.json`
- iTunesMetadata: artist `Electric Square Ltd`, v1.2/178904, genre Racing, 9+, Game Center on

---

## 2. File Formats

| Format | Description |
|---|---|
| `.app` | iOS application bundle |
| `.assets` / `.resS` / `.resource` | Unity asset bundles (UnityFS) |
| `level0–41` | Unity scene data |
| `.car` | iOS compiled asset catalog (`Assets.car`) |

---

## 3. Asset Structure

```
Detonation Racing.app/
├── Detonation Racing             # Thin launcher (70 KB)
├── Info.plist / PkgInfo
├── Assets.car / AppIcon*.png
└── Frameworks/
│   └── UnityFramework.framework/
│       └── UnityFramework        # Engine + game code (93 MB)
└── Data/
    ├── globalgamemanagers(+.assets/.resS)
    ├── level0–level41
    ├── sharedassets0–41(+.resS)
    ├── resources.assets(+.resS, 244 MB)
    ├── Managed/
    └── Raw/
```

---

## 4. Documentation Notes

- **Apple Arcade title** (racing subgenre, Game Center multiplayer/leaderboards)
- **42 levels** — level-based stunt racing structure
- Modern Unity IL2CPP iOS player; no third-party engine middleware beyond Unity + Game Center

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Detonation Racing [Electric Square Ltd] (v1.2 v178904 Univ FW os135).rc502_146\`*  
*Engine: Unity (IL2CPP), Electric Square Ltd 2021*