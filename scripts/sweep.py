"""Runs every DEV target through all three arms. Skips runs already saved, keeps going if one fails.
  python3 scripts/sweep.py            run everything missing
  python3 scripts/sweep.py --dry-run  show what would run
Held-out targets are never run here: do those by hand, once, at the end."""
import argparse, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARMS = ["none", "rea", "rea-directed"]

def plan(raw_dir, repeats=1):
    """(target, arm, repeat) still to do. repeats = total runs wanted per cell (1 = just the first)."""
    dev = json.loads((ROOT / "targets" / "split.json").read_text())["dev"]
    name = lambda t, rep: f"{t}.json" if rep == 1 else f"{t}.r{rep}.json"
    return [(t, a, rep) for rep in range(1, repeats + 1) for t in dev for a in ARMS
            if not (raw_dir / "dev" / a / name(t, rep)).exists()]

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--raw-dir", default=str(ROOT / "results" / "raw"))
    ap.add_argument("--repeats", type=int, default=1, help="total runs per cell, e.g. 3 = the first run plus 2 repeats")
    a = ap.parse_args(argv)
    todo = plan(pathlib.Path(a.raw_dir), a.repeats)
    print(f"{len(todo)} runs to do")
    if a.dry_run:
        for t, arm, rep in todo: print(f"  {t} {arm}" + (f" (repeat {rep})" if rep > 1 else ""))
        return 0
    failed = []
    for i, (t, arm, rep) in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {t} {arm}" + (f" (repeat {rep})" if rep > 1 else ""), flush=True)
        cmd = [sys.executable, str(ROOT / "scripts" / "run.py"), t, arm, "--raw-dir", a.raw_dir, "--repeat", str(rep)]
        if subprocess.run(cmd).returncode != 0:
            failed.append((t, arm, rep))
    print(f"done. failed runs: {failed or 'none'}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
