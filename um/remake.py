"""Godot remakes: prove every slice runs, compare assets with the dirty room, keep the clean room clean.

A remake project root is remakes/<game>/ (project.godot next to SPEC.md, acceptance.json, assets.json).
Godot: --godot EXE, else $GODOT, else S:/Godot/Godot_v4.7-stable_win64_console.exe, else godot on PATH.

    um remake init remakes/demo --name Demo        # add/update addons/gd_remake, autoloads, Web preset, skeletons
    um remake check remakes/demo                   # every scenario + the boot check, headless -> .gd_remake/results.json
    um remake check remakes/demo --slice movement --only jump.apex
    um remake status remakes/demo                  # per slice: implemented / checks_pass / integrated / played
    um remake played remakes/demo --capture clip.mp4 --note "beat level 1"
    um remake grid remakes/demo tests/scenarios/jump.gd --out jump.png   # every case side by side (windowed)
    um remake run remakes/demo --bridge 7777       # launch detached with the JSON bridge, wait for ping
    um remake bridge 7777 tree path=/root depth=2  # one bridge request: ping tree get set call eval action key ...
    um remake variants list remakes/demo
    um remake variants promote remakes/demo hero v2   # variants/hero/v2.png -> assets/hero.png
    um remake measure dirty/demo --out dirty/demo/manifest.json   # image/audio/model metrics (dirty or clean)
    um remake compare demo                         # clean assets vs their dirty refs -> dirty/demo/compare/index.html
    um remake leak demo                            # clean-room leak scan; exit 1 on any hit
    um remake serve remakes/demo --with-server     # web export + COOP/COEP static server (+ headless game server)

A slice is four facts, never merged: implemented (every automated check has a scenario file),
checks_pass (every required check passed at the CURRENT revision), integrated (the main scene ran
boot_frames frames headless without SCRIPT ERROR/ERROR lines), played (a capture was recorded at the
current revision). A result from an older revision is stale, not pass. Revision = sha256 over the project
files minus .godot/ .gd_remake/ exports/ .git/ *.md *.import *.uid (first 12 hex chars).
compare and leak default to U:/Tools/GameDecomp/{dirty,remakes}/<game> ($UM_DIRTY_ROOT, $UM_REMAKES_ROOT).
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import html
import json
import os
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote

from um.common import die, emit, need, to_posix

DEFAULT_GODOT = "S:/Godot/Godot_v4.7-stable_win64_console.exe"
ADDON_SRC = Path(__file__).resolve().parent / "godot" / "addons" / "gd_remake"
RUNNER = "res://addons/gd_remake/runner.gd"
AUTOLOADS = {"GdBridge": "*res://addons/gd_remake/bridge.gd", "Variants": "*res://addons/gd_remake/variants.gd"}
STATE = ".gd_remake"
BOOT_ID = "boot"
REV_SKIP_DIRS = {".godot", STATE, "exports", ".git"}
REV_SKIP_SUFFIXES = (".md", ".import", ".uid")
SIDECARS = (".import", ".uid")
DIRTY_ROOT = Path(to_posix(os.environ.get("UM_DIRTY_ROOT", "U:/Tools/GameDecomp/dirty")))
REMAKES_ROOT = Path(to_posix(os.environ.get("UM_REMAKES_ROOT", "U:/Tools/GameDecomp/remakes")))


def _now() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _read_json(p: Path, default=None):
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"{p}: {e}")


def _write_json(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, p)


def _files(root: Path, skip=frozenset()) -> list[tuple[str, Path]]:
    """Every file under root as sorted (relative posix path, path); `skip` holds relative dir paths."""
    out = []
    for dp, dns, fns in os.walk(root):
        rel = Path(dp).relative_to(root).as_posix()
        rel = "" if rel == "." else rel + "/"
        dns[:] = [d for d in dns if rel + d not in skip]
        out.extend((rel + f, Path(dp) / f) for f in fns)
    out.sort()
    return out


def _res_path(root: Path, res: str) -> Path:
    return root / res.removeprefix("res://")


def _tail(text: str, n: int = 25) -> str:
    return "\n".join(text.strip().splitlines()[-n:])


# --------------------------------------------------------------------------- project state


def project_root(d) -> Path:
    root = Path(d).resolve()
    if not (root / "project.godot").is_file():
        die(f"{root} has no project.godot (run `um remake init {d}`)")
    return root


def state_dir(root: Path) -> Path:
    d = root / STATE
    d.mkdir(exist_ok=True)
    (d / ".gdignore").touch()
    return d


def revision(root) -> str:
    """sha256 over sorted (relative posix path, bytes), minus tool/derived files; first 12 hex chars."""
    h = hashlib.sha256()
    for rel, p in _files(Path(root), REV_SKIP_DIRS):
        if rel.lower().endswith(REV_SKIP_SUFFIXES):
            continue
        data = p.read_bytes()
        h.update(f"{rel}\0{len(data)}\0".encode())
        h.update(data)
    return h.hexdigest()[:12]


def load_acceptance(root: Path) -> dict:
    p = root / "acceptance.json"
    acc = _read_json(p)
    if acc is None:
        die(f"{p} missing (run `um remake init {root}`)")
    seen = set()
    for c in acc.setdefault("checks", []):
        cid = c.get("id")
        if not cid:
            die(f"{p}: every check needs an id")
        if cid == BOOT_ID:
            die(f"{p}: check id '{BOOT_ID}' is reserved for the boot check")
        if cid in seen:
            die(f"{p}: duplicate check id {cid}")
        seen.add(cid)
        c.setdefault("slice", "default")
        c.setdefault("required", True)
        c.setdefault("scenario", None)
    return acc


def load_results(root: Path) -> dict:
    return _read_json(root / STATE / "results.json", {})


def load_plays(root: Path) -> list:
    return _read_json(root / STATE / "played.json", {}).get("plays", [])


# --------------------------------------------------------------------------- Godot processes


def godot_exe(arg: str | None = None) -> str:
    cand = arg or os.environ.get("GODOT")
    if cand:
        if Path(cand).is_file():
            return str(cand)
        found = shutil.which(cand)
        if found:
            return found
        die(f"Godot not found: {cand} (from {'--godot' if arg else '$GODOT'})")
    if Path(to_posix(DEFAULT_GODOT)).is_file():
        return to_posix(DEFAULT_GODOT)
    for name in ("godot", "godot4"):
        found = shutil.which(name)
        if found:
            return found
    die("Godot not found: pass --godot <Godot 4.7 console exe>, set GODOT, or put godot on PATH")


def _kill_tree(pid: int):
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
        return
    for kill in (lambda: os.killpg(pid, signal.SIGKILL), lambda: os.kill(pid, signal.SIGKILL)):
        try:
            kill()
            return
        except OSError:
            pass


def _capture(cmd: list[str], timeout: float | None) -> tuple[int | None, str]:
    """Run with stdout+stderr merged into one stream (keeps engine errors in order with markers).
    Returns (exit code or None on timeout, output). The whole process tree dies on timeout or Ctrl-C."""
    kw = {} if os.name == "nt" else {"start_new_session": True}
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, **kw)
    except FileNotFoundError:
        die(f"not found: {cmd[0]}")
    try:
        out, _ = p.communicate(timeout=timeout)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        _kill_tree(p.pid)
        out, _ = p.communicate()
        rc = None
    except KeyboardInterrupt:
        _kill_tree(p.pid)
        raise
    return rc, out.decode("utf-8", "replace").replace("\r\n", "\n")


def godot_import(exe: str, root: Path, timeout: float = 600):
    """Editor import pass: registers class_name scripts (GdScenario...) and imports new assets."""
    rc, out = _capture([exe, "--headless", "--path", str(root), "--import"], timeout)
    if rc is None:
        die(f"godot --import timed out after {timeout:.0f}s:\n{_tail(out)}")
    if rc != 0:
        print(f"um: warning: godot --import exited {rc}:\n{_tail(out, 10)}", file=sys.stderr)


def runner_cmd(exe: str, root: Path, user_args: list[str], headless: bool = True) -> list[str]:
    return [exe] + (["--headless"] if headless else []) + ["--path", str(root), "-s", RUNNER, "--"] + user_args


# --------------------------------------------------------------------------- runner output

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
BEGIN = re.compile(r"^GDR_BEGIN (.+?)\|(.*)$")
END = re.compile(r"^GDR_END (.+?)\|(.*) (\w+)$")
ENGINE_ERROR = re.compile(r"^(?:USER )?(?:SCRIPT )?ERROR:")
SEVERITY = {"pass": 0, "fail": 1, "timeout": 2, "error": 3}


def parse_log(text: str) -> dict:
    """Split runner output into engine errors per case (between GDR_BEGIN/GDR_END markers) and the rest.
    Each error message is the ERROR line plus its `at:` location line."""
    errors: dict[tuple, list[str]] = {}
    ended: dict[tuple, str] = {}
    begun: list[tuple] = []
    loose: list[str] = []
    cur = None
    lines = [ANSI.sub("", ln).rstrip() for ln in text.splitlines()]
    for i, raw in enumerate(lines):
        s = raw.strip()
        if m := BEGIN.match(s):
            cur = (m[1], m[2])
            begun.append(cur)
        elif m := END.match(s):
            ended[(m[1], m[2])] = m[3]
            cur = None
        elif ENGINE_ERROR.match(s):
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            msg = f"{s} [{nxt}]" if nxt.startswith("at:") else s
            (errors.setdefault(cur, []) if cur else loose).append(msg)
    return {"errors": errors, "ended": ended, "begun": begun, "loose": loose}


def merge_cases(scenarios: list[str], data: dict | None, log: str, rc: int | None) -> tuple[dict, list[str]]:
    """Runner JSON + its log -> ({scenario: [case results]}, unattributed engine errors).
    An engine error inside a passing case turns it into an error; cases that began but never reported
    (crash) and scenarios without any result become errors too."""
    parsed = parse_log(log)
    by: dict[str, list[dict]] = {s: [] for s in scenarios}
    for r in (data or {}).get("results", []):
        r = dict(r)
        engine = parsed["errors"].get((r.get("scenario"), r.get("case")), [])
        if engine:
            r["engine_errors"] = engine
            if r.get("status") == "pass":
                r["status"], r["message"] = "error", engine[0]
        by.setdefault(r.get("scenario"), []).append(r)
    reported = {(r.get("scenario"), r.get("case")) for rs in by.values() for r in rs}
    why = "timed out" if rc is None else f"exited {rc}"
    for key in parsed["begun"]:
        if key in reported:
            continue
        engine = parsed["errors"].get(key, [])
        status = parsed["ended"].get(key, "error")
        if status == "pass" and not engine:
            continue  # e.g. the runner's `<scenario>|load` step, which only reports failures
        if engine and status == "pass":
            status = "error"
        msg = engine[0] if engine else f"runner {why} during this case without a result"
        by.setdefault(key[0], []).append({"scenario": key[0], "case": key[1], "status": status, "message": msg,
                                          "failures": [], "metrics": {}, "engine_errors": engine})
        reported.add(key)
    loose = list(parsed["loose"])
    for s, rs in by.items():
        if not rs:
            related = [e for e in loose if s in e]
            rs.append({"scenario": s, "case": "*", "status": "error", "failures": [], "metrics": {},
                       "message": related[0] if related else f"no results for this scenario (runner {why})"})
    return by, loose


def _runner_json(p: Path) -> dict | None:
    """The runner's --out file; None when missing or cut off mid-write (the log then explains the crash)."""
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def aggregate(cases: list[dict]) -> str:
    if not cases:
        return "error"
    worst = max(cases, key=lambda c: SEVERITY.get(c.get("status"), 3)).get("status")
    return worst if worst in SEVERITY else "error"


def _check_entry(check: dict, cases: list[dict], rev: str, now: str, extra_msgs=()) -> dict:
    messages = list(extra_msgs)
    for c in cases:
        if c.get("status") != "pass":
            messages.append(f"{c.get('case')}: {c.get('status')}: {c.get('message') or '; '.join(c.get('failures') or [])}")
            messages += [f"{c.get('case')}: {f}" for f in (c.get("failures") or [])[1:5]]
    multi = len(cases) > 1
    metrics = {(f"{c.get('case')}/{k}" if multi else k): v for c in cases for k, v in (c.get("metrics") or {}).items()}
    return {"revision": rev, "status": aggregate(cases) if cases else "error", "slice": check.get("slice"),
            "required": check.get("required", True), "scenario": check.get("scenario"), "claim": check.get("claim"),
            "cases": cases, "messages": messages, "metrics": metrics, "run_at": now,
            "duration_ms": sum(int(c.get("duration_ms") or 0) for c in cases)}


# --------------------------------------------------------------------------- check / status / played


def cmd_check(a):
    root = project_root(a.dir)
    acc = load_acceptance(root)
    exe = godot_exe(a.godot)
    checks = acc["checks"]
    if a.slice:
        checks = [c for c in checks if c["slice"] == a.slice]
        if not checks:
            die(f"no checks in slice {a.slice!r}")
    if a.only and a.only != BOOT_ID:
        checks = [c for c in checks if c["id"] == a.only]
        if not checks:
            die(f"no check with id {a.only!r}")
    run_boot = not a.only or a.only == BOOT_ID
    if a.only == BOOT_ID:
        checks = []
    godot_import(exe, root)
    rev = revision(root)
    run_dir = state_dir(root) / "run"
    run_dir.mkdir(exist_ok=True)
    results = load_results(root)
    now = _now()
    t0 = time.time()
    auto = [c for c in checks if c["scenario"]]
    manual = [c for c in checks if not c["scenario"]]
    missing = {c["id"] for c in auto if not _res_path(root, c["scenario"]).is_file()}
    scenarios = sorted({c["scenario"] for c in auto if c["id"] not in missing})
    ran: dict[str, dict] = {}
    loose: list[str] = []
    if scenarios:
        out = run_dir / "scenarios.json"
        out.unlink(missing_ok=True)
        args = ["--scenarios", ",".join(scenarios), "--out", out.resolve().as_posix(), "--timeout", str(a.timeout)]
        rc, log = _capture(runner_cmd(exe, root, args), timeout=a.timeout * 10 * len(scenarios) + 120)
        (run_dir / "scenarios.log").write_text(log, encoding="utf-8")
        data = _runner_json(out)
        by, loose = merge_cases(scenarios, data, log, rc)
        for c in auto:
            if c["id"] not in missing:
                ran[c["id"]] = _check_entry(c, by[c["scenario"]], rev, now)
    for c in auto:
        if c["id"] in missing:
            ran[c["id"]] = _check_entry(c, [], rev, now, [f"scenario file missing: {c['scenario']}"])
    if run_boot:
        ran[BOOT_ID] = run_boot_check(exe, root, int(acc.get("boot_frames", 120)), rev, now, run_dir)
    results.update(ran)
    _write_json(root / STATE / "results.json", results)
    failed = [cid for cid, r in ran.items() if r["status"] != "pass" and r.get("required", True)]
    if a.json:
        emit({"revision": rev, "checks": ran, "manual": [c["id"] for c in manual], "unattributed_errors": loose,
              "failed_required": failed}, True)
    else:
        print(f"revision {rev}  ({len(ran)} checks, {time.time() - t0:.1f}s)")
        for cid, r in ran.items():
            tag = "" if r.get("required", True) else " (optional)"
            n = len(r["cases"])
            where = f"  [{r['slice']}]" if r.get("slice") else ""
            print(f"  {r['status'].upper():7} {cid}{tag}{where}  {n} case{'s' * (n != 1)}")
            for m in r["messages"][:8]:
                print(f"          {m}")
        for c in manual:
            print(f"  MANUAL  {c['id']}  [{c['slice']}]  {c.get('claim', '')}")
        for e in loose[:10]:
            print(f"  engine error outside any case: {e}")
        print(f"logs: {(run_dir).relative_to(root).as_posix()}/")
    sys.exit(1 if failed else 0)


def run_boot_check(exe: str, root: Path, frames: int, rev: str, now: str, run_dir: Path) -> dict:
    """Main scene for `frames` frames headless; any SCRIPT ERROR/ERROR line fails it."""
    out = run_dir / "boot.json"
    out.unlink(missing_ok=True)
    rc, log = _capture(runner_cmd(exe, root, ["--boot", str(frames), "--out", out.resolve().as_posix()]),
                       timeout=max(120, frames / 5 + 60))
    (run_dir / "boot.log").write_text(log, encoding="utf-8")
    res = (_runner_json(out) or {}).get("results") or []
    case = dict(res[0]) if res else {"scenario": "boot", "case": "main", "status": "error", "failures": [], "metrics": {},
                                     "message": f"runner wrote no result ({'timed out' if rc is None else f'exit {rc}'})"}
    parsed = parse_log(log)
    engine = parsed["loose"] + [e for errs in parsed["errors"].values() for e in errs]
    if engine:
        case["engine_errors"] = engine
        if case.get("status") == "pass":
            case["status"], case["message"] = "error", engine[0]
    entry = _check_entry({"slice": None, "required": True, "scenario": "boot", "claim": f"main scene runs {frames} frames headless"},
                         [case], rev, now)
    entry["messages"] += [e for e in engine[1:10]]
    return entry


def _fact(result: dict | None, rev: str) -> str:
    if not result:
        return "no"
    if result.get("revision") != rev:
        return "stale"
    return "yes" if result.get("status") == "pass" else "no"


def compute_status(root: Path, acc: dict, results: dict, plays: list, rev: str) -> dict:
    boot = results.get(BOOT_ID)
    integrated = {"state": _fact(boot, rev), "revision": (boot or {}).get("revision"), "status": (boot or {}).get("status")}
    last = plays[-1] if plays else None
    played = {"state": "no" if not last else ("yes" if last.get("revision") == rev else "stale"),
              "revision": (last or {}).get("revision"), "capture": (last or {}).get("capture")}
    slices: dict[str, list] = {}
    for c in acc["checks"]:
        slices.setdefault(c["slice"], []).append(c)
    rows = []
    for name, cs in slices.items():
        auto = [c for c in cs if c.get("scenario")]
        manual = [c["id"] for c in cs if not c.get("scenario")]
        missing = [c["id"] for c in auto if not _res_path(root, c["scenario"]).is_file()]
        impl = {"state": "yes" if auto and not missing else "no", "have": len(auto) - len(missing), "checks": len(auto),
                "missing": missing}
        required = [c for c in auto if c.get("required", True)]
        blocking, passed, stale = [], 0, False
        for c in required:
            r = results.get(c["id"])
            if c["id"] in missing:
                blocking.append({"id": c["id"], "reason": "no scenario file"})
            elif not r:
                blocking.append({"id": c["id"], "reason": "never run"})
            elif r.get("revision") != rev:
                stale = True
                blocking.append({"id": c["id"], "reason": f"stale: {r.get('status')} at {r.get('revision')}"})
            elif r.get("status") == "pass":
                passed += 1
            else:
                blocking.append({"id": c["id"], "reason": (r.get("messages") or [r.get("status")])[0]})
        hard = [b for b in blocking if not b["reason"].startswith("stale")]
        if not required:
            state = "no"
            blocking.append({"id": None, "reason": "no required automated checks"})
        else:
            state = "no" if hard else ("stale" if stale else "yes")
        optional = []
        for c in auto:
            if not c.get("required", True):
                r = results.get(c["id"])
                optional.append({"id": c["id"], "status": "never run" if not r else
                                 r.get("status") if r.get("revision") == rev else f"stale ({r.get('status')})"})
        rows.append({"slice": name, "implemented": impl,
                     "checks_pass": {"state": state, "passed": passed, "required": len(required), "blocking": blocking},
                     "integrated": integrated, "played": played, "manual": manual, "optional": optional})
    done = bool(rows) and all(r["checks_pass"]["state"] == "yes" for r in rows) and integrated["state"] == "yes"
    return {"revision": rev, "slices": rows, "integrated": integrated, "played": played, "done": done}


def format_status(st: dict) -> str:
    out = [f"revision {st['revision']}"]
    if not st["slices"]:
        out.append("no checks in acceptance.json")
    w = max([len(r["slice"]) for r in st["slices"]] + [5])
    out.append(f"{'slice':{w}}  {'implemented':13} {'checks_pass':15} {'integrated':11} played")
    for r in st["slices"]:
        im, cp = r["implemented"], r["checks_pass"]
        imp = "{} ({}/{})".format(im["state"], im["have"], im["checks"])
        cps = "{} ({}/{})".format(cp["state"], cp["passed"], cp["required"])
        out.append(f"{r['slice']:{w}}  {imp:13} {cps:15} {r['integrated']['state']:11} {r['played']['state']}")
        for b in cp["blocking"]:
            out.append(f"  blocks: {b['id'] + ' ' if b['id'] else ''}{b['reason']}")
        for o in r["optional"]:
            out.append(f"  optional: {o['id']} {o['status']}")
        if r["manual"]:
            out.append(f"  manual: {', '.join(r['manual'])} (not automated; covered only by playing)")
    integ = st["integrated"]
    if integ["state"] != "yes":
        out.append(f"integrated: {integ['state']}" + (f" (boot {integ['status']} at {integ['revision']})" if integ["revision"] else " (boot check never run)"))
    if st["done"]:
        out.append(f"overall: done at {st['revision']} (all required checks pass and the boot check passes at this revision)")
    else:
        why = [f"{r['slice']}: checks_pass {r['checks_pass']['state']}" for r in st["slices"] if r["checks_pass"]["state"] != "yes"]
        if integ["state"] != "yes":
            why.append(f"integrated {integ['state']}")
        out.append("overall: NOT done (" + ("; ".join(why) or "no checks") + ")")
    pl = st["played"]
    out.append(f"played: {pl['state']}" + (f" (last capture at {pl['revision']}: {pl['capture']})" if pl["revision"] else "")
               + " (separate from done; record with `um remake played`)")
    return "\n".join(out)


def cmd_status(a):
    root = project_root(a.dir)
    st = compute_status(root, load_acceptance(root), load_results(root), load_plays(root), revision(root))
    emit(st, True) if a.json else print(format_status(st))


def cmd_played(a):
    root = project_root(a.dir)
    cap = Path(a.capture)
    if not cap.is_file():
        die(f"capture not found: {cap}")
    entry = {"capture": cap.resolve().as_posix(), "revision": revision(root), "at": _now(), "note": a.note}
    p = state_dir(root) / "played.json"
    data = _read_json(p, {"plays": []})
    data.setdefault("plays", []).append(entry)
    _write_json(p, data)
    print(f"played at {entry['revision']}: {entry['capture']}")


# --------------------------------------------------------------------------- grid / run / bridge


def _to_res(root: Path, scenario: str) -> str:
    if scenario.startswith("res://"):
        return scenario
    p = Path(scenario)
    for cand in ([root / p] if not p.is_absolute() else []) + [p.resolve()]:
        if cand.is_file():
            try:
                return "res://" + cand.resolve().relative_to(root).as_posix()
            except ValueError:
                die(f"{cand} is outside the project {root}")
    die(f"scenario not found: {scenario}")


def cmd_grid(a):
    root = project_root(a.dir)
    exe = godot_exe(a.godot)
    scen = _to_res(root, a.scenario)
    out = Path(a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    side = Path(str(out) + ".json")
    for f in (out, side):
        f.unlink(missing_ok=True)
    godot_import(exe, root)
    args = ["--grid", scen, "--out", out.as_posix()] + (["--cell", a.cell] if a.cell else []) + (["--at", str(a.at)] if a.at else [])
    rc, log = _capture(runner_cmd(exe, root, args, headless=False), timeout=(a.at or 10) + 180)
    (state_dir(root) / "grid.log").write_text(log, encoding="utf-8")
    if not out.is_file():
        die(f"grid produced no image ({'timed out' if rc is None else f'exit {rc}'}):\n{_tail(log)}")
    print(out.as_posix())
    for r in (_runner_json(side) or {}).get("results", []):
        msg = f"  {r.get('message')}" if r.get("status") != "pass" and r.get("message") else ""
        print(f"  {r.get('status', '?').upper():7} {r.get('case')}{msg}")
    for e in parse_log(log)["loose"][:10]:
        print(f"  engine error: {e}")


def bridge_request(port: int, cmd: str, args: dict | None = None, timeout: float = 60.0, host: str = "127.0.0.1") -> dict | None:
    """One newline-delimited JSON request to the GdBridge autoload; None if the game closed without answering."""
    with socket.create_connection((host, int(port)), timeout=timeout) as s:
        s.sendall((json.dumps({"id": 1, "cmd": cmd, "args": args or {}}) + "\n").encode())
        buf = b""
        while b"\n" not in buf:
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
    line = buf.split(b"\n", 1)[0].strip()
    return json.loads(line) if line else None


def bridge_args(items: list[str]) -> dict:
    """One JSON object, or key=value pairs whose values are JSON when they parse (depth=2, value=[1,2]) else strings."""
    if len(items) == 1 and items[0].lstrip().startswith("{"):
        try:
            return json.loads(items[0])
        except json.JSONDecodeError as e:
            die(f"bad JSON args: {e}")
    out = {}
    for it in items:
        if "=" not in it:
            die(f"bridge args are key=value pairs or one JSON object, got {it!r}")
        k, v = it.split("=", 1)
        try:
            out[k] = json.loads(v)
        except json.JSONDecodeError:
            out[k] = v
    return out


def cmd_bridge(a):
    args = bridge_args(a.args)
    if a.command == "screenshot" and isinstance(args.get("path"), str):
        args["path"] = Path(args["path"]).resolve().as_posix()  # the game resolves paths against its own cwd
    try:
        resp = bridge_request(a.port, a.command, args, a.timeout)
    except OSError as e:
        die(f"bridge on port {a.port}: {e}")
    if resp is None:
        if a.command == "quit":
            emit({"ok": True, "result": "game closed"}, True)
            return
        die("bridge closed the connection without answering")
    if not resp.get("ok"):
        die(f"bridge {a.command}: {resp.get('error')}")
    emit(resp.get("result"), True)


def _spawn_detached(cmd: list[str], log: Path) -> subprocess.Popen:
    kw = ({"creationflags": subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt"
          else {"start_new_session": True})
    with open(log, "wb") as f:
        return subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, close_fds=True, **kw)


def cmd_run(a):
    root = project_root(a.dir)
    exe = godot_exe(a.godot)
    godot_import(exe, root)
    user = ([f"--gd-bridge={a.bridge}"] if a.bridge else []) + [x for v in a.variant for x in ("--variant", v)]
    cmd = [exe] + (["--headless"] if a.headless else []) + ["--path", str(root)] + ([a.scene] if a.scene else []) + (["--"] + user if user else [])
    if a.bridge:
        try:
            other = bridge_request(a.bridge, "ping", timeout=1)
            die(f"port {a.bridge} is already answered by a running game ({json.dumps((other or {}).get('result'))}); "
                f"quit it (`um remake bridge {a.bridge} quit`) or pick another port")
        except ValueError:
            die(f"port {a.bridge} is in use by something that is not a GdBridge")
        except OSError:
            pass
    log = state_dir(root) / "run.log"
    p = _spawn_detached(cmd, log)
    info = {"pid": p.pid, "port": a.bridge, "log": log.as_posix()}
    if a.bridge:
        deadline = time.time() + a.wait
        while True:
            if p.poll() is not None:
                die(f"game exited ({p.returncode}) before the bridge answered:\n{_tail(log.read_text('utf-8', 'replace'))}")
            try:
                resp = bridge_request(a.bridge, "ping", timeout=2)
                if resp and resp.get("ok"):
                    info["ping"] = resp.get("result")
                    break
            except OSError:
                pass
            if time.time() > deadline:
                die(f"bridge on port {a.bridge} did not answer within {a.wait}s; game pid {p.pid} still running (log {log})")
            time.sleep(0.3)
    emit(info, True)


# --------------------------------------------------------------------------- variants


def _is_sidecar(name: str) -> bool:
    return name.lower().endswith(SIDECARS) or name == ".gdignore"


def variant_slots(root: Path) -> dict[str, list[Path]]:
    vd = root / "variants"
    out = {}
    if vd.is_dir():
        for slot in sorted(p for p in vd.iterdir() if p.is_dir()):
            files = sorted(f for f in slot.iterdir() if f.is_file() and not _is_sidecar(f.name))
            if files:
                out[slot.name] = files
    return out


def _asset_base(name: str) -> str:
    for s in SIDECARS:
        if name.lower().endswith(s):
            return name[: -len(s)]
    return name


def _rel(p: str) -> str:
    """assets.json path -> project-relative posix path (accepts res://, ./ and backslashes)."""
    p = p.replace("\\", "/").removeprefix("res://")
    return p[2:] if p.startswith("./") else p


def promote(root: Path, slot: str, name: str) -> dict:
    """variants/<slot>/<name>.<ext> -> assets/<slot>.<ext>; drops the slot folder and stale provenance."""
    sd = root / "variants" / slot
    cands = [f for f in (sd.iterdir() if sd.is_dir() else []) if f.is_file() and not _is_sidecar(f.name) and f.stem == name]
    if len(cands) != 1:
        have = [f.stem for f in variant_slots(root).get(slot, [])]
        die(f"variant {slot}/{name}: {'ambiguous ' + str([c.name for c in cands]) if cands else 'not found'} (slot has {have})")
    src = cands[0]
    assets = root / "assets"
    assets.mkdir(exist_ok=True)
    removed = []
    for f in sorted(assets.iterdir()):
        base = Path(_asset_base(f.name))
        if f.is_file() and base.stem == slot and base.suffix:
            f.unlink()
            if not _is_sidecar(f.name):
                removed.append(f"assets/{f.name}")
    dest = assets / f"{slot}{src.suffix}"
    old_rel, new_rel = f"variants/{slot}/{src.name}", f"assets/{dest.name}"
    shutil.move(str(src), dest)
    shutil.rmtree(sd)
    md = root / "ASSETS.md"
    if md.exists():
        text = md.read_text(encoding="utf-8")
        md.write_text(text + ("" if text.endswith("\n") or not text else "\n") + f"promoted {slot}: {name}\n", encoding="utf-8")
    updated, dropped = 0, []
    aj = root / "assets.json"
    entries = _read_json(aj, None)
    if isinstance(entries, list):
        # the chosen variant's entry moves to the new path; entries of deleted files go (the replaced
        # asset's entry survives only when no entry described the chosen variant)
        claimed = any(_rel(str(e.get("path", ""))) == old_rel for e in entries if isinstance(e, dict))
        keep = []
        for e in entries:
            p = _rel(str(e.get("path", ""))) if isinstance(e, dict) else ""
            if p == old_rel:
                e["path"] = new_rel
                updated += 1
            elif p.startswith(f"variants/{slot}/") or (p in removed and (claimed or p != new_rel)):
                dropped.append(p)
                continue
            keep.append(e)
        _write_json(aj, keep)
    return {"promoted": new_rel, "from": old_rel, "replaced": removed,
            "assets_json_updated": updated, "assets_json_dropped": dropped}


def cmd_variants_list(a):
    root = project_root(a.dir)
    slots = {s: [f.stem for f in fs] for s, fs in variant_slots(root).items()}
    if a.json:
        emit(slots, True)
        return
    if not slots:
        print("no variants (put candidates in variants/<slot>/<name>.<ext>)")
    for s, names in slots.items():
        promoted = [f.name for f in (root / "assets").glob(f"{s}.*") if not _is_sidecar(f.name)] if (root / "assets").is_dir() else []
        print(f"{s}: {', '.join(names)}" + (f"   (current asset: {promoted[0]})" if promoted else ""))


def cmd_variants_promote(a):
    emit(promote(project_root(a.dir), a.slot, a.name), True)


# --------------------------------------------------------------------------- measure

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tga", ".webp", ".gif", ".dds", ".tif", ".tiff", ".psd", ".ico"}
AUDIO_EXT = {".wav", ".ogg", ".oga", ".mp3", ".flac", ".opus", ".m4a", ".aac", ".wma", ".aif", ".aiff", ".xwm"}
MODEL_EXT = {".gltf", ".glb", ".obj"}
MEASURE_SKIP = {".godot", STATE, ".git", "exports", "compare"}
MEASURE_SKIP_FILES = {"manifest.json", ".leak_cache.json"}


def kind_of(p: Path) -> str:
    ext = p.suffix.lower()
    return "image" if ext in IMAGE_EXT else "audio" if ext in AUDIO_EXT else "model" if ext in MODEL_EXT else "other"


def _pil():
    need("PIL", "pillow")
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None  # local game textures, not untrusted uploads
    return Image


def image_metrics(p: Path) -> dict:
    Image, np = _pil(), need("numpy")
    with Image.open(p) as im:
        frames = getattr(im, "n_frames", 1)
        rgba = im.convert("RGBA")
    a = np.asarray(rgba)
    h, w = a.shape[:2]
    alpha = a[..., 3]
    ys, xs = np.nonzero(alpha >= 32)
    m = {"w": w, "h": h, "has_alpha": bool((alpha < 255).any()),
         "bbox_w": int(xs.max() - xs.min() + 1) if len(xs) else 0, "bbox_h": int(ys.max() - ys.min() + 1) if len(ys) else 0}
    if frames > 1:
        m["frames"] = frames
    px = a[alpha >= 128][:, :3]
    if not len(px):
        m.update(palette=[], mean_luminance=None)
        return m
    px = px[:: max(1, len(px) // 65536)]
    lum = (px[:, 0] * 0.2126 + px[:, 1] * 0.7152 + px[:, 2] * 0.0722) / 255.0
    q = Image.fromarray(np.ascontiguousarray(px.reshape(-1, 1, 3)).astype(np.uint8), "RGB").quantize(16, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    top = sorted(q.getcolors(256) or [], reverse=True)[:8]
    m["palette"] = [{"hex": "#{:02x}{:02x}{:02x}".format(*pal[i * 3:i * 3 + 3]), "share": round(n / len(px), 4)} for n, i in top]
    m["mean_luminance"] = round(float(lum.mean()), 4)
    return m


def _db_in(rx: str, text: str) -> float | None:
    """Last match of a dB/LUFS value in ffmpeg's stderr (the summary comes last); -inf (silence) -> None."""
    vals = re.findall(rx, text)
    return None if not vals or "inf" in vals[-1] else float(vals[-1])


def audio_metrics(p: Path) -> dict:
    if not shutil.which("ffmpeg"):
        return {"error": "ffmpeg not on PATH"}
    m = {}
    if shutil.which("ffprobe"):
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                            "stream=sample_rate,channels,codec_name,duration:format=duration", "-of", "json", str(p)],
                           capture_output=True, text=True)
        d = json.loads(r.stdout or "{}")
        s = (d.get("streams") or [{}])[0]
        dur = s.get("duration") or (d.get("format") or {}).get("duration")
        m.update(duration_s=round(float(dur), 4) if dur else None, sample_rate=int(s["sample_rate"]) if s.get("sample_rate") else None,
                 channels=s.get("channels"), codec=s.get("codec_name"))
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-map", "0:a:0",
                          "-af", "ebur128=peak=true:framelog=verbose,volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    if "duration_s" not in m:
        dm = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
        hz = re.search(r"Audio: .*?(\d+) Hz, (mono|stereo|[\d.]+)", err)
        m.update(duration_s=round(int(dm[1]) * 3600 + int(dm[2]) * 60 + float(dm[3]), 4) if dm else None,
                 sample_rate=int(hz[1]) if hz else None, channels={"mono": 1, "stereo": 2}.get(hz[2]) if hz else None)
    m.update(peak_dbfs=_db_in(r"max_volume: (-?[\d.]+|-?inf) dB", err), mean_volume_db=_db_in(r"mean_volume: (-?[\d.]+|-?inf) dB", err),
             loudness_lufs=_db_in(r"\bI:\s+(-?[\d.]+|-?inf) LUFS", err), true_peak_dbfs=_db_in(r"Peak:\s+(-?[\d.]+|-?inf) dBFS", err))
    if m["peak_dbfs"] is None and m["loudness_lufs"] is None:
        m["error"] = "ffmpeg could not decode audio: " + (err.strip().splitlines() or ["?"])[-1]
    return m


def gltf_json(p: Path) -> dict:
    data = p.read_bytes()
    if data[:4] == b"glTF":
        clen, ctype = struct.unpack_from("<I4s", data, 12)
        if ctype != b"JSON":
            raise ValueError("GLB first chunk is not JSON")
        return json.loads(data[20:20 + clen].decode("utf-8"))
    return json.loads(data.decode("utf-8-sig"))


def _node_matrix(np, n: dict):
    if "matrix" in n:
        return np.array(n["matrix"], float).reshape(4, 4).T, any(abs(v) > 1e-6 for i, v in enumerate(n["matrix"][:11]) if i not in (0, 5, 10) and i % 4 != 3)
    x, y, z, w = n.get("rotation", [0, 0, 0, 1])
    r = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    m = np.eye(4)
    m[:3, :3] = r * np.array(n.get("scale", [1, 1, 1]), float)
    m[:3, 3] = n.get("translation", [0, 0, 0])
    return m, abs(abs(w) - 1) > 1e-6


def gltf_metrics(g: dict) -> dict:
    np = need("numpy")
    acc = g.get("accessors", [])
    prims = tris = verts = 0
    boxes: dict[int, tuple] = {}
    for mi, mesh in enumerate(g.get("meshes", [])):
        lo = hi = None
        for pr in mesh.get("primitives", []):
            prims += 1
            pos = pr.get("attributes", {}).get("POSITION")
            if pos is None:
                continue
            pa = acc[pos]
            n = pa.get("count", 0)
            verts += n
            cnt = acc[pr["indices"]].get("count", 0) if "indices" in pr else n
            mode = pr.get("mode", 4)
            tris += cnt // 3 if mode == 4 else max(cnt - 2, 0) if mode in (5, 6) else 0
            if "min" in pa and "max" in pa:
                lo = np.array(pa["min"][:3], float) if lo is None else np.minimum(lo, pa["min"][:3])
                hi = np.array(pa["max"][:3], float) if hi is None else np.maximum(hi, pa["max"][:3])
        if lo is not None:
            boxes[mi] = (lo, hi)
    nodes = g.get("nodes", [])
    scenes = g.get("scenes", [])
    children = {c for n in nodes for c in n.get("children", [])}
    roots = scenes[g.get("scene", 0)].get("nodes", []) if scenes else [i for i in range(len(nodes)) if i not in children]
    wlo = whi = None
    rotated = False
    stack, seen = [(r, np.eye(4)) for r in roots], set()
    while stack:
        i, parent = stack.pop()
        if i in seen or i >= len(nodes):
            continue
        seen.add(i)
        local, rot = _node_matrix(np, nodes[i])
        rotated |= rot
        world = parent @ local
        if nodes[i].get("mesh") in boxes:
            lo, hi = boxes[nodes[i]["mesh"]]
            corners = np.array([[x, y, z, 1] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]) @ world.T
            c = corners[:, :3]
            wlo = c.min(0) if wlo is None else np.minimum(wlo, c.min(0))
            whi = c.max(0) if whi is None else np.maximum(whi, c.max(0))
        stack.extend((c, world) for c in nodes[i].get("children", []))
    notes = []
    if wlo is None and boxes:  # meshes not placed by any node: raw mesh space
        wlo = np.min([b[0] for b in boxes.values()], 0)
        whi = np.max([b[1] for b in boxes.values()], 0)
        notes.append("no scene nodes reference meshes: bounds in mesh space")
    if rotated:
        notes.append("rotated nodes: axis-aligned box of rotated mesh boxes (can overestimate)")
    skins = g.get("skins", [])
    if skins:
        notes.append("skinned: bind-pose bounds")
    anims = []
    for i, an in enumerate(g.get("animations", [])):
        ends = [acc[s["input"]].get("max", [0])[0] for s in an.get("samplers", []) if s.get("input") is not None and s["input"] < len(acc)]
        anims.append({"name": an.get("name") or f"animation_{i}", "duration_s": round(max(ends), 4) if ends else None})
    m = {"meshes": len(g.get("meshes", [])), "primitives": prims, "tris": tris, "vertices": verts, "nodes": len(nodes),
         "skins": len(skins), "joints": len({j for s in skins for j in s.get("joints", [])}),
         "materials": len(g.get("materials", [])), "textures": len(g.get("textures", [])), "animations": anims}
    if wlo is not None:
        m["bounds"] = {"min": [round(float(v), 5) for v in wlo], "max": [round(float(v), 5) for v in whi]}
        m["size"] = [round(float(b - a), 5) for a, b in zip(wlo, whi)]
    if notes:
        m["bounds_note"] = "; ".join(notes)
    return m


def obj_metrics(p: Path) -> dict:
    verts, tris, groups = [], 0, 0
    with open(p, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("v "):
                verts.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("f "):
                tris += max(len(line.split()) - 3, 0)
            elif line.startswith(("o ", "g ")):
                groups += 1
    m = {"vertices": len(verts), "tris": tris, "groups": groups, "animations": []}
    if verts:
        lo = [min(v[i] for v in verts) for i in range(3)]
        hi = [max(v[i] for v in verts) for i in range(3)]
        m.update(bounds={"min": lo, "max": hi}, size=[round(b - a, 5) for a, b in zip(lo, hi)])
    return m


def measure_file(p: Path) -> tuple[str, dict]:
    k = kind_of(p)
    m = {"bytes": p.stat().st_size}
    try:
        if k == "image":
            m.update(image_metrics(p))
        elif k == "audio":
            m.update(audio_metrics(p))
        elif k == "model":
            m.update(obj_metrics(p) if p.suffix.lower() == ".obj" else gltf_metrics(gltf_json(p)))
    except Exception as e:  # one unreadable file must not sink a manifest of thousands
        m["error"] = f"{type(e).__name__}: {e}"
    return k, m


def measure_paths(paths: list, root=None) -> dict:
    ps = [Path(p).resolve() for p in paths]
    for p in ps:
        if not p.exists():
            die(f"not found: {p}")
    if root:
        root = Path(root).resolve()
    elif len(ps) == 1 and ps[0].is_dir():
        root = ps[0]
    else:
        root = Path(os.path.commonpath([p if p.is_dir() else p.parent for p in ps]))
    files = []
    for p in ps:
        if p.is_file():
            files.append(p)
            continue
        for rel, f in _files(p, MEASURE_SKIP):
            if not _is_sidecar(f.name) and not (p == root and rel in MEASURE_SKIP_FILES):
                files.append(f)
    files = sorted(set(files))
    with ThreadPoolExecutor(min(16, os.cpu_count() or 4)) as ex:
        measured = list(ex.map(measure_file, files))
    assets = []
    for f, (k, m) in zip(files, measured):
        try:
            rel = f.relative_to(root).as_posix()
        except ValueError:
            die(f"{f} is outside --root {root}")
        assets.append({"id": rel, "path": rel, "kind": k, "metrics": m})
    return {"root": root.as_posix(), "measured_at": _now(), "assets": assets}


def cmd_measure(a):
    man = measure_paths(a.paths, a.root)
    if a.out:
        _write_json(Path(a.out), man)
        kinds = {}
        for x in man["assets"]:
            kinds[x["kind"]] = kinds.get(x["kind"], 0) + 1
        errs = sum(1 for x in man["assets"] if "error" in x["metrics"])
        print(f"{a.out}: {len(man['assets'])} files {kinds}" + (f", {errs} unreadable" if errs else ""))
    else:
        emit(man, True)


# --------------------------------------------------------------------------- compare

COMPARE = {
    "image": [("w", "lin"), ("h", "lin"), ("aspect", "lin"), ("bbox_w", "lin"), ("bbox_h", "lin"), ("mean_luminance", "lin")],
    "audio": [("duration_s", "lin"), ("peak_dbfs", "db"), ("loudness_lufs", "db"), ("channels", "lin")],
    "model": [("tris", "lin"), ("vertices", "lin"), ("size_x", "lin"), ("size_y", "lin"), ("size_z", "lin"),
              ("joints", "lin"), ("animation_count", "lin")],
}


def _metric(m: dict | None, key: str):
    if not m:
        return None
    if key == "aspect":
        return round(m["w"] / m["h"], 4) if m.get("w") and m.get("h") else None
    if key.startswith("size_"):
        s = m.get("size")
        return s["xyz".index(key[-1])] if s else None
    if key == "animation_count":
        return len(m["animations"]) if isinstance(m.get("animations"), list) else None
    v = m.get(key)
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def rel_delta(dirty, clean, mode: str = "lin"):
    """(clean - dirty) / |dirty|; dB metrics are compared as linear amplitude."""
    if dirty is None or clean is None:
        return None
    if mode == "db":
        dirty, clean = 10 ** (dirty / 20), 10 ** (clean / 20)
    if dirty == 0:
        return 0.0 if clean == 0 else float("inf")
    return (clean - dirty) / abs(dirty)


def compare_assets(remake: Path, dirty: Path, tol: float) -> list[dict]:
    entries = _read_json(remake / "assets.json")
    if not isinstance(entries, list):
        die(f"{remake / 'assets.json'} missing or not a list")
    man = _read_json(dirty / "manifest.json")
    if man is None:
        die(f"{dirty / 'manifest.json'} missing: run `um remake measure {dirty} --out {dirty / 'manifest.json'}`")
    droot = Path(man["root"]) if man.get("root") and Path(man["root"]).is_dir() else dirty
    by_id = {x["id"]: x for x in man.get("assets", [])}
    rows = []
    for e in entries:
        path = _rel(str(e.get("path", "")))
        cp = remake / path
        r = {"path": path, "brief": e.get("brief") or Path(path).stem, "ref": e.get("ref"), "generator": e.get("generator"),
             "clean_file": cp, "dirty_file": None, "kind": kind_of(cp), "clean": None, "dirty": None, "rows": [], "problems": []}
        if cp.is_file():
            r["kind"], r["clean"] = measure_file(cp)
        else:
            r["problems"].append("clean file missing")
        d = by_id.get(e.get("ref")) if e.get("ref") else None
        if e.get("ref") and not d:
            r["problems"].append(f"ref {e.get('ref')!r} not in dirty manifest")
        elif not e.get("ref"):
            r["problems"].append("no dirty ref")
        if d:
            r["dirty"], r["dirty_file"] = d["metrics"], droot / d["path"]
            if d["kind"] != r["kind"]:
                r["problems"].append(f"kind mismatch: dirty {d['kind']} vs clean {r['kind']}")
        for key, mode in COMPARE.get(r["kind"], []):
            dv, cv = _metric(r["dirty"], key), _metric(r["clean"], key)
            if dv is None and cv is None:
                continue
            delta = rel_delta(dv, cv, mode)
            r["rows"].append({"key": key, "dirty": dv, "clean": cv, "delta": delta, "flag": delta is not None and abs(delta) > tol})
        rows.append(r)
    return rows


def _href(target: Path, base: Path) -> str:
    try:
        return quote(os.path.relpath(target, base).replace("\\", "/"))
    except ValueError:  # another drive
        return target.resolve().as_uri()


def _pct(d) -> str:
    return "—" if d is None else "{:+.1%}".format(d)


def _fmt(v) -> str:
    return "—" if v is None else f"{v:.4g}" if isinstance(v, float) else str(v)


def _preview(kind: str, f: Path | None, m: dict | None, base: Path) -> str:
    if not f or not f.is_file():
        return "<div class=missing>missing</div>"
    src = html.escape(_href(f, base))
    if kind == "image":
        return f"<img src=\"{src}\" loading=lazy>"
    if kind == "audio":
        return f"<audio controls preload=none src=\"{src}\"></audio>"
    if kind == "model" and m:
        anims = ", ".join(f"{a['name']} {_fmt(a['duration_s'])}s" for a in m.get("animations") or []) or "none"
        return (f"<div class=stats>{m.get('tris')} tris · {m.get('vertices')} verts · {m.get('joints', 0)} joints<br>"
                f"size {m.get('size')}<br>animations: {html.escape(anims)}</div>")
    return f"<a href=\"{src}\">{html.escape(f.name)}</a>"


def _swatches(m: dict | None) -> str:
    pal = (m or {}).get("palette") or []
    return "".join(f"<span class=sw style=\"background:{p['hex']};flex:{max(p['share'], 0.02)}\" title=\"{p['hex']} {p['share']:.0%}\"></span>"
                   for p in pal)


def render_compare_html(game: str, rows: list[dict], out: Path, tol: float) -> str:
    base = out.parent
    cards = []
    for r in rows:
        flags = [x for x in r["rows"] if x["flag"]]
        trs = "".join(
            f"<tr class=\"{'flag' if x['flag'] else ''}\"><td>{x['key']}<td>{_fmt(x['dirty'])}<td>{_fmt(x['clean'])}"
            f"<td>{_pct(x['delta'])}</tr>" for x in r["rows"])
        pal = (f"<div class=pal><span>dirty</span><div class=bar>{_swatches(r['dirty'])}</div></div>"
               f"<div class=pal><span>clean</span><div class=bar>{_swatches(r['clean'])}</div></div>") if r["kind"] == "image" else ""
        probs = "".join(f"<li>{html.escape(p)}</li>" for p in r["problems"])
        cards.append(
            f"<section class=\"card{' flagged' if flags or r['problems'] else ''}\"><h2>{html.escape(r['brief'])} "
            f"<small>{html.escape(r['path'])} ← {html.escape(str(r['ref']))}</small></h2>"
            + (f"<ul class=probs>{probs}</ul>" if probs else "")
            + f"<div class=pair><figure><figcaption>dirty reference</figcaption>{_preview(r['kind'], r['dirty_file'], r['dirty'], base)}</figure>"
            f"<figure><figcaption>clean</figcaption>{_preview(r['kind'], r['clean_file'], r['clean'], base)}</figure></div>"
            f"{pal}<table><tr><th>metric<th>dirty<th>clean<th>Δ</tr>{trs}</table></section>")
    nflag = sum(1 for r in rows if any(x["flag"] for x in r["rows"]) or r["problems"])
    css = ("body{font:14px system-ui,sans-serif;background:#16161a;color:#ddd;margin:24px}h1{margin:0 0 4px}"
           ".card{background:#202026;border:1px solid #333;border-radius:8px;padding:12px 16px;margin:14px 0}"
           ".flagged{border-color:#c33}h2{font-size:16px;margin:0 0 8px}small{color:#888;font-weight:normal}"
           ".pair{display:flex;gap:16px}figure{margin:0;flex:1}figcaption{color:#999;font-size:12px}"
           "img{width:100%;max-width:320px;max-height:320px;object-fit:contain;image-rendering:pixelated;background:repeating-conic-gradient(#555 0 25%,#777 0 50%) 0 0/16px 16px}"
           "table{border-collapse:collapse;margin-top:8px}td,th{padding:2px 10px;text-align:right}td:first-child,th:first-child{text-align:left}"
           "tr.flag td{color:#f55;font-weight:bold}.pal{display:flex;align-items:center;gap:8px;margin-top:6px}.pal span{width:40px;color:#999}"
           ".bar{display:flex;height:18px;flex:1;max-width:480px}.sw{display:block;height:18px}.missing{color:#f55}.probs{color:#f80;margin:0 0 8px}"
           ".stats{font-family:monospace}")
    return (f"<!doctype html><meta charset=utf-8><title>{html.escape(game)}: clean vs dirty</title><style>{css}</style>"
            f"<h1>{html.escape(game)}: clean assets vs dirty references</h1>"
            f"<p>{len(rows)} assets · {nflag} flagged · tolerance ±{tol:.0%} · {_now()} · dirty-room file, do not copy into the remake</p>"
            + "".join(cards))


def _game_dirs(a) -> tuple[Path, Path]:
    dirty = Path(a.dirty).resolve() if a.dirty else DIRTY_ROOT / a.game
    remake = Path(a.remake).resolve() if a.remake else REMAKES_ROOT / a.game
    for name, d in (("dirty", dirty), ("remake", remake)):
        if not d.is_dir():
            die(f"{name} dir not found: {d}")
    return dirty.resolve(), remake.resolve()


def _inside(p: Path, d: Path) -> bool:
    try:
        p.resolve().relative_to(d.resolve())
        return True
    except ValueError:
        return False


def cmd_compare(a):
    dirty, remake = _game_dirs(a)
    out = Path(a.out).resolve() if a.out else dirty / "compare" / "index.html"
    if _inside(out, remake):
        die(f"refusing to write {out} inside the remake: the report references dirty files; keep it in the dirty room")
    rows = compare_assets(remake, dirty, a.tol)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_compare_html(a.game, rows, out, a.tol), encoding="utf-8")
    for r in rows:
        flags = [f"{x['key']} {x['delta']:+.0%}" for x in r["rows"] if x["flag"]]
        state = "FLAG" if flags or r["problems"] else "ok"
        print(f"  {state:4} {r['brief']:20} {r['path']}  <- {r['ref']}" + (f"   {', '.join(flags + r['problems'])}" if flags or r["problems"] else ""))
    print(f"{out.as_posix()}  ({sum(1 for r in rows if any(x['flag'] for x in r['rows']) or r['problems'])}/{len(rows)} flagged, tol {a.tol:.0%})")


# --------------------------------------------------------------------------- leak scan

LEAK_SKIP = {".godot", STATE, "exports", ".git", "addons/gd_remake"}
DIRTY_SKIP = {"compare", ".git"}
REMAKE_CODE = {".gd", ".cs", ".gdshader", ".gdshaderinc", ".py", ".json", ".tscn", ".tres"}
DIRTY_TEXT = {".c", ".cpp", ".cc", ".h", ".hpp", ".cs", ".java", ".txt", ".gd", ".lua", ".json", ".py", ".js", ".ts",
              ".glsl", ".hlsl", ".shader"}
COMMENT_STYLE = {".py": "hash", ".gd": "hash", ".lua": "lua", ".json": None, ".txt": None, ".tscn": None, ".tres": None}
SHINGLE = 12
MIN_IDENTICAL = 64
DHASH_MAX = 6
DHASH16_MAX = 12
_STR = r'("(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\')'
COMMENTS = {"c": re.compile(_STR + r"|//[^\n]*|/\*.*?\*/", re.S), "hash": re.compile(_STR + r"|#[^\n]*"),
            "lua": re.compile(_STR + r"|--\[\[.*?\]\]|--[^\n]*", re.S)}
TOKEN = re.compile(r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'|0[xX][0-9a-fA-F]+[uUlL]*'
                   r"|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?[fFdDuUlL]*|[A-Za-z_]\w*|[^\s\w]")
AUTO_ID = re.compile(  # matched against lowercased identifiers
    r"\w*_(?=[0-9a-f]*\d)[0-9a-f]{6,}"                          # FUN_00401000 DAT_.. LAB_.. s_text_00401000
    r"|(?:fun|dat|ptr|lab|sub|loc|off|unk|byte|word|dword|qword|switchd|cased|thunk|field|joined)_(?:0x)?[0-9a-f]+(?:_\w+)?"
    r"|(?:local|param|stack|var|arg)_(?:res)?[0-9a-f]+|(?:local|param|stack|var|arg)\d+|stack0x[0-9a-f]+"
    r"|(?:in|unaff|extraout)_\w+|[a-z]{1,4}var\d+|[av]\d+|(?:concat|sub|zext|sext|carry|scarry|sborrow)\d+|undefined\d*")
KEYWORDS = frozenset("""
if else elif elseif for foreach while do switch case default break continue return goto then end repeat until match
var let const func function def class struct enum union interface extends implements class_name signal static public
private protected internal virtual override abstract sealed readonly volatile extern inline typedef typename template
namespace using import from as new delete this self super base null nil none true false void int float double char
bool boolean short long unsigned signed string str byte uint ulong ushort sbyte decimal object in is not and or pass
lambda try catch except finally throw throws raise with yield await async local get set value out ref params sizeof
typeof auto register include define ifdef ifndef endif pragma print len range size_t int8 int16 int32 int64 uint8
uint16 uint32 uint64 float32 float64 vector2 vector3 export onready tool preload load
""".split())


def _num(t: str) -> str:
    t = t.rstrip("fFdDuUlL") if not t.lower().startswith("0x") else t.rstrip("uUlL")
    try:
        v = int(t, 16) if t.lower().startswith("0x") else float(t)
    except ValueError:
        return t
    return str(int(v)) if isinstance(v, int) or (v == v and abs(v) != float("inf") and v.is_integer()) else repr(v)


def tokens(text: str, style: str | None):
    """Normalized tokens with a content flag: lowercase, comments stripped, numbers canonical,
    decompiler-generated names (FUN_x, DAT_x, local_x, param_x, uVarN, v1...) collapsed to <id>."""
    if style:
        text = COMMENTS[style].sub(lambda m: m.group(1) if m.group(1) is not None else " ", text)
    for m in TOKEN.finditer(text):
        t = m.group(0)
        c = t[0]
        if c in "\"'":
            yield '"' + t[1:-1].lower() + '"', len(t) > 5
        elif c.isdigit() or (c == "." and len(t) > 1):
            n = _num(t)
            yield n, n not in ("0", "1", "2")
        elif c.isalpha() or c == "_":
            tl = t.lower()
            if AUTO_ID.fullmatch(tl):
                yield "<id>", False
            else:
                yield tl, len(tl) > 1 and tl not in KEYWORDS
        else:
            yield t, False


def shingles(toks, k: int = SHINGLE):
    """(hash, window) of every k-token window holding at least one content token."""
    win, flags, n = deque(maxlen=k), deque(maxlen=k), 0
    for tok, content in toks:
        if len(flags) == k:
            n -= flags[0]
        win.append(tok)
        flags.append(content)
        n += content
        if len(win) == k and n:
            yield hash(tuple(win)), win


_SCRIPT_SRC = re.compile(r'script/source\s*=\s*"((?:\\.|[^"\\])*)"', re.S)


def _code_parts(p: Path) -> list[tuple[str, str | None]]:
    text = p.read_text(encoding="utf-8", errors="replace")
    ext = p.suffix.lower()
    if ext in (".tscn", ".tres"):  # embedded GDScript lives in an escaped string
        parts = [(m.group(1).replace('\\"', '"').replace("\\\\", "\\"), "hash") for m in _SCRIPT_SRC.finditer(text)]
        return parts + [(_SCRIPT_SRC.sub(" ", text), None)]
    return [(text, COMMENT_STYLE.get(ext, "c"))]


def _file_tokens(p: Path):
    for text, style in _code_parts(p):
        yield from tokens(text, style)


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _gray(im):
    Image = _pil()
    im = im.convert("RGBA")
    bg = Image.new("RGBA", im.size, (128, 128, 128, 255))
    bg.alpha_composite(im)
    return bg.convert("L")


def dhash(gray, size=None, n: int = 8) -> int | None:
    """n*n-bit difference hash of a grayscale image (optionally resampled to `size` first, the way the
    other image was stored); None for near-flat images, which would match every other flat image."""
    Image, np = _pil(), need("numpy")
    if size and gray.size != tuple(size):
        gray = gray.resize(tuple(size), Image.Resampling.BILINEAR)
    a = np.asarray(gray.resize((n + 1, n), Image.Resampling.LANCZOS), dtype=np.int16)
    if a.std() < 2:
        return None
    return int.from_bytes(np.packbits(a[:, 1:] > a[:, :-1]).tobytes(), "big")


def image_hashes(gray, size=None) -> tuple[int, int] | None:
    h8 = dhash(gray, size)
    return None if h8 is None else (h8, dhash(gray, size, 16))


def image_match(a: tuple[int, int], b: tuple[int, int]) -> int | None:
    """Hamming distance of the 64-bit dHashes when they are within DHASH_MAX and the 256-bit dHashes agree
    too (within DHASH16_MAX): the finer hash drops flat silhouettes that merely share a shape."""
    d8 = (a[0] ^ b[0]).bit_count()
    return d8 if d8 <= DHASH_MAX and (a[1] ^ b[1]).bit_count() <= DHASH16_MAX else None


def _image_sig(p: Path) -> dict | None:
    try:
        with _pil().open(p) as im:
            g = _gray(im)
    except Exception:  # not decodable by Pillow (proprietary DDS variants etc.): nothing to compare
        return None
    h = image_hashes(g)
    return {"w": g.size[0], "h": g.size[1], "dhash": None if h is None else [f"{h[0]:016x}", f"{h[1]:064x}"]}


CACHE_VERSION = 2


class _LeakCache:
    """<dirty>/.leak_cache.json: sha256 and image signatures keyed by path, valid while size+mtime match."""

    def __init__(self, path: Path):
        self.path = path
        old = _read_json(path, {}) if path.exists() else {}
        self.files = old.get("files", {}) if old.get("version") == CACHE_VERSION else {}
        self.changed = False

    def entry(self, rel: str, p: Path) -> dict:
        st = p.stat()
        e = self.files.get(rel)
        if not e or (e.get("size"), e.get("mtime")) != (st.st_size, st.st_mtime_ns):
            e = self.files[rel] = {"size": st.st_size, "mtime": st.st_mtime_ns}
            self.changed = True
        return e

    def get(self, rel: str, p: Path, field: str, compute):
        e = self.entry(rel, p)
        if field not in e:
            e[field] = compute(p)
            self.changed = True
        return e[field]

    def save(self, live: set):
        stale = set(self.files) - live
        for rel in stale:
            del self.files[rel]
        if self.changed or stale:
            _write_json(self.path, {"version": CACHE_VERSION, "files": self.files})


def _path_needles(dirty: Path) -> list[bytes]:
    p = str(dirty.resolve())
    forms = {p, p.replace("\\", "/"), p.replace("/", "\\"), p.replace("\\", "\\\\")}
    if len(p) > 2 and p[1] == ":":
        rest = p[2:].replace("\\", "/")
        forms |= {f"/{p[0]}{rest}", f"/mnt/{p[0]}{rest}"}
    elif p.startswith("/mnt/") and len(p) > 6:
        forms |= {f"{p[5]}:{p[6:]}", f"{p[5]}:{p[6:]}".replace("/", "\\")}
    return sorted({f.lower().encode() for f in forms})


def leak_scan(remake: Path, dirty: Path, min_shared: int = 3) -> dict:
    remake, dirty = remake.resolve(), dirty.resolve()
    if _inside(remake, dirty) or _inside(dirty, remake):
        die(f"remake {remake} and dirty {dirty} must not contain each other")
    hits = []
    cache = _LeakCache(dirty / ".leak_cache.json")
    dfiles = [(rel, p) for rel, p in _files(dirty, DIRTY_SKIP) if rel not in MEASURE_SKIP_FILES]
    rfiles, symlinks = [], []
    for dp, dns, fns in os.walk(remake):
        rel = Path(dp).relative_to(remake).as_posix()
        rel = "" if rel == "." else rel + "/"
        dns[:] = [d for d in dns if rel + d not in LEAK_SKIP]
        for name in dns + fns:
            if os.path.islink(os.path.join(dp, name)):
                symlinks.append((rel + name, os.path.realpath(os.path.join(dp, name))))
        rfiles.extend((rel + f, Path(dp) / f) for f in fns if not os.path.islink(os.path.join(dp, f)))
    for rel, target in symlinks:
        if _inside(Path(target), dirty):
            hits.append({"kind": "symlink", "remake": rel, "dirty": Path(target).relative_to(dirty).as_posix(),
                         "detail": f"symlink into the dirty room ({target})"})
    # (a) byte-identical files
    by_size: dict[int, list] = {}
    for rel, p in dfiles:
        by_size.setdefault(p.stat().st_size, []).append((rel, p))
    for rel, p in rfiles:
        size = p.stat().st_size
        if size < MIN_IDENTICAL or size not in by_size:
            continue
        mine = _sha256(p)
        for drel, dp_ in by_size[size]:
            if cache.get(drel, dp_, "sha256", _sha256) == mine:
                hits.append({"kind": "identical", "remake": rel, "dirty": drel, "detail": f"sha256 {mine[:12]}"})
    # (b) near-duplicate images (dHash)
    dimgs = {rel: (p, cache.entry(rel, p)) for rel, p in dfiles if p.suffix.lower() in IMAGE_EXT}
    todo = [rel for rel, (_, e) in dimgs.items() if "img" not in e]
    with ThreadPoolExecutor(min(16, os.cpu_count() or 4)) as ex:
        for rel, sig in zip(todo, ex.map(lambda r: _image_sig(dimgs[r][0]), todo)):
            dimgs[rel][1]["img"] = sig
    cache.changed |= bool(todo)
    dsig = {rel: (tuple(int(x, 16) for x in e["img"]["dhash"]), (e["img"]["w"], e["img"]["h"]))
            for rel, (_, e) in dimgs.items() if e["img"] and e["img"].get("dhash")}
    by_dim: dict[tuple, list] = {}
    for rel, (h, wh) in dsig.items():
        by_dim.setdefault(wh, []).append((rel, h))
    for rel, p in rfiles:
        if p.suffix.lower() not in IMAGE_EXT or not dsig:
            continue
        try:
            with _pil().open(p) as im:
                g = _gray(im)
        except Exception:
            continue
        best = {}
        aspect = g.size[0] / g.size[1]
        # as is, and resampled to each dirty size of similar aspect (undoes nearest-neighbour upscales etc.)
        for wh in [None] + [wh for wh in by_dim if wh != g.size and abs(wh[0] / wh[1] - aspect) <= 0.1 * aspect
                            and wh[0] * wh[1] <= 1 << 22]:
            mine_h = image_hashes(g, wh)
            if mine_h is None:
                continue
            for drel, dh in (((r, h) for r, (h, _) in dsig.items()) if wh is None else by_dim[wh]):
                d = image_match(mine_h, dh)
                if d is not None:
                    best[drel] = min(d, best.get(drel, 99))
        identical = {h["dirty"] for h in hits if h["remake"] == rel and h["kind"] == "identical"}
        for drel, d in sorted(best.items(), key=lambda kv: kv[1]):
            if drel not in identical:
                hits.append({"kind": "near-duplicate", "remake": rel, "dirty": drel, "detail": f"dHash hamming {d}"})
    # (c) shared normalized code shingles
    mine: dict[int, tuple] = {}
    owners: dict[int, set] = {}
    for rel, p in rfiles:
        if p.suffix.lower() not in REMAKE_CODE or rel == "assets.json":
            continue
        for h, win in shingles(_file_tokens(p)):
            owners.setdefault(h, set()).add(rel)
            mine.setdefault(h, tuple(win))
    if mine:
        for drel, dp_ in dfiles:
            if dp_.suffix.lower() not in DIRTY_TEXT:
                continue
            shared = {h for h, _ in shingles(_file_tokens(dp_)) if h in mine}
            per: dict[str, set] = {}
            for h in shared:
                for rel in owners[h]:
                    per.setdefault(rel, set()).add(h)
            for rel, hs in sorted(per.items()):
                if len(hs) >= min_shared:
                    sample = " ".join(mine[min(hs)])
                    hits.append({"kind": "code", "remake": rel, "dirty": drel,
                                 "detail": f"{len(hs)} shared {SHINGLE}-token shingles, e.g. `{sample}`"})
    # (d) absolute paths into the dirty room
    needles = _path_needles(dirty)
    for rel, p in rfiles:
        if p.stat().st_size > 32 << 20:
            continue
        data = p.read_bytes().lower()
        for n in needles:
            if n in data:
                hits.append({"kind": "path", "remake": rel, "dirty": None, "detail": f"contains {n.decode()}"})
                break
    cache.save({rel for rel, _ in dfiles})
    return {"remake": remake.as_posix(), "dirty": dirty.as_posix(), "remake_files": len(rfiles), "dirty_files": len(dfiles),
            "hits": hits}


def cmd_leak(a):
    dirty, remake = _game_dirs(a)
    res = leak_scan(remake, dirty, a.min_shared)
    if a.json:
        emit(res, True)
    else:
        print(f"leak scan: {res['remake']} ({res['remake_files']} files) vs {res['dirty']} ({res['dirty_files']} files)")
        for h in res["hits"]:
            print(f"  {h['kind'].upper():14} {h['remake']}" + (f"  ~  {h['dirty']}" if h["dirty"] else "") + f"  ({h['detail']})")
        print(f"{len(res['hits'])} hit{'s' * (len(res['hits']) != 1)}" + ("" if res["hits"] else ": clean"))
    sys.exit(1 if res["hits"] else 0)


# --------------------------------------------------------------------------- init / export / serve

PROJECT_GODOT = """; Engine configuration file.
; It's best edited using the editor UI and not directly,
; since the parameters that go here are not all obvious.
;
; Format:
;   [section] ; section goes between []
;   param=value ; assign values to parameters

config_version=5

[application]

config/name="{name}"
config/features=PackedStringArray("4.7", "GL Compatibility")

[rendering]

renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
"""
MAIN_TSCN = '[gd_scene format=3]\n\n[node name="Main" type="Node2D"]\n'
WEB_PRESET = """[preset.{i}]

name="Web"
platform="Web"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="exports/web/index.html"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false
script_export_mode=2

[preset.{i}.options]

custom_template/debug=""
custom_template/release=""
variant/extensions_support=false
variant/thread_support=false
vram_texture_compression/for_desktop=true
vram_texture_compression/for_mobile=false
html/export_icon=true
html/custom_html_shell=""
html/head_include=""
html/canvas_resize_policy=2
html/focus_canvas_on_start=true
html/experimental_virtual_keyboard=false
progressive_web_app/enabled=false
"""
GITIGNORE = [".godot/", ".gd_remake/", "exports/"]
_HEADER = re.compile(r"^\[([A-Za-z0-9_./ -]+)\]\s*$")


def _section(lines: list[str], section: str) -> tuple[int, int] | None:
    start = None
    for i, ln in enumerate(lines):
        m = _HEADER.match(ln)
        if m and start is not None:
            return start, i
        if m and m[1] == section:
            start = i
    return (start, len(lines)) if start is not None else None


def cfg_get(text: str, section: str, key: str) -> str | None:
    lines = text.splitlines()
    span = _section(lines, section)
    if span:
        for ln in lines[span[0] + 1:span[1]]:
            if ln.startswith(key + "="):
                return ln[len(key) + 1:]
    return None


def cfg_add(text: str, section: str, key: str, value: str) -> str:
    """Add key=value to a Godot ConfigFile section unless the key already exists there."""
    lines = text.splitlines()
    span = _section(lines, section)
    if span is None:
        return text.rstrip("\n") + f"\n\n[{section}]\n\n{key}={value}\n"
    s, e = span
    if any(ln.startswith(key + "=") for ln in lines[s + 1:e]):
        return text
    ins = e
    while ins > s + 1 and not lines[ins - 1].strip():
        ins -= 1
    lines.insert(ins, f"{key}={value}")
    if ins == s + 1:
        lines.insert(ins, "")
    return "\n".join(lines) + "\n"


def sync_tree(src: Path, dst: Path) -> tuple[int, int]:
    """Copy src over dst; delete dst files that src no longer has (keeping sidecars of files that still exist)."""
    copied = removed = 0
    keep = set()
    for rel, p in _files(src):
        keep.add(rel)
        d = dst / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        if not d.exists() or d.read_bytes() != p.read_bytes():
            shutil.copy2(p, d)
            copied += 1
    if dst.is_dir():
        for rel, p in _files(dst):
            if rel in keep or (_is_sidecar(p.name) and _asset_base(rel) in keep):
                continue
            p.unlink()
            removed += 1
    return copied, removed


def ensure_web_preset(root: Path) -> str:
    p = root / "export_presets.cfg"
    if not p.exists():
        p.write_text(WEB_PRESET.format(i=0), encoding="utf-8")
        return "created export_presets.cfg (Web)"
    text = p.read_text(encoding="utf-8")
    if re.search(r'^name="Web"\s*$', text, re.M):
        return ""
    idx = [int(x) for x in re.findall(r"^\[preset\.(\d+)\]", text, re.M)]
    p.write_text(text.rstrip("\n") + "\n\n" + WEB_PRESET.format(i=max(idx, default=-1) + 1), encoding="utf-8")
    return "added Web preset to export_presets.cfg"


def init_project(root: Path, name: str | None = None) -> list[str]:
    if not ADDON_SRC.is_dir():
        die(f"addon source missing: {ADDON_SRC}")
    root.mkdir(parents=True, exist_ok=True)
    log = []
    copied, removed = sync_tree(ADDON_SRC, root / "addons" / "gd_remake")
    log.append(f"addons/gd_remake: {copied} updated, {removed} removed")
    pg = root / "project.godot"
    if not pg.exists():
        pg.write_text(PROJECT_GODOT.format(name=(name or root.name).replace('"', '\\"')), encoding="utf-8")
        log.append("created project.godot")
    text = orig = pg.read_text(encoding="utf-8")
    if not cfg_get(text, "application", "run/main_scene"):
        if not (root / "main.tscn").exists():
            (root / "main.tscn").write_text(MAIN_TSCN, encoding="utf-8")
            log.append("created main.tscn")
        text = cfg_add(text, "application", "run/main_scene", '"res://main.tscn"')
    for k, v in AUTOLOADS.items():
        have = cfg_get(text, "autoload", k)
        if have is not None and have.strip('"') != v:
            log.append(f"warning: autoload {k} is {have}, expected \"{v}\" (left as is)")
        text = cfg_add(text, "autoload", k, f'"{v}"')
    if text != orig:
        pg.write_text(text, encoding="utf-8")
        log.append("updated project.godot (main scene / autoloads)")
    for d in ("tests/scenarios", "variants", "assets"):
        (root / d).mkdir(parents=True, exist_ok=True)
    acc = root / "acceptance.json"
    if not acc.exists():
        _write_json(acc, {"game": name or root.name, "boot_frames": 120, "checks": []})
        log.append("created acceptance.json")
    if not (root / "assets.json").exists():
        _write_json(root / "assets.json", [])
        log.append("created assets.json")
    gi = root / ".gitignore"
    have = gi.read_text(encoding="utf-8").splitlines() if gi.exists() else []
    add = [x for x in GITIGNORE if x not in have and x.rstrip("/") not in have]
    if add:
        gi.write_text("\n".join(have + add) + "\n", encoding="utf-8")
        log.append(f".gitignore: added {' '.join(add)}")
    msg = ensure_web_preset(root)
    if msg:
        log.append(msg)
    return log


def cmd_init(a):
    root = Path(a.dir).resolve()
    for line in init_project(root, a.name):
        print(line)
    print(f"ready: {root.as_posix()}  (next: write tests/scenarios/*.gd + acceptance.json, then `um remake check`)")


def _lan_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def _coop_handler(directory: str):
    from http.server import SimpleHTTPRequestHandler

    class Handler(SimpleHTTPRequestHandler):
        extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".wasm": "application/wasm", ".js": "application/javascript",
                          ".pck": "application/octet-stream", ".html": "text/html"}

        def __init__(self, *args, **kw):
            super().__init__(*args, directory=directory, **kw)

        def end_headers(self):
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

    return Handler


def cmd_serve(a):
    from http.server import ThreadingHTTPServer
    root = project_root(a.dir)
    web = root / "exports" / "web"
    index = web / "index.html"
    exe = godot_exe(a.godot) if (not a.no_export or a.with_server) else None
    if not a.no_export:
        msg = ensure_web_preset(root)
        if msg:
            print(msg)
        web.mkdir(parents=True, exist_ok=True)
        (root / "exports" / ".gdignore").touch()
        t0 = time.time()
        rc, log = _capture([exe, "--headless", "--path", str(root), "--export-release", "Web", index.as_posix()], timeout=900)
        (state_dir(root) / "export.log").write_text(log, encoding="utf-8")
        if rc != 0 or not index.is_file() or index.stat().st_mtime < t0 - 1:
            die(f"web export failed ({'timed out' if rc is None else f'exit {rc}'}):\n{_tail(log)}")
        print(f"exported {index.as_posix()}")
    elif not index.is_file():
        die(f"{index} missing: run without --no-export")
    child = None
    if a.with_server:
        log = state_dir(root) / "server.log"
        with open(log, "wb") as f:
            child = subprocess.Popen([exe, "--headless", "--path", str(root), "--", "--server", f"--port={a.server_port}"],
                                     stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                     **({} if os.name == "nt" else {"start_new_session": True}))
        print(f"game server pid {child.pid} on port {a.server_port} (log {log.as_posix()})")
    try:
        srv = ThreadingHTTPServer(("0.0.0.0", a.port), _coop_handler(str(web)))
    except OSError as e:
        if child:
            _kill_tree(child.pid)
        die(f"cannot listen on port {a.port}: {e}")
    lan = _lan_ip()
    q = f"?room=main&server={lan}:{a.server_port}"
    print(f"local: http://127.0.0.1:{a.port}/index.html{q}\nLAN:   http://{lan}:{a.port}/index.html{q}\nCtrl-C to stop", flush=True)

    def _stop(*_):
        raise KeyboardInterrupt

    for sig in ("SIGTERM", "SIGBREAK"):
        if hasattr(signal, sig):
            signal.signal(getattr(signal, sig), _stop)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
        if child:
            _kill_tree(child.pid)
            print(f"stopped game server pid {child.pid}")


# --------------------------------------------------------------------------- CLI


def register(sub):
    import argparse
    p = sub.add_parser("remake", help="Godot remakes: scenario checks, slice status, bridge, variants, asset metrics, leak scan",
                       description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cs = p.add_subparsers(dest="cmd", metavar="<cmd>")

    def cmd(name, help_, func, godot=False, project=True):
        q = cs.add_parser(name, help=help_)
        if project:
            q.add_argument("dir", help="remake project root (holds project.godot)")
        if godot:
            q.add_argument("--godot", help="Godot executable (default: $GODOT, S:/Godot/..., godot on PATH)")
        q.set_defaults(func=func)
        return q

    q = cmd("init", "scaffold or update a remake project (addon, autoloads, Web preset, skeletons)", cmd_init)
    q.add_argument("--name", help="game name (default: folder name)")
    q = cmd("check", "run scenario checks + the boot check headless; exit 1 if a required one fails", cmd_check, godot=True)
    q.add_argument("--slice", help="only checks of this slice")
    q.add_argument("--only", help="only this check id ('boot' = only the boot check)")
    q.add_argument("--timeout", type=float, default=30, help="per-case timeout in seconds")
    q.add_argument("--json", action="store_true")
    q = cmd("status", "per slice: implemented / checks_pass / integrated / played", cmd_status)
    q.add_argument("--json", action="store_true")
    q = cmd("played", "record that this revision was played (capture file must exist)", cmd_played)
    q.add_argument("--capture", required=True, help="recording or screenshot of the play session")
    q.add_argument("--note")
    q = cmd("grid", "render every case of a scenario side by side into one PNG (windowed)", cmd_grid, godot=True)
    q.add_argument("scenario", help="res://tests/scenarios/x.gd or a path to it")
    q.add_argument("--out", required=True)
    q.add_argument("--cell", help="cell size WxH (runner default 480x270)")
    q.add_argument("--at", type=float, help="screenshot after this many seconds at most")
    q = cmd("run", "launch the game detached (optionally with the JSON bridge)", cmd_run, godot=True)
    q.add_argument("--bridge", type=int, metavar="PORT", help="enable GdBridge on this port and wait for ping")
    q.add_argument("--headless", action="store_true")
    q.add_argument("--scene", help="res:// scene to run instead of the main scene")
    q.add_argument("--variant", action="append", default=[], metavar="SLOT=NAME", help="force a variant (repeatable)")
    q.add_argument("--wait", type=float, default=30, help="seconds to wait for the bridge")
    q = cs.add_parser("bridge", help="send one request to a running game's GdBridge")
    q.add_argument("port", type=int)
    q.add_argument("command", help="ping tree get set call eval action key frames wait screenshot quit")
    q.add_argument("args", nargs="*", help="key=value pairs (values parsed as JSON when valid) or one JSON object")
    q.add_argument("--timeout", type=float, default=60)
    q.set_defaults(func=cmd_bridge)
    q = cs.add_parser("variants", help="list or promote asset variants (variants/<slot>/<name>.<ext>)")
    vs = q.add_subparsers(dest="vcmd", metavar="<list|promote>")
    v = vs.add_parser("list", help="slots and their candidate names")
    v.add_argument("dir")
    v.add_argument("--json", action="store_true")
    v.set_defaults(func=cmd_variants_list)
    v = vs.add_parser("promote", help="move a variant to assets/<slot>.<ext> and drop the other candidates")
    v.add_argument("dir")
    v.add_argument("slot")
    v.add_argument("name")
    v.set_defaults(func=cmd_variants_promote)
    q = cs.add_parser("measure", help="image/audio/model metrics -> manifest (same for dirty and clean)")
    q.add_argument("paths", nargs="+")
    q.add_argument("--out", help="write the manifest here (else print it)")
    q.add_argument("--root", help="ids are relative to this dir (default: the single dir given, or the common parent)")
    q.set_defaults(func=cmd_measure)
    for name, help_, func in (("compare", "clean assets vs their dirty refs -> HTML in the dirty room", cmd_compare),
                              ("leak", "clean-room leak scan (identical files, near-duplicate images, shared code, paths)", cmd_leak)):
        q = cs.add_parser(name, help=help_)
        q.add_argument("game")
        q.add_argument("--dirty", help=f"dirty room (default {DIRTY_ROOT.as_posix()}/<game>)")
        q.add_argument("--remake", help=f"remake project (default {REMAKES_ROOT.as_posix()}/<game>)")
        q.set_defaults(func=func)
        if name == "compare":
            q.add_argument("--out", help="HTML path (default <dirty>/compare/index.html; never inside the remake)")
            q.add_argument("--tol", type=float, default=0.10, help="flag relative deltas above this (default 0.10)")
        else:
            q.add_argument("--json", action="store_true")
            q.add_argument("--min-shared", type=int, default=3, help="shared 12-token shingles that make a code hit")
    q = cmd("serve", "web export + static server with COOP/COEP headers (Ctrl-C stops)", cmd_serve, godot=True)
    q.add_argument("--port", type=int, default=8060)
    q.add_argument("--server-port", type=int, default=9080, help="game server port put in the printed URLs")
    q.add_argument("--no-export", action="store_true", help="serve the existing exports/web")
    q.add_argument("--with-server", action="store_true", help="also run the game headless with --server --port=<server-port>")
