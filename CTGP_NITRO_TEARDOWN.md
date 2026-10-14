# CTGP Nitro + Revolution (NDS ROM Hacks) — Teardown Documentation

**Games:** CT-GP Nitro (37.7 MB, 930 files) + CT-GP Nitro Revolution (22.9 MB, 626 files) — Mario Kart DS custom-track distributions  
**Platform:** Nintendo DS (flashcart/emu ROM hacks)  
**Developer:** CTGP Nitro Team (community; Revolution = later edition)  
**Base Game:** Mario Kart DS (Nintendo EAD, 2005 — ROM title `MARIOKARTDS`, code `AMCP`, maker `01`)  
**Format:** Patched NDS ROMs (EUR MKDS base)

---

## 1. Hack Architecture

**Type:** Full-ROM rebuilds on stock MKDS binaries  
- **Base ROM:** Mario Kart DS (EUR, AMCP) — ARM9 ~1.55 MB both builds
- **Custom content:** `.carc` archives (389 base / 278 Revolution — course archives), `.nsbmd` (96/90 — custom track models), `.nsbtx` (70/65), `.prm` (8 each — parameters?), `.nsbtp` (6 each), `.nsbca` (35/23), `.nsbma` (2 each)
- **NitroSDK 2D:** `.nclr` (95/41), `.ncgr` (92/33), `.nscr` (91/32)
- **Distribution:** DSi download-play stubs (`.srl` ×6), `.bak` (2, Revolution only), `.nbfc` (1, base only)

**Evidence from dump:**
- NDS headers retain stock `MARIOKARTDS`/AMCP/01 (patch-in-place distribution, like CTGP-7's LayeredFS pattern but baked)
- Revolution is the leaner rebuild (626 vs 930 files — fewer, newer tracks)

---

## 2. Documentation Notes

- DS-era answer to CTGP-7 (see `CTGP7_TEARDOWN.md`): new cups/tracks over stock MKDS, no engine modification
- `.carc`/`.prm` are the mod's custom course/parameter formats

---

*Generated from `CT-GP Nitro.nds` + `CT-GP Nitro Revolution.nds`*  
*Mod base: Mario Kart DS (Nintendo EAD proprietary NDS engine), community distributions*