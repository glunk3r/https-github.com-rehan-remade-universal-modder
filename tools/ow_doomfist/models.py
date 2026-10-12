"""Overwatch model geometry and coordinate transformation for Elden Ring.

Converts Z-up coordinate spaces (Overwatch, Blender) to Y-up (Elden Ring / Dantelion engine)
and normalizes character proportions to 1.95m canon height.
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
from enum import Enum


class PartType(str, Enum):
    HEAD = "head"
    BODY = "body"
    ARMS = "arms"
    LEGS = "legs"
    GAUNTLET = "gauntlet"


@dataclass
class BoundingBox:
    min_x: float = 0.0
    max_x: float = 0.0
    min_y: float = 0.0
    max_y: float = 0.0
    min_z: float = 0.0
    max_z: float = 0.0

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def depth(self) -> float:
        return self.max_z - self.min_z


@dataclass
class ModelPart:
    name: str
    part_type: PartType
    vertices: List[Tuple[float, float, float]] = field(default_factory=list)
    indices: List[int] = field(default_factory=list)
    uvs: List[Tuple[float, float]] = field(default_factory=list)
    normals: List[Tuple[float, float, float]] = field(default_factory=list)


class ModelTransformer:
    def __init__(self, target_height_m: float = 1.95):
        self.target_height_m = float(target_height_m)

    def transform_vertices(
        self,
        vertices: List[Tuple[float, float, float]],
        source_coord_system: str = "ow_z_up_cm",
    ) -> List[Tuple[float, float, float]]:
        """Transform vertices from Overwatch coordinate space to Elden Ring Dantelion Y-up space in metres.

        In Overwatch Z-up:
            x: Lateral (right positive)
            y: Forward (front positive)
            z: Vertical height (up positive)
        In Elden Ring Y-up:
            x: Lateral (right positive)
            y: Vertical height (up positive)
            z: Forward (front positive)
        """
        if not vertices:
            return []

        if source_coord_system == "ow_z_up_cm":
            # Extract vertical span in raw coordinates (z in ow_z_up_cm)
            z_vals = [v[2] for v in vertices]
            min_z = min(z_vals)
            max_z = max(z_vals)
            height_span = max_z - min_z

            if height_span <= 0:
                scale = 1.0 / 100.0
            else:
                scale = self.target_height_m / height_span

            out: List[Tuple[float, float, float]] = []
            for vx, vy, vz in vertices:
                # Map x -> x, z -> y (shifted so min_z maps to 0.0), y -> z
                er_x = vx * scale
                er_y = (vz - min_z) * scale
                er_z = vy * scale
                out.append((er_x, er_y, er_z))
            return out

        elif source_coord_system == "y_up_m":
            return list(vertices)

        raise ValueError(f"Unsupported coordinate system: {source_coord_system}")
