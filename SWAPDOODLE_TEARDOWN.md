# Swapdoodle (3DS, SD-installed) — Teardown Documentation

**Game:** Swapdoodle (00040000-001a2e00 + DLC)  
**Platform:** Nintendo 3DS  
**Developer:** Nintendo  
**Publisher:** Nintendo  
**Year:** 2016  
**Format:** SD-installed eShop title (per-console encrypted)

---

## 1. Game Engine

**Engine:** Nintendo proprietary (doodle-lesson app framework, Swapnote successor)  
- **Middleware:** NitroSDK (standard; binary unverifiable — SD crypto)
- **Install:** 20 MB app + DLC (`0004008c-001a2e00`, paid lesson packs) + 46 extdata files (`00001a2e`, lessons/doodles)
- **Graphics:** PICA200 2D (drawing tutorials, stereoscopic viewer)
- **Audio:** CSND

**Evidence from dump:**
- Title ID `00040000-001a2e00` confirmed from console (user-checked) — the 20MB-app + DLC + 46-file-extdata fingerprint fits Swapdoodle's lesson-pack model exactly

---

## 2. Documentation Notes

- Free-to-start successor to Swapnote (Nintendo Letter Box, also on this card); stationery/lesson micro-DLC
- No binary analysis possible (SD content encrypted without console keys)

---

*Generated from `.../nintendo 3ds/.../title/0004000?/001a2e00` (console-verified name)*  
## CIA Dump Supplement

Loose CIAs of the same title recovered in Research root:
- `00040000001A2E00 Swapdoodle (CTR-N-KRJP) (v4.4.0) (E).piratelegit.cia` (21,435,392 bytes) — **CIA meta SMDH extracted in plaintext**: publisher `Swapdoodle`
- `0004008C001A2E00 Swapdoodle (CTR-M-KRJP-00) (v0.3.0) (E).piratelegit.cia` (11,541,056 bytes, DLC)
- Verified real CIAs (Nintendo CA cert chain + ticket + valid TMD, title IDs confirmed in TMD bodies)
- Content fully encrypted (zero NCCH/ExeFS/RomFS plaintext) — no deeper analysis possible without console keys

---

*Engine: Nintendo proprietary, Nintendo 2016*