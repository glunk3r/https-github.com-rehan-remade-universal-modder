# StreetPass Mii Plaza (3DS, SD-installed) — Teardown Documentation

**Game:** StreetPass Mii Plaza (00040000-00022800 + 94MB update + DLC)  
**Platform:** Nintendo 3DS (built-in title, updated via eShop)  
**Developer:** Nintendo  
**Publisher:** Nintendo  
**Year:** 2011 (updates/DLC through 2016+)  
**Format:** SD-installed title (per-console encrypted)

---

## 1. Game Engine

**Engine:** Nintendo proprietary (Mii Plaza framework)  
- **Middleware:** NitroSDK (standard; binary unverifiable — SD crypto)
- **Install:** update `0004000e-00022800` (94 MB) + DLC `0004008c-00022800` (StreetPass games: Find Mii, Puzzle Swap, Monster Manor, Battleground Z, etc.)
- **Extdata:** `00000228` heavily used (12 files — greetings, progress, DLC state)
- **Graphics:** PICA200 2D/3D UI
- **Audio:** CSND

**Evidence from dump:**
- Title ID `00040000-00022800` confirmed from console (user-checked) — corrects my earlier Badge Arcade guess (same update+DLC pattern, wrong title)
- DLC container holds the paid StreetPass mini-games

---

## 2. Documentation Notes

- System-bundled title; eShop updates added SpotPass features and new games
- No binary analysis possible (SD content encrypted without console keys)

---

*Generated from `.../nintendo 3ds/.../title/0004000?/00022800` (console-verified name)*  
*Engine: Nintendo proprietary, Nintendo 2011*

---

## CIA Dump Supplement (related titles only)

No StreetPass Mii Plaza CIA in this batch. Sibling Nintendo CIA dumps (same card family) confirm the scene format baseline: real CIAs (Nintendo CA certs + tickets + valid TMDs) with fully encrypted content — same wall applies here.