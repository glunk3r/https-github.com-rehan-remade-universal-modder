# TrackMania² Collection (ManiaPlanet) — Teardown Documentation

**Game:** TrackMania² collection on ManiaPlanet (Canyon + Stadium + Valley + Lagoon) + ShootMania Storm  
**Platform:** PC (Windows)  
**Developer:** Nadeo  
**Publisher:** Ubisoft  
**Year:** 2011–2017 (Canyon 2011, Storm/Stadium/Valley 2013, Lagoon 2017; `_HD` folders dated 2017-05-18)  
**Engine:** Nadeo ManiaPlanet engine

---

## Answer to "which TrackMania game is in here"

**Not one game — the full TrackMania² set.** The dump holds all four TM² environments plus ShootMania Storm on the shared ManiaPlanet platform. It is definitively **TrackMania²-family (ManiaPlanet, 2011+)**, NOT TrackMania United/Nations, NOT Trackmania Turbo (2016 console), NOT Trackmania (2020). If a single install is in question, the 2017-05-18 `_HD` refresh wave (Lagoon era) is the freshest activity — but the data cannot single out one played title.

---

## 1. Game Engine

**Engine:** Nadeo ManiaPlanet engine (verified: `NadeoPak` v0x12 containers with plaintext tables)  
- **Middleware:** None licensed beyond platform (ManiaScript for gameplay scripting)
- **Executable:** None in dump (data/user-data style layout — engine binary analysis impossible)
- **Container:** NadeoPak (magic `NadeoPak\x12`, plaintext file tables with `Title:` markers)
- **Assets:** GBX (`*.Solid.Gbx`, `*.Material.Gbx`, `*.Texture.Gbx` + stock `Default*.Texture.Gbx`)
- **Scripting:** ManiaScript (gameplay logic)
- **Build paths:** `\ser-data\DATA\TM Canyon\3D\...` (Nadeo internal Perforce layout)

**Evidence from dump (per-pak `Title:` markers):**
| Pack | Title marker | Content |
|---|---|---|
| `TMCanyon.pak` (186 MB) | `Title:TMCanyon` | Canyon blocks, materials, `\ser-data\DATA\TM Canyon\` paths |
| `TMStadium.pak` (101 MB) | `Title:TMStadium` | Stadium |
| `TMValley.pak` (211 MB) | `Title:TMValley` | Valley |
| `TMLagoon.pak` (145 MB) | `Title:TMLagoon` | Lagoon |
| `SMStorm.pak` (156 MB) | `Title:SMStorm` | ShootMania Storm |
| `ShootMania.pak` (2 MB) | `Title:ManiaPlanet` | Shared Storm-side resources |
| `TrackMania.pak` (175 MB) | `Title:ManiaPlanet` | Shared base-platform pack (**not** a game — the "TrackMania" here is the platform base, hence the confusion) |
| `ManiaPlanet.pak` (60 MB) | `Title:ManiaPlanet` | Platform core (menus, default textures) |
| `ManiaPlanet_ActionFx.pak` | `Title:ManiaPlanet` | Action FX |
| `Titles.pak` (38 MB) | `Title:Titles` | Title registry |
| `Resource.pak` | — | Shared resources |

- Per-title dirs with `_HD` + `_skins` + `_music` splits; `GpuCache_D3D11_SM4/SM5` (shader caches); `Translations/`; `ManiaPlanet_Skins/Painter/Flags/Live`

---

## 2. Key Technical Details

- The `TrackMania.pak` naming trap: it carries `Title:ManiaPlanet`, i.e. shared platform data — the actual games are the four `TM*.pak` titles
- GBX asset reuse across titles (stock `Default*` textures in the platform pack)
- ManiaScript + NadeoPak + GBX = the full Nadeo platform fingerprint, distinct from the Firebrand DS TrackManias and the 2020 Trackmania reboot

---

*Generated from `C:\Users\gmbad\Downloads\teardown\Research\ManiaPlanet\`*  
*Engine: Nadeo ManiaPlanet, Nadeo 2011–2017*