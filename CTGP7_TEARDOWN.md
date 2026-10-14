# CTGP-7 (3DS Homebrew Mod) — Teardown Documentation

**Game:** CTGP-7 (Custom Track Grand Prix 7) — Mario Kart 7 mod distribution  
**Platform:** Nintendo 3DS (homebrew)  
**Developer:** CTGP-7 Team (community: PabloMK7 et al.)  
**Base Game:** Mario Kart 7 (Nintendo EAD, 2011)  
**Year:** 2016–present (mod distribution)  
**Format:** CIA installer + layered RomFS (`gamefs/`)

---

## 1. Mod Architecture

**Type:** Layered-FS RomFS replacement + custom launcher  
- **Base engine:** Nintendo EAD Mario Kart 7 in-house engine (NitroSDK on PICA200)
- **Installer:** `cia/CTGP-7.cia` (homebrew launcher, needs CFW/LumaLayeredFs)
- **Mod content:** `gamefs/Course/` + `Missions/` + `Sound/` + `UI/` (replaces stock RomFS files at runtime)
- **Config:** `config/version.bin`, `expectedVer.bin`, `launchopt.bin` (launcher version check + options)
- **Save redirection:** `savefs/` (isolated mod save data)
- **Assets:** `resources/`, `MyStuff/`, `Photos/`

**Evidence from dump:**
- Directory layout matches Luma3DS LayeredFs mod pattern (`gamefs/` RomFS override, `savefs/` redirect)
- `config/*.bin` launcher handshake files
- No base-game CIA included (mod only — requires owned Mario Kart 7)

---

## 2. File Formats

| Format | Description |
|---|---|
| `.cia` | Homebrew launcher (installable) |
| `.bin` (config) | Version/option blobs |
| Course/Missions/Sound/UI | MK7 SARC/BCRES asset overrides (course models, mission defs, audio, UI layouts) |

---

## 3. Documentation Notes

- **Community custom-track distribution** — new cups, courses, missions, music over stock MK7
- **No engine modification** — content-layer mod; base engine untouched
- Requires modded 3DS (CFW); online play via custom servers after Nintendo WFC shutdown

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\CTGP-7\`*  
*Mod for: Mario Kart 7 (Nintendo EAD proprietary 3DS engine), community distribution*