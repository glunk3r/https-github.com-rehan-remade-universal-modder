"""Build script for ReShade add-on ow_compositor.addon.

Locates available C++ compiler (clang++, g++, or cl.exe) and compiles
ow_addon.cpp with ReShade 6.8 headers into a 64-bit .addon binary.
"""
from pathlib import Path
import shutil
import subprocess
import sys


def build_addon(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    addon_dir = Path(__file__).resolve().parent
    src_file = addon_dir / "ow_addon.cpp"
    include_dir = addon_dir / "include"
    target_binary = output_dir / "ow_compositor.addon"

    if not src_file.is_file():
        raise FileNotFoundError(f"Source file not found: {src_file}")
    if not (include_dir / "reshade.hpp").is_file():
        raise FileNotFoundError(f"ReShade headers not found in {include_dir}")

    # Check compilers
    clang = shutil.which("clang++")
    gpp = shutil.which("g++")

    if gpp:
        print(f"[*] Compiling with g++: {gpp}")
        cmd = [
            gpp,
            "-O2",
            "-shared",
            "-static",
            "-static-libgcc",
            "-static-libstdc++",
            "-std=c++20",
            f"-I{include_dir}",
            str(src_file),
            "-o",
            str(target_binary),
        ]
    elif clang:
        print(f"[*] Compiling with clang++: {clang}")
        cmd = [
            clang,
            "-O2",
            "-shared",
            "-static",
            "-static-libgcc",
            "-static-libstdc++",
            "-std=c++20",
            f"-I{include_dir}",
            str(src_file),
            "-o",
            str(target_binary),
        ]
    else:
        raise RuntimeError("No suitable C++ compiler (clang++ or g++) found on PATH")

    print(f"    Command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"[-] Compilation failed:\n{proc.stderr}", file=sys.stderr)
        raise RuntimeError(f"Compiler returned exit code {proc.returncode}")

    if not target_binary.is_file() or target_binary.stat().st_size == 0:
        raise RuntimeError("Output binary was not produced")

    print(f"[+] Successfully compiled {target_binary.name} ({target_binary.stat().st_size} bytes)")
    return target_binary


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "build"
    try:
        bin_path = build_addon(out_dir)
        print(f"[+] Output: {bin_path}")
        sys.exit(0)
    except Exception as e:
        print(f"[-] Error: {e}", file=sys.stderr)
        sys.exit(1)
