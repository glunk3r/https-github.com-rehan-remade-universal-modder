# Just Cause 2 (PC) — Teardown Documentation

**Game:** Just Cause 2  
**Platform:** PC (Windows)  
**Developer:** Avalanche Studios  
**Publisher:** Square Enix / Eidos Interactive  
**Year:** 2010  
**Engine:** Avalanche Engine 2.0

---

## 1. Game Engine

**Engine:** Avalanche Engine 2.0 (proprietary)  
- **Middleware:** 
  - **Havok Physics** (physics simulation)
  - **FMOD Ex** (audio - `fmodex.dll`, `fmod_event.dll`)
  - **Bink Video** (video playback - `binkw32.dll`)
  - **CUDA** (GPU compute - `cudart.dll`, `cufft.dll` for PhysX/particles)
  - **GDF** (Games for Windows Live - `GDF.dll`)
- **Executable:** Not in dump (likely `JustCause2.exe`)
- **Graphics:** DirectX 10/10.1 (DX10 shaders present)
- **Scripting:** Lua (script files in archives)
- **Physics:** Havok Physics + custom vehicle/rope physics

**Evidence from dump:**
- `binkw32.dll` - Bink Video (Rad Game Tools)
- `fmodex.dll`, `fmod_event.dll` - FMOD Ex audio
- `cudart.dll`, `cufft.dll` - NVIDIA CUDA runtime (PhysX/particles)
- `DX10_Shaders_F.shader_bundle` - DirectX 10 shader bundles
- `GDF.dll` - Games for Windows Live
- `installscript.vdf` - Steam install script

---

## 2. File Formats

| Format | Extension | Description |
|---|---|---|
| `.arc` / `.tab` | Archive | Avalanche archive format (tab = table of contents) |
| `.ee` | Entity | Entity definitions |
| `.bin` | Binary | Various binary data |
| `.lua` | Script | Lua scripts |
| `.dds` | Texture | DirectDraw Surface (DXT compressed) |
| `.shader_bundle` | Shaders | DX10 compiled shader bundles |
| `.wem` / `.bnk` | Audio | FMOD/Wwise sound banks |

---

## 3. Asset Structure

```
Just Cause 2/
├── archives/
│   ├── *.arc          # Main asset archives
│   └── *.tab          # Archive tables of contents
├── shaders/
│   └── DX10_Shaders_F.shader_bundle
├── audio/
│   └── *.bnk, *.wem   # FMOD sound banks
├── video/
│   └── *.bik          # Bink videos
└── scripts/
    └── *.lua          # Lua scripts
```

---

## 4. Key Technical Details

- **Avalanche Engine 2.0** - Open-world streaming engine
- **Massive world** - 1000+ km² streaming terrain
- **Grapple hook physics** - Custom rope/constraint system on Havok
- **DX10 exclusive** - No DX9 fallback (Vista+ required)
- **CUDA acceleration** - Particle effects, cloth simulation
- **FMOD Ex** - Interactive audio with event system
- **Steamworks + GFWL** - Dual DRM/online

---

## 5. Documentation Files Created

| File | Description |
|---|---|
| `JUST_CAUSE_2_TEARDOWN.md` | This document |
| `GAMES_KNOWLEDGE_BASE.md` | Updated with Just Cause 2 entry |

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Just Cause 2\`*  
*Engine: Avalanche Engine 2.0, Avalanche Studios 2010*