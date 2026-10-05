"""Offline tests for the pieces that don't need a game, a GPU or a fal key.

    uv run --with pytest pytest -q
"""
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from um import backup, fal, publish, scan, sprite, video  # noqa: E402


# --------------------------------------------------------------------------- scan

def make(root: Path, files: dict):
    for rel, data in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data if isinstance(data, bytes) else data.encode())


def engine_of(tmp_path, files):
    make(tmp_path, files)
    hits, _ = scan.detect(scan.Index(tmp_path))
    return hits[0][0], hits[0][3]


def test_unity_mono_and_version(tmp_path):
    key, det = engine_of(tmp_path, {
        "UnityPlayer.dll": b"MZ", "Game_Data/Managed/Assembly-CSharp.dll": b"MZ",
        "Game_Data/globalgamemanagers": b"\0" * 20 + b"2022.3.21f1\0" + b"\0" * 100,
        "Game_Data/app.info": "Studio\nCoolGame",
    })
    assert key == "unity-mono"
    assert det["version"] == "2022.3.21f1" and det["product"] == "CoolGame"


def test_unity_il2cpp(tmp_path):
    key, _ = engine_of(tmp_path, {"UnityPlayer.dll": b"MZ", "GameAssembly.dll": b"MZ",
                                  "Game_Data/il2cpp_data/Metadata/global-metadata.dat": b"\xaf\x1b\xb1\xfa"})
    assert key == "unity-il2cpp"


def test_unreal_version_from_exe(tmp_path):
    exe = b"MZ" + b"\0" * 5000 + "++UE5+Release-5.3".encode("utf-16-le") + b"\0" * 100
    key, det = engine_of(tmp_path, {"Proj/Binaries/Win64/Proj-Win64-Shipping.exe": exe, "Proj/Content/Paks/Proj-Windows.pak": b"x",
                                    "Proj/Content/Paks/Proj-Windows.utoc": b"x"})
    assert key == "unreal" and det["engine_version"] == "UE5+Release-5.3" and det["iostore"]


def test_godot_pck(tmp_path):
    key, det = engine_of(tmp_path, {"game.exe": b"MZ", "game.pck": b"GDPC" + struct.pack("<4I", 2, 4, 2, 1)})
    assert key == "godot" and det["version"].startswith("4.2.1")


def test_gamemaker_and_rpgmaker(tmp_path):
    assert engine_of(tmp_path / "a", {"data.win": b"FORM\0\0\0\0GEN8\0\0\0\0\0\x11"})[0] == "gamemaker"
    assert engine_of(tmp_path / "b", {"www/js/rpg_core.js": "//", "Game.exe": b"MZ"})[0] == "rpgmaker-mvmz"


def test_managed_pe(tmp_path):
    # minimal PE32 with a CLR header directory entry
    pe = bytearray(1024)
    pe[0:2] = b"MZ"
    struct.pack_into("<I", pe, 0x3C, 0x80)
    pe[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<H", pe, 0x84, 0x14C)
    opt = 0x80 + 24
    struct.pack_into("<H", pe, opt, 0x10B)
    struct.pack_into("<I", pe, opt + 96 + 14 * 8, 0x2000)
    p = tmp_path / "Game.exe"
    p.write_bytes(bytes(pe))
    assert scan.pe_info(p) == {"arch": "x86", "managed": True}


def test_vdf():
    d = scan._vdf('"AppState" { "appid" "105600" "name" "Terraria" "installdir" "Terraria" }')
    assert d["AppState"]["installdir"] == "Terraria"


@pytest.mark.parametrize("library_name,install_name,game_name", [
    ("SteamLibrary", "ExampleGame", "Example Game"),
    ("SteamLibrary", "ExampleGame", "Example Game\u2122"),
    ("SteamLibrary", "Jeu\u00e9", "Example Game"),
    ("Biblioth\u00e8que", "ExampleGame", "Example Game"),
])
def test_steam_games_utf8(tmp_path, monkeypatch, library_name, install_name, game_name):
    root = tmp_path / "Steam"
    library = tmp_path / library_name
    apps = library / "steamapps"
    game_path = apps / "common" / install_name
    game_path.mkdir(parents=True)
    (root / "steamapps").mkdir(parents=True)
    (root / "steamapps/libraryfolders.vdf").write_text(
        '"libraryfolders" { "0" { "path" "' + library.as_posix() + '" } }', encoding="utf-8",
    )
    (apps / "appmanifest_123.acf").write_text(
        f'"AppState" {{ "appid" "123" "name" "{game_name}" "installdir" "{install_name}" }}',
        encoding="utf-8",
    )
    monkeypatch.setattr(scan, "steam_roots", lambda: [root])

    # Emulate a non-UTF-8 Windows default on every test platform, using real files.
    original_read_text = Path.read_text

    def read_text(path, encoding=None, errors=None, **kwargs):
        return original_read_text(path, encoding=encoding or "cp1252", errors=errors, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)

    assert scan.steam_games() == [{
        "store": "steam", "appid": "123", "name": game_name,
        "path": str(game_path), "workshop": None,
    }]

def test_known_game_longest_key_wins(tmp_path):
    # "grand theft auto v" is a substring of "grand theft auto v enhanced";
    # the more specific entry must win, not whichever lands first in the dict
    d = tmp_path / "Grand Theft Auto V Enhanced"
    d.mkdir()
    for i in range(6):
        (d / f"f{i}.txt").write_text("x")
    r = scan.scan(str(d))
    assert r["routes"][0]["route"] == scan.KNOWN["grand theft auto v enhanced"][0]


# --------------------------------------------------------------------------- sprite

def sprite_on_white(w=64, h=48):
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    for x in range(20, 40):
        for y in range(10, 30):
            im.putpixel((x, y), (200, 30, 30, 255))
    im.putpixel((30, 20), (255, 255, 255, 255))   # an interior white "eye" must survive
    return im


def test_cutout_keeps_interior_white():
    out = sprite.cutout(sprite_on_white())
    assert out.size == (20, 20)
    assert out.getpixel((10, 10))[3] == 255          # the interior white pixel is still opaque
    assert out.getpixel((0, 0))[:3] == (200, 30, 30)


def test_fit_and_hard_alpha():
    f = sprite.fit(sprite.cutout(sprite_on_white()), 10, 10, anchor="bottom")
    assert f.size == (10, 10) and f.getbbox()[3] == 10
    assert set(sprite.hard_alpha(f).getchannel("A").getdata()) <= {0, 255}


def test_sheet_slice_roundtrip():
    frames = [Image.new("RGBA", (8, 8), (i * 40, 0, 0, 255)) for i in range(5)]
    sh = sprite.sheet(frames, cols=3)
    assert sh.size == (24, 16)
    assert len(sprite.slice_sheet(sh, 8, 8)) == 5


@pytest.mark.parametrize("alpha", [1, 64, 128, 192, 254, 255])
@pytest.mark.parametrize("operation", ["fit", "sheet", "squash"])
def test_sprite_placement_preserves_rgba(alpha, operation):
    # Placing a frame on a transparent canvas must not apply its alpha twice.
    im = Image.new("RGBA", (8, 8), (200, 100, 50, alpha))
    if operation == "fit":
        out = sprite.fit(im, 8, 8)
    elif operation == "sheet":
        out = sprite.slice_sheet(sprite.sheet([im]), 8, 8)[0]
    else:
        out = sprite.simple_frames(im, n=1, kind="squash")[0]
    assert out.tobytes() == im.tobytes()


def test_team_mask():
    im = Image.new("RGBA", (4, 1), (0, 0, 0, 255))
    im.putpixel((0, 0), (20, 60, 240, 255))            # saturated blue -> player colour
    im.putpixel((1, 0), (200, 200, 200, 255))          # grey stays
    rgb, mask = sprite.team_mask(im)
    assert mask.getpixel((0, 0)) > 200 and mask.getpixel((1, 0)) == 0


def test_seamless_edges_match():
    import numpy as np
    ramp = np.tile(np.linspace(0, 255, 64)[None, :, None], (64, 1, 4)).astype(np.uint8)   # huge seam at the wrap
    ramp[..., 3] = 255
    out = np.asarray(sprite.seamless(Image.fromarray(ramp))).astype(int)
    before = np.abs(ramp[:, 0, :3].astype(int) - ramp[:, -1, :3].astype(int)).mean()
    after = np.abs(out[:, 0, :3] - out[:, -1, :3]).mean()
    assert before > 200 and after < 12


# --------------------------------------------------------------------------- fal (offline parts)

def test_kv_and_urls(tmp_path):
    assert fal._kv(["prompt=a cat", "num_images:=2", "flag:=true"]) == {"prompt": "a cat", "num_images": 2, "flag": True}
    res = {"images": [{"url": "https://v3.fal.media/a.png", "content_type": "image/png"}, {"url": "https://v3.fal.media/b.png"}],
           "mask_image": {"url": "https://v3.fal.media/m.png"}}
    assert [u for _, u, _ in fal._urls_in(res)] == ["https://v3.fal.media/a.png", "https://v3.fal.media/b.png", "https://v3.fal.media/m.png"]


# --------------------------------------------------------------------------- publish

def test_publish_check(tmp_path, capsys):
    # fixtures assembled at runtime so this file doesn't trip the toolkit's own publish check
    fake_key = "FAL" + "_KEY=" + "abcdefghijklmnopqrstuvwxyz0123"
    ghidra_name = "FUN" + "_00401000"
    make(tmp_path / "mod", {"src/Mod.cs": f"int {ghidra_name}();\n// " + "Decompiled with ILSpy", "README.md": "My mod, built with dnSpy notes",
                            "config.txt": fake_key})
    make(tmp_path / "game", {"data/big.bin": b"x" * 4096})
    (tmp_path / "mod" / "copied.bin").write_bytes(b"x" * 4096)
    assert publish.check(str(tmp_path / "mod"), str(tmp_path / "game")) == 1
    out = capsys.readouterr().out
    assert "game file copied verbatim" in out and "FAL_KEY assignment" in out and "Ghidra auto-name" in out
    normalized = out.replace("\\", "/")
    assert "decompiler header x1 in src/Mod.cs" in normalized and "README.md" not in normalized.split("decompiler header")[-1].split("\n")[0]


@pytest.mark.parametrize("label,key", [
    # assembled at runtime so this file doesn't trip the toolkit's own publish check
    ("OpenAI key", "sk-" + "proj-" + "Ab3_dE-f" + "Gh1jK2lM3nO4pQ5rS6tU7vW8xY9z0" * 4),
    ("OpenAI key", "sk-" + "svcacct-" + "Ab3_dE-f" + "Gh1jK2lM3nO4pQ5rS6tU7vW8xY9z0" * 4),
    ("OpenAI key", "sk-" + "Gh1jK2lM3nO4pQ5rS6tU7vW8xY9z0" * 2),
    ("GitHub token", "github" + "_pat_" + "11ABCDEFG0123456789abc" + "_" + "aB3dE5fG7hJ9kL1mN3pQ5rS7tU9vW1xY3zA5bC7dE9fG1hJ3kL5mN7pQ9rS1t"),
    ("GitHub token", "gh" + "p_" + "aB3dE5fG7hJ9kL1mN3pQ5rS7tU9vW1xY3z"),
])
def test_secret_patterns_catch_current_key_formats(label, key):
    rx = dict(publish.SECRET_PATTERNS)[label]
    assert rx.search(f"key = {key}\n"), key


def test_secret_patterns_ignore_ordinary_text():
    text = "sk-learn-style-kebab-case-identifiers-are-not-keys and github_pat_ alone"
    assert not [label for label, rx in publish.SECRET_PATTERNS if rx.search(text)]


# --------------------------------------------------------------------------- video

@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="needs ffmpeg")
def test_compile_small_edl(tmp_path):
    for i, color in enumerate(["red", "blue"]):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=s=640x360:d=3:r=30", "-f", "lavfi", "-i", "sine=f=440:d=3",
                        "-shortest", str(tmp_path / f"c{i}.mp4")], check=True)
    edl = {"size": [640, 360], "fps": 30, "bpm": 120, "beat_lock": True, "transition": {"type": "cut"},
           "segments": [{"clip": "c0.mp4", "in": 0, "beats": 4, "hook": "Hello"},
                        {"clip": "c1.mp4", "in": 0.5, "beats": 4, "title": "A title", "credit": "@someone", "transition": {"type": "fade", "duration": 0.3}},
                        {"card": {"title": "The end"}, "dur": 1.5}]}
    (tmp_path / "edl.json").write_text(json.dumps(edl))
    video.compile_edl(tmp_path / "edl.json", str(tmp_path / "out.mp4"))
    info = video.probe(tmp_path / "out.mp4")
    assert abs(info["duration"] - (2 + 2 + 1.5)) < 0.15 and info["audio"]


# --------------------------------------------------------------------------- knowledge base

from um import kb  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def test_repo_knowledge_is_valid():
    root = REPO / "knowledge"
    for p, _, _ in kb.notes(root):
        fails, _ = kb.check_note(p, root)
        assert not fails, (p, fails)
    idx, rows = kb.build_index(root)
    assert (root / "INDEX.md").read_text(encoding="utf-8") == idx, "run `um kb index`"
    assert len(rows) >= 7


def test_kb_new_check_search(tmp_path):
    import shutil
    root = tmp_path / "knowledge"
    root.mkdir()
    shutil.copy(REPO / "knowledge" / "TEMPLATE.md", root / "TEMPLATE.md")
    p = kb.new_note(root, "Hades II", "A new boon god", agent="Codex (gpt-6)", route="loader-api")
    fails, _ = kb.check_note(p, root)
    assert any("unfilled template text" in f for f in fails)          # a fresh scaffold must not pass
    good = p.read_text(encoding="utf-8")
    good = good.replace("FILL IN: exact build", "1.0.1 (Steam)").replace("anti_cheat: FILL IN", "anti_cheat: none")
    good = good.replace("> Two to four sentences: what you built", "> Added a boon god via a Lua mod loader")
    good = good.replace("The most valuable section. Numbered; each one symptom → cause → fix.", "")
    good = good.replace("1. **Symptom.** What you saw. **Cause:** what it really was. **Fix:** what worked.",
                        "1. **Boons never offered.** **Cause:** pool cached at load. **Fix:** register before the run starts.")
    p.write_text(good, encoding="utf-8")
    fails, _ = kb.check_note(p, root)
    assert not fails, fails
    res = kb.search(root, ["boon"])
    assert res and res[0]["path"].endswith("a-new-boon-god.md")
    assert kb.search(root, ["boon"], route="native-hook") == []


def test_kb_check_rejects_secrets_and_dumps(tmp_path):
    note = tmp_path / "n.md"
    code = "\n".join(f"int x{i} = {i};" for i in range(160))
    note.write_text("---\nkind: technique\ntitle: t\ntags: [x]\ndate: 2026-09-30\nagents: [a]\n---\n# t\n"
                    f"```c\n{code}\n```\n" + "FAL" + "_KEY=abcdefghijklmnopqrstuvwxyz0123\n")
    fails, _ = kb.check_note(note)
    assert any("code block" in f for f in fails) and any("FAL_KEY" in f for f in fails)


@pytest.mark.parametrize("url", ["https://github.com/alice/universal-modder.git", "https://github.com/alice/universal-modder",
                                 "git@github.com:alice/universal-modder.git", "ssh://git@github.com/alice/universal-modder.git"])
def test_pr_head_from_fork(url):
    # gh looks a bare --head branch up in the base repo; a PR from a fork needs "<owner>:<branch>"
    assert kb.pr_head("kb/a-b", url) == "alice:kb/a-b"


def test_pr_head_same_repo():
    assert kb.pr_head("kb/a-b", None) == "kb/a-b"


# --------------------------------------------------------------------------- backup

def test_backup_handles_pre_1980_timestamps(tmp_path, monkeypatch):
    import os
    monkeypatch.setattr(backup, "_root", lambda name: (tmp_path / "snaps" / name).mkdir(parents=True, exist_ok=True)
                        or tmp_path / "snaps" / name)
    src = tmp_path / "src"
    make(src, {"old.txt": "from 1970", "new.txt": "fresh"})
    os.utime(src / "old.txt", (0, 0))
    zp = backup.create(str(src), name="t")
    assert set(backup._manifest(zp)["files"]) == {"old.txt", "new.txt"}


def test_backup_diff_and_restore_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(backup, "_root", lambda name: (tmp_path / "snaps" / name).mkdir(parents=True, exist_ok=True)
                        or tmp_path / "snaps" / name)
    src = tmp_path / "src"
    make(src, {"save.dat": "v1", "sub/cfg.ini": "a=1"})
    backup.create(str(src), name="t")
    (src / "save.dat").write_text("v2")
    (src / "sub" / "cfg.ini").unlink()
    make(src, {"extra.log": "new"})
    d = backup.diff("t", str(src))
    assert (d["changed"], d["removed"], d["added"]) == (["save.dat"], ["sub/cfg.ini"], ["extra.log"])
    with pytest.raises(SystemExit):  # no --yes: report only, touch nothing
        backup.restore("t", str(src))
    assert (src / "save.dat").read_text() == "v2"
    backup.restore("t", str(src), clean=True, yes=True)
    assert (src / "save.dat").read_text() == "v1"
    assert (src / "sub" / "cfg.ini").read_text() == "a=1"
    assert not (src / "extra.log").exists()
    assert backup.snapshots("t-pre-restore")  # the state before the restore was kept


# --------------------------------------------------------------------------- comfy

from um import comfy  # noqa: E402


@pytest.fixture
def fake_comfy():
    """A stand-in for ComfyUI's HTTP API: /system_stats, /models, /object_info, /prompt, /history, /view."""
    import io
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from urllib.parse import parse_qs, urlparse

    state = {"prompts": [], "polls": 0, "models_route": True}
    png = io.BytesIO()
    im = Image.new("RGBA", (16, 16), (255, 255, 255, 255))      # a red square on a white background
    im.paste((200, 30, 30, 255), (4, 4, 12, 12))
    im.save(png, "PNG")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, body: bytes, code=200, ctype="application/json"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            u = urlparse(self.path)
            if u.path == "/system_stats":
                self._send(json.dumps({"system": {"comfyui_version": "0.9.0", "pytorch_version": "2.9.0"},
                                       "devices": [{"name": "fake", "type": "cpu"}]}).encode())
            elif u.path == "/models/checkpoints" and state["models_route"]:
                self._send(json.dumps(["sd15.safetensors", "sdxl_base.safetensors"]).encode())
            elif u.path == "/object_info/CheckpointLoaderSimple":
                spec = ["COMBO", {"options": ["v3.safetensors"]}]
                self._send(json.dumps({"CheckpointLoaderSimple": {"input": {"required": {"ckpt_name": spec}}}}).encode())
            elif u.path == "/history/p1":
                state["polls"] += 1                                  # the first poll finds it still running
                done = {"p1": {"status": {"status_str": "success", "completed": True},
                               "outputs": {"9": {"images": [{"filename": "um_00001_.png", "subfolder": "", "type": "output"}]}}}}
                self._send(json.dumps(done if state["polls"] > 1 else {}).encode())
            elif u.path == "/view" and parse_qs(u.query).get("filename") == ["um_00001_.png"]:
                self._send(png.getvalue(), ctype="image/png")
            else:
                self._send(b"404: Not Found", 404, "text/plain")

        def do_POST(self):
            wf = json.loads(self.rfile.read(int(self.headers["Content-Length"])))["prompt"]
            state["prompts"].append(wf)
            if wf.get("4", {}).get("inputs", {}).get("ckpt_name") == "missing.safetensors":
                err = {"error": {"message": "Prompt outputs failed validation", "details": ""},
                       "node_errors": {"4": {"class_type": "CheckpointLoaderSimple", "errors": [
                           {"message": "Value not in list", "details": "ckpt_name: 'missing.safetensors' not in [...]"}]}}}
                self._send(json.dumps(err).encode(), 400)
            else:
                self._send(json.dumps({"prompt_id": "p1", "number": 0, "node_errors": {}}).encode())

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    state["url"] = f"http://127.0.0.1:{srv.server_address[1]}"
    yield state
    srv.shutdown()


def test_comfy_image_sprite(fake_comfy, tmp_path, monkeypatch):
    from um import cli
    monkeypatch.setattr(comfy.time, "sleep", lambda s: None)
    out = tmp_path / "gen"
    cli.main(["comfy", "image", "a red potion", "--url", fake_comfy["url"], "--out", str(out), "--seed", "7", "--sprite"])
    wf = fake_comfy["prompts"][-1]
    assert wf["4"]["inputs"]["ckpt_name"] == "sd15.safetensors"               # the first checkpoint listed
    assert (wf["5"]["inputs"]["width"], wf["3"]["inputs"]["seed"]) == (512, 7)  # SD 1.5 size, the given seed
    assert "plain flat white background" in wf["6"]["inputs"]["text"]
    assert Image.open(out / "a_red_potion.png").size == (16, 16)
    cut = Image.open(out / "a_red_potion_cut.png")                           # cut out and trimmed locally
    assert cut.size == (8, 8) and cut.getpixel((0, 0)) == (200, 30, 30, 255)
    rec = json.loads((out / "comfy_manifest.jsonl").read_text().splitlines()[-1])
    assert rec["prompt_id"] == "p1" and rec["seed"] == 7 and rec["workflow"]["9"]["class_type"] == "SaveImage"


def test_comfy_run_set_and_errors(fake_comfy, tmp_path, monkeypatch):
    monkeypatch.setattr(comfy.time, "sleep", lambda s: None)
    wf = comfy.txt2img("x", "sd15.safetensors")
    wf["6"]["_meta"] = {"title": "Positive"}
    (tmp_path / "wf.json").write_text(json.dumps(wf))
    wf = comfy.apply_set(comfy.load_workflow(tmp_path / "wf.json"), ["Positive.text=a v1.5 sword=sharp", "3.seed:=42"])
    assert (wf["6"]["inputs"]["text"], wf["3"]["inputs"]["seed"]) == ("a v1.5 sword=sharp", 42)
    assert [Path(f).name for f in comfy.generate(fake_comfy["url"], wf, tmp_path / "o", "sword")] == ["sword.png"]
    (tmp_path / "ui.json").write_text(json.dumps({"nodes": [], "links": []}))
    with pytest.raises(SystemExit):
        comfy.load_workflow(tmp_path / "ui.json")                            # UI format: needs Export (API)
    with pytest.raises(SystemExit):
        comfy.queue(fake_comfy["url"], comfy.txt2img("x", "missing.safetensors"))   # validation error reported
    fake_comfy["models_route"] = False
    assert comfy.checkpoints(fake_comfy["url"]) == ["v3.safetensors"]        # older servers: /object_info
    assert comfy.status(fake_comfy["url"])["version"] == "0.9.0"


def test_skill_copies_match():
    # .agents/skills and .claude/skills are real copies of skills/ (Windows clones turn symlinks into text files)
    root = Path(__file__).resolve().parents[1]
    def tree(d):
        return {p.relative_to(d).as_posix(): p.read_bytes() for p in sorted(d.rglob("*")) if p.is_file()}
    src = tree(root / "skills")
    for copy in (".agents/skills", ".claude/skills"):
        assert not (root / copy).is_symlink(), f"{copy} must be a folder, not a symlink"
        assert tree(root / copy) == src, (f"{copy} differs from skills/: rm -rf .agents/skills .claude/skills && "
                                          "cp -r skills .agents/skills && cp -r skills .claude/skills")
    assert not any((root / d).exists() for d in (".gemini/skills", ".github/skills")), "agents read .agents/skills"



# --------------------------------------------------------------------------- remake (no Godot needed)

from um import remake  # noqa: E402


def _remake_tree(root: Path, files: dict):
    make(root, files)
    return root


def test_remake_revision_ignores_derived_files_and_tracks_content(tmp_path):
    root = _remake_tree(tmp_path / "p", {"project.godot": "config_version=5\n", "a.gd": "xy", "b.gd": "z"})
    rev = remake.revision(root)
    assert len(rev) == 12
    make(root, {".godot/imported/x.ctex": b"\1", ".gd_remake/results.json": "{}", "exports/web/index.html": "<html>",
                "SPEC.md": "# spec", "icon.png.import": "[remap]", "a.gd.uid": "uid://abc"})
    assert remake.revision(root) == rev
    make(root, {"a.gd": "x", "b.gd": "yz"})            # same bytes in total, moved across a file boundary
    assert remake.revision(root) != rev
    make(root, {"a.gd": "xy", "b.gd": "z"})
    assert remake.revision(root) == rev
    (root / "b.gd").rename(root / "c.gd")             # same bytes under another path
    assert remake.revision(root) != rev


def _acc(checks):
    return {"game": "demo", "boot_frames": 10, "checks": checks}


def _res(rev, status="pass", msg=""):
    return {"revision": rev, "status": status, "messages": [msg] if msg else [], "cases": []}


def test_remake_status_keeps_the_four_facts_apart(tmp_path):
    root = _remake_tree(tmp_path / "p", {"project.godot": "", "tests/scenarios/jump.gd": "", "tests/scenarios/run.gd": "",
                                          "tests/scenarios/hit.gd": "", "tests/scenarios/extra.gd": ""})
    acc = _acc([
        {"id": "jump", "slice": "movement", "scenario": "res://tests/scenarios/jump.gd"},
        {"id": "run", "slice": "movement", "scenario": "res://tests/scenarios/run.gd"},
        {"id": "feel", "slice": "movement", "scenario": None, "claim": "feels like the original"},
        {"id": "extra", "slice": "movement", "scenario": "res://tests/scenarios/extra.gd", "required": False},
        {"id": "hit", "slice": "combat", "scenario": "res://tests/scenarios/hit.gd"},
    ])
    acc = {**acc, "checks": [{**c, "required": c.get("required", True)} for c in acc["checks"]]}
    cur, old = "aaaaaaaaaaaa", "bbbbbbbbbbbb"
    results = {"jump": _res(cur), "run": _res(cur), "extra": _res(cur, "fail", "x"), "hit": _res(old), "boot": _res(cur)}
    plays = [{"revision": old, "capture": "c.mp4"}]
    st = remake.compute_status(root, acc, results, plays, cur)
    s = {r["slice"]: r for r in st["slices"]}
    assert s["movement"]["checks_pass"]["state"] == "yes"          # failing optional check does not block
    assert s["movement"]["manual"] == ["feel"] and s["movement"]["implemented"]["state"] == "yes"
    assert s["combat"]["checks_pass"]["state"] == "stale"          # old pass is not a pass
    assert st["integrated"]["state"] == "yes" and st["played"]["state"] == "stale"
    assert not st["done"] and "NOT done" in remake.format_status(st)

    results["hit"] = _res(cur)
    st = remake.compute_status(root, acc, results, plays, cur)
    assert st["done"] and st["played"]["state"] == "stale"          # done never implies played
    assert "overall: done" in remake.format_status(st)

    results["boot"] = _res(cur, "error", "SCRIPT ERROR: boom")
    st = remake.compute_status(root, acc, results, plays + [{"revision": cur, "capture": "d.mp4"}], cur)
    assert not st["done"] and st["integrated"]["state"] == "no" and st["played"]["state"] == "yes"

    results["boot"], results["hit"] = _res(cur), _res(cur, "fail", "hp 90 != 80")
    (root / "tests/scenarios/run.gd").unlink()
    st = remake.compute_status(root, acc, results, plays, cur)
    s = {r["slice"]: r for r in st["slices"]}
    assert s["movement"]["implemented"]["state"] == "no" and s["movement"]["checks_pass"]["state"] == "no"
    assert {"id": "hit", "reason": "hp 90 != 80"} in s["combat"]["checks_pass"]["blocking"] and not st["done"]


RUNNER_LOG = """Godot Engine v4.7.stable.official - https://godotengine.org
GDR_BEGIN res://tests/scenarios/a.gd|load
GDR_END res://tests/scenarios/a.gd|load pass
GDR_BEGIN res://tests/scenarios/a.gd|default
GDR_END res://tests/scenarios/a.gd|default pass
GDR_BEGIN res://tests/scenarios/b.gd|walk left
SCRIPT ERROR: Invalid access to property or key 'hp' on a base object of type 'Nil'.
          at: run (res://tests/scenarios/b.gd:12)
GDR_END res://tests/scenarios/b.gd|walk left pass
GDR_BEGIN res://tests/scenarios/b.gd|walk right
GDR_END res://tests/scenarios/b.gd|walk right fail
ERROR: Condition "!is_inside_tree()" is true.
   at: get_global_transform (scene/2d/node_2d.cpp:416)
GDR_BEGIN res://tests/scenarios/c.gd|default
"""


def test_remake_runner_errors_are_attributed_to_the_case_in_progress():
    data = {"results": [
        {"scenario": "res://tests/scenarios/a.gd", "case": "default", "status": "pass", "message": "", "failures": []},
        {"scenario": "res://tests/scenarios/b.gd", "case": "walk left", "status": "pass", "message": "", "failures": []},
        {"scenario": "res://tests/scenarios/b.gd", "case": "walk right", "status": "fail", "message": "x 3 != 4",
         "failures": ["x 3 != 4"]},
    ]}
    scen = ["res://tests/scenarios/a.gd", "res://tests/scenarios/b.gd", "res://tests/scenarios/c.gd", "res://tests/scenarios/d.gd"]
    by, loose = remake.merge_cases(scen, data, RUNNER_LOG, 1)
    a, b, c, d = (by[s] for s in scen)
    assert [(x["case"], x["status"]) for x in a] == [("default", "pass")]           # load step is no case
    left = next(x for x in b if x["case"] == "walk left")
    assert left["status"] == "error" and left["message"].startswith("SCRIPT ERROR: Invalid access") and "b.gd:12" in left["message"]
    assert next(x for x in b if x["case"] == "walk right")["status"] == "fail"
    assert c[0]["status"] == "error" and "during this case" in c[0]["message"]      # began, crashed, never reported
    assert d[0]["status"] == "error"                                                 # never ran at all
    assert loose and loose[0].startswith('ERROR: Condition "!is_inside_tree()"')     # between cases: not pinned on one
    assert remake.aggregate(b) == "error" and remake.aggregate(a) == "pass"


def test_remake_variants_promote(tmp_path):
    root = _remake_tree(tmp_path / "p", {
        "project.godot": "", "variants/hero/v1.png": b"one", "variants/hero/v2.png": b"two",
        "variants/hero/v2.png.import": "[remap]", "variants/sword/a.png": b"s",
        "assets/hero.webp": b"old", "assets/hero.webp.import": "[remap]", "assets/heron.png": b"keep",
        "ASSETS.md": "# Assets\n- hero: generated", "assets.json": json.dumps([
            {"path": "variants/hero/v2.png", "brief": "hero", "ref": "chars/hero.png", "generator": "fal-ai/x"},
            {"path": "res://variants/hero/v1.png", "brief": "hero"},
            {"path": "assets/hero.webp", "brief": "hero (old)"},
            {"path": "assets/heron.png", "brief": "bird"}])})
    out = remake.promote(root, "hero", "v2")
    assert (root / "assets/hero.png").read_bytes() == b"two"
    assert not (root / "assets/hero.webp").exists() and not (root / "assets/hero.webp.import").exists()
    assert (root / "assets/heron.png").exists() and (root / "variants/sword/a.png").exists()
    assert not (root / "variants/hero").exists()
    entries = json.loads((root / "assets.json").read_text())
    assert [(e["path"], e["brief"]) for e in entries] == [("assets/hero.png", "hero"), ("assets/heron.png", "bird")]
    assert entries[0]["ref"] == "chars/hero.png"
    assert (root / "ASSETS.md").read_text().splitlines()[-1] == "promoted hero: v2"
    assert out["replaced"] == ["assets/hero.webp"]
    with pytest.raises(SystemExit):
        remake.promote(root, "sword", "nope")


def test_remake_measure_image(tmp_path):
    im = Image.new("RGBA", (40, 30), (0, 0, 0, 0))
    im.paste((255, 0, 0, 255), (5, 4, 15, 10))      # 10x6 red
    im.paste((0, 0, 255, 255), (15, 4, 20, 10))     # 5x6 blue
    im.save(tmp_path / "s.png")
    m = remake.image_metrics(tmp_path / "s.png")
    assert (m["w"], m["h"], m["has_alpha"], m["bbox_w"], m["bbox_h"]) == (40, 30, True, 15, 6)
    pal = {p["hex"]: p["share"] for p in m["palette"]}
    assert pal == pytest.approx({"#ff0000": 2 / 3, "#0000ff": 1 / 3}, abs=0.01)
    assert m["mean_luminance"] == pytest.approx((2 * 0.2126 + 0.0722) / 3, abs=0.01)


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="needs ffmpeg")
def test_remake_measure_audio(tmp_path):
    import math
    import wave
    rate, n = 22050, int(22050 * 1.5)
    with wave.open(str(tmp_path / "beep.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h", int(16384 * math.sin(2 * math.pi * 440 * i / rate))) for i in range(n)))
    k, m = remake.measure_file(tmp_path / "beep.wav")
    assert k == "audio" and "error" not in m, m
    assert m["duration_s"] == pytest.approx(1.5, abs=0.01) and (m["sample_rate"], m["channels"]) == (22050, 1)
    assert m["peak_dbfs"] == pytest.approx(-6.0, abs=0.3)          # half scale
    assert -12 < m["loudness_lufs"] < -6


def _gltf():
    return {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [0]}],
            "nodes": [{"name": "root", "scale": [2, 2, 2], "translation": [0, 1, 0], "children": [1]},
                      {"name": "body", "mesh": 0, "translation": [1, 0, 0], "skin": 0}, {"name": "j0"}, {"name": "j1"}],
            "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1}, {"attributes": {"POSITION": 0}}]}],
            "skins": [{"joints": [2, 3]}],
            "accessors": [{"count": 24, "type": "VEC3", "componentType": 5126, "min": [-1, 0, -0.5], "max": [1, 2, 0.5]},
                          {"count": 36, "type": "SCALAR", "componentType": 5123},
                          {"count": 3, "type": "SCALAR", "componentType": 5126, "min": [0], "max": [1.25]}],
            "animations": [{"name": "walk", "samplers": [{"input": 2, "output": 0}], "channels": []}, {"samplers": []}]}


def test_remake_measure_gltf_and_glb(tmp_path):
    g = _gltf()
    (tmp_path / "m.gltf").write_text(json.dumps(g))
    body = json.dumps(g).encode()
    body += b" " * (-len(body) % 4)
    (tmp_path / "m.glb").write_bytes(b"glTF" + struct.pack("<II", 2, 20 + len(body)) + struct.pack("<I", len(body)) + b"JSON" + body)
    for name in ("m.gltf", "m.glb"):
        k, m = remake.measure_file(tmp_path / name)
        assert k == "model" and "error" not in m, m
        assert (m["primitives"], m["tris"], m["vertices"], m["joints"]) == (2, 12 + 8, 48, 2)
        assert m["size"] == pytest.approx([4, 4, 2])                 # parent scale 2 applies to the child mesh
        assert m["bounds"]["min"] == pytest.approx([0, 1, -1])         # (-1 + 1) * 2 + 0, 0 * 2 + 1, -0.5 * 2
        assert m["animations"] == [{"name": "walk", "duration_s": 1.25}, {"name": "animation_1", "duration_s": None}]


def _noise_pattern(seed, size=32):
    import random
    rnd = random.Random(seed)
    im = Image.new("RGB", (8, 8))
    im.putdata([(rnd.randrange(256),) * 3 for _ in range(64)])
    return im.resize((size, size), Image.Resampling.BILINEAR)


def test_remake_leak_scan_hits(tmp_path):
    dirty, rem = tmp_path / "dirty", tmp_path / "remake"
    blob = bytes(range(256)) * 2
    decompiled = """
    /* WARNING: Removing unreachable block (ram,0x00401a2c) */
    void FUN_00401000(int param_1)
    {
      int iVar1;
      iVar1 = param_1 * 0x14 + DAT_00403000;
      if (iVar1 > 100) { player_health = player_health - iVar1; uVar2 = spawn_particles("blood_splat", iVar1 / 4); }
      local_8 = boss_rage_timer * 0.25 + param_1; FUN_00401200(local_8, iVar1);
    }
    """
    make(dirty, {"raw/blob.bin": blob, "decomp/combat.c": decompiled})
    _noise_pattern(1).save(dirty / "raw" / "tex.png")
    copied = """
    // damage, reworked from my notes (every 12-token window touches a decompiler name or 0x14)
    void apply_damage(int param_2) {
      int local_c;
      local_c = param_2 * 20 + DAT_00499999;   // base
      if (local_c > 100) { player_health = player_health - local_c; uVar7 = spawn_particles("blood_splat", local_c / 4); }
      local_10 = boss_rage_timer * 0.25 + param_2; FUN_00409999(local_10, local_c);
    }
    """
    make(rem, {"project.godot": "", "data/blob.dat": blob, "src/Combat.cs": copied,
               "scenes/x.tscn": f'[ext_resource path="{(dirty / "raw" / "tex.png").as_posix()}"]',
               "addons/gd_remake/copy.bin": blob})              # the toolkit's own addon is not scanned
    import numpy as np                                      # upscaled, re-noised, resampled copy
    near = np.asarray(_noise_pattern(1).resize((96, 96), Image.Resampling.NEAREST), dtype=np.int16)
    near = near + np.random.default_rng(0).integers(-12, 13, near.shape)
    Image.fromarray(near.clip(0, 255).astype(np.uint8)).resize((80, 80), Image.Resampling.BICUBIC).save(rem / "tex_big.png")
    _noise_pattern(2).save(rem / "other.png")
    hits = remake.leak_scan(rem, dirty)["hits"]
    got = {(h["kind"], h["remake"], h["dirty"]) for h in hits}
    assert ("identical", "data/blob.dat", "raw/blob.bin") in got
    assert ("near-duplicate", "tex_big.png", "raw/tex.png") in got
    assert ("code", "src/Combat.cs", "decomp/combat.c") in got
    assert any(k == "path" and r == "scenes/x.tscn" for k, r, _ in got)
    assert not any(r.startswith("addons/") or r == "other.png" for _, r, _ in got)
    assert (dirty / ".leak_cache.json").exists()


def test_remake_leak_scan_clean_remake_has_no_hits(tmp_path):
    dirty, rem = tmp_path / "dirty", tmp_path / "remake"
    make(dirty, {"decomp/player.c": """
    void FUN_00402000(int param_1) { if (param_1 > 0) { DAT_00405000 = DAT_00405000 + param_1; } return; }
    """, "raw/flat.png": b""})
    Image.new("RGB", (16, 16), (40, 40, 40)).save(dirty / "raw" / "flat.png")
    _noise_pattern(3).save(dirty / "raw" / "t.png")
    make(rem, {"project.godot": "", "player.gd": """
extends CharacterBody2D
# original movement code
@export var speed := 220.0
func _physics_process(delta: float) -> void:
    if Input.is_action_pressed("jump") and is_on_floor():
        velocity.y = -speed * 1.6
    velocity.x = Input.get_axis("left", "right") * speed
    move_and_slide()
"""})
    Image.new("RGB", (32, 32), (200, 200, 200)).save(rem / "flat_light.png")   # flat images have no structure to match
    box = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    box.paste((220, 40, 40, 255), (8, 8, 56, 60))
    box.save(dirty / "raw" / "hero.png")
    box = Image.new("RGBA", (64, 80), (0, 0, 0, 0))     # a redrawn sprite may share the silhouette
    box.paste((200, 60, 50, 255), (10, 10, 54, 70))
    box.save(rem / "hero.png")
    _noise_pattern(4, 64).save(rem / "t.png")
    assert remake.leak_scan(rem, dirty)["hits"] == []


def test_remake_init_is_idempotent_and_keeps_user_files(tmp_path):
    root = tmp_path / "demo"
    make(root, {"project.godot": 'config_version=5\n\n[application]\n\nconfig/name="Mine"\nrun/main_scene="res://game.tscn"\n\n'
                                 '[autoload]\n\nVariants="*res://my/variants.gd"\n',
                "acceptance.json": '{"checks": [{"id": "x"}]}'})
    remake.init_project(root, "demo")
    pg = (root / "project.godot").read_text()
    assert 'GdBridge="*res://addons/gd_remake/bridge.gd"' in pg and 'Variants="*res://my/variants.gd"' in pg
    assert pg.count("Variants=") == 1 and 'run/main_scene="res://game.tscn"' in pg and not (root / "main.tscn").exists()
    assert json.loads((root / "acceptance.json").read_text()) == {"checks": [{"id": "x"}]}
    assert json.loads((root / "assets.json").read_text()) == []
    preset = (root / "export_presets.cfg").read_text()
    assert 'name="Web"' in preset and 'export_path="exports/web/index.html"' in preset and "variant/thread_support=false" in preset
    addon = sorted(p.relative_to(remake.ADDON_SRC).as_posix() for p in remake.ADDON_SRC.rglob("*") if p.is_file())
    assert addon and all((root / "addons/gd_remake" / a).is_file() for a in addon)
    (root / "addons/gd_remake" / addon[0]).write_text("stale")
    (root / "addons/gd_remake/gone.gd").write_text("old file")
    before = {p: p.read_bytes() for p in (root / "project.godot", root / "export_presets.cfg", root / ".gitignore")}
    remake.init_project(root, "demo")
    assert (root / "addons/gd_remake" / addon[0]).read_bytes() == (remake.ADDON_SRC / addon[0]).read_bytes()
    assert not (root / "addons/gd_remake/gone.gd").exists()
    assert {p: p.read_bytes() for p in before} == before
    assert (root / ".gitignore").read_text().splitlines() == [".godot/", ".gd_remake/", "exports/"]
    fresh = tmp_path / "fresh"
    remake.init_project(fresh)
    assert 'run/main_scene="res://main.tscn"' in (fresh / "project.godot").read_text() and (fresh / "main.tscn").exists()


def test_remake_compare_flags_and_refuses_report_in_remake(tmp_path, capsys):
    dirty, rem = tmp_path / "dirty", tmp_path / "remake"
    dirty.mkdir()
    Image.new("RGBA", (32, 32), (200, 10, 10, 255)).save(dirty / "hero.png")
    remake._write_json(dirty / "manifest.json", remake.measure_paths([dirty]))
    make(rem, {"assets.json": json.dumps([{"path": "assets/hero.png", "brief": "hero", "ref": "hero.png"},
                                          {"path": "assets/tree.png", "brief": "tree", "ref": "nope.png"}])})
    (rem / "assets").mkdir()
    Image.new("RGBA", (32, 48), (200, 10, 10, 255)).save(rem / "assets/hero.png")
    rows = {r["brief"]: r for r in remake.compare_assets(rem, dirty, 0.10)}
    flagged = {x["key"] for x in rows["hero"]["rows"] if x["flag"]}
    assert flagged == {"h", "aspect", "bbox_h"}
    assert "clean file missing" in rows["tree"]["problems"] and any("not in dirty manifest" in p for p in rows["tree"]["problems"])
    from um import cli
    with pytest.raises(SystemExit):
        cli.main(["remake", "compare", "demo", "--dirty", str(dirty), "--remake", str(rem), "--out", str(rem / "c.html")])
    cli.main(["remake", "compare", "demo", "--dirty", str(dirty), "--remake", str(rem)])
    page = (dirty / "compare" / "index.html").read_text(encoding="utf-8")
    assert "../hero.png" in page and "#c80a0a" in page
    assert "FLAG hero" in capsys.readouterr().out


def test_remake_bridge_cli_exits_nonzero_on_error(capsys):
    import socket
    import threading
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen()
    port = srv.getsockname()[1]
    seen = []

    def serve():
        for _ in range(2):
            c, _ = srv.accept()
            req = json.loads(c.makefile().readline())
            seen.append(req)
            ok = req["cmd"] != "get"
            c.sendall((json.dumps({"id": req["id"], "ok": ok, "result": {"echo": req["args"]}} if ok else
                                  {"id": req["id"], "ok": False, "error": "no such node"}) + "\n").encode())
            c.close()

    threading.Thread(target=serve, daemon=True).start()
    from um import cli
    cli.main(["remake", "bridge", str(port), "set", "path=/root/Player", "prop=position", "value=[1, 2.5]", "pressed=true"])
    assert json.loads(capsys.readouterr().out) == {"echo": {"path": "/root/Player", "prop": "position", "value": [1, 2.5], "pressed": True}}
    with pytest.raises(SystemExit) as e:
        cli.main(["remake", "bridge", str(port), "get", '{"path": "/root/Nope", "prop": "x"}'])
    assert e.value.code != 0 and seen[1]["args"] == {"path": "/root/Nope", "prop": "x"}
    srv.close()
