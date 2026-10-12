"""Fetch ReShade 6.x Addon API headers from official ReShade repository.

Downloads header files into tools/ow_passthrough/addon/include/
"""
from pathlib import Path
import urllib.request
import ssl
import sys

HEADERS = [
    "reshade.hpp",
    "reshade_api.hpp",
    "reshade_api_device.hpp",
    "reshade_api_pipeline.hpp",
    "reshade_api_resource.hpp",
    "reshade_api_format.hpp",
    "reshade_events.hpp",
    "reshade_overlay.hpp",
]

BASE_URL = "https://raw.githubusercontent.com/crosire/reshade/v6.8.0/include/"


def fetch_headers(target_dir: Path) -> bool:
    target_dir.mkdir(parents=True, exist_ok=True)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print(f"[*] Fetching ReShade 6.8.0 headers into {target_dir}...")
    for h in HEADERS:
        dest = target_dir / h
        if dest.is_file() and dest.stat().st_size > 0:
            print(f"    [OK] {h} already present ({dest.stat().st_size} bytes)")
            continue
        url = BASE_URL + h
        print(f"    Fetching {url} -> {dest.name}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "UniversalModder/1.0"})
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                content = resp.read()
                dest.write_bytes(content)
                print(f"    [+] Saved {h} ({len(content)} bytes)")
        except Exception as e:
            print(f"    [-] Failed to fetch {h}: {e}", file=sys.stderr)
            return False
    return True


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "include"
    success = fetch_headers(out_dir)
    sys.exit(0 if success else 1)
