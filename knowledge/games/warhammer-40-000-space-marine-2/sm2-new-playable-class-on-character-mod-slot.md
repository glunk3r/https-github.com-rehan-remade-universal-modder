---
kind: game
title: "A new playable class in Space Marine 2 on Saber's CHARACTER_MOD slot (a Chaplain)"
game: "Warhammer 40,000: Space Marine 2"
games_also: []
game_version: "Steam build 25799387 (Patch 15.1, Oct 2026); class first built on Patch 14.x (Sep 2026) and rebased onto Patch 15"
platform: windows
engine: unknown
route: data
tools: ["Saber SM2 Mod Tools (ModEditor, ModelConverter, UsfExporter)", "Python 3 (zipfile, own SSL text parser for 3-way merges)"]
anti_cheat: "EasyAntiCheat. Everything here uses Saber's official mods folder (client_pc/root/mods), which flags the session 'Mods Detected' (private lobbies, separate progression). No injection, no EAC interaction, PvE only."
status: working
agents: ["Claude Code (Opus 5.5)"]
humans: []
date: 2026-10-14
links: []
tags: [space-marine-2, saber, new-class, character-mod, chaplain, mastery, perks, armoury, talker, constructor]
---

# A new playable class in Space Marine 2 on Saber's CHARACTER_MOD slot (a Chaplain)

> A seventh playable PvE class (a Chaplain: own armour set, robes with cloth physics, own perk tree, own war-cry
> ability, own default voice, own melee weapon) added to Space Marine 2 entirely through data, on one of the class
> slots Saber reserves for modders. It plays in missions and the armoury in game. This note is the class-level recipe;
> the model, weapon and voice details live in the other SM2 notes (foundations, models, weapons, voices).

## Setup
- Steam build 25799387 (Patch 15.1). Built on Patch 14.x, then rebased with a 3-way merge onto Patch 15 (see the
  foundations note). Saber's Mod Tools, Oct 2026 update.
- Everything is text overrides in a mod pak plus one rebuilt character constructor model.

## Route and why
Data route on a **pre-registered class slot**. Saber ships three playable class slots, `CHARACTER_MOD_1..3`, each
with PvE and PvP variants:
- `ssl/player/characters/characters_library.sso`: `CHARACTER_MOD_N = { isHidden = True, __type = "CharacterDesc" }`.
- `ssl/main/user/mastery/mastery_library.sso`: `PVE_CHARACTER_MOD_N` / `PVP_CHARACTER_MOD_N` with only
  `character = "CHARACTER_MOD_N"`.
- `ssl/characters/player/marine/outfits/for_modders/pc_{pve,pvp}_modded_characterN_{client,authority,server}.cls`:
  one-line stubs, e.g. `__type = "pc_marine_pve_client"`. Their `.ssc` / sslbin modules are already compiled and
  already listed in `initial/replicas/initial_replicas_all_{client,server}.resource` and the scene replica lists.
- `ssl/game_mode/rules/available_game_mode_characters_library.sso` already lists the slot, and
  `weapon_loadout_skills_library.sso` already has `PVE_CHARACTER_MOD_N -> "SoldierModN"` packs.
So no new compiled class, enum or replica entry is needed: you fill the slot with data. A brand-new class name
would need compiled code (a new brand crashes the boot), which is exactly what the slots avoid.

## How the game works (what we had to learn)

### The files a class needs, and what each one does
| File | What we changed |
|---|---|
| `player/characters/characters_library.sso` | `CHARACTER_MOD_2.isHidden = False` (makes it selectable) |
| `main/user/mastery/mastery_library.sso` | `PVE_CHARACTER_MOD_2` filled in: `masterSkill` (base perks) + `tiers` of `MasteryLevel` entries (money/xp cost + skill link per level) - grew from 3 lines to ~350, cloned from a retail class's block |
| `main/user/mastery/mastery_skills_library.sso` | the class's `MasterySkill` sets: the base set (e.g. spawn-with-ability perk, dodge preset, reload-holster, healing injector) and a `<Class>_Progression` table of `LevelN = { perks = [...] }` |
| `player/perks/perk_server_factory.sso` (**server pak**) | new `PerkDesc` entries, e.g. `SpawnWith<Ability>` = `PerkTriggerPassive` + `PerkApplicationSetAbility` pointing at the class ability uid. Perks live only in the server pak's `default_other.pak` |
| `main/user/mastery/ui_armory_ordered_mastery_library.sso` | append `"PVE_CHARACTER_MOD_2"` so the class shows in the armoury class list |
| `ui/fusion/hud/squad_panel/code/ui_character_library.sso` | new `UiCharacterIconData`: tac-team image, roster card, class icon (we reused `soldier`), `masteryName/Desc`, `masteryAbility` (the HUD's ability icon), `characterName`, `narrativeName` |
| `ui/fusion/assets/switchers/class_icons/ui_switcher_class_icons_base.sso` | `PVE_CHARACTER_MOD_2 = { __value = "soldier" }` (icon switch) |
| `sounds/voiceover/talker/talkers_library.sso` | `PVE_CHARACTER_MOD_2 = { def = "<talker>" }` (default talker for the mastery) |
| `main/user/weapon_loadouts/skills/weapon_loadout_skills_library.sso` | the slot's `SoldierMod2` pack: allowed firearms / melee / abilities; we added our own melee weapon (`melee_mod_1 = { __type = "WeaponSkillLocks" }`) |
| `body/customization/character_customization_library.sso` | a `PVE_PVP_CHARACTER_MOD_2` section (armour regions, presets, shared items); the class key also appears in shared items' class lists |
| `body/customization/armor_pattern_library.sso`, `global_armor_color_pattern_library.sso` | add the class to the per-class pattern/colour availability blocks |
| `loading_scene_logic/customizable_character_dummy_factory.sso` | the armoury/lobby figure for `PVE_CHARACTER_MOD_2` (and PvP) |
| `characters/.../pc_pve_modded_character2_client.cls` | full class: cloned from a retail class (~28k lines), `geom.nameTpl` = the constructor, `animSet`, cloth (`prop_cloth_sim_magnus`), jiggle (`prop_phys_jiggle`), `masteryType = "PVE_CHARACTER_MOD_2"` |
| `..._authority.cls` | full clone (~64k lines): same constructor and animSet, voice/sound blueprints, `talkerRef` |
| `..._server.cls` | short child of `pc_marine_pve_server`: `talkerRef` + `masteryType` |
| `texts/strings_english.str` (and every other `.str` the game reads) | the new UI keys |

### Body, animation and physics
- The class body is a **character constructor** tpl (all armour pieces in one model, shown/hidden by customization
  regions). We put the Chaplain pieces into the shared soldier constructor, so the class uses the soldier `animSet`
  and inherits all Tactical armour. See the models note for the constructor merge rules (joint accessor types, vertex
  colour pin channels, tangents, hidden regions for unowned objects, `tpl.resource` / `tpl_markup`).
- **Physics is per class FILE, not per model.** Cloth sims, CDT collision shapes, jiggle chains and motion dampers
  live in the class `.cls`. When a class shares a constructor with another class, merge the missing cloth/jiggle
  entries into its `.cls`, or pieces from the other class hang stiff or stretch.
- Never skin anything to a bone the class's animSet doesn't animate (bones grafted in from an NPC rig): at spawn they
  freeze, and every vertex weighted to them stretches into "sheets" in missions. The lobby looks perfect (rest pose),
  so test in a mission.

### Abilities, perks and weapons
- The class ability (a clone of a retail war cry) uses Saber's **AbilityUid enum extension** (`.ext` file on the
  enum's `.ssl.resource`). A cloned ability needs every uid-keyed file: ability library, UI ability library, ability
  view libraries, action controller cast types, command bindings, filter rules, the VO trigger, the server class's
  ability-ready chatter list, the granting perk and the HUD `masteryAbility`. Server logic keys on the controller's
  `factoryUid`, so damage/traps/perks of the original keep working.
- A class-only melee weapon: Saber's `melee_mod_1..5` ability slots + the class's weapon pack (see the weapons note).
- `SpawnWith*` perks are how a class gets its ability at spawn; weapon-type perks key on `MeleeStrikeWeaponType`.

### Voice
- The class's own voice must be the **BASE talker**: set `talkerRef.def` in BOTH `_authority.cls` and `_server.cls`
  (the server is authoritative and syncs it), plus the `talkers_library` entry. Then the social wheel, chatter and
  ability lines use it. Mission dialogue routes key on base talkers too, so extend each route's speaker switch for the
  new talker (an unknown talker silently drops the line). Details in the voices note.

## Build steps
1. Copy a retail class's `client` and `authority` `.cls` text into the slot's stub files (keep `__type` at the
   bottom), change `nameTpl`, `animSet`, `masteryType`; write the short server child with `talkerRef` + `masteryType`.
2. Unhide the slot in `characters_library.sso`; fill `PVE_CHARACTER_MOD_N` in `mastery_library.sso` from a retail
   class's block; add the class's skill sets to `mastery_skills_library.sso` and any new perks to the SERVER
   `perk_server_factory.sso`.
3. Add the UI entries (armoury order, squad panel icon data, class-icon switcher), the talker, strings in every `.str`
   file the game reads.
4. Build the customization section: start from a retail class section, then add your items; make every preset's key
   set match retail's for that patch (see Gotchas).
5. Add the armoury dummy entries for the slot (PvE and PvP), with `characterInfo.masteryType` = your slot.
6. Rebuild the constructor if the class has new armour; merge physics into the class files.
7. Pack (ZIP_STORED), test: class select -> armoury -> mission -> ability -> voice lines -> mission end.

## Verification
- In game (2026-10-03, user-confirmed): the class is selectable, the armoury and missions render it correctly, robes
  simulate in missions, perks and the ability work, the default voice drives the social wheel and chatter.
- Not verified: PvP use of the slot (we only filled the PvE side), and class behaviour in every operation's scripted
  dialogue beyond the routes we patched.

## Gotchas
1. **Armoury shows every slot as "none", nothing selectable, the whole constructor drawn at once.** Cause: Saber's
   dummy-factory entries for the slot are Tactical copies with `characterInfo.masteryType = "PVE_SOLDIER"`, so the
   lobby resolves the loadout in the Tactical library section. Changing `nameTpl` alone isn't enough. Fix: rebuild
   both dummy entries with `masteryType = PVE_CHARACTER_MOD_N`.
2. **Selecting the class, re-entering the arming chamber: UI frozen, camera still turns.** Cause: the customization
   section was cloned from Tactical including `isChampion` presets, which are only a `skinOverride` to Tactical's
   champion doll; the slot has no champion doll, so `TakeDoll` returns null (visible in the `.ssldmp` JSON). Fix:
   drop every `isChampion` preset from a cloned class section.
3. **Robes explode into huge sheets on the armoury figure only.** Cause: the NPC robe cloth configs don't behave on
   the preview dummy. Fix: remove the robe sims from the dummy entries (missions keep them), or use Saber's long-robe
   dummy settings.
4. **Stretched dark "sheets" in missions, lobby perfect.** Cause: pieces skinned to grafted bones the animSet never
   drives. Fix: move those weights to the nearest animated ancestor or a jiggle-driven bone.
5. **A whole armour slot greys out: "Armour part is not available for the selected Class".** Cause (misleading text):
   a preset with a blank equipped uid for a section (after Patch 15 split vanity into HALO/CLOTH/COAT, presets with
   the old keys left those blank) or an equipped challenge-locked item. Fix: give every preset retail's key set for the
   current patch; strip or satisfy challenge locks.
6. **Social wheel still uses the old voice after setting the talker.** Cause: only the authority class was changed;
   the server class is authoritative. Fix: set `talkerRef` in both.
7. **Boot crash after adding a "voice node" class for the default voice.** Cause: a new compiled blueprint node class
   (own sslbin) - new brands crash the boot. Fix: data only (`talkerRef`), no new classes.
8. **Ability cast hangs (charge kept, shooting blocked) after pointing the ability's animation task at an emote.**
   Cause: an ability anim task cannot start emotes (they only play through the smart/level-sequence path), and the
   controller left `OnFail` unwired. Fix: keep the retail anim; start emotes via a server `BlueprintNodeEnterSmart`
   with an inline `SmartServerDesc`; wire `OnFail` before experimenting.
9. **A stale standalone pak shadows the class.** An older test pak that ships its own copy of a class file and sorts
   first wins the whole file (first-alphabetical rule), e.g. an old voice pak reverting the class to another
   constructor. Fix: when the class misbehaves after an update, list every installed pak that ships any of the files in
   the table above.
10. **After a game patch the class half-works.** Patch 15 grew both constructors ~15 %, renamed presets
    (`PVP_*` -> `PVE_PVP_*`), added a class and new customization sections. Fix: re-export from the new retail,
    re-apply your edits with a tree 3-way merge, and audit presets against retail.

## Assets
The class armour, helmets and robes came from retail parts (the NPC Chaplain's body, other constructors' pieces) plus
custom helmets (AI-generated base meshes, repainted). The voice was generated text-to-speech, converted to the game's
Wwise format.

## Open questions
- Whether slots 1 and 3 have any hard-coded differences from slot 2 (we only used slot 2).
- Whether the PvP variant of a slot can be filled the same way without breaking matchmaking rules.
