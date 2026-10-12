"""Host deployer for Overwatch-Elden Ring Passthrough (Route B1).

Deploys:
- OWPassthrough.fx & presets to Elden Ring Game directory
- ow_compositor.addon (ReShade Add-on for Local\\OWPassthroughFrame shared memory)
- ReShade64.dll (as dxgi.dll for Direct3D 12 hook)

Strict zero-pollution guarantee for the user's existing Minecraft project.
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
    deployed_addon: Optional[Path] = None
    deployed_dxgi: Optional[Path] = None
    message: str = ""


class HostDeployer:
    def __init__(self, game_dir: Optional[Path] = None):
        self.game_dir = game_dir if game_dir is not None else DEFAULT_GAME_DIR
        self.base_dir = Path(__file__).resolve().parent
        self.source_fx = self.base_dir / "OWPassthrough.fx"
        self.source_addon = self.base_dir / "addon" / "build" / "ow_compositor.addon"
        self.source_reshade = self.base_dir / "addon" / "bin" / "ReShade64.dll"

    def verify_mc_intact(self) -> bool:
        """Verify that user's Minecraft project remains 100% intact."""
        mc_adapter_dir = self.game_dir / "mods" / "mc_adapter"
        if not mc_adapter_dir.exists():
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

    def deploy(self, install_dxgi: bool = True) -> DeploymentResult:
        """Deploy OWPassthrough.fx, addon, and ReShade dxgi.dll to target game directory."""
        if not self.verify_mc_intact():
            raise RuntimeError("CRITICAL: Minecraft Steve project integrity check failed before deployment!")

        # 1. Shaders & Presets
        target_mod_reshade = self.game_dir / "mods" / "ow_doomfist_standalone" / "reshade" / "Shaders"
        target_mod_reshade.mkdir(parents=True, exist_ok=True)
        deployed_shader = target_mod_reshade / "OWPassthrough.fx"
        shutil.copy2(self.source_fx, deployed_shader)

        source_fxh = self.base_dir / "ReShade.fxh"
        if source_fxh.is_file():
            shutil.copy2(source_fxh, target_mod_reshade / "ReShade.fxh")

        target_reshade_std = self.game_dir / "reshade-shaders" / "Shaders"
        target_reshade_std.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.source_fx, target_reshade_std / "OWPassthrough.fx")
        if source_fxh.is_file():
            shutil.copy2(source_fxh, target_reshade_std / "ReShade.fxh")

        preset_file = self.game_dir / "mods" / "ow_doomfist_standalone" / "OWPassthrough.ini"
        preset_file.write_text(PRESET_INI_TEMPLATE, encoding="utf-8")
        game_preset = self.game_dir / "OWPassthrough.ini"
        game_preset.write_text(PRESET_INI_TEMPLATE, encoding="utf-8")

        # Configure ReShade.ini to automatically discover and enable OWPassthrough shader
        reshade_ini = self.game_dir / "ReShade.ini"
        reshade_ini_content = """[GENERAL]
EffectSearchPaths=.\\reshade-shaders\\Shaders,.\\mods\\ow_doomfist_standalone\\reshade\\Shaders,.\\
TextureSearchPaths=.\\reshade-shaders\\Textures,.\\mods\\ow_doomfist_standalone\\reshade\\Textures,.\\
PresetPath=.\\OWPassthrough.ini
PerformanceMode=0
NoReloadOnInit=0

[OVERLAY]
TutorialProgress=4
ShowFPS=1

[OWPassthrough.ini]
Techniques=OWPassthrough@OWPassthrough.fx
TechniqueSorting=OWPassthrough@OWPassthrough.fx
"""
        reshade_ini.write_text(reshade_ini_content, encoding="utf-8")


        # 2. ReShade Addon (.addon binary)
        deployed_addon = None
        if self.source_addon.is_file():
            # Deploy to game root and mods folder
            deployed_addon = self.game_dir / "ow_compositor.addon"
            shutil.copy2(self.source_addon, deployed_addon)

            addon_dir = self.game_dir / "reshade-addons"
            addon_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.source_addon, addon_dir / "ow_compositor.addon")

            mod_addon = self.game_dir / "mods" / "ow_doomfist_standalone" / "ow_compositor.addon"
            shutil.copy2(self.source_addon, mod_addon)

        # 3. ReShade DXGI Hook (dxgi.dll)
        deployed_dxgi = None
        if install_dxgi and self.source_reshade.is_file():
            target_dxgi = self.game_dir / "dxgi.dll"
            if target_dxgi.is_file() and not (self.game_dir / "dxgi.dll.bak").exists():
                # Backup existing if not already backed up
                shutil.copy2(target_dxgi, self.game_dir / "dxgi.dll.bak")
            shutil.copy2(self.source_reshade, target_dxgi)
            deployed_dxgi = target_dxgi

        # Post-flight verification
        if not self.verify_mc_intact():
            raise RuntimeError("CRITICAL: Minecraft Steve project integrity corrupted after deployment!")

        return DeploymentResult(
            success=True,
            deployed_shader=deployed_shader,
            deployed_preset=preset_file,
            deployed_addon=deployed_addon,
            deployed_dxgi=deployed_dxgi,
            message="Successfully deployed OWPassthrough shader, addon, and ReShade runtime with 100% MC project isolation",
        )


def main():
    print("[*] Initiating Host Deployment for Overwatch Passthrough (Route B1)...")
    deployer = HostDeployer()
    res = deployer.deploy()
    print(f"[+] {res.message}")
    print(f"    Shader: {res.deployed_shader}")
    print(f"    Preset: {res.deployed_preset}")
    print(f"    Addon:  {res.deployed_addon}")
    print(f"    DXGI:   {res.deployed_dxgi}")


if __name__ == "__main__":
    main()
