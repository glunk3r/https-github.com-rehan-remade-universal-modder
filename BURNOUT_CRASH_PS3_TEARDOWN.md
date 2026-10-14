# Burnout Crash (PS3 PSN Trial) — Teardown Documentation

**Game:** Burnout® CRASH! (Trial)  
**Platform:** PlayStation 3 (PSN)  
**Developer:** Criterion Games  
**Publisher:** Electronic Arts  
**Year:** 2011  
**Format:** PS3 PKG + EDAT license

---

## 1. Game Engine

**Engine:** Criterion Games proprietary engine (post-RenderWare in-house tech)  
- **Middleware:** Unknown (PKG content encrypted — not inspectable)
- **Package:** `BURNOUTCRASH.pkg` (1,108,519,712 bytes, `\x7FPKG` magic)
- **Content ID:** `UP0006-NPUB30464_00-CRASHTRIAL0000NA` — **trial version** (US, NPUB30464)
- **License:** `UP0006-NPUB30464_00-CRASHBUY000000NA.edat` (unlock key for full game)
- **Graphics:** PS3 RSX (LibGCM/GCM)
- **Audio:** PS3 ATRAC3/XMA-style (typical)

**Evidence from dump:**
- PKG magic + Content ID parsed from header; `CRASHTRIAL` marker confirms trial
- EDAT pairs the trial PKG (standard PSN trial→full unlock scheme)

---

## 2. File Formats (PS3 Standard)

| Format | Description |
|---|---|
| `.pkg` | PS3 package (encrypted) |
| `.edat` | Encrypted data / license |
| `.self` / `.elf` | Signed executables (inside, encrypted) |
| `.sdat` / `.psarc` | Game archives (typical, inside) |

---

## 3. Documentation Notes

- **PSN trial** — time/content-limited; EDAT unlocks the paid full game
- **Sibling of the XBLA dump** (STFS, Title ID `58410B5D`) — same 2011 Criterion top-down spin-off on both consoles
- No middleware claims possible without PKG decryption (PS3 keys + ps3tools)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\BURNOUT CRASH!\`*  
*Engine: Criterion Games proprietary, Criterion Games 2011*