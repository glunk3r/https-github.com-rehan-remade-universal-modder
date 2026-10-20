---
kind: game
title: 'Dying Light 2: a new katana with its own blueprint, stash delivery, localised name and tuned damage'
game: 'Dying Light 2: Reloaded Edition'
games_also: []
game_version: 'Steam build 25208540 (ph_pc_tech_rel-ph-patch29, 2026-08-25)'
platform: windows
engine: unknown
route: data
tools: [python zipfile, um scan, um backup, um win]
anti_cheat: none found by um scan (online co-op exists; tested single-player only)
status: working
agents:
- Claude Code (Opus 5.5)
humans:
- Terlaime
date: '2026-10-18'
links: []
tags: [c-engine, techland, pak, scr, binsloc, localisation, weapon, blueprint, stash]
---
# Dying Light 2: a new katana with its own blueprint, stash delivery, localised name and tuned damage

> A new two-handed katana, "Black Lotus" (ru "Черный лотос"), for Dying Light 2. It has the stats of an existing
> legendary katana, the model of a store-DLC katana, a crafting blueprint that appears in the player's stash,
> its own Russian/English name and description, and its own damage table tuned so the inventory shows exactly
> 700. Everything is data: an extra `data2.pak` plus rebuilt language paks, with no loader and no code. It was
> verified in the real game by the human: blueprint in the stash, crafted, weapon mods fitted, name and 700
> damage shown.

## Setup
- Dying Light 2: Reloaded Edition, Steam app 534380, build id 25208540; `ph/source/data/build.metadata` says
  `ph_pc_tech_rel-ph-patch29_202608250709_6422187`. Windows 10, DX12.
- Nothing installed into the game except the mod files. Python 3 (`zipfile`) was enough to read and write the
  paks.
- `um scan "dying light 2"` reports "Unknown native engine" and suggests native hooks. Ignore that route: the
  game is Techland's C-Engine, and item, crafting and damage data are plain-text scripts inside zip paks.

## Route and why
- **Data route:** override and add `.scr` files through an extra pak, `ph/source/data2.pak`. The game mounts
  `data2.pak` and higher over `data0.pak`, and a file with the same path wins.
- **Considered and rejected:**
  - Native hooks: not needed for items.
  - A brand-new 3D model: `.msh` and `.rpack` need Techland's own tooling, so the mod reuses an existing
    mesh.
- **Known limitation:** two of the mod's files are whole game files with additions (the stash script, the
  damage definitions), and the language paks are rebuilt copies of the game's. That's fine on your own
  machine. To share the mod, ship a patcher that builds them from the user's install, not the files.

## How the game works (what we had to learn)
- **Paks:** `ph/source/data0.pak` (scripts, prefabs, presets) and `data1.pak` (maps) are ordinary zip files
  (deflate). Scripts are ASCII with CRLF line endings.
- **Items live in `scripts/inventory/`:**
  - `inventory_gen.scr` is generated from Techland's spreadsheet. It holds the concrete items: `Item("<id>",
    CategoryType_Melee) { use <base>(); ...overrides... }`.
  - `inventory_weapondefintions.scr` (sic) holds the base subs (`sub wpn_15hs_b()` and so on): mesh, skin
    tag, animation prefix, hit reactions, default damage table.
  - **`inventory_ugc.scr` is an empty hook "to add new unique Items definitions"** (its own comment says so),
    and the game DLL references it. Putting new items there means you don't have to override
    `inventory_gen.scr` (114k lines). It needs `import "inventory_weapondefintions.scr"` to `use` a base sub.
    It works in the main campaign, not only in community maps.
- **Two items with the same base:** "Toudi's Wrath" is `wpn_15hs_b_fpp_ll` (base `wpn_15hs_b`). The Black
  Hand katana is `wpn_15hs_q_fpp_Killing_Gentleman_Katana_<rarity>` (base `wpn_15hs_q`). The two bases are
  identical except for the mesh (`wpn_15hs_16_fpp/tpp.msh`) and the HUD icon. So "stats of A, look of B" is
  `use wpn_15hs_q();` plus A's item-level overrides: Condition, StaminaDamage, StaminaUsage, Color,
  TierSpread, Rank, repair costs and DismantleResult.
  - The DLC katana's mesh and icon live in the base game assets (`common_meshes_pc.rpack`,
    `gui/common_pc/common_textures__pc.atlas`). The new item has no `StoreID`, so it isn't gated by owning
    that DLC. Its name and look are used only on the player's own copy.
- **Blueprints** are `CategoryType_Collectable` items with `ItemType(ItemType_CraftPlan)`, `CraftplanType("Weapon")`,
  `RequiredItem("<material>", n)` lines and `CraftedItem("<weapon id>", 1, 1)`. They can live in
  `inventory_ugc.scr` too.
- **Stash** (`scripts/inventory/stash_dlc.scr`):
  - Every stock entry is gated by ownership. The game DLL knows these entry kinds: `DLC_Set`, `Store_Set`,
    `Collectable_Set`, `Docket_Set`, `Server_Set`, each with a `_With_Cooldown` variant.
  - `Collectable_Set_With_Cooldown("<collectable the player owns>", 1.0) { Item(1, "<id>");
    BlockedByItem("<id>"); ID(<unused id>); }` hands an item to anyone who owns that collectable.
  - Gating on the starting medkit blueprint `Craftplan_Medkit_Small` reaches every player.
  - There is no hook file for the stash, so this one needs the whole file overridden.
- **Damage:**
  - Weapons have `DamageTiers("<table>")`, and `TierSpread(t, t)` picks entry `<table>_<t>`. Each entry is
    `Damage("<table>_<t>") { Cut("<n>"); }` in `scripts/damagedefinitions.scr`.
  - Toudi's Wrath uses `slashing_tier_damages_28`.
  - The inventory number is that base value times rarity and weapon-mod multipliers. In our case it showed
    636 for a base of 328.
  - A private table (`blacklotus_tier_damages_0..28`) appended to `damagedefinitions.scr` changes only this
    weapon. An item already in the save picks up the new value, mods included.
- **Text:**
  - Names are `Name("&key&")`, resolved from `ph/source/data_lang/data<lang>.pak` →
    `texts/pc/pc_<lang>_lang.binsloc`.
  - binsloc layout:
    1. `u32 1`.
    2. A u16-length string `lockit::LockitBinaryResource` and a short type header.
    3. Two sections, `m_keys` and `m_Values`. Each section is `0x1e`, a u16 name length, the name, `u32 size`
       (counts from the count field to the section end), `u32 count`, then `count` strings, each a u16
       length plus UTF-8 bytes.
    4. A `0x2b` `m_IntKeys` section (empty) and a closing `0xff`.
  - Keys and values pair up by index, and keys aren't sorted. Appending a key and a value works: a
    parse-and-rewrite of the stock file is byte-identical, and the new keys showed in game.

## Build steps
1. Back up saves: `um backup create "<Steam>\userdata\<id>\534380\remote" --name dl2-saves`.
2. Read the scripts straight out of `data0.pak` with `zipfile`, into a folder outside any repo.
3. Write `scripts/inventory/inventory_ugc.scr`:
   - imports `inventorystuff.scr` and `inventory_weapondefintions.scr`;
   - the weapon item: `use wpn_15hs_q();`, Toudi's overrides, `DamageTiers("<your table>")`,
     `Name("&<YourKey>_N&")`, `Description("&<YourKey>_D&")`, a new random 19-digit `UID`, `GameVersion`
     equal to the newest `inventory_items_version_NNN`;
   - the blueprint item.
4. Generate at build time from the user's own `data0.pak`:
   - `stash_dlc.scr` with one `Collectable_Set_With_Cooldown` block added after the last stock set;
   - `damagedefinitions.scr` with your tier table added before the final `}`.
5. Zip all three into `ph/source/data2.pak` (keep the paths `scripts/...`).
6. Language: copy `data_lang/dataru.pak` and `dataen.pak` to `.orig`. Rebuild each pak entry by entry,
   keeping each entry's compression, with your keys appended to the binsloc. Install them over the originals.
7. Launch, open the stash in a safehouse, take the blueprint, craft. To tune damage, read the number the
   inventory shows (S) at base B and set the base to `round(B * target / S)`. Here that was
   328 × 700 / 636 = 361, which showed exactly 700.

## Verification
- **Oracle:** the human played and reported:
  - the stash shows the blueprint;
  - crafting gives the katana with the Black Hand model and icon;
  - weapon mods can be fitted;
  - the inventory shows the Russian name and description, and damage 700 after retuning.
- The agent checked offline:
  - the game loads with the mod, with no crash or script errors (screenshot through `um win shot`);
  - the binsloc parse/rewrite round trip is byte-identical;
  - the rebuilt language paks hold the same entry list as the originals.
- **Not verified:**
  - co-op or online with the mod (a "connection to matchmaking servers lost" popup appeared on the first
    modded launch; cause unknown, possibly unrelated);
  - English UI;
  - behaviour after a game patch;
  - whether `BlockedByItem` stops a second blueprint after the first is used.

## Gotchas
1. **`um scan` says "Unknown native engine" and suggests proxy-DLL hooks.** **Cause:** C-Engine has no
   signature in the scanner. **Fix:** look inside `ph/source/data0.pak`. It's a zip of text scripts; take
   the data route.
2. **Searching the language pak for a visible string finds nothing.** **Cause:** the text is in the binary
   `.binsloc`, as UTF-8 with u16 lengths. **Fix:** parse the `m_keys`/`m_Values` sections and map key →
   text. That's how `wpn_15hs_b_fpp_ll` = "Toudi's Wrath" and `Killing_Gentleman` = "The Black Hand" were
   found.
3. **The name shows as `?????`.** **Cause:** a literal Cyrillic string in `Name("...")`. `.scr` string
   literals aren't Unicode-aware. **Fix:** use a `&key&` and put the text in the binsloc.
4. **The name is blank after adding the key.** **Cause:** a patched `texts/pc/pc_ru_lang.binsloc` inside
   `data2.pak` is ignored. Texts load only from `data_lang/data<lang>.pak`. All other text stayed fine,
   which proved the file wasn't loaded at all. **Fix:** rebuild and replace `data_lang/dataru.pak` (and
   `dataen.pak`), keeping `.orig` backups.
5. **There's no free stash slot: every stock entry is DLC- or store-gated.** **Fix:** use
   `Collectable_Set_With_Cooldown` on a collectable everyone has (`Craftplan_Medkit_Small`), plus
   `BlockedByItem` on your blueprint.
6. **"Use model B" isn't a skin swap.** **Cause:** the store katana's look is its mesh, set in its base sub
   (`wpn_15hs_q`), not a `Skin(...)` line. **Fix:** `use` that base sub and copy the other weapon's item-level
   stats.
7. **Damage doesn't change after pointing the katana at its own table.** **Cause:** the new table started
   with the stock value. The shown number is base × hidden multipliers. **Fix:** measure once and scale (see
   Build steps). Changing the weapon mods later changes the multiplier, and so the shown number.
8. **Steam updates and "verify integrity" overwrite `data_lang/*.pak`.** **Fix:** rebuild from the fresh
   files, refresh the `.orig` copies, reinstall. Uninstall: delete `data2.pak`, restore the `.orig` paks.

## Assets
None generated. The mesh and icon are the game's own, referenced by name.

## Cost and time
One session, about three hours wall-clock, including four in-game test rounds by the human. No API spend.

## Open questions
- Can a separate language pak (another name in `data_lang/`) add keys without replacing the stock pak?
  Untested.
- Is there an official mod path (Techland's developer tools) that would make this shareable without
  overriding whole game files?
- Player-placed Nightrunner hideouts: researched and judged out of reach for a data mod. Hideout activities
  are text (`scripts/activities_info.scr`, `ow_small_safezone_*`, type `SafeZone`), but their placement
  lives in the binary map data (`maps/city/*.location_mgr.pc.bin`, generated `cb_generated_content` prefabs
  in `data1.pak`). Items can spawn prefabs (`SpawnPrefabName`, used by mines), and
  `prefabs/activities/uvspots/uv_location_minisafezone.prefab` holds a UV-light location logic, so a
  throwable "UV zone" might work. Untried.
