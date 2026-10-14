# Saints Row: Moneyshot (XBLA Prototype) — Teardown Documentation

**Game:** Saint's Row Moneyshot (prototype, unreleased)  
**Platform:** Xbox 360 (Xbox Live Arcade)  
**Developer:** Digital Extremes (likely — cancelled 2011 XBLA project; unconfirmed, STFS encrypted)  
**Publisher:** THQ (presumed, unconfirmed)  
**Year:** 2011 (prototype)  
**Format:** STFS package (Xbox 360 container)

---

## 1. Game Engine

**Engine:** Digital Extremes Evolution Engine (likely — DE's Dark Sector-era tech; unconfirmed, STFS encrypted)  
- **Middleware:** Unknown (STFS content encrypted — not inspectable)
- **Format:** STFS (`LIVE` magic), Title ID `58410B87`, display name `Saint's Row Moneyshot`, 608,759,808 bytes
- **Graphics:** Xbox 360 Xenos
- **Status:** Cancelled prototype (never released; leaked/dev dump)

**Evidence from dump:**
- Path `58410B87\000D0000\<hash>` = standard Xbox 360 content layout
- STFS magic + title ID + display name parsed from header

---

## 2. Documentation Notes

- **Cancelled Saints Row spin-off** — XBLA/PSN shooter set in the Saints Row universe, dropped during THQ's collapse
- Sibling container to the Burnout Crash XBLA dump (same `58410Bxx` title-ID family pattern, same STFS forensics)
- No middleware claims possible without Xbox 360 keys/extractors

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\Saints Row - Moneyshot (World) (Proto) (XBLA)\`*  
*Engine: Digital Extremes Evolution (likely, unconfirmed), 2011 prototype*