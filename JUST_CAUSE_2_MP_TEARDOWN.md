# Just Cause 2 - Multiplayer Mod (PC) — Teardown Documentation

**Game:** Just Cause 2 Multiplayer Mod (JC2-MP)  
**Platform:** PC (Windows)  
**Developer:** Nanos.io (community mod team)  
**Publisher:** Nanos.io / Steam  
**Year:** 2014 (mod release)  
**Base Game:** Just Cause 2 (Avalanche Engine 2.0)  
**Mod Engine:** Custom network layer + Lua scripting

---

## 1. Mod Architecture

**Type:** Client-side hook + server authoritative  
- **Hook Method:** DLL injection (`Jcmp.dll`, `JcmpLauncher.exe`)
- **Networking:** Custom UDP protocol (RakNet-like)
- **Scripting:** **Lua** (extensive Lua API exposed)
- **Crash Reporting:** CrashRpt (`CrashRpt1301.dll`, `CrashSender1301.exe`)
- **Steam Integration:** `steam_api.dll`

**Evidence from dump:**
- `Jcmp.dll` - Main mod hook DLL
- `JcmpLauncher.exe` - Launcher/injector
- `data/jc2mp.arc` - Mod asset archive
- `CrashRpt1301.dll` - Crash reporting
- `steam_api.dll` - Steamworks integration
- `thirdpartylegalnotices.txt` - Third-party licenses

---

## 2. File Formats

| Format | Extension | Description |
|---|---|---|
| `.arc` | Archive | Mod asset archive (custom format) |
| `.lua` | Script | Lua scripts (client/server/shared) |
| `.dll` | Native | Hook DLLs, crash reporter |
| `.exe` | Executable | Launcher, crash sender |

---

## 3. Asset Structure

```
Just Cause 2 - Multiplayer Mod/
├── Jcmp.dll                 # Main hook DLL
├── JcmpLauncher.exe         # Launcher/injector
├── steam_api.dll            # Steamworks
├── CrashRpt1301.dll         # Crash reporting
├── CrashSender1301.exe      # Crash sender
├── crashrpt_lang.ini        # Crash reporter locale
├── thirdpartylegalnotices.txt
└── data/
    └── jc2mp.arc            # Mod assets (scripts, UI, etc.)
```

---

## 4. Mod Technical Details

- **Lua API** - Exposes game functions for multiplayer sync
- **Client-side prediction** - Local player prediction with server reconciliation
- **Entity synchronization** - Vehicles, players, projectiles synced
- **Custom UI** - Lua-based UI system (CEF or custom)
- **Server browser** - Steam-based matchmaking
- **Anti-cheat** - Basic integrity checks

---

## 5. Documentation Notes

- **Community mod** - Not official Avalanche Studios product
- **Hooks into JC2 process** - Memory manipulation, function hooking
- **Lua scripting** - Primary modding interface
- **Requires base game** - Just Cause 2 on Steam
- **Open source** - Available on GitHub (nanos-world/jc2-mp)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Just Cause 2 - Multiplayer Mod\`*  
*Mod: JC2-MP, Nanos.io 2014 (hooks Avalanche Engine 2.0)*