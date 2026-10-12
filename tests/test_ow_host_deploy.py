"""TDD test suite for Elden Ring Host Passthrough Deployment.

Validates:
- Pre-flight and post-flight verification of the user's MC project isolation
- Safe deployment of OWPassthrough.fx and ReShade presets into Elden Ring Game directory
- Zero interference with mc_adapter or any Steve assets
"""
import pytest
from pathlib import Path

from tools.ow_passthrough.deploy_host import (
    HostDeployer,
    DeploymentResult,
)


def test_host_deployer_mc_isolation():
    deployer = HostDeployer()
    # MC adapter intactness check
    assert deployer.verify_mc_intact() is True


def test_host_deployer_run(tmp_path):
    # Test deployment into temporary game root
    mock_game_dir = tmp_path / "Game"
    mock_game_dir.mkdir()
    (mock_game_dir / "eldenring.exe").touch()

    deployer = HostDeployer(game_dir=mock_game_dir)
    res: DeploymentResult = deployer.deploy()

    assert res.success is True
    assert res.deployed_shader.is_file()
    assert res.deployed_preset.is_file()

    content = res.deployed_shader.read_text(encoding="utf-8")
    assert "OWPassthrough" in content
    assert "DepthConstant" in content

    preset_content = res.deployed_preset.read_text(encoding="utf-8")
    assert "0.050067" in preset_content

    assert res.deployed_addon is not None
    assert res.deployed_addon.is_file()
    assert res.deployed_dxgi is not None
    assert res.deployed_dxgi.is_file()
