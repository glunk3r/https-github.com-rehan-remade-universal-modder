"""Scheme B: Overwatch PC Native Keybinding input controller for Genji (源氏).

Mappings:
- Left Click (VK_LBUTTON): Shuriken Linear (3 stars in a straight line)
- Right Click (VK_RBUTTON): Shuriken Fan (3 stars spread in 28° cone)
- Shift (VK_SHIFT): Swift Strike (影 - 15m/s supersonic dash slice)
- E (VK_E): Deflect (闪 - 2.0s frontal attack parry/invulnerability)
- Q (VK_Q): Dragonblade (龙刃 - 6.0s Katana slash state)
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from tools.ow_doomfist.input_controller import VirtualKey


class GenjiAbilityState(Enum):
    IDLE = auto()
    SHURIKEN_LINEAR = auto()
    SHURIKEN_FAN = auto()
    SWIFT_STRIKE_DASHING = auto()
    DEFLECT_ACTIVE = auto()
    DRAGONBLADE_ACTIVE = auto()


@dataclass
class GenjiActionEvent:
    ability: str
    projectile_count: int = 0
    spread_deg: float = 0.0
    dash_velocity_mps: float = 0.0
    duration_s: float = 0.0


class GenjiInputController:
    def __init__(self):
        self.current_state = GenjiAbilityState.IDLE
        self.primary_cooldown = 0.0
        self.state_timer = 0.0

    def on_key_down(self, vk: VirtualKey) -> Optional[GenjiActionEvent]:
        # 1. Left Click -> Shuriken Linear (3-burst)
        if vk == VirtualKey.LBUTTON:
            if self.primary_cooldown <= 0.0 and self.current_state in (GenjiAbilityState.IDLE, GenjiAbilityState.DRAGONBLADE_ACTIVE):
                self.primary_cooldown = 0.28  # 0.28s cooldown
                return GenjiActionEvent(ability="ShurikenLinear", projectile_count=3, spread_deg=0.0)
            return None

        # 2. Right Click -> Shuriken Fan (3-spread)
        elif vk == VirtualKey.RBUTTON:
            if self.primary_cooldown <= 0.0 and self.current_state in (GenjiAbilityState.IDLE, GenjiAbilityState.DRAGONBLADE_ACTIVE):
                self.primary_cooldown = 0.28
                return GenjiActionEvent(ability="ShurikenFan", projectile_count=3, spread_deg=28.0)
            return None

        # 3. Shift -> Swift Strike (影)
        elif vk == VirtualKey.SHIFT and self.current_state in (GenjiAbilityState.IDLE, GenjiAbilityState.DRAGONBLADE_ACTIVE):
            self.current_state = GenjiAbilityState.SWIFT_STRIKE_DASHING
            self.state_timer = 0.25  # 0.25s dash duration
            return GenjiActionEvent(ability="SwiftStrike", dash_velocity_mps=15.0, duration_s=0.25)

        # 4. E -> Deflect (闪)
        elif vk == VirtualKey.KEY_E and self.current_state in (GenjiAbilityState.IDLE, GenjiAbilityState.DRAGONBLADE_ACTIVE):
            self.current_state = GenjiAbilityState.DEFLECT_ACTIVE
            self.state_timer = 2.0  # 2.0s parry duration
            return GenjiActionEvent(ability="Deflect", duration_s=2.0)

        # 5. Q -> Dragonblade (龙刃)
        elif vk == VirtualKey.KEY_Q and self.current_state == GenjiAbilityState.IDLE:
            self.current_state = GenjiAbilityState.DRAGONBLADE_ACTIVE
            self.state_timer = 6.0  # 6.0s ult duration
            return GenjiActionEvent(ability="Dragonblade", duration_s=6.0)

        return None

    def on_key_up(self, vk: VirtualKey) -> Optional[GenjiActionEvent]:
        return None

    def update(self, dt: float) -> None:
        if self.primary_cooldown > 0.0:
            self.primary_cooldown = max(0.0, self.primary_cooldown - dt)

        if self.current_state in (GenjiAbilityState.SWIFT_STRIKE_DASHING, GenjiAbilityState.DEFLECT_ACTIVE, GenjiAbilityState.DRAGONBLADE_ACTIVE):
            self.state_timer -= dt
            if self.state_timer <= 0.0:
                self.current_state = GenjiAbilityState.IDLE
