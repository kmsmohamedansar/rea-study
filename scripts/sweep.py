"""Runs every DEV target through all three arms. Skips runs already saved, keeps going if one fails.
  python3 scripts/sweep.py            run everything missing
  python3 scripts/sweep.py --dry-run  show what would run
Held-out targets are never run here: do those by hand, once, at the end."""
import argparse, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARMS = ["none", "rea", "rea-directed"]

def plan(raw_dir):
    dev = json.loads((ROOT / "targets" / "split.json").read_text())["dev"]
    return [(t, a) for t in dev for a in ARMS if not (raw_dir / "dev" / a / f"{t}.json").exists()]

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--raw-dir", default=str(ROOT / "results" / "raw"))
    a = ap.parse_args(argv)
    todo = plan(pathlib.Path(a.raw_dir))
    print(f"{len(todo)} runs to do")
    if a.dry_run:
        for t, arm in todo: print(f"  {t} {arm}")
        return 0
    failed = []
    for i, (t, arm) in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {t} {arm}", flush=True)
        if subprocess.run([sys.executable, str(ROOT / "scripts" / "run.py"), t, arm, "--raw-dir", a.raw_dir]).returncode != 0:
            failed.append((t, arm))
    print(f"done. failed runs: {failed or 'none'}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
