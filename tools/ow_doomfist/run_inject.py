"""CLI script to physically inject Doomfist character model, skin, and skills into Elden Ring."""
from pathlib import Path
import sys

from tools.ow_doomfist.inject import DoomfistInjector


def main():
    target_dir = Path(r"C:\Program Files (x86)\Steam\steamapps\common\ELDEN RING\Game")
    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1])

    print(f"[Doomfist Injector] Target directory: {target_dir}")
    if not target_dir.is_dir():
        print(f"[Error] Target directory does not exist: {target_dir}", file=sys.stderr)
        sys.exit(1)

    injector = DoomfistInjector(game_dir=target_dir)
    report = injector.inject()

    if not report.success:
        print(f"[Error] Injection failed: {report.error_message}", file=sys.stderr)
        sys.exit(1)

    print("[Success] Doomfist injected successfully!")
    print(f"  Backup saved to: {report.backup_dir}")
    print(f"  Total deployed files: {len(report.deployed_files)}")
    for f in report.deployed_files:
        print(f"    - {f.name} ({f.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
