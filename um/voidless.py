"""2D game art from Voidless (https://voidless.dev): sprites, 8-way turns, and animation sets that keep one size.

    um voidless key set                                      # hidden prompt; or set VOIDLESS_API_KEY
    um voidless credits                                      # plan and credits left
    um voidless sprite "a rusty scrap drone enemy" --facing right --name drone
    um voidless sprite "a red health potion" --type object --size 64 --style pixel-art
    um voidless rotate <asset_id>                            # one sprite -> 8 facings (10 credits)
    um voidless animate <asset_id> --preset combat           # a whole set in one call, one size across clips
    um voidless animate <asset_id> --prompt "walk: walks left; hit: recoils" --hold-facing
    um voidless presets                                      # named animation sets you can ask for
    um voidless asset <asset_id>                             # frames, image keys and download urls
    um voidless fetch <asset_id> --out assets/gen            # download every frame again, free

Voidless generates a character once and then works on that asset, so every later call shares its look: `rotate`
adds the eight facings, `animate` adds clips. The reason to reach for it over a one-shot image call is the set
rather than the single sprite -- clips come back scaled to one base size with the feet on the ground, which is
what a mod needs and what a per-image service leaves you to fix by hand. `--hold-facing` ends each clip on the
frame it began, so a directional loop does not drift; `--flip-facings` mirrors the left-side clips from the
right-side ones at half the price.

Voidless is a paid service: it needs an account, an API key (https://voidless.dev/api-docs) and credits.
An image costs 1 on the default model and up to 15 on the dearest (`--model` lists them), an 8-way rotation
10, and an animation set 100 a pass (200 at --quality ultra). `--type tileset` is always drawn by
gpt-image-2.5 at 5 credits whatever --model says, because it is the only model that generates the type.
`um voidless credits` shows what is left. The key
is read from VOIDLESS_API_KEY, else from where `um voidless key set` stored it (the desktop keyring on Linux, an
owner-only ~/.secrets/voidless-key elsewhere), else from VOIDLESS_API_KEY=... in a .env.
Files land in --out (default assets/gen), and each call appends a line to <out>/voidless_manifest.jsonl (asset
and frame ids, prompt, settings, files) so an asset can be traced back to the call that made it.
"""
from __future__ import annotations

import getpass
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from um.common import die

DEFAULT_URL = "https://api.voidless.dev"
DEFAULT_CDN = "https://cdn.voidless.dev"
TYPES = ["object", "character", "character portrait", "artwork", "tileset", "ui"]
# Credits per image: flux2-klein 1, flux-juggernaut 1, seedream-5-flash 2, gpt-image-2.5 5,
# retro-diffusion 10, nano-banana-2 15.
MODELS = ["flux2-klein", "gpt-image-2.5", "seedream-5-flash", "nano-banana-2", "retro-diffusion",
          "flux-juggernaut"]
TILESET_MODEL = "gpt-image-2.5"      # the server overrides --model for tilesets; see cmd_sprite
DIMENSIONS = ["2d", "top down", "isometric"]
SIZES = [32, 64, 128, 512, 1024]
FACINGS = ["forward", "right"]          # front view or side profile; side profiles rotate best
POSES = ["idle", "tpose"]
QUALITIES = ["high", "ultra"]                 # low/standard resolve but are not offered
BODY_TYPES = ["humanoid", "quadruped"]
_DEFAULT_KEY_FILE = "~/.secrets/voidless-key"
KEYRING_ATTRS = ["service", "voidless.dev", "key", "api"]
_KEY_CACHE: str | None = None


# --------------------------------------------------------------------------- key


def key_file() -> Path:
    return Path(os.environ.get("UM_VOIDLESS_KEY_FILE") or _DEFAULT_KEY_FILE).expanduser()


def _read_dotenv(p: Path) -> str | None:
    try:
        m = re.search(r"^\s*VOIDLESS_API_KEY\s*=\s*['\"]?([^'\"\s]+)", p.read_text(), re.M)
    except OSError:
        return None
    return m.group(1) if m else None


def keyring_available() -> bool:
    from um.fal import keyring_available
    return keyring_available()


def keyring_get() -> str | None:
    """The key in the desktop keyring (libsecret's secret-tool, the same route as `um fal key`), or None."""
    from um.fal import _secret_tool
    r = _secret_tool("lookup", *KEYRING_ATTRS)
    return (r.stdout.strip() or None) if r and r.returncode == 0 else None


def keyring_set(value: str) -> bool:
    from um.fal import _secret_tool
    r = _secret_tool("store", "--label", "Voidless API key (universal-modder)", *KEYRING_ATTRS, value=value)
    return bool(r and r.returncode == 0)


def keyring_clear() -> bool:
    from um.fal import _secret_tool
    r = _secret_tool("clear", *KEYRING_ATTRS)
    return bool(r and r.returncode == 0)


def _key_candidates():
    """(label, reader) in precedence order. Nothing is read until its reader is called, so a VOIDLESS_API_KEY in
    the environment never touches the keyring."""
    from um.fal import _read_file
    named, kf = os.environ.get("UM_VOIDLESS_KEY_FILE"), key_file()
    yield "VOIDLESS_API_KEY environment variable", lambda: (os.environ.get("VOIDLESS_API_KEY") or "").strip() or None
    if named:                                                 # a file named on purpose comes before the keyring
        yield f"key file {kf} (UM_VOIDLESS_KEY_FILE)", lambda: _read_file(kf)
    yield f"OS keyring ({' '.join(KEYRING_ATTRS)})", keyring_get
    if not named:
        yield f"key file {kf}", lambda: _read_file(kf)
    for p in dict.fromkeys((Path.cwd() / ".env", Path(__file__).resolve().parents[1] / ".env")):
        yield f".env {p}", lambda p=p: _read_dotenv(p)


def key_sources() -> list[tuple[str, str]]:
    """(label, key) for every source that has a key, in precedence order: the first one is used."""
    return [(label, k) for label, read in _key_candidates() if (k := read())]


def api_key() -> str:
    """The first key found, read once per run (a poll loop would otherwise ask the keyring every few seconds)."""
    global _KEY_CACHE
    if not _KEY_CACHE:
        _KEY_CACHE = next((k for _, read in _key_candidates() if (k := read())), None)
    if not _KEY_CACHE:
        die("no Voidless key. Create one at https://voidless.dev/api-docs, then `um voidless key set` "
            "(or set VOIDLESS_API_KEY)")
    return _KEY_CACHE


def cmd_key(a):
    from um.fal import file_mode, mask, write_key_file
    if a.action == "set":
        value = Path(a.from_file).expanduser().read_text().strip() if a.from_file else getpass.getpass("Voidless API key (hidden): ").strip()
        if not value:
            die("empty key, nothing stored")
        if not value.startswith("void_"):
            print("note: Voidless keys start with void_; storing it anyway", file=sys.stderr)
        if getattr(a, "file_only", False):
            print(f"stored in {write_key_file(value, key_file())} as {mask(value)} (plaintext, owner-only)")
        elif keyring_set(value) and keyring_get() == value:
            print(f"stored in the OS keyring as {mask(value)} ({' '.join(KEYRING_ATTRS)})")
        elif keyring_available():
            die("could not write to the OS keyring (is it unlocked?); "
                "`um voidless key set --file-only` stores the key in a plaintext file instead")
        else:
            print(f"no OS keyring (no secret-tool); stored in {write_key_file(value, key_file())} as {mask(value)} "
                  "(plaintext, owner-only)")
        if os.environ.get("VOIDLESS_API_KEY"):
            print("note: VOIDLESS_API_KEY is set in this environment and takes precedence over the stored key")
    elif a.action == "clear":
        removed = []
        if keyring_get() and keyring_clear():
            removed.append("OS keyring")
        kf = key_file()
        if kf.exists():
            kf.unlink()
            removed.append(str(kf))
        print("removed: " + ", ".join(removed) if removed else "nothing to remove")
    else:
        sources = key_sources()
        if not sources:
            print("no Voidless key configured; run `um voidless key set`")
        for i, (label, k) in enumerate(sources):
            print(f"{'active  ' if i == 0 else 'shadowed'}  {label}  ->  {mask(k)}")
        kf = key_file()
        print(f"keyring     {'available' if keyring_available() else 'not available (no secret-tool)'}")
        print(f"key file    {kf} {'exists (mode ' + file_mode(kf) + ')' if kf.exists() else 'absent'}")


# --------------------------------------------------------------------------- http


def base_url(url: str | None = None) -> str:
    return (url or os.environ.get("VOIDLESS_API_URL") or DEFAULT_URL).rstrip("/")


def cdn_url(key: str | None) -> str | None:
    """Stored keys are R2 paths (assets/<uid>/…). Drive refs have no public URL."""
    if not key or not isinstance(key, str) or key.startswith("gdrive:"):
        return None
    if re.match(r"^https?://", key):
        return key
    cdn = (os.environ.get("VOIDLESS_CDN_URL") or DEFAULT_CDN).rstrip("/")
    return f"{cdn}/{key.lstrip('/')}"


def _error(code: int, body: bytes) -> str:
    """Voidless errors are {error:{message}} or {message}: one readable line."""
    try:
        err = json.loads(body)
    except ValueError:
        return f"HTTP {code}: {body[:500].decode(errors='replace')}"
    msg = (err.get("error") or {}).get("message") if isinstance(err.get("error"), dict) else None
    return f"HTTP {code}: {msg or err.get('message') or err.get('error') or body[:200].decode(errors='replace')}"


def request(base: str, method: str, path: str, body: dict | None = None, retries: int = 3, timeout: float = 900):
    """JSON call to /api<path> with the API key.

    The timeout is deliberately long: generation answers when the image is finished, not when the request is
    accepted, so a short socket timeout would abandon work that has already been charged.
    """
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries + 1):
        req = urllib.request.Request(f"{base}/api{path}", data=data, method=method, headers={
            "x-api-key": api_key(), "Accept": "application/json",
            "User-Agent": "universal-modder", **({"Content-Type": "application/json"} if data is not None else {})})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                payload = r.read()
            return json.loads(payload) if payload else {}
        except ValueError:
            die(f"Voidless {method} {path} answered with something that isn't JSON")
        except urllib.error.HTTPError as e:
            line = _error(e.code, e.read())
            if attempt < retries and e.code in (429, 502, 503, 504):
                wait_s = 15.0 * (attempt + 1)
                print(f"um: {line}; retrying in {wait_s:.0f} s", file=sys.stderr)
                time.sleep(wait_s)
                continue
            die(f"Voidless {method} {path} -> {line}")
        except urllib.error.URLError as e:
            die(f"no Voidless API at {base} ({e.reason})")
        except OSError as e:                                  # a timeout or reset while reading the answer
            die(f"Voidless {method} {path} failed: {e or type(e).__name__}")


def download(url: str, path: Path) -> Path:
    req = urllib.request.Request(url, headers={"User-Agent": "universal-modder"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            path.write_bytes(r.read())
    except OSError as e:                                      # URLError, HTTPError, or a timeout while reading
        die(f"could not download {url}: {getattr(e, 'reason', None) or e or type(e).__name__}")
    return path


def record(out: Path, rec: dict):
    with open(out / "voidless_manifest.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(t=time.strftime("%Y-%m-%dT%H:%M:%S"), **rec)) + "\n")


def _name(name: str | None, fallback: str) -> str:
    return name or "_".join(re.sub(r"[^a-z0-9 ]", "", fallback.lower()).split()[:5]) or "sprite"


def _save(out: Path, stem: str, keys, label: str) -> list[str]:
    """Download every image key under one stem. Returns the paths written."""
    saved = []
    urls = [u for u in (cdn_url(k) for k in keys) if u]
    for i, url in enumerate(urls):
        ext = Path(url.split("?")[0]).suffix or ".png"
        suffix = f"_{i:02d}" if len(urls) > 1 else ""
        p = download(url, out / f"{stem}{suffix}{ext}")
        saved.append(str(p))
        print(f"um: {label} -> {p}")
    return saved


def _cost(data: dict) -> str:
    c = data.get("cost") or data.get("credits")
    return f" ({c} credits)" if c else ""


# --------------------------------------------------------------------------- commands


def cmd_credits(a, base, out):
    me = request(base, "GET", "/users/me")
    if a.json:
        print(json.dumps(me, indent=2))
        return
    # the account shape is {username, email, tier, subscribed, credits, ...}; there is no "plan"
    for field in ("username", "email", "tier", "subscribed", "credits"):
        if me.get(field) is not None:
            print(f"{field:12} {me[field]}")


def cmd_presets(a, base, out):
    data = request(base, "GET", "/generate/multi-animation/presets")
    if a.json:
        print(json.dumps(data, indent=2))
        return
    # a preset is {key, label, actions[]}; `animate --preset` wants the key
    presets = data if isinstance(data, list) else (data.get("presets") or [])
    for p in presets:
        if isinstance(p, dict):
            actions = ", ".join(p.get("actions") or [])
            print(f"{str(p.get('key', '?')):24} {p.get('label') or ''}")
            if actions:
                print(f"{'':24}   {actions}")
        else:
            print(p)


def cmd_asset(a, base, out):
    asset = request(base, "GET", f"/assets/{a.asset_id}")
    if a.json:
        print(json.dumps(asset, indent=2))
        return
    print(f"asset   {asset.get('id')}  {asset.get('name') or ''}")
    if url := cdn_url(asset.get("file")):
        print(f"base    {url}")
    for i, f in enumerate((asset.get("meta_data") or {}).get("frames") or []):
        imgs = f.get("images") or []
        print(f"frame   id={f.get('id', i)} {f.get('name') or f.get('type') or '?'}  {len(imgs)} image(s)")
        if a.urls:
            for k in imgs:
                if u := cdn_url(k):
                    print(f"          {u}")


def cmd_sprite(a, base, out):
    # A tileset is generated by one model whatever --model says: the server replaces it. Say so,
    # rather than let a run quietly cost five times what the chosen model would have.
    model = a.model
    if a.type == "tileset" and model != TILESET_MODEL:
        print(f"um: tilesets are always generated with {TILESET_MODEL} (5 credits); "
              f"ignoring --model {model}", file=sys.stderr)
        model = TILESET_MODEL

    # Every one of prompt/colours/dimension/size/type/model/seed is REQUIRED -- the endpoint answers
    # 422 "The given data is invalid." rather than filling anything in, so none of them may be omitted.
    body = {
        "prompt": a.prompt, "type": a.type, "model": model, "seed": a.seed,
        "dimension": a.dimension, "size": a.size, "colours": a.colours,
        "palette": [], "style": a.style,
        # referenceImage and styleImage have no default downstream: leaving them out is a 422.
        "referenceImage": "", "styleImage": "",
        "options": {"facing": a.facing, "pose": a.pose, "bodyType": a.body_type,
                    "aspect": a.aspect, "mode": ""},
    }
    data = request(base, "POST", "/generate/image", body, timeout=a.timeout)
    stem = _name(a.name, a.prompt)
    saved = _save(out, stem, [data.get("file")], "sprite")
    asset_id = data.get("assetId")
    print(f"um: asset {asset_id}{_cost(data)}  (pass it to `um voidless rotate` or `animate`)")
    record(out, dict(cmd="sprite", asset=asset_id, prompt=a.prompt, type=a.type, model=model,
                     dimension=a.dimension, size=a.size, style=a.style, seed=data.get("seed"), files=saved))


def cmd_rotate(a, base, out):
    data = request(base, "POST", "/generate/image-rotations", {"id": a.asset_id}, timeout=a.timeout)
    saved = []
    for f in data.get("frames") or []:
        saved += _save(out, _name(a.name, f"{a.asset_id} rotations"), f.get("images") or [], "rotation")
    print(f"um: 8-way rotation on asset {a.asset_id}{_cost(data)}")
    record(out, dict(cmd="rotate", asset=a.asset_id, files=saved))


def cmd_animate(a, base, out):
    if not a.preset and not a.prompt:
        die("give --preset (see `um voidless presets`) or --prompt \"name: what happens; name: what happens\"")
    # The endpoint animates a LIST of images, not an asset id: `items` is [{assetId, frameId?}] in
    # placement order. Sending {"id": …} is accepted and then rejected as "attach at least one image".
    body = {
        "items": [{"assetId": int(a.asset_id)} | ({"frameId": a.frame_id} if a.frame_id is not None else {})],
        "preset": a.preset or "", "prompt": a.prompt or "", "quality": a.quality,
        "holdFacing": a.hold_facing, "flipFacings": not a.no_flip_facings, "autoFlip": a.auto_flip,
    }
    data = request(base, "POST", "/generate/multi-animation", body, timeout=a.timeout)
    saved = []
    for r in data.get("results") or []:
        for f in r.get("frames") or []:
            clip = _name(None, f.get("name") or f.get("type") or "clip")
            saved += _save(out, f"{_name(a.name, str(a.asset_id))}_{clip}", f.get("images") or [], f"clip {clip}")
    if skipped := [s for r in (data.get("results") or []) for s in (r.get("skipped") or [])]:
        print(f"um: skipped {json.dumps(skipped)}", file=sys.stderr)
    print(f"um: animation set on asset {a.asset_id}{_cost(data)}"
          + (f"  quality={data['quality']}" if data.get("quality") else ""))
    record(out, dict(cmd="animate", asset=a.asset_id, preset=a.preset, prompt=a.prompt,
                     quality=a.quality, hold_facing=a.hold_facing, files=saved))


def cmd_fetch(a, base, out):
    """Download an asset's frames again, without generating anything.

    Generation and download are separate steps, and only the first one costs credits. A download cut
    short by a dropped connection or a cancelled command used to leave you having paid for frames
    with no way to get them -- the API still has them, so this just asks again. Free.
    """
    asset = request(base, "GET", f"/assets/{a.asset_id}")
    stem = _name(a.name, str(asset.get("name") or a.asset_id))
    saved = []
    if not a.frames_only:
        saved += _save(out, stem, [asset.get("file")], "base")
    for i, f in enumerate((asset.get("meta_data") or {}).get("frames") or []):
        if a.frame_id is not None and f.get("id") != a.frame_id:
            continue
        clip = _name(None, f.get("name") or f.get("type") or f"frame{i}")
        saved += _save(out, f"{stem}_{clip}", f.get("images") or [], f"frame {clip}")
    print(f"um: {len(saved)} file(s) from asset {a.asset_id} (no credits spent)")
    record(out, dict(cmd="fetch", asset=a.asset_id, files=saved))


def main(a):
    if a.cmd == "key":
        return cmd_key(a)
    base = base_url(getattr(a, "url", None))
    out = Path(getattr(a, "out", "assets/gen"))
    out.mkdir(parents=True, exist_ok=True)
    {"credits": cmd_credits, "presets": cmd_presets, "asset": cmd_asset, "fetch": cmd_fetch,
     "sprite": cmd_sprite, "rotate": cmd_rotate, "animate": cmd_animate}[a.cmd](a, base, out)


def register(sub):
    import argparse
    p = sub.add_parser("voidless", help="2D sprites with Voidless: 8-way turns and animation sets that keep one size",
                       description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cs = p.add_subparsers(dest="cmd", metavar="<cmd>")

    def cmd(name, help_, out=True):
        q = cs.add_parser(name, help=help_)
        q.add_argument("--url", help=f"API address (default: $VOIDLESS_API_URL or {DEFAULT_URL})")
        if out:
            q.add_argument("--out", default="assets/gen", help="output folder (default assets/gen)")
            q.add_argument("--name", help="output file stem")
            q.add_argument("--timeout", type=float, default=900, help="seconds to wait for the result")
        q.set_defaults(func=main)
        return q

    q = cmd("credits", "plan and credits left", out=False)
    q.add_argument("--json", action="store_true")
    q = cmd("presets", "named animation sets `animate --preset` accepts", out=False)
    q.add_argument("--json", action="store_true")
    q = cmd("asset", "frames, image keys and download urls for one asset", out=False)
    q.add_argument("asset_id")
    q.add_argument("--urls", action="store_true", help="print every image url")
    q.add_argument("--json", action="store_true")

    q = cmd("fetch", "download an asset's frames again without generating (free)")
    q.add_argument("asset_id")
    q.add_argument("--frame-id", type=int, help="only this frame")
    q.add_argument("--frames-only", action="store_true", help="skip the base image")

    q = cmd("sprite", "text -> sprite on a transparent background (5 credits)")
    q.add_argument("prompt")
    q.add_argument("--type", default="character", choices=TYPES,
                   help="'character' is a full-body sprite; 'object' props and items; 'artwork' scenes")
    q.add_argument("--model", default="flux2-klein", choices=MODELS,
                   help="flux2-klein (1 credit) unless you need another: flux-juggernaut 1, "
                        "seedream-5-flash 2, gpt-image-2.5 5, retro-diffusion 10, nano-banana-2 15. "
                        "--type tileset always uses gpt-image-2.5 whatever you pass")
    q.add_argument("--size", type=int, default=512, choices=SIZES,
                   help="output px: 32/64/128 read as pixel art, 512 otherwise, 1024 high-res")
    q.add_argument("--dimension", default="2d", choices=DIMENSIONS,
                   help="'2d' side view, 'top down' overhead, 'isometric' 2.5D")
    q.add_argument("--colours", type=int, default=8, help="colour count for pixel-art reduction (4-12)")
    q.add_argument("--style", default="", help="style preset, e.g. pixel-art, cartoon, anime, hand-drawn")
    q.add_argument("--facing", default="forward", choices=FACINGS,
                   help="characters: front view or side profile. Side profiles rotate best, and a left-facing "
                        "sprite is a mirrored right one, so generate 'right' and flip")
    q.add_argument("--pose", default="idle", choices=POSES,
                   help="'idle' for animation sets and rotations; 'tpose' only for rigging")
    q.add_argument("--body-type", default="humanoid", choices=BODY_TYPES, help="characters: body plan")
    q.add_argument("--aspect", default="1:1", choices=["1:1", "16:9"], help="16:9 only applies to --type artwork")
    q.add_argument("--seed", type=int, default=0, help="0 = random")

    q = cmd("rotate", "asset id -> the eight facings as one frame (10 credits)")
    q.add_argument("asset_id")

    q = cmd("animate", "asset id -> an animation set, every clip scaled to the same base size")
    q.add_argument("asset_id")
    q.add_argument("--preset", help="a named set from `um voidless presets`")
    q.add_argument("--prompt", help="without a preset: 'name: what happens; name: what happens'")
    q.add_argument("--hold-facing", action="store_true",
                   help="end each clip on the frame it started from, so a directional loop does not drift")
    q.add_argument("--no-flip-facings", action="store_true",
                   help="animate the left-side clips too instead of mirroring them from the right (costs double)")
    q.add_argument("--auto-flip", action="store_true",
                   help="afterwards, mirror every right-side clip that has no left twin (free)")
    q.add_argument("--quality", default="high", choices=QUALITIES,
                   help="high (100 credits per pass) or ultra (200)")
    q.add_argument("--frame-id", type=int,
                   help="animate one frame of the asset (e.g. a rotation) instead of its base image")

    kp = cs.add_parser("key", help="store / inspect the Voidless API key (OS keyring first)",
                       description="`um voidless` takes the key from VOIDLESS_API_KEY first, then from a file named "
                                   "by UM_VOIDLESS_KEY_FILE, then from the OS keyring (libsecret's secret-tool, as "
                                   "`um fal key` uses: Linux), then from ~/.secrets/voidless-key (owner-only, what "
                                   "`um voidless key set` writes where there's no keyring), then from "
                                   "VOIDLESS_API_KEY=... in a .env. Keys are never printed in full.")
    ka = kp.add_subparsers(dest="action", metavar="<action>")
    ks = ka.add_parser("set", help="store a key from a hidden prompt (or --from-file)")
    ks.add_argument("--from-file", metavar="PATH")
    ks.add_argument("--file-only", action="store_true", help="skip the OS keyring; write the owner-only key file")
    ka.add_parser("status", help="show every source and which one is active (keys are masked)")
    ka.add_parser("clear", help="delete the stored key (keyring entry and key file)")
    kp.set_defaults(func=main, cmd="key", action="status")
    for _a in ka.choices.values():
        _a.set_defaults(func=main, cmd="key")
