# Midnight Club: Street Racing (PS2) — Teardown Documentation

**Game:** Midnight Club: Street Racing  
**Platform:** PlayStation 2  
**Developer:** Angel Studios (Rockstar San Diego)  
**Publisher:** Rockstar Games  
**Year:** 2000  
**Format:** BIN/CUE (PS2 disc image)

> Correction: earlier revision of this doc labeled the game PS1. Verified — Midnight Club: Street Racing is a PlayStation 2 (and GBA) title. This file replaces `MIDNIGHT_CLUB_PS1_TEARDOWN.md`.

---

## 1. Game Engine

**Engine:** Angel Game Engine (AGE)  
- **Middleware:** None (custom PS2 engine)  
- **Format:** BIN/CUE (raw disc image)  
- **Graphics:** PS2 GS (Emotion Engine + Graphics Synthesizer)  
- **Audio:** PS2 SPU2 (VAG ADPCM)  
- **Scripting:** None found (C/C++, MIPS EE)  
- **Physics:** Custom vehicle physics

**Evidence:**
- Angel Studios (later Rockstar San Diego) in-house tech, precursor to RAGE
- PS2 launch-window title — no middleware common
- Open-world streaming on PS2 (technical achievement)

---

## 2. File Formats (PS2 Standard)

| Format | Description |
|---|---|
| `.bin` / `.cue` | Disc image (raw sectors) |
| `.pss` | PS2 video (PSS/MPEG2) |
| `.vag` | PS2 ADPCM audio |
| `.tm2` | PS2 texture format (TIM2) |
| `.mdl` / `.obj` | Custom model formats |
| `.map` | Level/map data |

---

## 3. Asset Structure (Expected PS2 Disc)

```
CD_ROOT/
├── SYSTEM.CNF         # Boot configuration
├── SLUS_XXX.XX        # Main executable (ELF)
├── DATA/              # Game data
│   ├── LEVELS/        # Track data
│   ├── CARS/          # Vehicle models
│   ├── TEXTURES/      # .tm2 textures
│   ├── AUDIO/         # .vag audio
│   └── VIDEO/         # .pss movies
└── FMV/               # Full motion video
```

---

## 4. Documentation Notes

- **Angel Studios** — later became Rockstar San Diego; engine lineage is Angel Game Engine (AGE)
- **Open-world racing** — first in genre on console
- **Streaming technology** — no loading screens (PS2 achievement)
- **GBA sibling** — a separate Game Boy Advance version exists
- **Disc image** — requires PS2 tooling/emulator to extract
- **Reference:** https://www.pcgamingwiki.com/wiki/Engine:Angel_Game_Engine

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Midnight Club - Street Racing (USA)\`*  
*Engine: Angel Game Engine (AGE), Angel Studios 2000*