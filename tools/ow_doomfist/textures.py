"""PBR texture packing and format conversion for Elden Ring Dantelion engine.

Handles:
- OpenGL to DirectX Normal map conversion (invert Green channel)
- Specular / Metallic / Roughness channel packing
"""
from typing import Tuple, Dict, Any


class PBRTexturePacker:
    """Packs standard PBR texture maps into FromSoftware Dantelion format."""

    def pack_material(
        self,
        albedo_rgb: Tuple[int, int, int],
        normal_gl: Tuple[int, int, int],
        roughness: int,
        metallic: int,
    ) -> Dict[str, Any]:
        """Convert and pack PBR material attributes."""
        r, g, b = normal_gl
        # DirectX normal map has inverted green channel compared to OpenGL
        dx_g = 255 - g
        normal_dx = (r, dx_g, b)

        packed_specular = {
            "metallic": int(metallic),
            "roughness": int(roughness),
        }

        return {
            "albedo_rgb": albedo_rgb,
            "normal_dx": normal_dx,
            "packed_specular": packed_specular,
        }
