# Burnout Crash (XBLA) — Teardown Documentation

**Game:** Burnout® CRASH!  
**Platform:** Xbox 360 (Xbox Live Arcade)  
**Developer:** Criterion Games  
**Publisher:** Electronic Arts  
**Year:** 2011  
**Format:** STFS package (Xbox 360 container)

---

## 1. Game Engine

**Engine:** Criterion Games proprietary engine (post-RenderWare in-house tech)  
- **Middleware:** Unknown (STFS content encrypted — not inspectable)
- **Format:** STFS (`LIVE` magic), Title ID `58410B5D`, 1,126,445,056 bytes
- **Display name (from header):** `Burnout® CRASH!`
- **Graphics:** Xbox 360 Xenos (DirectX 9-class)
- **Audio:** Xbox 360 XMA (typical)
- **Scripting:** Unknown

**Evidence from dump:**
- Path `58410B5D\000D0000\<hash>` = standard Xbox 360 content layout (title ID `58410B5D`)
- STFS magic `LIVE` verified at offset 0x0
- Single 1.07 GB package (within XBLA 2 GB limit)

---

## 2. File Formats (Xbox 360 Standard)

| Format | Description |
|---|---|
| STFS | Secure Transacted File System (LIVE/PIRS/CON) |
| `.xex` | Xbox executable (inside package, encrypted) |
| `.xma` | Xbox compressed audio (typical) |
| `.dds` | Textures (typical) |

---

## 3. Documentation Notes

- **Top-down spin-off** — pinball-style crash gameplay, unlike mainline Burnout
- **XBLA + PSN release** (this dump is the Xbox 360 XBLA package)
- **Container verified**, contents require Xbox 360 keys/extractors (Velocity, wxPirs)
- No middleware claims possible without decrypting the package

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Burnout Crash (World) (XBLA)\`*  
*Engine: Criterion Games proprietary, Criterion Games 2011*