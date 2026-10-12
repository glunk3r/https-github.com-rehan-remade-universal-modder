"""TDD test suite for OWPassthroughServer real-time Windows input polling.

Validates:
- Background loop polls GetAsyncKeyState for Scheme B keys (RBUTTON, LBUTTON, SHIFT, E, Q)
- Key down and key up state transitions are dispatched to orchestrator
- Ability state transitions update correctly in real time
"""
import pytest
from unittest.mock import patch

from tools.ow_passthrough.ow_server import OWPassthroughServer
from tools.ow_doomfist.input_controller import VirtualKey, AbilityState


def test_server_input_polling_rocket_punch_charge():
    server = OWPassthroughServer(width=32, height=32, fps=60)

    # Initially idle
    assert server.orchestrator.input_controller.current_state == AbilityState.IDLE

    # Mock GetAsyncKeyState: Right mouse button DOWN (0x8000)
    def mock_get_async_key_state(vk):
        if vk == VirtualKey.RBUTTON.value:
            return 0x8000
        return 0

    with patch("ctypes.windll.user32.GetAsyncKeyState", side_effect=mock_get_async_key_state):
        server.poll_host_inputs()

    assert server.orchestrator.input_controller.current_state == AbilityState.ROCKET_PUNCH_CHARGING

    # Step time forward by 0.6s -> Tier 2
    server.orchestrator.step_frame(dt=0.6)
    assert server.orchestrator.input_controller.charge_tier == 2

    # Mock GetAsyncKeyState: Right mouse button RELEASED (0x0)
    with patch("ctypes.windll.user32.GetAsyncKeyState", return_value=0):
        server.poll_host_inputs()

    server.orchestrator.step_frame(dt=0.016)
    assert server.orchestrator.input_controller.current_state == AbilityState.ROCKET_PUNCH_DASHING
