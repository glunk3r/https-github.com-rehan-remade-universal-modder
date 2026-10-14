# Cave Story PSP (Homebrew Port, RC1) — Teardown Documentation

**Game:** Cave Story PSP (release candidate 1, homebrew)  
**Platform:** PlayStation Portable (homebrew, FW 1.0/1.5-kxploit/3.XX OE, GAME150 folder)  
**Developer:** "-Z." (PSP port, Jul 8, 2007); original: Studio Pixel (Daisuke Amaya)  
**Publisher:** None (homebrew)  
**Year:** 2007  
**Engine:** Studio Pixel custom engine (Organya audio engine)

---

## 1. Port Architecture

**Type:** Native homebrew port (not emulation)  
- **Loader:** `cavestory/EBOOT.PBP` (818,511 bytes — kxploit-era PBP)
- **Data:** `cavestory/data.csz` (1,532,782 bytes — compressed game data)
- **Saves:** Compatible with Windows version (`Profile.dat`, `290.rec`, case-sensitive)
- **Docs:** `readme.txt` (install notes + known script bugs from widescreen framing)

**Evidence from dump (`readme.txt`, verbatim facts):**
- Targets FW 1.0 (no mod), 1.5 (kxploit), 3.XX OE custom firmware
- Widescreen exposes offscreen sprites/text overflow (documented per-area bug list: Balrog fight, Egg Corridor, Labyrinth, Hell, credits...)
- Signed "-Z. 7/8/07"

---

## 2. Key Technical Details

- Early PSP homebrew history artifact (pre-PSN Cave Story era, 4 years before the Nicalis ports)
- Data-compatible with the Windows original — engine logic ported 1:1, bugs preserved

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\cavestory-psp-rc1.zip`*  
*Engine: Studio Pixel custom (homebrew PSP port by "-Z.", 2007)*