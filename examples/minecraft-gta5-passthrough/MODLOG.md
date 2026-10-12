# MODLOG

## Goal

Prepare the existing Minecraft Java + Grand Theft Auto V Legacy passthrough as a single-player Melty mashup. GTA V Legacy is the primary game; Minecraft Java Edition is the companion. Preserve the project's real gameplay, use only Melty-managed installation requirements, and do not change or bypass anti-cheat settings. The user approved adapting the project if needed, even if some GTA-side features change.

## Source and established design

- Source of truth: this folder's `README.md` and implementation.
- GTA V Legacy build: 1.0.3889.0. Minecraft Java Edition: 26.3 with Fabric Loader 0.19.5 and Fabric API 0.161.0+26.3.
- Single-player, story-mode passthrough: real Minecraft is rendered into GTA V; GTA camera and ground drive Minecraft; block, combat, mob, flight, and Nether events are bridged between the games.
- The repository's root `LICENSE` is MIT. `README.md` credits ScriptHookV, ReShade, Fabric, alloc8or's native database, Java-WebSocket, and the inspirations; it also records that the code was written with Claude Code.

## Publishing and safety findings

- Melty lists a live, closely matching mashup, `Minecraft GTA V` (v0.1.4), open for remixes. Its source is not linked. Do not copy its package or create a second listing until a new build is actually ready.
- Melty's GTA V Legacy game information lists Ultimate ASI Loader as auto-installed; Script Hook V is not auto-installed and is proprietary. The current project uses ScriptHookV APIs and its installer writes `-nobattleye -noBE`. Those dependencies and launch arguments cannot be carried into the approved Melty adaptation.
- Melty's GTA V Legacy guidance says to build for story mode only, disclose that on the listing, and never put `-nobattleye` in `commandline.txt`. Keep GTA's anti-cheat settings untouched.
- Minecraft's game information says no loader is automatically installed. The package must bring a supported portable Prism setup and Fabric instance rather than asking players to install Fabric manually.
- The project uses the repository's MIT license; third-party runtimes/assets still require their own redistribution review. Do not include either game's files or assets.

## Work and verification

- Installed official Eclipse Temurin JDK 25.0.4.1 under `%LOCALAPPDATA%\Programs\Temurin\jdk-25.0.4.1`.
- Built the Minecraft Fabric mod successfully with `mc\gradlew.bat --no-daemon build`; output: `mc\build\libs\passthrough-0.1.0.jar` (207,644 bytes).
- The GTA V Legacy native plugin is not yet adapted or built. This PC has no discovered GTA V Legacy install: `um scan "Grand Theft Auto V"` found none, Steam's registered library has no app 271590, and the checked Rockstar/Epic/Xbox paths do not contain `GTA5.exe`.
- `um scan` found an Xbox Minecraft launcher package at `C:\XboxGames\Minecraft- Java Edition\Content`, but it did not identify a Java game installation. No Visual Studio C++ build tools were found.
- No game has been launched and no real gameplay screenshot has been captured. The Minecraft jar is a build artifact, not a release package.

## Next

Get the exact GTA V Legacy install folder (or install the game on this PC). Then choose and verify an ASI-loader-only GTA integration that leaves anti-cheat configuration untouched. Build and exercise it in story mode before packaging. Keep the Melty listing as a draft until both games can be launched, real gameplay media is captured, the package passes Melty's checks, and the installed release passes Melty's test.
