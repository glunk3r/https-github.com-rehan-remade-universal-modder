"""Scheme B: Overwatch PC Native Keybinding input controller and state machine.

Mappings:
- Right Click (VK_RBUTTON): Rocket Punch (Hold to charge, release to dash)
- Shift (VK_SHIFT): Seismic Slam (Leap and ground slam)
- E (VK_E): Rising Uppercut (Vertical launch)
- Left Click (VK_LBUTTON): Hand Cannon (4-pellet shotgun)
- Q (VK_Q): Meteor Strike ultimate
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class VirtualKey(int, Enum):
    LBUTTON = 0x01
    RBUTTON = 0x02
    SHIFT = 0x10
    KEY_E = 0x45
    KEY_Q = 0x51
    E = 0x45
    Q = 0x51


class AbilityState(Enum):
    IDLE = auto()
    ROCKET_PUNCH_CHARGING = auto()
    ROCKET_PUNCH_DASHING = auto()
    SEISMIC_SLAM_LEAP = auto()
    RISING_UPPERCUT = auto()
    METEOR_STRIKE_TARGETING = auto()
    METEOR_STRIKE_SLAM = auto()


@dataclass
class InputEvent:
    ability: str
    tier: int = 1
    dash_velocity_mps: float = 0.0
    vertical_velocity_mps: float = 0.0
    pellet_count: int = 0
    shockwave_radius_m: float = 0.0


class DoomfistInputController:
    def __init__(self):
        self.current_state = AbilityState.IDLE
        self.charge_time = 0.0
        self.charge_tier = 1
        self.state_timer = 0.0
        self.hand_cannon_cooldown = 0.0

    def on_key_down(self, vk: VirtualKey) -> Optional[InputEvent]:
        if vk == VirtualKey.RBUTTON and self.current_state == AbilityState.IDLE:
            self.current_state = AbilityState.ROCKET_PUNCH_CHARGING
            self.charge_time = 0.0
            self.charge_tier = 1
            return None

        elif vk == VirtualKey.SHIFT and self.current_state == AbilityState.IDLE:
            self.current_state = AbilityState.SEISMIC_SLAM_LEAP
            self.state_timer = 0.5  # 0.5s air time before impact
            return InputEvent(ability="SeismicSlam", shockwave_radius_m=9.0)

        elif vk == VirtualKey.KEY_E and self.current_state == AbilityState.IDLE:
            self.current_state = AbilityState.RISING_UPPERCUT
            self.state_timer = 0.45  # 0.45s rising duration
            return InputEvent(ability="RisingUppercut", vertical_velocity_mps=9.5)

        elif vk == VirtualKey.LBUTTON:
            if self.hand_cannon_cooldown <= 0.0:
                self.hand_cannon_cooldown = 0.35  # 0.35s shot cooldown
                return InputEvent(ability="HandCannon", pellet_count=4)
            return None

        elif vk == VirtualKey.KEY_Q and self.current_state == AbilityState.IDLE:
            self.current_state = AbilityState.METEOR_STRIKE_TARGETING
            self.state_timer = 4.0  # up to 4s targeting phase
            return InputEvent(ability="MeteorStrike")

        return None

    def on_key_up(self, vk: VirtualKey) -> Optional[InputEvent]:
        if vk == VirtualKey.RBUTTON and self.current_state == AbilityState.ROCKET_PUNCH_CHARGING:
            tier = self.charge_tier
            vel = 12.0 if tier == 1 else (16.0 if tier == 2 else 20.5)
            self.current_state = AbilityState.ROCKET_PUNCH_DASHING
            self.state_timer = 0.35  # 0.35s dash duration
            return InputEvent(
                ability="RocketPunch",
                tier=tier,
                dash_velocity_mps=vel,
            )
        return None

    def update(self, dt: float) -> Optional[InputEvent]:
        if self.hand_cannon_cooldown > 0.0:
            self.hand_cannon_cooldown = max(0.0, self.hand_cannon_cooldown - dt)

        if self.current_state == AbilityState.ROCKET_PUNCH_CHARGING:
            self.charge_time += dt
            if self.charge_time >= 1.0:
                self.charge_tier = 3
            elif self.charge_time >= 0.5:
                self.charge_tier = 2
            else:
                self.charge_tier = 1
            return None

        elif self.current_state == AbilityState.ROCKET_PUNCH_DASHING:
            self.state_timer -= dt
            if self.state_timer <= 0.0:
                self.current_state = AbilityState.IDLE
            return None

        elif self.current_state == AbilityState.SEISMIC_SLAM_LEAP:
            self.state_timer -= dt
            if self.state_timer <= 0.0:
                self.current_state = AbilityState.IDLE
                # Ground impact shockwave event
                return InputEvent(ability="SeismicSlamImpact", shockwave_radius_m=9.0)
            return None

        elif self.current_state == AbilityState.RISING_UPPERCUT:
            self.state_timer -= dt
            if self.state_timer <= 0.0:
                self.current_state = AbilityState.IDLE
            return None

        return None
