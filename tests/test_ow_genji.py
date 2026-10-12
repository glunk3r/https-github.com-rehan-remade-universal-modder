"""TDD test suite for Overwatch Genji (源氏) skills, Scheme B input, and visual rendering.

Covers:
- Scheme B Native Keybindings for Genji:
  - Left Click (VK_LBUTTON): Shuriken Linear 3-star burst
  - Right Click (VK_RBUTTON): Shuriken Fan of 3 stars
  - Shift (VK_SHIFT): Swift Strike (影 - 15m/s dash slash)
  - E (VK_E): Deflect (闪 - 2.0s frontal attack parry/invulnerability)
  - Q (VK_Q): Dragonblade (龙刃 - "人龙合一" 6.0s Katana sweep state)
- Visual rendering with Cybernetic Ninja geometry and Dragonblade aura
- Full publishing to Seqlock shared memory bridge
"""
import pytest
from tools.ow_genji.input_controller import (
    GenjiInputController,
    GenjiAbilityState,
)
from tools.ow_doomfist.input_controller import VirtualKey
from tools.ow_passthrough.guest_renderer import (
    GuestCharacterRenderer,
    RenderCamera,
)
from tools.ow_passthrough.shared_memory import SharedMemoryBridge


def test_genji_skills_and_scheme_b_input_state_machine():
    ctrl = GenjiInputController()
    assert ctrl.current_state == GenjiAbilityState.IDLE

    # 1. Left Click -> Shuriken Linear Burst (3 stars)
    act_left = ctrl.on_key_down(VirtualKey.LBUTTON)
    assert act_left is not None
    assert act_left.ability == "ShurikenLinear"
    assert act_left.projectile_count == 3
    assert act_left.spread_deg == 0.0

    # Cooldown prevents immediate spamming
    assert ctrl.on_key_down(VirtualKey.LBUTTON) is None
    ctrl.update(0.3)

    # 2. Right Click -> Shuriken Fan (3 stars spread)
    act_right = ctrl.on_key_down(VirtualKey.RBUTTON)
    assert act_right is not None
    assert act_right.ability == "ShurikenFan"
    assert act_right.projectile_count == 3
    assert act_right.spread_deg >= 25.0
    ctrl.update(0.3)

    # 3. Shift -> Swift Strike (影)
    act_shift = ctrl.on_key_down(VirtualKey.SHIFT)
    assert act_shift is not None
    assert act_shift.ability == "SwiftStrike"
    assert act_shift.dash_velocity_mps >= 14.0
    assert ctrl.current_state == GenjiAbilityState.SWIFT_STRIKE_DASHING

    # Dash completes after 0.25s
    ctrl.update(0.3)
    assert ctrl.current_state == GenjiAbilityState.IDLE

    # 4. E -> Deflect (闪)
    act_e = ctrl.on_key_down(VirtualKey.KEY_E)
    assert act_e is not None
    assert act_e.ability == "Deflect"
    assert act_e.duration_s >= 2.0
    assert ctrl.current_state == GenjiAbilityState.DEFLECT_ACTIVE

    # Deflect expires after 2.0s
    ctrl.update(2.1)
    assert ctrl.current_state == GenjiAbilityState.IDLE

    # 5. Q -> Dragonblade (龙刃)
    act_q = ctrl.on_key_down(VirtualKey.KEY_Q)
    assert act_q is not None
    assert act_q.ability == "Dragonblade"
    assert act_q.duration_s >= 6.0
    assert ctrl.current_state == GenjiAbilityState.DRAGONBLADE_ACTIVE

    # Dragonblade active for 6 seconds
    ctrl.update(6.1)
    assert ctrl.current_state == GenjiAbilityState.IDLE


def test_genji_renderer_posture_and_dragonblade_visuals():
    bridge = SharedMemoryBridge(width=64, height=64)
    renderer = GuestCharacterRenderer(width=64, height=64, bridge=bridge)

    # Switch hero to Genji
    renderer.set_character("Genji")
    assert renderer.character_name == "Genji"
    assert pytest.approx(renderer.bounding_height_m, abs=0.1) == 1.78  # Genji canon height 1.78m

    ctrl = GenjiInputController()

    # Trigger Dragonblade (Q)
    ctrl.on_key_down(VirtualKey.KEY_Q)
    renderer.update_genji_ability_state(ctrl)
    assert renderer.dragonblade_active is True

    # Render frame with Dragonblade green glow aura
    cam = RenderCamera(eye=(0.0, 1.0, -2.5), target=(0.0, 1.0, 0.0), fov_deg=60.0)
    slot_idx = renderer.render_and_publish(camera=cam)
    assert slot_idx in (0, 1, 2)

    # Read frame back
    read_res = bridge.read_latest_frame(max_age_ms=100.0)
    assert read_res.is_valid is True
    assert len(read_res.color_data) == 64 * 64 * 4
