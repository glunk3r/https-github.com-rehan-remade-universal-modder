# Camping Mama: Outdoor Adventures (NDS) — Teardown Documentation

**Game:** Camping Mama: Outdoor Adventures (USA)  
**Platform:** Nintendo DS  
**Developer:** Unknown (Cooking Mama franchise; ROM maker code `5G`)  
**Publisher:** Majesco Entertainment (franchise publisher; unconfirmed from binary)  
**Year:** 2011  
**Format:** NDS ROM (`Camping Mama - Outdoor Adventures (USA).nds`, 64 MB)

---

## 1. Game Engine

**Engine:** Cooking Mama custom DS engine (unconfirmed — no dev strings recovered)  
- **Middleware:** **NONE** — Nintendo NitroSDK only (evidenced)
- **ROM:** 64 MB, ARM9 753,184 bytes, ARM7 156,716 bytes, **6,461 files**
- **2D formats:** `.ncgr` (1,492) / `.nclr` (1,183) / `.nanr` (1,166) / `.ncer` (1,166) / `.nscr` (964) — full NitroSDK set
- **3D formats:** `.nsbmd` (257 models), `.nsbca` (44 animations), `.nsbtx` (27 textures)
- **Custom formats:** `.bghb` (60), `.amob` (51) — Mama-engine specific (backgrounds? animated objects?)
- **Messages:** `.msb` (15 — Nintendo Message Studio binaries)
- **Audio:** `.sdat` (5 banks)
- **Fonts:** `.nftr` (4)
- **Distribution:** download-play stubs (`.srl` ×2), in-ROM `readme.txt`

**Evidence from dump:**
- NDS header: title `CAMPING MAMA`, game code `TCME`, maker `5G`
- `area/area*.NCGR/NCER/NCLR/NANR` per-area 2D sets — area-streamed mini-game structure

---

## 2. Key Technical Details

- Densest NitroSDK-format usage in the DS set so far (6,461 files) with a Mama-specific `.bghb`/`.amob` layer on top
- Standard Nintendo message/font/sound pipeline (MSB/NFTR/SDAT) — first-party-tooling shop

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Camping Mama - Outdoor Adventures (USA).nds`*  
*Engine: Cooking Mama custom DS engine (NitroSDK), Unknown Developer 2011*