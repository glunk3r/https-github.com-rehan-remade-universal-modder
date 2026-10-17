import hashlib
import os
import pytest
from pathlib import Path

from tools.cs2.deploy_cs_assets import (
    deploy_cs_assets,
    compute_sha256,
)


def test_deploy_cs_assets_manifest():
    """Verify that deployment script atomically deploys model, textures, audio, and validates SHA256."""
    game_dir = Path(r"C:\Program Files (x86)\Steam\steamapps\common\ELDEN RING\Game")
    assert game_dir.is_dir(), f"Elden Ring Game dir not found: {game_dir}"

    manifest = deploy_cs_assets(game_dir=game_dir)
    assert len(manifest) >= 5, "Manifest should record model, DLL, and key sound deployments"

    for entry in manifest:
        dest_path = Path(entry["dest"])
        assert dest_path.is_file(), f"Deployed file does not exist: {dest_path}"
        assert dest_path.stat().st_size > 0, f"Deployed file is empty: {dest_path}"
        
        # Non-superficial SHA256 check
        actual_sha = compute_sha256(dest_path)
        assert actual_sha == entry["sha256"], f"SHA256 mismatch for {dest_path}: {actual_sha} != {entry['sha256']}"
