# Mount & Blade II: Bannerlord

**Identify.** `Modules/Native/SubModule.xml`, module `ModuleData/` folders and `TaleWorlds.*.dll`
assemblies in `bin/Win64_Shipping_Client/`. Bannerlord has managed gameplay code and native engine
components. For single-player mods, start with the game's official module system.

## Routes

1. **Data:** put the mod in `Modules/<id>/` with its own `SubModule.xml` and `ModuleData/` XML.
   Register managed XML through the manifest's `Xmls` entries; engine-side XML uses
   `ModuleData/project.mbproj`. Use XML merging or XSLT for targeted changes, and check the installed
   version's schemas and merge rules. Keep base-game files intact. See TaleWorlds'
   [module guide](https://moddocs.bannerlord.com/asset-management/quickguide_create_a_mod/) and
   [XML merging guide](https://moddocs.bannerlord.com/bestpractices/merging_module_xml_files_with_native/).
2. **C# module:** build a DLL containing an `MBSubModuleBase` subclass, normally deployed under the
   mod's `bin/Win64_Shipping_Client/`. Its DLL name and fully qualified entry class must match
   `SubModule.xml`. Use lifecycle callbacks to register campaign behaviors, models or mission logic;
   inspect the current declarations before choosing a hook. For persistent campaign features, inspect
   `CampaignBehaviorBase.RegisterEvents` and `SyncData` plus the relevant save-system types.
3. **Managed patches:** when a suitable public hook is absent, use
   [Bannerlord.Harmony](https://github.com/BUTR/Bannerlord.Harmony) for managed methods. Check the
   current compatible release, declare its module dependency and verify the exact target overload.
   Harmony does not patch native `TaleWorlds.Native.dll` functions. Avoid bundling a conflicting copy
   of shared libraries.

## Knowledge first, then current source

- Run `um kb search "Bannerlord"`. The existing
  [v1.4.8 total-conversion field note](https://github.com/rehan-remade/universal-modder/blob/main/knowledge/games/mount-and-blade-ii-bannerlord/bannerlord-borderlands-2-total-conversion.md)
  links asset, combat, creature and crash-analysis notes. These are historical, version-specific
  observations, not compatibility guarantees for another build.
- Record the real local install, full game version, active modules and dependency versions in
  `MODLOG.md`. Compare the live `Version.xml`, `Modules/Native/SubModule.xml` and relevant DLLs with
  any MCP index metadata before trusting exact API signatures. A stable install can coexist with an
  older or Beta index; a tool's reported "installed version" may describe its saved import state.
- The DLLs and XML of the current local install are the implementation authority. Reference its
  assemblies when building; confirm method signatures, lifecycle and data IDs there. Keep ILSpy
  output outside the repository. Online API docs, generated scaffolds and old mod cases are leads
  until checked against those files.

## Optional BannerlordSage MCP

[BannerlordSage](https://github.com/hby7921/BannerlordSage) indexes an owner's local game files and
registered mod sources. It is an optional research helper; without it, read the field notes and
inspect local DLLs/XML directly. Follow its current README for setup with a real local game path.

1. **Check coverage:** `bannerlord_index_status` reports the active profile, indexed version, scopes
   and toolset. Compare these with the live files above. If versions differ, treat indexed source as
   historical and obtain source from the current installation before implementing exact APIs.
2. **Find a pattern:** `search_bannerlord_knowledge` with `intent: "make_mod"` routes a requirement
   across knowledge, docs, API and source. `search_mod_knowledge` and `find_mod_implementations` can
   narrow cases using `gameVersion`. Relevance alone does not prove the case implements the feature.
3. **Follow evidence:** `read_mod_knowledge` with `includeSourceMap: true` exposes the record's source
   map and reuse limits. Follow its registered `sourceId` with `read_mod_context`, `read_mod_type` or
   `read_mod_file`; then check the current official types with `read_csharp_type`, `search_source`
   and `read_file`, and data with `search_xml`. Recheck version alignment before using these results.
4. **Choose the toolset:** `start:bannerlord` defaults to `query-first`, including source/knowledge
   queries and `generate_harmony_patch`. `start:bannerlord:full` adds `create_mod_workspace`,
   `generate_xslt_patch` and experimental editor authoring. Generated code is a starting point;
   validate signatures, XML and paths. Full mode does not make an outdated index current.

## Verify and record limits

- Build against the target installation without deployment first. Validate the manifest, referenced
  DLLs, XML IDs and XSLT output. Use `bannerlord_doctor` against the real game directory when available
  to check module dependencies, missing DLLs, duplicate libraries and load-order declarations.
- Back up saves before a modded launch. Test one small feature in the real game with the intended
  module order and inspect logs. Campaign initialization or persistence changes need a new campaign
  and a save/load round trip; check existing-save compatibility separately if promised. Mission
  changes need the relevant battle or scene, not only a successful menu launch.
- Record compile, static, in-game and save/load results separately. Module health checks and indexed
  source inspection do not prove runtime behavior. Ship only authored code/assets; keep game files,
  extracted content, decompiled source, index databases and local credentials out of the release.
