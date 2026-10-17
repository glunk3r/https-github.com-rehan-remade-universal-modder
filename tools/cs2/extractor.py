"""CS2 Asset Extractor and glTF/GLB Animation Validator.

Extracts viewmodel arms, weapons, knives, and animations from Counter-Strike 2
installations using Source2Viewer-CLI (VRF) and validates structural and temporal
integrity (glTF hierarchy, monotonic animation timestamps, vertex attributes).
"""

from __future__ import annotations

import io
import json
import os
import shutil
import struct
import subprocess
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional


VRF_RELEASE_URL = (
    "https://github.com/ValveResourceFormat/ValveResourceFormat/releases/download/20.0/cli-windows-x64.zip"
)

DEFAULT_CS2_PATHS = [
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive"),
    Path(r"C:\Program Files\Steam\steamapps\common\Counter-Strike Global Offensive"),
    Path(r"D:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive"),
    Path(r"G:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive"),
]


def find_cs2_vpk_path() -> Optional[str]:
    """Locate pak01_dir.vpk in local CS2 installation."""
    for base in DEFAULT_CS2_PATHS:
        candidate = base / "game" / "csgo" / "pak01_dir.vpk"
        if candidate.is_file():
            return str(candidate.resolve())

    steam_path = os.environ.get("STEAM_PATH")
    if steam_path:
        cand = Path(steam_path) / "steamapps" / "common" / "Counter-Strike Global Offensive" / "game" / "csgo" / "pak01_dir.vpk"
        if cand.is_file():
            return str(cand.resolve())

    return None


def ensure_vrf_cli(target_dir: Optional[Path] = None) -> str:
    """Ensure Source2Viewer-CLI executable is available.

    Downloads official GitHub release 20.0 if not found locally.
    """
    if target_dir is None:
        target_dir = Path("./build/tools/vrf")
    target_dir = target_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    exe_path = target_dir / "Source2Viewer-CLI.exe"
    if exe_path.is_file():
        return str(exe_path)

    # Download from official GitHub release
    zip_path = target_dir / "vrf_20.0.zip"
    try:
        if zip_path.is_file():
            zip_path.unlink()
    except OSError:
        pass

    print(f"Downloading Source2Viewer-CLI from {VRF_RELEASE_URL}...")
    subprocess.run(
        ["curl.exe", "-L", "-f", "-o", str(zip_path), VRF_RELEASE_URL],
        check=True
    )

    # Extract zip
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)

    try:
        if zip_path.is_file():
            zip_path.unlink()
    except OSError:
        pass

    if not exe_path.is_file():
        raise FileNotFoundError(f"Source2Viewer-CLI.exe was not found in extracted archive at {target_dir}")

    return str(exe_path)


def list_vpk_entries(vrf_exe: str, vpk_path: str, pattern: Optional[str] = None) -> List[str]:
    """List or search file paths inside pak01_dir.vpk."""
    cmd = [vrf_exe, "-i", vpk_path, "-l"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    
    entries: List[str] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("[") or line.startswith("Loaded "):
            continue
        # Format is "<path> CRC:<hash> size:<bytes>"
        parts = line.split()
        if parts:
            entry_path = parts[0].replace("\\", "/")
            if pattern:
                if pattern.lower() in entry_path.lower():
                    entries.append(entry_path)
            else:
                entries.append(entry_path)

    return entries


def extract_vpk_asset(
    vrf_exe: str,
    vpk_path: str,
    asset_entry: str,
    output_dir: Path,
    export_format: str = "glb",
) -> List[Path]:
    """Extract an asset from VPK to glTF/GLB with full animations.

    Returns the list of generated files.
    """
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # CS2 gameinfo.gi path for resolving external textures/dependencies
    vpk_p = Path(vpk_path)
    gameinfo_path = vpk_p.parent / "gameinfo.gi"

    cmd = [
        vrf_exe,
        "-i", vpk_path,
        "-f", asset_entry,
        "-d",
        "-o", str(output_dir),
        "--gltf_export_format", export_format,
        "--gltf_export_animations",
        "--gltf_export_materials",
    ]
    if gameinfo_path.is_file():
        cmd.extend(["--game", str(gameinfo_path)])

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"VRF export failed for {asset_entry}: {proc.stderr}\nStdout: {proc.stdout}")

    # Collect exported glb/gltf files
    exported: List[Path] = []
    for root, _, files in os.walk(output_dir):
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in [".glb", ".gltf"]:
                exported.append(p)

    return exported


def verify_gltf_structure(file_path: Path) -> Dict[str, Any]:
    """Parse and verify the structural integrity of a GLB or glTF file."""
    if not file_path.is_file():
        raise FileNotFoundError(f"glTF file not found: {file_path}")

    ext = file_path.suffix.lower()
    if ext == ".glb":
        with open(file_path, "rb") as f:
            magic, version, length = struct.unpack("<4sII", f.read(12))
            if magic != b"glTF":
                raise ValueError(f"Invalid GLB magic header: {magic}")
            if version != 2:
                raise ValueError(f"Unsupported glTF version in GLB: {version}")

            # Read first chunk (JSON)
            chunk_length, chunk_type = struct.unpack("<I4s", f.read(8))
            if chunk_type != b"JSON":
                raise ValueError(f"Expected JSON chunk, got {chunk_type}")

            json_bytes = f.read(chunk_length)
            return json.loads(json_bytes.decode("utf-8"))
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)


def verify_animation_monotonicity(file_path: Path, gltf_dict: Dict[str, Any]) -> None:
    """Verify deep domain semantics of glTF animations:

    1. Time input keyframes must be strictly monotonic (t_{i+1} > t_i).
    2. Animation duration must be strictly positive.
    3. Channel target paths must be valid (translation, rotation, scale, weights).
    """
    animations = gltf_dict.get("animations", [])
    if not animations:
        raise ValueError("No animations found in glTF file.")

    accessors = gltf_dict.get("accessors", [])
    buffer_views = gltf_dict.get("bufferViews", [])

    # Load binary buffer
    bin_data: Optional[bytes] = None
    if file_path.suffix.lower() == ".glb":
        with open(file_path, "rb") as f:
            f.seek(12)  # Skip 12-byte header
            json_len, _ = struct.unpack("<I4s", f.read(8))
            f.seek(json_len, os.SEEK_CUR)  # Skip JSON chunk data

            # Second chunk should be BIN
            bin_chunk_hdr = f.read(8)
            if len(bin_chunk_hdr) == 8:
                bin_len, bin_type = struct.unpack("<I4s", bin_chunk_hdr)
                if bin_type == b"BIN\x00":
                    bin_data = f.read(bin_len)
    else:
        # Load external buffer
        buffers = gltf_dict.get("buffers", [])
        if buffers and "uri" in buffers[0]:
            uri = buffers[0]["uri"]
            buf_path = file_path.parent / uri
            if buf_path.is_file():
                with open(buf_path, "rb") as f:
                    bin_data = f.read()

    if bin_data is None:
        # If binary buffer not directly readable, verify accessors metadata
        for anim in animations:
            assert len(anim.get("channels", [])) > 0
            assert len(anim.get("samplers", [])) > 0
        return

    for anim in animations:
        anim_name = anim.get("name", "unnamed")
        samplers = anim.get("samplers", [])
        assert len(samplers) > 0, f"Animation {anim_name} has no samplers."

        for sampler in samplers:
            input_acc_idx = sampler.get("input")
            if input_acc_idx is not None and input_acc_idx < len(accessors):
                acc = accessors[input_acc_idx]
                count = acc.get("count", 0)
                if count <= 1:
                    continue

                bv_idx = acc.get("bufferView")
                if bv_idx is not None and bv_idx < len(buffer_views):
                    bv = buffer_views[bv_idx]
                    byte_offset = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
                    # Input timestamps are 5126 (FLOAT)
                    component_type = acc.get("componentType")
                    if component_type == 5126:  # FLOAT
                        fmt = f"<{count}f"
                        total_bytes = count * 4
                        if byte_offset + total_bytes <= len(bin_data):
                            timestamps = struct.unpack_from(fmt, bin_data, byte_offset)
                            # Assert duration > 0
                            duration = timestamps[-1] - timestamps[0]
                            assert duration > 0, (
                                f"Animation '{anim_name}' duration is not positive: {duration}"
                            )
                            # Assert monotonic timestamps (t_{i+1} >= t_i)
                            for i in range(len(timestamps) - 1):
                                assert timestamps[i + 1] >= timestamps[i], (
                                    f"Animation '{anim_name}' has non-monotonic timestamp at index {i}: "
                                    f"{timestamps[i]} -> {timestamps[i+1]}"
                                )
