"""Overwatch Asset Scanner and Mesh Parser.

Scans local Overwatch CASC installation offline and parses exported 3D geometry
(Wavefront OBJ / SMD) into parsed meshes for the Passthrough Renderer.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional


@dataclass
class ExtractedHeroAsset:
    hero_name: str
    mesh_files: List[Path] = field(default_factory=list)
    texture_files: List[Path] = field(default_factory=list)


@dataclass
class ParsedMesh:
    vertices: List[Tuple[float, float, float]] = field(default_factory=list)
    normals: List[Tuple[float, float, float]] = field(default_factory=list)
    uvs: List[Tuple[float, float]] = field(default_factory=list)
    face_count: int = 0

    @property
    def vertex_count(self) -> int:
        return len(self.vertices)

    @property
    def height_m(self) -> float:
        if not self.vertices:
            return 0.0
        ys = [v[1] for v in self.vertices]
        return max(ys) - min(ys)


class OverwatchAssetScanner:
    def __init__(self, ow_dir: Path):
        self.ow_dir = Path(ow_dir)
        self.data_dir = self.ow_dir / "data"

    def is_valid_installation(self) -> bool:
        exe_exists = (self.ow_dir / "Overwatch.exe").is_file()
        return exe_exists or self.data_dir.is_dir()

    def has_casc_data(self) -> bool:
        if not self.data_dir.is_dir():
            return False
        has_config = (self.data_dir / ".build.config").is_file()
        has_data_files = any(self.data_dir.glob("data.*"))
        return has_config or has_data_files


class WavefrontMeshParser:
    """Parses standard Wavefront OBJ files into memory."""

    def parse_file(self, obj_path: Path) -> ParsedMesh:
        vertices: List[Tuple[float, float, float]] = []
        normals: List[Tuple[float, float, float]] = []
        uvs: List[Tuple[float, float]] = []
        faces_count = 0

        with open(obj_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split()
                prefix = parts[0]

                if prefix == "v" and len(parts) >= 4:
                    vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
                elif prefix == "vn" and len(parts) >= 4:
                    normals.append((float(parts[1]), float(parts[2]), float(parts[3])))
                elif prefix == "vt" and len(parts) >= 3:
                    uvs.append((float(parts[1]), float(parts[2])))
                elif prefix == "f":
                    faces_count += 1

        return ParsedMesh(
            vertices=vertices,
            normals=normals,
            uvs=uvs,
            face_count=faces_count,
        )
