---
name: multiplayer-remake
description: Study a multiplayer game the user owns (including anti-cheat-protected and live-service titles) well enough to rebuild its online play as original work, e.g. in Godot. Offline static analysis of client and dedicated-server binaries, data and message schemas; dynamic analysis only on offline/LAN modes and servers the user hosts; then a netcode spec and an authoritative-server remake. Use for "remake <game>'s multiplayer", "how does <game> sync players", "what does <game>'s server tick do", "rebuild this co-op mode in Godot".
---

# Multiplayer remakes

A remake needs the game's **rules and network design**, never its live client. Everything here works on
files on disk, the user's own servers and the remake. Read `skills/mod-any-game/references/safety.md`
("Multiplayer games you are remaking") first; it is the boundary.

## 1. Recon (offline)
- `um scan "<game>"` for engine, anti-cheat and runtime. Anti-cheat present means: never launch the client
  online, never attach a debugger or injector to it, never open the anti-cheat module in a decompiler.
- Look for a **dedicated server** build (Steam tools, `*Server.exe`, `-server` targets). It is usually the
  best source: the authoritative logic, often fewer protections, and you can host it yourself.
- Note the stack: engine netcode (Unreal replication, Unity Netcode/Mirror/Photon, Source, custom UDP),
  transport, tick rate hints in configs.

## 2. Static analysis of the netcode
Decompile client and server (`reverse-engineering` skill: Ghidra/REA for native, ILSpy/Cpp2IL for managed,
FModel/UAssetGUI for Unreal data). Recover, with the evidence (function, address, constant) for each:
- **Authority model:** what the server owns vs what the client predicts (movement, hits, inventory).
- **Message set:** every RPC / replicated property / packet type, its fields, direction, reliability.
- **Tick and rates:** server tick, snapshot/send rates, interpolation delay, input buffering.
- **Prediction & reconciliation:** client-side prediction, rewind/lag compensation for hits.
- **Session flow:** lobby, join, spawn, match state machine, end of round, reconnect.
- **Relevancy/interest:** what each client is sent and when.

## 3. Dynamic analysis (own servers only)
- Run the official **offline/LAN** mode, or **host the dedicated server on this machine** and connect the
  user's own clients to it. Never official servers.
- Capture only that traffic (Wireshark on the loopback/LAN adapter) to confirm rates, sizes and ordering
  against the static findings. No injection into a protected client, even locally; if the offline mode
  ships without anti-cheat, the normal `reverse-engineering` dynamic tools are fine there.

## 4. Netcode spec -> remake
Write `NETCODE.md` next to the remake's `SPEC.md`: authority table, message list, rates, prediction
scheme, session state machine - each claim with its evidence or marked "unverified". Then build it fresh:
- **Godot 4:** high-level multiplayer (`MultiplayerAPI`, `MultiplayerSpawner`, `MultiplayerSynchronizer`,
  RPCs) over ENet, or a custom `PacketPeer` layer when the original's model does not fit. Server
  authoritative by default; client prediction where the original had it.
- Your own protocol, your own servers. The remake never talks to the original game's services.
- Verify with a headless server plus 2+ clients on one machine (Godot `--headless` for the server),
  scripted inputs, and assertions on synced state - not by eye.

## 5. Record
Field note (`share-field-notes`): the netcode architecture you found, how you verified it, and the traps.
No decompiled code, no packet dumps, nothing from official servers in the note.
