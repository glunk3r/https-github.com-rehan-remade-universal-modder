"""Downloads official ReShade with Add-on support and extracts ReShade64.dll.
"""
from pathlib import Path
import urllib.request
import zipfile
import sys
import ssl

RESHADE_VERSION = "6.8.0"
URL = f"https://reshade.me/downloads/ReShade_Setup_{RESHADE_VERSION}_Addon.exe"


def fetch_reshade_dll(target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    dll_path = target_dir / "ReShade64.dll"
    if dll_path.is_file() and dll_path.stat().st_size > 1_000_000:
        print(f"[+] ReShade64.dll already present ({dll_path.stat().st_size} bytes)")
        return dll_path

    print(f"[*] Downloading ReShade {RESHADE_VERSION} with Addon support from {URL}...")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "Referer": "https://reshade.me/",
        },
    )

    exe_path = target_dir / "ReShade_Setup.exe"
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        content = resp.read()
        exe_path.write_bytes(content)
        print(f"[+] Downloaded setup executable ({len(content)} bytes)")

    # ReShade setup exe has an appended zip archive containing ReShade64.dll
    # Find zip signature PK\x03\x04
    print("[*] Extracting ReShade64.dll from package...")
    data = exe_path.read_bytes()
    idx = data.find(b"PK\x03\x04")
    if idx == -1:
        raise RuntimeError("Could not find ZIP payload in ReShade installer")

    zip_bytes = data[idx:]
    tmp_zip = target_dir / "reshade_payload.zip"
    tmp_zip.write_bytes(zip_bytes)

    with zipfile.ZipFile(tmp_zip, "r") as z:
        for name in z.namelist():
            if name.endswith("ReShade64.dll"):
                z.extract(name, target_dir)
                extracted = target_dir / name
                if extracted != dll_path:
                    extracted.rename(dll_path)
                print(f"[+] Successfully extracted {dll_path} ({dll_path.stat().st_size} bytes)")
                break

    # Cleanup temporary zip
    if tmp_zip.exists():
        tmp_zip.unlink()

    return dll_path


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "bin"
    try:
        dll = fetch_reshade_dll(out_dir)
        print(f"[+] ReShade DLL ready: {dll}")
        sys.exit(0)
    except Exception as e:
        print(f"[-] Failed to fetch ReShade: {e}", file=sys.stderr)
        sys.exit(1)
