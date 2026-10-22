---
kind: game
title: Native HDR output for the Xenia emulator (fp16 scRGB presenter)
game: Burnout Paradise
games_also: []
game_version: 'Burnout Paradise artist build (BURNOUT_X360_ARTIST.XEX, title 45410806, patch hash 0CC027FC408913C2)'
platform: windows
engine: native
route: emulator
tools: []
anti_cheat: none
status: working
agents:
- GitHub Copilot
humans: []
date: '2026-10-21'
links: []
tags: []
---
# Native HDR output for the Xenia emulator (fp16 scRGB presenter)

> Native HDR output (fp16 scRGB swapchain, SDR-white scaling, optional highlight
> expansion) added to both GPU/UI backends of a xenia-canary fork so Burnout
> Paradise presents as a real HDR signal on Windows HDR displays. Verified
> in-game: the log shows the swapchain at the queried SDR white level of 240
> nits, and the game runs normally through it. The "true HDR" extraction route
> was investigated and closed with evidence: the game renders entirely in
> 8-bit LDR.

## Setup
- Emulator: xenia-canary netplay fork, branch `canary_burnout5-2026-online-experiment`
  (2026-07 GPU code), HDR work on branch `canary_burnout5-hdr-output`
  (commits 845804931, a1f303bcd, 3e7a77e9b), source at
  `%USERPROFILE%\Documents\xenia-b5-2025-online-exp\xenia-burnout5`.
- Game files at `E:\Burnout_tcartwright\Burnout_tcartwright`; the setup runs the
  artist build `BURNOUT_X360_ARTIST.XEX` (title 45410806 "Burnout Paradise",
  patch DB hash 0CC027FC408913C2, a dev/artist build with an active xenia-canary
  patch ecosystem in the `patches/` folder).
- Host: Windows 11, HDR enabled, SDR white level 240 nits, NVIDIA RTX 4070 SUPER.
- Build: VS2022 + `xb.ps1 build --config=release` (CMake+ninja), Vulkan SDK
  1.4.357.0 (for the shader compile steps), clang-format 19 from the VS Llvm dir.
- Ghidra 12.1.4 with the XEXLoaderWV extension for the XEX recon.

## Route and why
Route: `emulator` - the emulator owns presentation, so native HDR output is an
emulator feature (C++ presenter + presentation shaders), not a game mod.
Considered and rejected: presenting the game's "true HDR" pre-tonemap buffer -
proved impossible (see below); the alternative would have been re-engineering
the game's post pipeline, which is a game-engine mod, not presentation.

## How the game works (what we had to learn)
- The Xenia presenter pipeline (both backends): guest front buffer (8_8_8_8 or
  2_10_10_10) -> IssueSwap applies the guest gamma ramp -> gamma-encoded
  guest output image (10-bit) -> paint effect chain (bilinear / CAS / FSR,
  optional dither for 8bpc swapchains) -> host swapchain. Before this work the
  swapchain was always 8-bit SDR.
- Burnout Paradise (artist build) renders entirely in 8-bit LDR: runtime RT
  logging over ~8 min (boot+menu+attract, bloom active) shows 14 render target
  creations, ALL color targets ColorRenderTargetFormat 0 (k_8_8_8_8), depth
  D24S8/D24FS8, zero fp16 / 16_16 / 2_10_10_10 targets. The front buffer is a
  2560x1440 k_8_8_8_8 resolve. So there is no pre-tonemap HDR buffer to
  present, and highlight expansion of SDR content is the only native-HDR
  mechanism for this game.
- The game's graphics settings live in a global data block; the bloom
  parameter float JeBobs' patch touches is at 0x82F307E0 (default 1.0 in the
  image, patched to 0.3), sitting between LOD-distance floats and menu strings.
- XEXLoaderWV imports BURNOUT_X360_ARTIST.XEX headless and full auto-analysis
  succeeds (~265 s); the PowerPC constant reference analyzer did not find code
  xrefs to the patched settings addresses (values are data, likely written at
  runtime config load).

## Build steps
1. `git switch -c <branch> && .\xb.ps1 build --config=release` in the xenia
   clone. The CMake build regenerates shader bytecode (SPIR-V + DXBC) from the
   .xesl sources automatically; bytecode dirs are gitignored.
2. Enable `present_hdr = true` in `xenia-burnout5.config.toml` (new cvars are
   auto-added to the config), optionally `present_hdr_expansion` (0..1) and
   `present_hdr_sdr_white_level` (nits, 0 = query Windows).
3. Run `xenia_burnout5.exe <path-to-xex>`; check `xenia.log` for
   "HDR output with an SDR white level of N nits".
4. Debug: `--gpu_log_render_targets=true` logs RT creations and front buffer
   format changes (D3D12 backend).

## Verification
- Oracle: `xenia.log` line from the real game run:
  "D3D12Presenter: HDR output with an SDR white level of 240.00002 nits
  (scRGB scale 3.0000002)" - proving an fp16 scRGB swapchain was created and
  the Windows SDR white level was queried live.
- The game boots and renders normally through the HDR swapchain (no D3D12
  errors; GDI screenshots of the window look normal but are DWM-tonemapped,
  so they cannot show HDR luminance).
- NOT verified programmatically: the perceptual HDR result (brightness of sun
  vs sky with expansion on/off) - needs eyeballs on the physical HDR display;
  the user was given exact steps.
- Burnout true-HDR absence verified via `gpu_log_render_targets` (all-LDR
  RT evidence, ~8 min of runtime).

## Gotchas
1. **Emulator ignores your Vulkan HDR work.** *Symptom:* HDR swapchain never
   appears, no errors. *Cause:* on this fork `gpu = any` picks the **Direct3D
   12** backend on Windows, and the window title says
   "<Direct3D 12 - RTV/DSV 2x2 ...>". *Fix:* implement presenter features in
   BOTH backends; check the title bar / log ("Direct3D 12 device and OS
   features" vs Vulkan init) to see which one is actually running.
2. **DEFINE_float does not exist.** *Symptom:* C2039 'present_hdr_expansion'
   is not a member of 'cvars'. *Cause:* xenia's cvar macros are
   DEFINE_bool/int32/uint32/int64/double/string/path - no float; and each
   DEFINE is TU-local, so other .cc files need DECLARE_* in a shared header.
   *Fix:* use DEFINE_double + DECLARE_double in the shared presenter header
   (pattern: DECLARE_bool(present_render_pass_clear) in presenter.h).
3. **HLSL packoffsets are per-shader-cbuffer, GLSL push-constant offsets are
   shared across stages.** *Symptom:* HDR constants read as garbage in DXBC
   while Vulkan works. *Cause:* in the XESL block_offset_member_xe(glsl_bytes,
   hlsl_packoffset, ...) the GLSL offset counts from the whole push constant
   block (VS uses 0-15), but the HLSL packoffset counts from the fragment
   shader's own cbuffer (its byte 0 = block byte 16). *Fix:* e.g. GLSL offset
   32 pairs with hlsl c1.x (not c2.x) for bilinear; c0.x for the immediate PS.
4. **`linear` is a reserved word in HLSL.** *Symptom:* DXBC build step fails
   with X3000 "unexpected token 'linear'" while SPIR-V compiles fine.
   *Cause:* a shader helper parameter named `linear`. *Fix:* rename it; don't
   trust glslang alone to validate XESL, the build compiles DXBC too.
5. **DXGI color-space support flag name.** *Symptom:* C2065
   'DXGI_COLOR_SPACE_SUPPORT_PRESENT'. *Cause:* the SDK constant is
   DXGI_SWAP_CHAIN_COLOR_SPACE_SUPPORT_FLAG_PRESENT. *Fix:* use the full name.
6. **DISPLAYCONFIG enum values for HDR queries.** GET_ADVANCED_COLOR_INFO is
   type 9 and GET_SDR_WHITE_LEVEL is type 11 (not 5/8); SDRWhiteLevel is in
   thousandths of 80 nits (nits = 80 * value / 1000). Match the path to the
   window's monitor via DISPLAYCONFIG_SOURCE_DEVICE_NAME.viewGdiDeviceName vs
   MONITORINFOEXW.szDevice.
7. **D3D12 swapchain format is a compile-time constant in the presenter.**
   kSwapChainFormat is used for the DXGI swapchain desc, the RTV descriptors
   AND the pipeline RTVFormats, so HDR needs a dynamic format (stored in the
   paint context) plus a second set of "final" pipelines with fp16 RTV format.
8. **Pipeline cache bug in this fork:** GuestOutputPaintPipeline::swapchain_format
   was never assigned, so the final-effect pipeline was destroyed and
   recreated every frame. Found while adding the HDR cache key - fixed by
   storing the format (and is_hdr) after creation.
9. **Empty patch TOMLs look like load errors.** "PatchDB: Cannot load patch
   file" for Zackypoo's Bloom / Graphics Boost - they are 0-byte placeholder
   files in the patches folder, not a patcher bug.
10. **Shader bytecode is generated, not committed.** src/*/shaders/bytecode/ is
    gitignored and rebuilt by the ninja DXBC/SPIR-V steps; `xb buildshaders`
    also exists but is not needed for a normal build. New .ps.xesl variant
    files are picked up automatically.

## Assets
None - presentation-path code only.

## Cost and time
One session (~3.5 h) end to end: recon, both backend implementations, in-game
verification, RE pass with Ghidra.

## Open questions
- Perceptual tuning of the expansion curve (knee at 0.18 linear, squared ramp,
  4x max) - should be eyeballed against real footage on the HDR display.
- Game-side synergy: JeBobs/community bloom patches (the 0x82F307E0 float)
  plus `present_hdr_expansion` - whether pushing bloom/exposure up game-side
  makes the expansion look better.
- The retail BURNOUT_X360_INTERNAL/EXTERNAL XEXs were not RT-profiled; the
  artist build was assumed representative (same engine).
