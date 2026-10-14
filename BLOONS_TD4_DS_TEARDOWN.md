# Bloons TD 4 (NDS) — Teardown Documentation

**Game:** Bloons TD 4 (Europe)  
**Platform:** Nintendo DS  
**Developer:** Unknown (DS port; franchise: Ninja Kiwi)  
**Publisher:** Unknown (ROM maker code `YH`)  
**Year:** 2009–2010 (TD4 era)  
**Format:** NDS ROM (`Bloons TD 4 (Europe).nds`, 7 MB)

---

## 1. Game Engine

**Engine:** Custom DS engine (unconfirmed — no dev strings recovered)  
- **Middleware:** **NONE** — Nintendo NitroSDK only (evidenced)
- **ROM:** 7 MB, ARM9 1,982,016 bytes, ARM7 153,696 bytes, 226 files
- **2D formats:** `.ntfi`/`.ntfp`/`.ntft` (55 each — Nitro font/image/tile family), `.fnt` (11 fonts), `.alpha` (8)
- **Config:** `.xml` (37: `gamemodes/DefaultGameMode/hints.xml`, `paths/*.xml` — 20+ track path definitions: `ant_hill`, `cactus_creek`, `dna_test`...)
- **Manual:** `.blz` compressed pages (`manual/m2dres_narc.blz`, `manpages_narc.blz` + euro variant)
- **Audio:** `.sadl` + `.sdat` (Nitro sound bank + sequences)

**Evidence from dump:**
- NDS header: title `BLOONSTD4`, game code `KUVP`, maker `YH`
- XML-driven tower-defense data (modes, hints, track paths) — data-driven design, no scripting evidenced

---

## 2. Key Technical Details

- Tower paths as individual XML files per track — modder-friendly layout
- BLZ-compressed manual pages (GBA-era compression surviving on DS)

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Bloons TD 4 (Europe).nds`*  
*Engine: Custom DS engine (NitroSDK), Unknown Developer*