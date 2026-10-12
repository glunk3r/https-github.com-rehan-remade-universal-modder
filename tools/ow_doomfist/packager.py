"""Packages Doomfist character assets and skill parameters into an Elden Ring ModEngine2 mod package."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

from tools.ow_doomfist.skills import DoomfistSkillManager


@dataclass
class PackResult:
    success: bool
    output_dir: Path
    generated_files: List[Path] = field(default_factory=list)
    error_message: Optional[str] = None


class DoomfistModPackager:
    def __init__(self, staging_dir: Path):
        self.staging_dir = Path(staging_dir)
        self.skill_manager = DoomfistSkillManager()

    def build_mod_package(self) -> PackResult:
        try:
            self.staging_dir.mkdir(parents=True, exist_ok=True)
            parts_dir = self.staging_dir / "parts"
            parts_dir.mkdir(parents=True, exist_ok=True)

            generated: List[Path] = []

            # 1. Generate parts files
            # wp_a_2040.dcx: Right-hand weapon part (Doomfist Gauntlet)
            # bd_m_2040.dcx: Body armor part (Doomfist Cybernetic Torso)
            # hd_m_2040.dcx: Head armor part (Doomfist Head)
            part_specs = [
                ("wp_a_2040.dcx", b"DCX\x00\x00\x00\x01DOOMFIST_GAUNTLET_FLVER_DATA"),
                ("bd_m_2040.dcx", b"DCX\x00\x00\x00\x01DOOMFIST_BODY_FLVER_DATA"),
                ("hd_m_2040.dcx", b"DCX\x00\x00\x00\x01DOOMFIST_HEAD_FLVER_DATA"),
            ]

            for filename, dummy_content in part_specs:
                p = parts_dir / filename
                p.write_bytes(dummy_content)
                generated.append(p)

            # 2. Generate ModEngine2 configuration
            config_path = self.staging_dir / "config_eldenring.toml"
            config_toml = (
                "# ModEngine2 Configuration for Overwatch Doomfist\n"
                "[modengine]\n"
                "enabled = true\n"
                "\n"
                "[extension.mod_loader]\n"
                "enabled = true\n"
                "load_order = [\"parts\", \"action\", \"param\"]\n"
                "mods = [\n"
                "    { enabled = true, name = \"Overwatch_Doomfist\", path = \"parts\" }\n"
                "]\n"
            )
            config_path.write_text(config_toml, encoding="utf-8")
            generated.append(config_path)

            # 3. Generate param patch manifest
            param_patch_path = self.staging_dir / "param_patches.json"
            param_data = self.skill_manager.generate_param_dict()
            param_patch_path.write_text(json.dumps(param_data, indent=2, ensure_ascii=False), encoding="utf-8")
            generated.append(param_patch_path)

            return PackResult(
                success=True,
                output_dir=self.staging_dir,
                generated_files=generated,
            )
        except Exception as e:
            return PackResult(
                success=False,
                output_dir=self.staging_dir,
                error_message=str(e),
            )
