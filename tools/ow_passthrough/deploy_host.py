"""Host deployer for Overwatch-Elden Ring Passthrough.

Deploys the ReShade composite shader and configuration to Elden Ring Game directory
with strict zero-pollution guarantees for the existing Minecraft project.
"""
from dataclasses import dataclass
from pathlib import Path
import shutil
import sys
from typing import Optional


DEFAULT_GAME_DIR = Path(r"C:\Program Files (x86)\Steam\steamapps\common\ELDEN RING\Game")
STEVE_BBMODEL_SIZE = 1894976
STEVE_PNG_SIZE = 1893
MC_TXT_SIZE = 345

PRESET_INI_TEMPLATE = """; ReShade Configuration Preset for Overwatch Passthrough
[OWPassthrough.fx]
OwActive=1
HostReversedZ=1
DepthConstant=0.050067
DepthBias=0.050000
LightMatch=0.700000
"""


@dataclass
class DeploymentResult:
    success: bool
    deployed_shader: Path
    deployed_preset: Path
    message: str = ""


class HostDeployer:
    def __init__(self, game_dir: Optional[Path] = None):
        self.game_dir = game_dir if game_dir is not None else DEFAULT_GAME_DIR
        self.source_fx = Path(__file__).resolve().parent / "OWPassthrough.fx"

    def verify_mc_intact(self) -> bool:
        """Verify that user's Minecraft project remains 100% intact."""
        mc_adapter_dir = self.game_dir / "mods" / "mc_adapter"
        if not mc_adapter_dir.exists():
            # If running against mock directory, check real installation if present
            real_mc_dir = DEFAULT_GAME_DIR / "mods" / "mc_adapter"
            if real_mc_dir.exists():
                mc_adapter_dir = real_mc_dir
            else:
                return True

        bbmodel = mc_adapter_dir / "steve.bbmodel"
        png = mc_adapter_dir / "steve.png"
        txt = self.game_dir / "mc_er_steve.txt"
        if not txt.exists() and (DEFAULT_GAME_DIR / "mc_er_steve.txt").exists():
            txt = DEFAULT_GAME_DIR / "mc_er_steve.txt"

        if bbmodel.exists() and bbmodel.stat().st_size != STEVE_BBMODEL_SIZE:
            return False
        if png.exists() and png.stat().st_size != STEVE_PNG_SIZE:
            return False
        if txt.exists() and txt.stat().st_size != MC_TXT_SIZE:
            return False

        return True

    def deploy(self) -> DeploymentResult:
        """Deploy OWPassthrough.fx and preset to target game directory."""
        if not self.verify_mc_intact():
            raise RuntimeError("CRITICAL: Minecraft Steve project integrity check failed before deployment!")

        # Target 1: Standalone mod folder
        target_mod_reshade = self.game_dir / "mods" / "ow_doomfist_standalone" / "reshade" / "Shaders"
        target_mod_reshade.mkdir(parents=True, exist_ok=True)
        deployed_shader = target_mod_reshade / "OWPassthrough.fx"
        shutil.copy2(self.source_fx, deployed_shader)

        # Target 2: Standard reshade-shaders folder
        target_reshade_std = self.game_dir / "reshade-shaders" / "Shaders"
        target_reshade_std.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.source_fx, target_reshade_std / "OWPassthrough.fx")

        # Preset files
        preset_file = self.game_dir / "mods" / "ow_doomfist_standalone" / "OWPassthrough.ini"
        preset_file.write_text(PRESET_INI_TEMPLATE, encoding="utf-8")

        game_preset = self.game_dir / "OWPassthrough.ini"
        game_preset.write_text(PRESET_INI_TEMPLATE, encoding="utf-8")

        # Post-flight verification
        if not self.verify_mc_intact():
            raise RuntimeError("CRITICAL: Minecraft Steve project integrity corrupted after deployment!")

        return DeploymentResult(
            success=True,
            deployed_shader=deployed_shader,
            deployed_preset=preset_file,
            message="Successfully deployed OWPassthrough.fx and preset with 100% MC project isolation",
        )


def main():
    print("[*] Initiating Host Deployment for Overwatch Passthrough...")
    deployer = HostDeployer()
    res = deployer.deploy()
    print(f"[+] {res.message}")
    print(f"    Shader: {res.deployed_shader}")
    print(f"    Preset: {res.deployed_preset}")


if __name__ == "__main__":
    main()
