"""Injector module: deploys Doomfist character model, textures, configuration, and skill parameters directly into Elden Ring's mod directory."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import shutil
import io
from PIL import Image

from tools.ow_doomfist.skills import DoomfistSkillManager


@dataclass
class InjectionReport:
    success: bool
    backup_dir: Path
    deployed_files: List[Path] = field(default_factory=list)
    error_message: Optional[str] = None


class DoomfistInjector:
    def __init__(self, game_dir: Path):
        self.game_dir = Path(game_dir)
        self.adapter_dir = self.game_dir / "mods" / "mc_adapter"
        self.backup_dir = self.adapter_dir / "backup_before_doomfist"
        self.skill_manager = DoomfistSkillManager()

    def generate_doomfist_skin(self) -> bytes:
        """Generate an authentic 64x64 Doomfist character skin PNG.

        Features:
        - Akande Ogundimu's skin tone
        - Cybernetic chest implants and metallic collar
        - Crimson combat sash and dark tactical trousers
        - Massive golden/bronze robotic Doomfist gauntlet on the right arm
        """
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        pixels = img.load()

        # Color palette
        skin_base = (115, 75, 50, 255)
        skin_shadow = (95, 60, 40, 255)
        cyber_metal = (60, 65, 70, 255)
        cyber_light = (170, 175, 180, 255)
        trousers = (40, 42, 45, 255)
        crimson_sash = (185, 35, 35, 255)
        gold_base = (218, 165, 32, 255)
        gold_dark = (165, 120, 20, 255)
        gold_light = (255, 215, 0, 255)

        # 1. Head (x: 0..32, y: 0..16)
        for y in range(0, 16):
            for x in range(0, 32):
                pixels[x, y] = skin_base if (x + y) % 2 == 0 else skin_shadow

        # Face cybernetic brow and ear implants
        for x in range(8, 16):
            pixels[x, 8] = cyber_metal
            pixels[x, 12] = skin_shadow

        # 2. Torso (x: 16..40, y: 16..32)
        for y in range(16, 32):
            for x in range(16, 40):
                if y >= 28:
                    pixels[x, y] = crimson_sash  # Combat sash belt
                elif 18 <= y <= 24 and 20 <= x <= 26:
                    pixels[x, y] = cyber_metal   # Cybernetic chest reactor
                elif 19 <= y <= 23 and 22 <= x <= 24:
                    pixels[x, y] = cyber_light   # Core glow
                else:
                    pixels[x, y] = skin_base

        # 3. Left Arm (Regular arm) (x: 32..48, y: 48..64)
        for y in range(48, 64):
            for x in range(32, 48):
                pixels[x, y] = skin_base

        # 4. Right Arm - The Doomfist Gauntlet! (x: 40..56, y: 16..32)
        for y in range(16, 32):
            for x in range(40, 56):
                # Reinforced golden exoskeleton plating
                if (x + y) % 3 == 0:
                    pixels[x, y] = gold_light
                elif (x + y) % 3 == 1:
                    pixels[x, y] = gold_base
                else:
                    pixels[x, y] = gold_dark

        # Gauntlet knuckles / cable conduits
        for y in range(26, 32):
            for x in range(44, 48):
                pixels[x, y] = cyber_metal

        # 5. Legs (Trousers & boots) (x: 0..16, y: 16..32 and 16..32, y: 48..64)
        for y in range(16, 32):
            for x in range(0, 16):
                pixels[x, y] = trousers if y < 28 else cyber_metal

        for y in range(48, 64):
            for x in range(0, 32):
                pixels[x, y] = trousers if y < 58 else cyber_metal

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def generate_doomfist_model_json(self) -> str:
        """Generate Blockbench model specification with enlarged Doomfist Gauntlet geometry."""
        model_dict = {
            "meta": {
                "format_version": "4.5",
                "model_format": "free",
                "box_uv": False,
            },
            "name": "doomfist",
            "resolution": {"width": 64, "height": 64},
            "elements": [
                {
                    "name": "head",
                    "from": [-4, 24, -4],
                    "to": [4, 32, 4],
                    "faces": {"north": {"uv": [8, 8, 16, 16]}},
                },
                {
                    "name": "body",
                    "from": [-4, 12, -2],
                    "to": [4, 24, 2],
                    "faces": {"north": {"uv": [20, 20, 28, 32]}},
                },
                {
                    "name": "left_arm",
                    "from": [4, 12, -2],
                    "to": [8, 24, 2],
                    "faces": {"north": {"uv": [36, 52, 40, 64]}},
                },
                {
                    "name": "doomfist_gauntlet",
                    # Enlarged mechanical dimensions for the legendary Doomfist gauntlet
                    "from": [-9, 10, -3.5],
                    "to": [-4, 26, 3.5],
                    "faces": {"north": {"uv": [44, 20, 52, 32]}},
                },
                {
                    "name": "right_arm",
                    "from": [-8, 12, -2],
                    "to": [-4, 24, 2],
                    "faces": {"north": {"uv": [44, 20, 48, 32]}},
                },
                {
                    "name": "left_leg",
                    "from": [0, 0, -2],
                    "to": [4, 12, 2],
                    "faces": {"north": {"uv": [4, 20, 8, 32]}},
                },
                {
                    "name": "right_leg",
                    "from": [-4, 0, -2],
                    "to": [0, 12, 2],
                    "faces": {"north": {"uv": [20, 52, 24, 64]}},
                },
            ],
            "animations": [],
        }
        return json.dumps(model_dict, indent=2)

    def inject(self) -> InjectionReport:
        try:
            self.adapter_dir.mkdir(parents=True, exist_ok=True)
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            deployed: List[Path] = []

            # 1. Backup existing assets
            for fname in ("steve.png", "steve.bbmodel"):
                src = self.adapter_dir / fname
                if src.is_file():
                    dst = self.backup_dir / fname
                    shutil.copy2(src, dst)

            cfg_src = self.game_dir / "mc_er_steve.txt"
            if cfg_src.is_file():
                shutil.copy2(cfg_src, self.backup_dir / "mc_er_steve.txt")

            # 2. Deploy Doomfist Skin
            skin_path = self.adapter_dir / "steve.png"
            skin_bytes = self.generate_doomfist_skin()
            skin_path.write_bytes(skin_bytes)
            deployed.append(skin_path)

            # 3. Deploy Doomfist 3D Model
            model_path = self.adapter_dir / "steve.bbmodel"
            # Also keep a named copy doomfist.bbmodel
            named_model_path = self.adapter_dir / "doomfist.bbmodel"
            model_content = self.generate_doomfist_model_json()
            model_path.write_text(model_content, encoding="utf-8")
            named_model_path.write_text(model_content, encoding="utf-8")
            deployed.extend([model_path, named_model_path])

            # 4. Deploy and optimize runtime configuration (mc_er_steve.txt)
            cfg_path = self.game_dir / "mc_er_steve.txt"
            current_cfg: Dict[str, str] = {}
            if cfg_path.is_file():
                for line in cfg_path.read_text(encoding="utf-8").splitlines():
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        current_cfg[k.strip()] = v.strip()

            # Ensure optimal rendering flags for Doomfist
            current_cfg["hide_native"] = "1"
            current_cfg["occlusion"] = "1"
            current_cfg["abs_bias"] = "0.05"
            current_cfg["rel_bias"] = "0.05"

            new_cfg_lines = [f"{k}={v}" for k, v in sorted(current_cfg.items())]
            cfg_path.write_text("\n".join(new_cfg_lines) + "\n", encoding="utf-8")
            deployed.append(cfg_path)

            # 5. Ensure sentinel overlay and damage hook files are active
            for sentinel in ("mc_er_overlay.txt", "mc_er_damage.txt"):
                s_path = self.game_dir / sentinel
                if not s_path.is_file():
                    s_path.write_text("", encoding="utf-8")
                deployed.append(s_path)

            # 6. Deploy Doomfist skill parameter patches
            param_patch_path = self.game_dir / "param_patches.json"
            param_data = self.skill_manager.generate_param_dict()
            param_patch_path.write_text(json.dumps(param_data, indent=2, ensure_ascii=False), encoding="utf-8")
            deployed.append(param_patch_path)

            return InjectionReport(
                success=True,
                backup_dir=self.backup_dir,
                deployed_files=deployed,
            )
        except Exception as e:
            return InjectionReport(
                success=False,
                backup_dir=self.backup_dir,
                error_message=str(e),
            )
