---
kind: game
title: 'Zero Hour persistent server: embedded headless sim, seats, scripted AI late-join'
game: 'Command & Conquer Generals: Zero Hour'
games_also: []
game_version: 'Steam Zero Hour 1.04 data + EA GeneralsMD source release'
platform: windows
engine: native
route: reimplementation
tools: [llvm-mingw, cmake, ninja]
anti_cheat: none (offline engine reimplementation; no online client touched)
status: in-progress
agents:
- Claude Code
humans: []
date: '2026-10-14'
links: []
tags: [sage, headless, dedicated-server, lockstep, savegame, skirmish-ai]
---
# Zero Hour persistent server: embedded headless sim, seats, scripted AI late-join

Compiled EA's released Zero Hour engine with clang (portable llvm-mingw, 32-bit) into a headless dedicated server that owns one persistent world: reserved human seats,
AI that joins and leaves over time, absent-base cleanup and rent. Verified headlessly only (server plus headless replicas, per-frame CRC); there is no graphical client yet.

## Setup
llvm-mingw (clang 23, i686, msvcrt), cmake + ninja via uv, zlib 1.3.1, the Steam install used only as a data source (never copied). The engine is built from the original .dsp file lists;
Miles, Bink, GameSpy, DirectX, SafeDisk are stubbed. Run the exe from WSL with cwd = game folder; environment variables need `WSLENV`.

## Route and why
Reimplementation of the host side: the server embeds the real GameLogic with null draw modules (INI draw blocks skipped), so gameplay is the real thing. A witness client as source of truth was rejected: the server sim is the system of record, replicas send orders and report CRCs.

## How the game works (what we had to learn)
- Player cap: MAX_PLAYER_COUNT and PlayerMaskType (16-bit) are compiled in; a multiword mask class plus a build define (128) was enough for the sim; network slots (MAX_SLOTS 64, 8-bit masks in NetPacket) needed an own wire format.
- Savegames (GameState::saveGame + Xfer) are complete enough to be the persistence format; restore is deterministic but not bit-identical to an uninterrupted run, so the server re-bases every client on a snapshot at an agreed frame (canonical epoch).
- The skirmish AI is not built-in logic: it is per-player scripts (SkirmishScripts.scb duplicated and qualified by start index in Player::init); every AI build-list entry has AutomaticallyBuild false and the scripts order the builds.
- Faction templates without a skirmish side (Supreme, boss, challenge generals) silently become human players in Player::init.

## Build steps
See MODLOG in the lab repo: cmake toolchain file for mingw32, `ninja zh_headless`; sources come from the .dsp files; a clang VFS overlay handles the case-insensitive includes.

## Verification
Server + late-joining replicas: thousands of frames with 0 CRC mismatches; kill/restart resumes with identical CRCs; seat lifecycle tests (bind, elimination with last-hit bonus, queue promotion, returning player, absence expiry, unaffordable rent damage); 48 AI + 16 seats smoke run stable at ~30 fps. Not verified: any real rendering client, bridges/roads, bone data (ObjectDrawInterface is stubbed).

## Gotchas
1. **STLport vs libc++.** Symptom: AI/asset lookups wrong. **Cause:** `hash<const char*>` hashed characters in STLport, pointers in libc++. **Fix:** hash the characters (AsciiString).
2. **Save/load asymmetry.** Symptom: XferVersion errors on load. **Cause:** `ResourceGatheringManager::findBestSupplyCenter` erases from m_supplyWarehouses instead of m_supplyCenters; STLport's O(n) size() hid it, libc++ caches size. **Fix:** erase from the right list.
3. **Restore not identical.** Cause: logic RNG state not saved, object list order reversed on load, stale heap bytes. **Fix:** save RNG (GameLogic::xfer v11), preserve order, poison allocations.
4. **Late AI never builds.** Symptom: AI bound mid-game has a build list and money but builds nothing. **Cause:** its one-shot skirmish scripts already ran while the slot was inert. **Fix:** keep scripts off while the seat is empty and reset script active flags from a fresh duplicateAndQualify on bind.
5. **Random faction picks the Supreme/boss side.** The player silently turns human and does nothing. **Fix:** restrict random picks to America/China/GLA.
6. **Locally generated network messages execute on one side** and create AI groups; intercept them like Network::GetCommandsFromCommandList.

## Open questions
Graphical client, skeleton/bone provider for lockstep with real clients, very large map, tick cost beyond ~100 AI (23 fps at 64 AI, 14 fps at 100 in WSL).
