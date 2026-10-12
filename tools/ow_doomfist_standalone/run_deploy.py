"""CLI runner to deploy the completely isolated Overwatch Doomfist Standalone mod."""
from pathlib import Path
import sys

from tools.ow_doomfist_standalone.mod_packager import StandaloneModPackager


def main():
    target_dir = Path(r"C:\Program Files (x86)\Steam\steamapps\common\ELDEN RING\Game")
    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1])

    print(f"[Standalone Doomfist Packager] Target: {target_dir}")
    if not target_dir.is_dir():
        print(f"[Error] Target directory not found: {target_dir}", file=sys.stderr)
        sys.exit(1)

    # Pre-flight check: ensure mc_adapter is not touched
    mc_adapter = target_dir / "mods" / "mc_adapter"
    steve_size_before = (mc_adapter / "steve.bbmodel").stat().st_size if (mc_adapter / "steve.bbmodel").is_file() else None

    packager = StandaloneModPackager(game_dir=target_dir)
    res = packager.build_and_deploy()

    if not res.success:
        print(f"[Error] Deployment failed: {res.error_message}", file=sys.stderr)
        sys.exit(1)

    # Post-flight check: verify mc_adapter was completely untouched
    if steve_size_before is not None:
        steve_size_after = (mc_adapter / "steve.bbmodel").stat().st_size
        assert steve_size_before == steve_size_after, "FATAL: mc_adapter was modified!"

    print("[Success] Standalone Overwatch Doomfist mod deployed cleanly!")
    print(f"  Isolated Mod Directory: {res.output_dir}")
    print(f"  Total files generated: {len(res.generated_files)}")
    for f in res.generated_files:
        print(f"    - {f.relative_to(target_dir)} ({f.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
