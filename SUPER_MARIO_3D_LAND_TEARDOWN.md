# Super Mario 3D Land (3DS, SD-installed) — Teardown Documentation

**Game:** Super Mario 3D Land (00040000-00053f00)  
**Platform:** Nintendo 3DS  
**Developer:** Nintendo EAD Tokyo  
**Publisher:** Nintendo  
**Year:** 2011  
**Format:** SD-installed eShop title (per-console encrypted)

---

## 1. Game Engine

**Engine:** Nintendo EAD Tokyo proprietary 3D platform engine  
- **Middleware:** NitroSDK (standard; binary unverifiable — SD crypto)
- **Install:** 290 MB app, no update, no extdata on card
- **Graphics:** Stereoscopic 3D platforming (fixed-angle + free camera hybrid)
- **Audio:** CSND (orchestrated + synthesized mix)

**Evidence from dump:**
- Title ID `00040000-00053f00` confirmed from console (user-checked) — corrects my Tomodachi Life guess

---

## 2. Documentation Notes

- 3DS launch-window flagship 3D Mario; StreetPass mystery-box features
- No binary analysis possible (SD content encrypted without console keys)

---

*Generated from `.../nintendo 3ds/.../title/00040000/00053f00` (console-verified name)*  
## CIA Dump Supplement

Loose CIAs of the same title recovered in Research root (exact duplicates — `(1)` = re-downloaded copy):
- `0004000000053F00 Super Mario 3D Land (CTR-P-AREP) (v0.1.0) (E).legit.cia` (304,744,768 bytes) ×2
- Verified real CIA (Nintendo CA cert chain + ticket + valid TMD, title ID confirmed in TMD body)
- Content fully encrypted (zero NCCH/ExeFS/RomFS plaintext) — no deeper analysis possible without console keys

---

*Engine: Nintendo EAD Tokyo proprietary 3DS engine, 2011*