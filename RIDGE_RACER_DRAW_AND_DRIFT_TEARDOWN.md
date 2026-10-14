# Ridge Racer Draw and Drift (Android) — Teardown Documentation

**Game:** Ridge Racer (Draw and Drift)  
**Platform:** Android  
**Developer:** Unknown  
**Publisher:** Bandai Namco Entertainment  
**Year:** ~2016 (v1.2.4, version_code 30, target SDK 24)  
**Engine:** **Unity 5.3.7f1** (Mono)

---

## 1. Game Engine

**Engine:** **Unity 5.3.7f1** (verified in `libunity.so`, both `armeabi-v7a` and `x86`)  
- **Middleware:**
  - **Unity Engine 5.3.7f1**
  - **Google Play Games** (`libgpg.so`)
  - **Google Play Billing + License Verification** (`BILLING`, `CHECK_LICENSE` permissions)
  - **SQLite** (`libsqlite3.so`)
- **Package:** `eu.bandainamcoent.ridgeracerdrawanddrift`, v1.2.4 (code 30)
- **Architectures:** ARMv7 + x86 (no ARM64 — 32-bit era build)
- **Graphics:** OpenGL ES (Unity 5.x built-in pipeline)
- **Scripting:** **C#** (Mono — `libmono.so`, pre-IL2CPP)
- **Physics:** Unity PhysX (built-in)
- **Expansion:** OBB `main.30.eu.bandainamcoent.ridgeracerdrawanddrift.obb` (~190 MB total)

**Evidence from dump:**
- `lib/armeabi-v7a|/x86/libunity.so` both contain version string `5.3.7f1`
- `libmono.so` → Mono backend (IL2CPP would use `libil2cpp.so`)
- `manifest.json`: package, version, permissions (BILLING, CHECK_LICENSE, VIBRATE, storage, network)
- `assets/bin/` (Unity data), `assets/vg_*.png` (viewer assets)

---

## 2. File Formats

| Format | Description |
|---|---|
| APK (+ split config) | Android package |
| OBB | Opaque Binary Blob expansion file |
| `.so` | Native libs (ARMv7/x86) |
| Unity `.assets` | Asset bundles inside OBB |

---

## 3. Documentation Notes

- **Free-to-play mobile Ridge Racer** — draw-racing-line gameplay + classic drifting
- **32-bit only** (ARMv7/x86, no arm64-v8a) — predates Google's 64-bit requirement
- **Unity 5.3 LTS era** (2016) with Mono scripting
- Distinct from the 3DS (Namco proprietary) and Vita (Cellius Proprietary) Ridge Racers

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Ridge Racer Draw and Drift\`*  
*Engine: Unity 5.3.7f1 (Mono), Unknown Developer (~2016)*