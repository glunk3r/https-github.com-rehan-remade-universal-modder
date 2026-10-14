# Battle Riders (PC) — Teardown Documentation

**Game:** Battle Riders  
**Platform:** PC (Windows, Steam)  
**Developer:** Unknown  
**Publisher:** Unknown (Steam release)  
**Year:** Unknown (Unity 4.7 era, ~2015–2016)  
**Engine:** **Unity 4.7.0f1**

---

## 1. Game Engine

**Engine:** **Unity 4.7.0f1** (Mono scripting backend, pre-IL2CPP)  
- **Middleware:**
  - **Unity Engine 4.7.0f1** (verified: `mainData` version string `4.7.0f1`)
  - **Steamworks** (`steam_api.dll`, `Plugins/CSteamworks.dll`)
  - SmartSteamEmu files present in dump (**crack/emulator, not game tech**)
- **Executables:** `BattleRiders.exe`, `LAUNCHER.exe`, `LAUNCHER_x64.exe`
- **Graphics:** DirectX 9/11 (Unity 4.x built-in pipeline)
- **Scripting:** **C# + UnityScript + Boo** (`Assembly-CSharp-firstpass.dll`, `Assembly-UnityScript.dll`, `Assembly-UnityScript-firstpass.dll`, `Boo.Lang.dll`, `UnityScript.Lang.dll`)
- **Physics:** Unity PhysX (built-in)
- **UI:** uGUI (`UnityEngine.UI.dll` — Unity 4.6+ UI system)

**Evidence from dump:**
- `BattleRiders_Data/mainData` header contains Unity version string `4.7.0f1`
- `Managed/` has UnityScript + Boo assemblies (only possible on Unity 4.x — Boo removed in 5.0)
- `Mono/` runtime folder (not `MonoBleedingEdge`) → Mono backend, not IL2CPP
- 26 levels (`level0`–`level25`), `sharedassets0–26.assets`, `resources.assets`
- `PlayerConnectionConfigFile`, `ScreenSelector.bmp` (Unity player defaults)

---

## 2. File Formats

| Format | Description |
|---|---|
| `.assets` | Unity asset bundles (serialized, pre-UnityFS format) |
| `.dll` (Managed) | C#/UnityScript/Boo assemblies (Mono) |
| `level0–25` | Unity scene data |
| `mainData` | Global managers + version header |

---

## 3. Asset Structure

```
Battle.Riders/
├── BattleRiders.exe             # Unity player
├── LAUNCHER.exe / LAUNCHER_x64.exe
├── steam_api.dll / SmartSteamEmu*.dll  # Steamworks + emu (crack)
├── RemoveMessagebox.dll
└── BattleRiders_Data/
    ├── mainData                 # Version 4.7.0f1
    ├── level0–level25
    ├── sharedassets0–26.assets
    ├── resources.assets
    ├── Managed/                 # C#, UnityScript, Boo, uGUI
    ├── Mono/                    # Mono runtime
    ├── Plugins/                 # CSteamworks, steam_api
    └── Resources/
```

---

## 4. Documentation Notes

- **Unity 4.x confirmed** by version string + Boo/UnityScript assemblies
- **SmartSteamEmu** files are third-party crack artifacts, not game middleware
- 26 levels suggests level-based vehicular combat structure

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Battle.Riders\`*  
*Engine: Unity 4.7.0f1 (Mono), Unknown Developer*