"""TDD tests for Scheme B (Overwatch PC Native Keybindings) input state machine.

Bindings:
- Right Click (VK_RBUTTON): Hold to charge Rocket Punch, release to fire dash
- Shift (VK_SHIFT): Leap and ground slam (Seismic Slam)
- E (VK_E): Rising Uppercut (vertical launch)
- Left Click (VK_LBUTTON): Hand Cannon (4-pellet shotgun)
- Q (VK_Q): Meteor Strike ultimate
"""
import pytest
from tools.ow_doomfist.input_controller import (
    DoomfistInputController,
    AbilityState,
    VirtualKey,
    InputEvent,
)


def test_rocket_punch_charge_and_release_tiers():
    ctrl = DoomfistInputController()

    # Initially idle
    assert ctrl.current_state == AbilityState.IDLE

    # 1. Press Right Click -> enters CHARGING
    ctrl.on_key_down(VirtualKey.RBUTTON)
    assert ctrl.current_state == AbilityState.ROCKET_PUNCH_CHARGING
    assert ctrl.charge_time == 0.0

    # Advance 0.3s -> Tier 1
    ctrl.update(0.3)
    assert ctrl.charge_tier == 1
    assert ctrl.current_state == AbilityState.ROCKET_PUNCH_CHARGING

    # Advance to 0.7s total -> Tier 2
    ctrl.update(0.4)
    assert ctrl.charge_tier == 2

    # Advance to 1.2s total -> Tier 3 (max)
    ctrl.update(0.5)
    assert ctrl.charge_tier == 3
    assert ctrl.charge_time >= 1.1

    # Release Right Click -> fires Rocket Punch
    action = ctrl.on_key_up(VirtualKey.RBUTTON)
    assert action is not None
    assert action.ability == "RocketPunch"
    assert action.tier == 3
    assert action.dash_velocity_mps >= 20.0
    assert ctrl.current_state == AbilityState.ROCKET_PUNCH_DASHING

    # After dash completes (0.35s), returns to IDLE
    ctrl.update(0.4)
    assert ctrl.current_state == AbilityState.IDLE


def test_seismic_slam_trigger_and_impact():
    ctrl = DoomfistInputController()

    # Press Shift -> triggers Seismic Slam leap
    action = ctrl.on_key_down(VirtualKey.SHIFT)
    assert action is not None
    assert action.ability == "SeismicSlam"
    assert ctrl.current_state == AbilityState.SEISMIC_SLAM_LEAP

    # In air for 0.4s
    ctrl.update(0.4)
    assert ctrl.current_state == AbilityState.SEISMIC_SLAM_LEAP

    # Impacts ground at 0.5s -> triggers shockwave event
    impact_event = ctrl.update(0.15)
    assert impact_event is not None
    assert impact_event.shockwave_radius_m >= 8.0
    assert ctrl.current_state == AbilityState.IDLE


def test_rising_uppercut_trigger():
    ctrl = DoomfistInputController()

    # Press E -> triggers Rising Uppercut
    action = ctrl.on_key_down(VirtualKey.KEY_E)
    assert action is not None
    assert action.ability == "RisingUppercut"
    assert action.vertical_velocity_mps >= 9.0
    assert ctrl.current_state == AbilityState.RISING_UPPERCUT

    # Finishes in 0.45s
    ctrl.update(0.5)
    assert ctrl.current_state == AbilityState.IDLE


def test_hand_cannon_trigger():
    ctrl = DoomfistInputController()

    # Left Click -> fires 4 pellets
    action = ctrl.on_key_down(VirtualKey.LBUTTON)
    assert action is not None
    assert action.ability == "HandCannon"
    assert action.pellet_count == 4

    # Cooldown prevents immediate spamming
    immediate_next = ctrl.on_key_down(VirtualKey.LBUTTON)
    assert immediate_next is None  # still cooling down

    # Wait cooldown 0.35s
    ctrl.update(0.4)
    subsequent = ctrl.on_key_down(VirtualKey.LBUTTON)
    assert subsequent is not None


def test_meteor_strike_trigger():
    ctrl = DoomfistInputController()

    # Press Q -> enters Meteor Strike targeting
    action = ctrl.on_key_down(VirtualKey.KEY_Q)
    assert action is not None
    assert action.ability == "MeteorStrike"
    assert ctrl.current_state == AbilityState.METEOR_STRIKE_TARGETING
