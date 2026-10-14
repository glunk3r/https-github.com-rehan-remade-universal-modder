# DSi Mini-Apps + GBA Ports (Batch) — Teardown Documentation

**Games:** FSPDS (homebrew) · Zelda Four Swords AE · DSi Browser · 3DS Transfer Tool · Paper Plane · PictoChat · SMA 1–4 (GBA)  
**Platforms:** Nintendo DS/DSi + Game Boy Advance  

---

## 1. FSPDS — Flipnote Studio Player DS (Homebrew)

- **File:** `FSPDS-V1.0.79212842R.nds` (749,568 bytes; ROM title `HOMEBREW`, code `####`, zero-file FAT, ARM9 711 KB)
- **What:** Homebrew Flipnote player — plays Flipnote Studio flipnotes from FAT/SD on stock DS consoles without a DSi (per embedded strings: devkitPro build, "Flipnote Collective", per-region DSi codes, built-in flipnotes, config-file path caching)
- **Engine:** devkitPro homebrew (libnds)

## 2. Zelda Four Swords Anniversary Edition (DSiWare Port)

- **File:** `Legend of Zelda, The - Four Swords Anniversary Edition (Europe, Australia).nds` (14,848,000 bytes; `ZELDA 4SWORD`/KQ9V/01)
- **Developer:** Grezzo (likely — DSiWare port work; unconfirmed from binary)
- **Publisher:** Nintendo
- **Year:** 2011 (DSiWare anniversary release)
- **Engine:** Nintendo proprietary (NitroSDK)

## 3. Nintendo DSi Browser (Rev 3)

- **File:** `Nintendo DSi Browser (USA) (Rev 3).nds` (10,155,032 bytes; `WWW BROWSER`/HNGE/01)
- **Developer:** Opera Software (Opera-based DSi browser)
- **Publisher:** Nintendo
- **Engine:** Opera (Presto) + NitroSDK shell

## 4. Nintendo 3DS Transfer Tool

- **File:** `Nintendo 3DS Transfer Tool (USA).nds` (2,380,800 bytes; `CARDBOARD`/HNOE/01)
- **Developer/Publisher:** Nintendo (DSi→3DS system-migration tool)

## 5. Paper Airplane Chase (Paper Plane)

- **File:** `Paper Airplane Chase (USA).nds` (1,386,496 bytes; `PAPERPLANE`/KAME/01)
- **Developer/Publisher:** Nintendo (DSiWare micro-game)

## 6. PictoChat

- **File:** `pictochat.nds` (479,168 bytes; `PctChat`/HNEA/01)
- **Developer/Publisher:** Nintendo (DS firmware chat app, dumped as ROM)

## 7. Super Mario Advance 1–4 (GBA)

- **Files:** `Super Mario Advance (USA, Europe).gba` (AMAE) · `...2 - Super Mario World` (AA2E) · `...3 - Yoshi's Island` (A3AE) · `...4 - Super Mario Bros. 3` (AX4E) — 4,194,304 bytes each
- **Developer:** Nintendo R&D2 (ports)
- **Publisher:** Nintendo
- **Years:** 2001 / 2001 / 2002 / 2003
- **Engine:** Nintendo proprietary GBA (SNES-port lineage)

---

*Generated from Research batch (NDS headers + FSPDS strings + GBA headers)*  
*All first-party Nintendo (except FSPDS homebrew); engines Nintendo proprietary unless noted*