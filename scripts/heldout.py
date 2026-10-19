"""Runs the HELD-OUT targets, once each per arm. Deliberately separate from sweep.py.

  python3 scripts/heldout.py                         show the plan, run nothing
  python3 scripts/heldout.py --run-held-out-once     run everything not yet run

Never repeats, never overwrites (run.py refuses a held-out result that exists). A run that fails
before the model is called is a harness fault: tell the person doing the analysis, who moves the
failed record aside with the reason (see docs/analysis-plan.md) so that one cell can be redone."""
import argparse, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARMS = ["none", "rea", "rea-directed"]

def plan(raw_dir):
    held = json.loads((ROOT / "targets" / "split.json").read_text())["heldout"]
    return [(t, a) for t in held for a in ARMS if not (raw_dir / "heldout" / a / f"{t}.json").exists()]

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-held-out-once", action="store_true", help="actually run; without this nothing is run")
    ap.add_argument("--raw-dir", default=str(ROOT / "results" / "raw"))
    a = ap.parse_args(argv)
    todo = plan(pathlib.Path(a.raw_dir))
    print(f"{len(todo)} held-out runs still to do (each is scored once, no repeats)")
    for t, arm in todo: print(f"  {t} {arm}")
    if not a.run_held_out_once:
        print("\nNothing run. Add --run-held-out-once to run these.")
        return 0
    failed = []
    for i, (t, arm) in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {t} {arm}", flush=True)
        cmd = [sys.executable, str(ROOT / "scripts" / "run.py"), t, arm, "--heldout", "--raw-dir", a.raw_dir]
        if subprocess.run(cmd).returncode != 0:
            failed.append((t, arm))
    print(f"done. runs that did not exit 0: {failed or 'none'}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
