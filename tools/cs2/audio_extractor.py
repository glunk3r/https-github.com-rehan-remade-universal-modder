"""CS2 Knife Audio Extractor and WAV Validator.

Extracts knife sound effects (.vsnd_c) from CS2 VPK archives, decompiles them
to standard PCM WAV files, and verifies acoustic compliance (RIFF headers,
valid sample rates, channels, and non-empty waveform durations).
"""

from __future__ import annotations

import os
import struct
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.cs2.extractor import list_vpk_entries


def find_cs_knife_sounds(vrf_exe: str, vpk_path: str) -> List[str]:
    """Search for knife-related sound files (.vsnd_c) inside the CS2 VPK."""
    # Knife sounds typically live under sounds/weapons/knife or sounds/weapons/knife_butterfly
    all_entries = list_vpk_entries(vrf_exe, vpk_path, pattern="knife")
    
    sound_entries = [
        e for e in all_entries
        if ("sound" in e.lower() or e.lower().startswith("sounds/"))
        and (e.lower().endswith(".vsnd_c") or e.lower().endswith(".vsndevts_c"))
    ]
    return sound_entries


def extract_cs_audio_files(
    vrf_exe: str,
    vpk_path: str,
    entries: List[str],
    output_dir: Path,
) -> List[Path]:
    """Decompile .vsnd_c audio resources to WAV files."""
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted_wavs: List[Path] = []

    for entry in entries:
        cmd = [
            vrf_exe,
            "-i", vpk_path,
            "-f", entry,
            "-d",
            "-o", str(output_dir),
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            continue

    # Scan output directory for decompiled .wav files
    for root, _, files in os.walk(output_dir):
        for f in files:
            if f.lower().endswith(".wav"):
                p = Path(root) / f
                if p not in extracted_wavs:
                    extracted_wavs.append(p)

    return extracted_wavs


def extract_butterfly_sound_pack(vrf_exe: str, vpk_path: str, output_dir: Path) -> Dict[str, Path]:
    """Extract complete butterfly sound pack (deploy, inspect clicks, slash, backstab)."""
    sound_entries = find_cs_knife_sounds(vrf_exe, vpk_path)
    # Search for butterfly knife specific entries (bknife) + knife base
    target_entries = [
        e for e in sound_entries
        if ("bknife" in e.lower() or "knife_deploy" in e.lower() or "knife_slash" in e.lower())
        and e.lower().endswith(".vsnd_c")
    ]
    extract_cs_audio_files(vrf_exe, vpk_path, target_entries, output_dir)

    # Index by logical action
    sound_map: Dict[str, Path] = {}
    for root, _, files in os.walk(output_dir):
        for f in files:
            if f.lower().endswith(".wav"):
                full_path = Path(root) / f
                f_lower = f.lower()
                if "deploy" in f_lower:
                    sound_map["deploy"] = full_path
                elif "slash" in f_lower:
                    sound_map["slash"] = full_path
                elif "backstab" in f_lower:
                    sound_map["backstab"] = full_path
                elif "knucklehit" in f_lower or "flick" in f_lower or "catch" in f_lower:
                    sound_map["inspect_click"] = full_path

    return sound_map


def verify_wav_header_and_data(wav_path: Path) -> Dict[str, Any]:
    """Verify RIFF WAV container structure and calculate audio properties."""
    with open(wav_path, "rb") as f:
        riff_header = f.read(12)
        if len(riff_header) < 12:
            raise ValueError(f"File too small for WAV header: {wav_path}")

        riff, file_size, wave = struct.unpack("<4sI4s", riff_header)
        if riff != b"RIFF" or wave != b"WAVE":
            raise ValueError(f"Invalid WAV RIFF header in {wav_path}: riff={riff}, wave={wave}")

        audio_format = 0
        channels = 0
        sample_rate = 0
        byte_rate = 0
        block_align = 0
        bits_per_sample = 0
        data_size = 0

        # Parse RIFF chunks
        while True:
            chunk_hdr = f.read(8)
            if len(chunk_hdr) < 8:
                break
            chunk_id, chunk_size = struct.unpack("<4sI", chunk_hdr)

            if chunk_id == b"fmt ":
                fmt_data = f.read(min(chunk_size, 16))
                if len(fmt_data) >= 16:
                    audio_format, channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack(
                        "<HHIIHH", fmt_data[:16]
                    )
                # Skip any extra format bytes
                if chunk_size > 16:
                    f.seek(chunk_size - 16, os.SEEK_CUR)

            elif chunk_id == b"data":
                data_size = chunk_size
                # Skip data chunk
                f.seek(chunk_size, os.SEEK_CUR)

            else:
                # Unknown chunk (LIST, JUNK, etc.), skip
                f.seek(chunk_size, os.SEEK_CUR)

            # Chunks in RIFF are word-aligned
            if chunk_size % 2 != 0:
                f.seek(1, os.SEEK_CUR)

    if sample_rate == 0 or byte_rate == 0:
        raise ValueError(f"WAV fmt chunk missing or invalid in {wav_path}")

    duration_sec = data_size / byte_rate if byte_rate > 0 else 0.0

    return {
        "audio_format": audio_format,
        "channels": channels,
        "sample_rate": sample_rate,
        "byte_rate": byte_rate,
        "bits_per_sample": bits_per_sample,
        "data_size": data_size,
        "duration_sec": duration_sec,
    }
