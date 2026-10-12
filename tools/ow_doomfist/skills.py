"""Doomfist skill specifications and physics parameter definitions for Elden Ring.

Maps Doomfist's signature combat abilities:
1. Rocket Punch (火箭重拳) - Multi-tier charge, hyperarmor, supersonic dash, wall-slam knockback
2. Rising Uppercut (上勾拳) - Vertical impulse, airborne juggle state
3. Seismic Slam (裂地重击) - Forward leap, ground pound, conical shockwave
4. Hand Cannon (手炮) - Left-hand shotgun blast
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class RocketPunchTier:
    tier: int
    charge_time_sec: float
    dash_velocity_mps: float
    damage_multiplier: float
    knockback_impulse: float
    forward_distance_m: float


@dataclass
class RocketPunchSpec:
    name: str = "RocketPunch"
    name_cn: str = "火箭重拳"
    charge_tiers: List[RocketPunchTier] = field(default_factory=list)
    hyperarmor_active: bool = True
    hyperarmor_poise_multiplier: float = 6.0
    wall_slam_extra_damage: float = 1.5
    knockback_type: str = "KNOCKDOWN_WALL_SLAM"


@dataclass
class RisingUppercutSpec:
    name: str = "RisingUppercut"
    name_cn: str = "上勾拳"
    vertical_launch_velocity_mps: float = 9.5
    launch_enemy_into_air: bool = True
    stamina_cost: int = 24
    fp_cost: int = 14
    hitbox_radius_m: float = 1.8


@dataclass
class SeismicSlamSpec:
    name: str = "SeismicSlam"
    name_cn: str = "裂地重击"
    aoe_radius_m: float = 9.0
    cone_angle_deg: float = 65.0
    applies_ground_knockdown: bool = True
    damage_base: int = 320
    forward_leap_distance_m: float = 7.5


@dataclass
class HandCannonSpec:
    name: str = "HandCannon"
    name_cn: str = "手炮"
    pellet_count: int = 4
    spread_angle_deg: float = 12.0
    damage_per_pellet: int = 45
    effective_range_m: float = 15.0


class DoomfistSkillManager:
    """Manages skill definitions and translates them into Elden Ring parameter table records."""

    def __init__(self):
        self.rocket_punch = RocketPunchSpec(
            charge_tiers=[
                RocketPunchTier(tier=1, charge_time_sec=0.2, dash_velocity_mps=12.0, damage_multiplier=1.2, knockback_impulse=6.0, forward_distance_m=4.0),
                RocketPunchTier(tier=2, charge_time_sec=0.6, dash_velocity_mps=16.0, damage_multiplier=2.0, knockback_impulse=10.0, forward_distance_m=7.0),
                RocketPunchTier(tier=3, charge_time_sec=1.1, dash_velocity_mps=20.5, damage_multiplier=3.6, knockback_impulse=18.5, forward_distance_m=11.0),
            ]
        )
        self.rising_uppercut = RisingUppercutSpec()
        self.seismic_slam = SeismicSlamSpec()
        self.hand_cannon = HandCannonSpec()

    def get_rocket_punch(self) -> RocketPunchSpec:
        return self.rocket_punch

    def get_rising_uppercut(self) -> RisingUppercutSpec:
        return self.rising_uppercut

    def get_seismic_slam(self) -> SeismicSlamSpec:
        return self.seismic_slam

    def get_hand_cannon(self) -> HandCannonSpec:
        return self.hand_cannon

    def generate_param_dict(self) -> Dict[str, Any]:
        """Generate structured parameter patch dictionary for Elden Ring mod loaders."""
        return {
            "version": "1.0.0",
            "character": "Doomfist",
            "skills": {
                "RocketPunch": {
                    "action_name": self.rocket_punch.name,
                    "name_cn": self.rocket_punch.name_cn,
                    "charge_levels": len(self.rocket_punch.charge_tiers),
                    "max_velocity_mps": self.rocket_punch.charge_tiers[-1].dash_velocity_mps,
                    "hyperarmor": self.rocket_punch.hyperarmor_active,
                    "poise_multiplier": self.rocket_punch.hyperarmor_poise_multiplier,
                    "knockback_type": self.rocket_punch.knockback_type,
                },
                "RisingUppercut": {
                    "action_name": self.rising_uppercut.name,
                    "name_cn": self.rising_uppercut.name_cn,
                    "vertical_velocity_mps": self.rising_uppercut.vertical_launch_velocity_mps,
                    "juggle_airborne": self.rising_uppercut.launch_enemy_into_air,
                },
                "SeismicSlam": {
                    "action_name": self.seismic_slam.name,
                    "name_cn": self.seismic_slam.name_cn,
                    "radius_m": self.seismic_slam.aoe_radius_m,
                    "cone_angle": self.seismic_slam.cone_angle_deg,
                    "knockdown": self.seismic_slam.applies_ground_knockdown,
                },
                "HandCannon": {
                    "action_name": self.hand_cannon.name,
                    "name_cn": self.hand_cannon.name_cn,
                    "pellets": self.hand_cannon.pellet_count,
                    "spread_angle": self.hand_cannon.spread_angle_deg,
                },
            },
        }
