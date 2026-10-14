# Animal Crossing: New Leaf — Welcome amiibo (3DS, SD-installed) — Teardown Documentation

**Game:** Animal Crossing: New Leaf – Welcome amiibo (00040000-00198f00 + 14MB update)  
**Platform:** Nintendo 3DS  
**Developer:** Nintendo EAD  
**Publisher:** Nintendo  
**Year:** 2016 (Welcome amiibo update; original New Leaf 2012)  
**Format:** SD-installed eShop title (per-console encrypted)

---

## 1. Game Engine

**Engine:** Nintendo EAD proprietary Animal Crossing engine  
- **Middleware:** NitroSDK (standard; binary unverifiable — SD crypto)
- **Install:** 935 MB app (largest on card) + 14 MB update (`0004000e-00198f00`), extdata `0000198f` (2 files)
- **Graphics:** PICA200 life-sim (top-down village, stereoscopic depth)
- **Audio:** CSND (K.K. Slider procedural-ish music system, hourly themes)

**Evidence from dump:**
- Title ID `00040000-00198f00` confirmed from console (user-checked)
- Update slot matches the Welcome amiibo v1.4/v1.5 patch line

---

## 2. Documentation Notes

- Welcome amiibo revision adds amiibo + RV campground content over the 2012 base
- No binary analysis possible (SD content encrypted without console keys)

---

*Generated from `.../nintendo 3ds/.../title/0004000?/00198f00` (console-verified name)*  
## CIA Dump Supplement

Loose CIA of the same title recovered in Research root:
- `0004000000198F00 Animal Crossing - New Leaf - Welcome Amiibo (CTR-P-EAAP) (v5.0.0) (W).piratelegit.cia` (980,691,264 bytes)
- Verified real CIA (Nintendo CA cert chain + ticket + valid TMD, title ID confirmed in TMD body)
- Content fully encrypted (zero NCCH/ExeFS/RomFS plaintext; single `IVFC` hit is random coincidence at 1/4B odds over 980 MB) — no deeper analysis possible without console keys

---

*Engine: Nintendo EAD proprietary 3DS engine, Nintendo EAD 2016*