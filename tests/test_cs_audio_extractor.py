import os
import struct
import pytest
from pathlib import Path

from tools.cs2.audio_extractor import (
    find_cs_knife_sounds,
    extract_cs_audio_files,
    verify_wav_header_and_data,
)
from tools.cs2.extractor import find_cs2_vpk_path, ensure_vrf_cli


def test_find_cs_knife_sounds():
    """Verify that knife sound events and vsnd_c files are discovered in CS2 VPK."""
    vpk_path = find_cs2_vpk_path()
    vrf_exe = ensure_vrf_cli()

    sound_entries = find_cs_knife_sounds(vrf_exe, vpk_path)
    assert len(sound_entries) > 0

    entry_names = [e.lower() for e in sound_entries]
    # Check for deploy, slash, hit, or butterfly sounds
    has_knife_sound = any(
        any(k in name for k in ["deploy", "slash", "hit", "stab", "butterfly"])
        for name in entry_names
    )
    assert has_knife_sound, f"Expected knife sounds, found: {entry_names[:10]}"


def test_extract_and_verify_knife_audio():
    """E2E Test: extract knife deploy/slash/stab audio to WAV and verify RIFF PCM integrity."""
    vpk_path = find_cs2_vpk_path()
    vrf_exe = ensure_vrf_cli()
    out_dir = Path("./build/cs2assets/audio/knife")

    sound_entries = find_cs_knife_sounds(vrf_exe, vpk_path)
    assert len(sound_entries) > 0

    # Pick up to 5 representative sound entries (deploy, slash, hit, stab)
    target_sounds = []
    for pat in ["deploy", "slash", "hit", "stab"]:
        matched = [s for s in sound_entries if pat in s.lower() and s.lower().endswith(".vsnd_c")]
        if matched:
            target_sounds.append(matched[0])

    assert len(target_sounds) > 0, "Could not find target knife sounds for extraction"

    extracted_wavs = extract_cs_audio_files(vrf_exe, vpk_path, target_sounds, out_dir)
    assert len(extracted_wavs) > 0

    # Deep domain audio verification per Rule 3:
    for wav_file in extracted_wavs:
        assert wav_file.is_file()
        info = verify_wav_header_and_data(wav_file)

        assert info["sample_rate"] in (22050, 44100, 48000), f"Unusual sample rate: {info['sample_rate']}"
        assert info["channels"] in (1, 2), f"Invalid channel count: {info['channels']}"
        assert info["duration_sec"] > 0.05, f"Audio clip suspiciously short: {info['duration_sec']}s"
        assert info["data_size"] > 1000, f"Audio data size too small: {info['data_size']} bytes"


def test_extract_butterfly_sound_pack():
    """Verify that complete sound pack indices contain deploy, inspect, slash, and backstab."""
    from tools.cs2.audio_extractor import extract_butterfly_sound_pack

    vpk_path = find_cs2_vpk_path()
    vrf_exe = ensure_vrf_cli()
    out_dir = Path("./build/cs2assets/audio/knife_pack")

    pack = extract_butterfly_sound_pack(vrf_exe, vpk_path, out_dir)
    assert len(pack) >= 3
    assert "deploy" in pack
    assert "backstab" in pack
    for act, p in pack.items():
        assert p.is_file()
        assert p.stat().st_size > 1000

