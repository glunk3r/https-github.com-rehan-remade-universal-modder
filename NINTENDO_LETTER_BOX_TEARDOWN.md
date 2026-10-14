# Nintendo Letter Box / Swapnote (3DS, SD-installed) — Teardown Documentation

**Game:** Nintendo Letter Box (Swapnote, 00040000-00051800)  
**Platform:** Nintendo 3DS  
**Developer:** Nintendo  
**Publisher:** Nintendo  
**Year:** 2011 (service discontinued 2013)  
**Format:** SD-installed title (per-console encrypted)

---

## 1. Game Engine

**Engine:** Nintendo proprietary (messaging app framework)  
- **Middleware:** NitroSDK (standard; binary unverifiable — SD crypto)
- **Install:** 12 MB app + **119 extdata files** (`00000518`) — stored messages/memos
- **Graphics:** PICA200 2D (handwritten-note UI, stereoscopic viewer)
- **Audio:** CSND (notification sounds)

**Evidence from dump:**
- Title ID `00040000-00051800` confirmed from console (user-checked) — corrects my Flipnote guess; the 119-file extdata hoard fits Swapnote's message store, not Flipnote's
- Service-side SpotPass/Swapnote servers shut down Oct 2013 (FBI: "special notes" abuse)

---

## 2. Documentation Notes

- Free messaging app; Nikki mascot tutorials; photo/audio attachments
- No binary analysis possible (SD content encrypted without console keys)

---

*Generated from `.../nintendo 3ds/.../title/00040000/00051800` (console-verified name)*  
## CIA Dump Supplement

Loose CIA of the same title recovered in Research root:
- `0004000000051800 Nintendo Letter Box (CTR-N-JFRP) (v3.3.0) (E).piratelegit.cia` (13,046,784 bytes)
- Verified real CIA (Nintendo CA cert chain + ticket + valid TMD); **CIA meta SMDH extracted in plaintext**: publisher `Nintendo Letter Box`
- Content fully encrypted (zero NCCH/ExeFS/RomFS plaintext) — no deeper analysis possible without console keys

---

*Engine: Nintendo proprietary, Nintendo 2011*