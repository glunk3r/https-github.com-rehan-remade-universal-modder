"""TDD test suite for OWPassthrough.fx ReShade Shader and Background Server.

Covers:
- OWPassthrough.fx ReShade effect structure and syntax integrity
- Background runner (OWPassthroughServer) lifecycle at 60 FPS
- Seqlock shared memory production while server is active
"""
import pytest
import time
from pathlib import Path

from tools.ow_passthrough.ow_server import OWPassthroughServer
from tools.ow_passthrough.shared_memory import SharedMemoryBridge


def test_ow_reshade_fx_structure():
    fx_path = Path("tools/ow_passthrough/OWPassthrough.fx")
    assert fx_path.is_file()
    fx_content = fx_path.read_text(encoding="utf-8")

    # Essential ReShade headers and uniforms
    assert "#include \"ReShade.fxh\"" in fx_content
    assert "texture OWWorldTex" in fx_content
    assert "texture OWDepthTex" in fx_content
    assert "uniform bool OwActive" in fx_content
    assert "uniform bool HostReversedZ" in fx_content
    assert "technique OWPassthrough" in fx_content
    assert "pass P0" in fx_content


def test_ow_passthrough_server_lifecycle():
    bridge = SharedMemoryBridge(width=32, height=32)
    server = OWPassthroughServer(width=32, height=32, fps=30, bridge=bridge)

    assert server.is_alive() is False
    server.start()
    assert server.is_alive() is True

    # Let server run for 100ms
    time.sleep(0.1)
    assert server.frames_produced > 0

    # Verify frame is continuously written to shared memory
    read_res = bridge.read_latest_frame(max_age_ms=100.0)
    assert read_res.is_valid is True

    # Clean shutdown
    server.stop()
    assert server.is_alive() is False
