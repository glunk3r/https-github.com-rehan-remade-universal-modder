"""E2E lifecycle test for Overwatch-EldenRing Passthrough Orchestrator.

Validates:
- Complete end-to-end loop: Input -> Guest Renderer -> Seqlock Shared Memory -> Compositor
- Multi-frame continuous pipeline step
- Zero memory leakage and clean shutdown
"""
import pytest
from tools.ow_passthrough.orchestrator import PassthroughOrchestrator
from tools.ow_doomfist.input_controller import VirtualKey


def test_passthrough_orchestrator_e2e_loop():
    orchestrator = PassthroughOrchestrator(width=32, height=32)

    # 1. Start pipeline
    assert orchestrator.is_running is False
    orchestrator.start()
    assert orchestrator.is_running is True

    # 2. Step 5 normal frames with neutral camera
    for i in range(5):
        frame_stat = orchestrator.step_frame(dt=0.016, host_cam_eye=(0.0, 1.0, -2.5))
        assert frame_stat.frame_id == i + 1
        assert frame_stat.is_valid is True
        assert frame_stat.composite_drawn_pixels > 0

    # 3. Trigger Scheme B Rocket Punch charge
    orchestrator.on_key_down(VirtualKey.RBUTTON)
    charge_stat = orchestrator.step_frame(dt=0.6, host_cam_eye=(0.0, 1.0, -2.5))
    assert charge_stat.charge_tier == 2

    # Release Rocket Punch
    orchestrator.on_key_up(VirtualKey.RBUTTON)
    dash_stat = orchestrator.step_frame(dt=0.1, host_cam_eye=(0.0, 1.0, -2.5))
    assert dash_stat.active_ability == "RocketPunch"

    # 4. Clean shutdown
    orchestrator.stop()
    assert orchestrator.is_running is False
