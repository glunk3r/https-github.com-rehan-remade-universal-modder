"""Elden Ring CS Weapon Assets Deployment & Verification Tool.

Deploys CS2 viewmodel geometry (CSVM binary), textures, audio waveforms,
and hook DLL into the Elden Ring Game directory with atomic SHA256
verification and automated backup creation.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_GAME_DIR = Path(r"C:\Program Files (x86)\Steam\steamapps\common\ELDEN RING\Game")


def compute_sha256(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file in uppercase hexadecimal."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


def deploy_file_atomic(src: Path, dest: Path) -> Dict[str, Any]:
    """Copy a file to destination with directory creation and SHA256 validation."""
    if not src.is_file():
        raise FileNotFoundError(f"Source file does not exist: {src}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    src_sha = compute_sha256(src)
    src_size = src.stat().st_size

    shutil.copy2(src, dest)
    dest_sha = compute_sha256(dest)

    if src_sha != dest_sha:
        raise ValueError(f"Integrity check failed during deployment of {src.name}: {src_sha} != {dest_sha}")

    return {
        "src": str(src.resolve()),
        "dest": str(dest.resolve()),
        "size": src_size,
        "sha256": dest_sha,
    }


def deploy_cs_assets(game_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Deploy all CS weapon assets into Elden Ring mods directory."""
    if game_dir is None:
        game_dir = DEFAULT_GAME_DIR
    game_dir = game_dir.resolve()
    if not game_dir.is_dir():
        raise FileNotFoundError(f"Elden Ring Game directory not found at: {game_dir}")

    workspace_root = Path(__file__).resolve().parent.parent.parent
    mods_dir = game_dir / "mods" / "mc_adapter"
    mods_dir.mkdir(parents=True, exist_ok=True)

    manifest: List[Dict[str, Any]] = []

    # 1. Deploy CSVM binary model
    model_src = workspace_root / "build" / "cs2assets" / "cs_butterfly_viewmodel.bin"
    if model_src.is_file():
        model_dest = mods_dir / "cs_butterfly_viewmodel.bin"
        manifest.append(deploy_file_atomic(model_src, model_dest))

    # 2. Deploy Textures
    tex_dir = workspace_root / "build" / "cs2assets" / "butterfly_knife" / "weapons" / "models" / "knife" / "knife_butterfly"
    if tex_dir.is_dir():
        for f in tex_dir.glob("*.png"):
            dest_f = mods_dir / "textures" / "knife_butterfly" / f.name
            manifest.append(deploy_file_atomic(f, dest_f))

    # 3. Deploy Audio (sounds)
    audio_dirs = [
        workspace_root / "build" / "cs2assets" / "audio" / "knife_pack",
        workspace_root / "build" / "cs2assets" / "audio" / "knife",
    ]
    target_sounds_dir = mods_dir / "sounds"
    for adir in audio_dirs:
        if adir.is_dir():
            for root, _, files in os.walk(adir):
                for f in files:
                    if f.lower().endswith(".wav"):
                        src_p = Path(root) / f
                        dest_p = target_sounds_dir / f
                        # Avoid duplicates
                        if not any(m["dest"] == str(dest_p.resolve()) for m in manifest):
                            manifest.append(deploy_file_atomic(src_p, dest_p))

    # 3.1 Update sounds_manifest.txt with CS audio event entries
    manifest_txt = target_sounds_dir / "sounds_manifest.txt"
    cs_sound_entries = [
        "cs.knife.deploy|knife_deploy1.wav|1.000|1.000|1.000\n",
        "cs.knife.slash|knife_slash1.wav|1.000|1.000|1.000\n",
        "cs.knife.slash|knife_slash2.wav|1.000|1.000|1.000\n",
        "cs.knife.inspect|bknife_look03_a.wav|1.000|1.000|1.000\n",
        "cs.knife.inspect|bknife_look03_b.wav|1.000|1.000|1.000\n",
        "cs.knife.inspect|bknife_look03_c.wav|1.000|1.000|1.000\n",
        "cs.knife.clack|bknife_n_clacks_02.wav|1.000|1.000|1.000\n",
        "cs.knife.clack|bknife_n_clacks_05.wav|1.000|1.000|1.000\n",
        "cs.knife.hit|bknife_n_knucklehit_02.wav|1.000|1.000|1.000\n",
    ]
    existing_lines = manifest_txt.read_text(encoding="utf-8").splitlines(keepends=True) if manifest_txt.is_file() else []
    for entry in cs_sound_entries:
        if entry not in existing_lines:
            existing_lines.append(entry)
    manifest_txt.write_text("".join(existing_lines), encoding="utf-8")

    # 4. Deploy dinput8.dll
    dll_candidates = [
        workspace_root / "mc-core" / "build" / "bin" / "eldenring" / "dinput8.dll",
        workspace_root / "mc-core" / "build" / "bin" / "Release" / "dinput8.dll",
        workspace_root / "mc-core" / "build" / "bin" / "RelWithDebInfo" / "dinput8.dll",
    ]
    dll_src = next((p for p in dll_candidates if p.is_file()), None)
    if dll_src:
        dll_dest = game_dir / "dinput8.dll"
        if dll_dest.is_file():
            backup_p = game_dir / "dinput8.dll.bak_cs_deploy"
            shutil.copy2(dll_dest, backup_p)
        manifest.append(deploy_file_atomic(dll_src, dll_dest))

    return manifest


if __name__ == "__main__":
    print("=== Deploying CS2 Weapon Assets to Elden Ring ===")
    res = deploy_cs_assets()
    for item in res:
        print(f"  [DEPLOYED] {Path(item['dest']).name} ({item['size']} bytes) -> SHA256: {item['sha256'][:16]}...")
    print(f"Successfully deployed {len(res)} assets with 100% SHA256 integrity.")
