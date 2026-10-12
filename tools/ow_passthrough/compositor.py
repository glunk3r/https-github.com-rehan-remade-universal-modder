"""Depth-testing compositor: evaluates Elden Ring reversed-Z depth against Guest linear depth."""
from enum import Enum, auto


class CompositePixel(Enum):
    DRAW_GUEST = auto()
    OCCLUDED_BY_HOST = auto()
    TRANSPARENT = auto()


class DepthCompositor:
    def __init__(self, depth_constant: float = 0.050067, abs_bias: float = 0.05):
        self.depth_constant = depth_constant
        self.abs_bias = abs_bias

    def test_depth(
        self,
        guest_linear_z: float,
        guest_alpha: float,
        host_reversed_z: float,
    ) -> CompositePixel:
        """Evaluate if guest pixel is drawn or occluded by host geometry.

        In Elden Ring:
            Reversed-Z depth buffer where 1.0 is near and 0.0 is far.
            Linear distance = depth_constant / host_reversed_z.
        """
        if guest_alpha <= 0.01:
            return CompositePixel.TRANSPARENT

        if host_reversed_z <= 0.0:
            # Nothing in host background (skybox or unrendered far plane)
            host_distance = float("inf")
        else:
            host_distance = self.depth_constant / host_reversed_z

        if guest_linear_z <= host_distance + self.abs_bias:
            return CompositePixel.DRAW_GUEST

        return CompositePixel.OCCLUDED_BY_HOST
