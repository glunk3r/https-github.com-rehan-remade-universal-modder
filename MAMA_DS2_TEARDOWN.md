# Cooking Mama 3 + Crafting Mama (NDS) — Teardown Documentation

**Games:** Cooking Mama 3: Shop & Chop (USA, B3CE/5G) + Crafting Mama (USA, BQ8E/5G)  
**Platform:** Nintendo DS  
**Developer:** Unknown (Mama franchise; ROM maker code `5G` across all three Mama dumps)  
**Publisher:** Majesco Entertainment (franchise publisher; unconfirmed from binary)  
**Year:** 2009 (CM3) / 2010 (Crafting Mama, est.)  
**Format:** NDS ROMs (64 MB each)

---

## 1. Game Engines (two different pipelines!)

**Cooking Mama 3** (9,845 files, ARM9 376,712 bytes) — Nitro-flavored pipeline:  
- `.nclr` (2,928) / `.ncbr` (2,411 — Nitro character Bates?) / `.ncer` (1,773) / `.nanr` (1,264) / `.ncgr` (863) / `.nscr` (207) / `.nmar` + `.nmcr` (27 each) / `.bin` (334) / `.srl` (6) / `.nftr` (2) / `.nbfc` (1)

**Crafting Mama** (2,389 files, ARM9 372,128 bytes) — fully custom pipeline:  
- `.psrt` (1,311) / `.bin` (558) / `.pobj` (278) / `.pbg` (230) / `.srl` (6) / `.nftr` (2) / `.nbfc` + `.nbfp` (1 each) / `.sdat` (1) / `.nclr` (1!)

- **Middleware:** **NONE** — Nintendo NitroSDK only (both)
- **Audio:** SDAT (both)
- **Distribution:** DSi download-play stubs (`.srl`)

**Evidence from dump:**
- NDS headers: `COOKINGMAMA3`/B3CE, `CRAFTINGMAMA`/BQ8E, maker `5G` (same as Camping Mama TCME/5G)
- Crafting Mama's near-total format break (`.psrt`/`.pobj`/`.pbg`) vs Cooking Mama 3's Nitro set suggests **different developers** for the two titles despite one franchise/publisher

---

## 2. Key Technical Details

- Cooking Mama 3's `.ncbr` count (2,411) is the dominant format — character Bates resources, i.e. minigame-character-driven design
- Crafting Mama strips Nitro 2D almost entirely (single `.nclr`) for its own `.psrt`/`.pobj`/`.pbg` pipeline — worth a dedicated format-reverse-engineering pass

---

*Generated from `Cooking Mama 3 - Shop & Chop (USA).nds` + `Crafting Mama (USA).nds`*  
*Engines: Mama-family custom DS pipelines (NitroSDK), Unknown Developers*