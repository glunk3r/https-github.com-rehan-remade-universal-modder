# Safety, legality, etiquette

These rules keep the user's accounts, saves and machine safe, and keep their mod shareable. None of this is
legal advice. When a game's EULA or mod policy matters, read it (search "<publisher> mod policy").

## Online games and anti-cheat: the bright line
- **Only single-player/offline, or servers the user runs.** Injecting into an online client breaks its terms
  and gets accounts banned. Doing it to gain an advantage over other players is cheating. Refuse aimbots,
  ESP/wallhacks, speed/teleport hacks, recoil scripts and packet manipulation for multiplayer games,
  whatever the framing.
- **Kernel or user-mode anti-cheat is a stop sign for code injection.** That covers EasyAntiCheat, BattlEye,
  Vanguard, EA Javelin, Ricochet, ACE, nProtect, XIGNCODE and mhyprot. Allowed:
  - official modding surfaces (Workshop, creative/map editors, official mod kits);
  - an official offline mode that ships without the anti-cheat. Elden Ring launched offline through
    `ModEngine2`/`me3` with EAC disabled is the community norm, with seamless co-op as its own separate
    thing.
- **Never:**
  - disable or bypass anti-cheat;
  - spoof hardware IDs;
  - tamper with DRM (Denuvo, Steam stub) or ownership checks.

  If a loader needs the game's EXE patched past DRM, stop.
- VAC (Valve) bans for modified clients on VAC-secured servers. Run local tests with `-insecure` and never
  join public servers while anything is injected.
- Tools running next to a protected game (debuggers, Cheat Engine, overlays that inject) can trip its
  anti-cheat even when you don't touch it. Close protected games before RE sessions.

## Multiplayer games you are remaking
Rebuilding a game as original work needs its rules, not its live client, so the bright line above still
holds and this adds what IS allowed (workflow in `skills/multiplayer-remake`):
- **Static analysis of the files on disk**, for any multiplayer title the user owns, anti-cheat or not:
  decompile client and dedicated-server binaries, read data tables, configs, network message schemas.
  Ghidra/ILSpy on a file is not running the game, so the anti-cheat is never engaged.
- **Dynamic analysis only where nothing official is involved:** official offline/LAN modes, a dedicated
  server the user hosts on their own machine, private sessions between the user's own clients, and the
  remake itself. Capture traffic only from those.
- **Never:** reverse-engineer the anti-cheat module itself, connect an instrumented or modified client to
  official servers, probe, scrape or load-test official servers or APIs, or reuse account credentials.
- The remake gets its own netcode and servers. Do not re-implement a private protocol to talk to the
  original game's live services.

## Ownership and redistribution
- Mod games the user owns, from their own install or dumps of cartridges and discs they own. Don't download
  ROMs, ISOs or game files.
- **Don't publish:**
  - game files, or byte-identical copies of them;
  - extracted assets;
  - decompiled source;
  - retail offsets or decompiler names baked into shipped code.

  `um publish check --game <install>` catches the obvious cases.
- **Do publish:**
  - your code and your assets (fal output is yours to use under fal's terms; check the model's license for
    commercial use);
  - patches, diffs, and converters or installers that transform the user's own files at install time.
- Credit loaders, libraries and references, and disclose AI use honestly. Communities react badly to
  undisclosed "vibe-coded" releases, and some (certain recomp Discords) ban AI projects.
- Takedowns happen even without assets (SNK and a Metal Slug recomp; Activision and the H2M mod). Commercial
  use, monetization and leaked material raise the risk sharply. Knowledge from betas and leaks is fine to use;
  don't ship leaked code or builds, or a mod that only runs with them.

## The user's machine
- **Back up first:** `um backup create` for saves, profiles and config, before any modded launch. Restoring
  should be one command, written down in MODLOG.md.
- **Loaders and proxy DLLs** (`winhttp.dll`, `version.dll`, `dinput8.dll`, `dxgi.dll`) sit in the game
  folder. Tell the user what you added and how to remove it. Better still, use a separate copy of the game
  or a mod manager profile.
- **Registry and config changes:** `um win reg set` backs up the key first. Note what changed.
- **Input automation takes over the user's mouse and keyboard.**
  - Check `um win drive --proc X idle`. A small number means they're active.
  - Ask before long automated runs.
  - WinDrive only sends input while the game is in the foreground.
- **Processes:** kill by exact PID. `pkill -f <pattern>` from an agent shell kills the agent's own shell.
  Don't leave topmost windows (`untop`), global hooks or orphaned ffmpeg/PowerShell processes behind.
- **Networking:** bind any bridge, debugger or MCP server you add to `127.0.0.1` with a token. Some RE tools
  bind `0.0.0.0` by default.
- **Scripts from strangers:** a viral mod's "download" is often malware. Only run loaders from their
  official repositories and releases.

## When to stop and ask
- The game has online components with anti-cheat, and the idea touches them.
- The only route is bypassing a protection.
- A step would delete or overwrite saves or game files without a backup.
- Publishing: always the user's call.
