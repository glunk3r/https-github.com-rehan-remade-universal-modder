# Burnout Legends (PSP) — Teardown Documentation

**Game:** Burnout Legends (ULUS10025, v2.00)  
**Platform:** PlayStation Portable  
**Developer:** Criterion Games  
**Publisher:** Electronic Arts  
**Year:** 2005 (EBOOT dated Nov 2005, FW 2.00)  
**Format:** UMD ISO (505,905,152 bytes, 900 entries)

---

## 1. Game Engine

**Engine:** Criterion PSP proprietary (verified: decrypted `BOOT.BIN`, 5,090,701 bytes)  
- **Middleware (verified via binary evidence):**
  - **PMF Video** (`.pmf` ×129: localized `ovid/<lang>%d.pmf` movie paths — PSP H.264 video)
  - **ATRAC3 Audio** (`.at3` ×132 + `sceAtrac3plus`/`sceSasCore` SDK imports — PSP native audio)
- **Executable:** `PSP_GAME\SYSDIR\BOOT.BIN` (decrypted) + `EBOOT.BIN` (encrypted) + `UPDATE\` FW updater
- **Assets:** `.dat` (106), `.bgv`/`.hdt`/`.hwd`/`.ldt`/`.lwd` (90 each — track data variants), `.sdt`/`.swd` (47 — sound?), `.btv` (40), `.bgd` (34), `.bin` (30), `.mus` (21), `.m2v` (7), `.txd` (3), `.kfs`/`.icn` (2), `PARAM.SFO` ×2
- **Physics:** In-house (no Havok/PhysX strings)

**Falsified:** `Criterion` ×1 = router UPnP XML junk (`Criterion Games port mapping` — miniupnp description, not engine). `Miles` ×1 = `Distance Travelled Medals (Miles)` (gameplay units, not RAD Miles). `Kh`/`D3D` = opcode noise. No RenderWare/Bink/Havok/Lua strings in 5 MB of code.

**Evidence from dump:**
- `PARAM.SFO`: `DISC_ID ULUS10025`, `TITLE Burnout Legends`, `DISC_VERSION 2.00`, `PSP_SYSTEM_VER 2.00`
- 14 `.prx` PSP modules

---

## 2. Key Technical Details

- **No RenderWare strings** in decrypted code — same pattern as the Paradise Remastered finding; Criterion's PSP engine carries no RW name traces (engine cell: Criterion proprietary, matching the xlsx convention for Legends)
- PMF-per-language movie system (`ovid/dutch/englis/french/german/italia/sp...`)

---

*Generated from `Burnout Legends (PSP) (En,Fr,De,Es,It,Nl) (v2.00).iso` (`PSP_GAME\SYSDIR\BOOT.BIN`)*  
*Engine: Criterion PSP proprietary, Criterion Games 2005*