# NASCAR Rumble (PS1) — Teardown Documentation

**Game:** NASCAR Rumble  
**Platform:** PlayStation 1 (PSX)  
**Developer:** Electronic Arts (EA Redwood Shores / Tiburon)  
**Publisher:** EA Sports  
**Year:** 1999  
**Format:** BIN/CUE (PS1 disc image)

---

## 1. Game Engine

**Engine:** EA proprietary engine (PS1)  
- **Middleware:** None (custom PS1 engine)  
- **Format:** BIN/CUE (raw disc image)  
- **Graphics:** PS1 GPU (GTE + rasterizer)  
- **Audio:** PS1 SPU (ADPCM/VAG)  
- **Scripting:** None found (C/MIPS assembly)  
- **Physics:** Custom arcade racing physics

**Evidence:**
- EA Sports NASCAR series on PS1
- Arcade-style (not sim) - "Rumble" branding
- PS1 era EA typically used custom engines

---

## 2. File Formats (PS1 Standard)

| Format | Description |
|---|---|
| `.bin` / `.cue` | Disc image (raw sectors) |
| `.str` | PS1 video (MDEC) |
| `.vag` | PS1 ADPCM audio |
| `.tim` | PS1 texture format (TIM) |
| `.mdl` / `.obj` | Custom model formats |
| `.map` | Track data |

---

## 3. Asset Structure (Expected PS1 Disc)

```
CD_ROOT/
├── SYSTEM.CNF         # Boot configuration
├── SLUS_XXX.XX        # Main executable (ELF)
├── DATA/              # Game data
│   ├── TRACKS/        # Track data
│   ├── CARS/          # Vehicle models
│   ├── TEXTURES/      # .tim textures
│   ├── AUDIO/         # .vag, .xm audio
│   └── VIDEO/         # .str movies
└── FMV/               # Full motion video
```

---

## 4. Documentation Notes

- **EA Sports NASCAR** - Arcade sub-series (Rumble, Thunder)
- **PS1 exclusive** - No PC version
- **Arcade physics** - Weapons, power-ups, destruction
- **Disc image** - Requires PS1 tools to extract
- **EA Redwood Shores/Tiburon** - EA's racing studio

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\NASCAR Rumble (USA, Canada)\`*  
*Engine: EA proprietary engine (PS1), EA Sports 1999*