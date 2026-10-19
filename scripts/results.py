"""Scores every raw run and writes results/<split>.json and results/summary.md.
  python3 scripts/results.py [--raw-dir DIR] [--out-dir DIR]
Numbers come only from files in results/raw, each of which names its machine."""
import argparse, json, pathlib, statistics as st, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from score import score, parse_footer

ROOT = pathlib.Path(__file__).resolve().parent.parent

def answer_text(r):
    """The answer is the LAST assistant message that carries the JSON footer line. Normally that is the final result. If a late
    message (for example a reply to a stale background notification) replaced it, an earlier message holds the real answer.
    Records made before the harness kept every message only have the final result."""
    final = r["raw"].get("result", "")
    if parse_footer(final)[0] is not None:
        return final, False
    for t in reversed(r.get("assistant_texts") or []):
        if parse_footer(t)[0] is not None:
            return t, True
    return final, False

def collect(raw_dir):
    rows = []
    for f in sorted(raw_dir.glob("*/*/*.json")):
        r = json.loads(f.read_text()); raw = r["raw"]
        text, from_earlier = answer_text(r)
        s = score(r["target"], text)
        s["answer_not_last"] = from_earlier
        if raw.get("parse_error") is not None or raw.get("is_error") or r["exit"] != 0:
            s["grade"] = "failed"
        s.update(arm=r["arm"], split=r["split"], repeat=r.get("repeat", 1), wall_s=r["wall_s"], turns=raw.get("num_turns"),
                 cost_usd=raw.get("total_cost_usd"), tools_used=r.get("tools_used", {}),
                 rea_tools_available=r.get("rea_tools_available"), machine=r["machine"], model=r["model"])
        rows.append(s)
    return rows

def summarise(rows):
    out = {}
    for arm in sorted({r["arm"] for r in rows}):
        rs = [r for r in rows if r["arm"] == arm]
        wrong = [r for r in rs if r["grade"] in ("partial", "wrong")]
        right = [r for r in rs if r["grade"] == "right"]
        mean = lambda xs: round(st.mean(xs), 3) if xs else None
        out[arm] = {"n": len(rs), "right": len(right), "partial": sum(r["grade"] == "partial" for r in rs),
            "wrong": sum(r["grade"] == "wrong" for r in rs), "failed": sum(r["grade"] == "failed" for r in rs), "mean_fraction": mean([r["fraction"] for r in rs if r["grade"] != "failed"]),
            "footer_missing": sum(not r["footer_ok"] for r in rs),
            "not_right_admitted_unknown": sum(r["admitted_unknown"] for r in wrong),
            "not_right_total": len(wrong),
            "mean_conf_right": mean([r["confidence"] for r in right if r["confidence"] is not None]),
            "mean_conf_not_right": mean([r["confidence"] for r in wrong if r["confidence"] is not None]),
            "unknown_target_runs": sum(r["admitted_relevant"] is not None for r in rs),
            "unknown_admitted": sum(r["admitted_relevant"] is True for r in rs),
            "unknown_overclaimed": sum(r["admitted_relevant"] is not None and bool(r["forbidden_hits"]) for r in rs),
            "runs_that_called_rea": sum(any(k.startswith("mcp__rea") for k in r["tools_used"]) for r in rs),
            "runs_with_rea_available": sum(bool(r["rea_tools_available"]) for r in rs),
            "mean_wall_s": mean([r["wall_s"] for r in rs]), "mean_turns": mean([r["turns"] for r in rs if r["turns"]]),
            "total_cost_usd": round(sum(r["cost_usd"] or 0 for r in rs), 2)}
    return out

def repeats_section(rows):
    """Cells run more than once: how much do runs of the same cell differ? Counts every run of those targets."""
    cells = {}
    for r in rows: cells.setdefault((r["target"], r["arm"]), []).append(r)
    multi = {k: v for k, v in cells.items() if len(v) > 1}
    if not multi: return []
    L = ["## repeats (every run of targets that were run more than once)", "",
         "| arm | targets | runs | right | called REA | mean s (min-max) | mean turns (min-max) |", "|---|---|---|---|---|---|---|"]
    for arm in sorted({k[1] for k in multi}):
        rs = [r for (t, a), v in multi.items() if a == arm for r in v]
        ok = [r for r in rs if r["grade"] != "failed"]
        w = [r["wall_s"] for r in ok]; tu = [r["turns"] for r in ok if r["turns"]]
        called = sum(any(k.startswith("mcp__rea") for k in r["tools_used"]) for r in rs)
        L.append(f"| {arm} | {len({t for (t, a) in multi if a == arm})} | {len(rs)} | {sum(r['grade'] == 'right' for r in rs)} | {called} | "
                 f"{round(st.mean(w), 1)} ({min(w)}-{max(w)}) | {round(st.mean(tu), 1)} ({min(tu)}-{max(tu)}) |")
    L += ["", "Per target, natural `rea` arm: runs that called REA", "", "| target | called REA / runs |", "|---|---|"]
    for (t, a), v in sorted(multi.items()):
        if a == "rea": L.append(f"| {t} | {sum(any(k.startswith('mcp__rea') for k in r['tools_used']) for r in v)} / {len(v)} |")
    return L + [""]

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", default=str(ROOT / "results" / "raw"))
    ap.add_argument("--out-dir", default=str(ROOT / "results"))
    ap.add_argument("--excl", default=None, help="exclusions file (default results/exclusions.json)")
    a = ap.parse_args(argv)
    rows = collect(pathlib.Path(a.raw_dir)); out = pathlib.Path(a.out_dir); out.mkdir(exist_ok=True)
    excl_file = pathlib.Path(a.excl) if a.excl else ROOT / "results" / "exclusions.json"
    excl = json.loads(excl_file.read_text()) if excl_file.exists() else []
    gone = {(e["target"], e["arm"], e["repeat"]) for e in excl}
    excluded = [r for r in rows if (r["target"], r["arm"], r["repeat"]) in gone]
    rows = [r for r in rows if (r["target"], r["arm"], r["repeat"]) not in gone]
    lines = ["# Results", "", "Generated by scripts/results.py from results/raw. Machines named per row in the JSON files.", ""]
    for split in ("dev", "heldout", "phase2b"):
        sub = [r for r in rows if r["repeat"] == 1 and ((r["split"] == split and r["target"] != "p09b") or (split == "phase2b" and r["target"] == "p09b"))]
        if not sub: continue
        (out / f"{split}.json").write_text(json.dumps({"rows": sub, "summary": summarise(sub)}, indent=1))
        lines += [f"## {split}", "", "| arm | n | right | partial | wrong | failed runs | mean facts found | real-unknown runs: admitted / overclaimed | runs that called REA | mean s | mean turns |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for arm, s in summarise(sub).items():
            lines.append(f"| {arm} | {s['n']} | {s['right']} | {s['partial']} | {s['wrong']} | {s['failed']} | {s['mean_fraction']} | {s['unknown_admitted']} / {s['unknown_overclaimed']} of {s['unknown_target_runs']} | {s['runs_that_called_rea']} of {s['n']} (available in {s['runs_with_rea_available']}) | {s['mean_wall_s']} | {s['mean_turns']} |")
        lines.append("")
    lines += repeats_section(rows)
    if excluded:
        lines += ["## excluded runs (kept in results/raw, not counted above)", "", "| target | arm | repeat | seconds | grade as recorded | reason |", "|---|---|---|---|---|---|"]
        why = {(e["target"], e["arm"], e["repeat"]): e["reason"] for e in excl}
        for r in excluded:
            lines.append(f"| {r['target']} | {r['arm']} | {r['repeat']} | {r['wall_s']} | {r['grade']} | {why[(r['target'], r['arm'], r['repeat'])]} |")
        lines.append("")
    (out / "summary.md").write_text("\n".join(lines)); print("\n".join(lines)); return 0

if __name__ == "__main__":
    sys.exit(main())
