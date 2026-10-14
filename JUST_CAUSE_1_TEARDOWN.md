# Just Cause (PC) — Teardown Documentation

**Game:** Just Cause  
**Platform:** PC (Windows)  
**Developer:** Avalanche Studios  
**Publisher:** Square Enix / Eidos Interactive  
**Year:** 2006  
**Engine:** Avalanche Engine 1.0

---

## 1. Game Engine

**Engine:** Avalanche Engine 1.0 (predecessor of JC2's Avalanche Engine 2.0)  
- **Middleware:**
  - **Bink Video** — confirmed (`binkw32.dll` + 46 `.bik` files in `PC\FMV\`)
  - **DirectX 9** (`d3dx9_26.dll`, Feb 2006 SDK)
- **Executable:** `JustCause.exe` (1.8 MB, **packed** — 2 PE sections, `.text` virtual size 10 MB vs 1.8 MB raw; no plaintext middleware strings)
- **Container:** `.arc` / `.tab` (same archive family as Just Cause 2: `pc0.arc`–`pc4.arc`, ~4.4 GB total + `pc.tab`)
- **Audio:** Avalanche in-house SFX banks — `.sab` (`CSW2` magic) + `.sob` (`CTF2` magic), 252 + 219 files with LOD1–LOD3 variants
- **Scripting:** Unknown (packed exe; no Lua evidence as in JC2)
- **Physics:** In-house (no Havok/PhysX strings recoverable — exe packed, inconclusive)

**Evidence from dump:**
- `Archives/pc.tab` + `pc0.arc`–`pc4.arc` (same `.arc`/`.tab` format as JC2)
- `PC\Sfx\` banks: `CSW2` (audio data) / `CTF2` (object defs), LOD-tiered (`_LOD1/2/3`)
- `PC\FMV\` (46 `.bik`), `binkw32.dll`
- `testapp.exe`, `JCSetup.exe`, `regsetup.exe`, `dm-Jc.nfo`

---

## 2. File Formats

| Format | Description |
|---|---|
| `.arc` / `.tab` | Avalanche archives + table of contents |
| `.sab` (`CSW2`) | Avalanche SFX audio bank |
| `.sob` (`CTF2`) | Avalanche SFX object definitions |
| `.bik` | Bink Video (FMV) |

---

## 3. Asset Structure

```
Just Cause/
├── JustCause.exe                # Packed main executable
├── binkw32.dll / d3dx9_26.dll
├── Archives/
│   ├── pc.tab                   # Archive TOC (84 KB)
│   └── pc0.arc–pc4.arc          # Game data (~4.4 GB)
├── PC/
│   ├── FMV/                     # 46 .bik movies
│   └── Sfx/                     # .sab/.sob banks (Character, Contact,
│                                #  Dialogue+English, Environment, Explosion,
│                                #  Fire, GUI, Mission, Music (664 MB), Vehicle, Weapon)
├── testapp.exe / JCSetup.exe / regsetup.exe
└── settings.txt / pc_file_order.log
```

---

## 4. Key Technical Details

- **Avalanche Engine 1.0** — first iteration; `.arc`/`.tab` pipeline carried into JC2
- **LOD-tiered audio** — every SFX bank ships LOD1–LOD3 (distance-based mixing)
- **664 MB music bank** (`MUSIC.sab`) — streamed open-world soundtrack
- **Packed exe** — strings analysis inconclusive; middleware beyond Bink/DX9 unconfirmed

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Just Cause\`*  
*Engine: Avalanche Engine 1.0, Avalanche Studios 2006*