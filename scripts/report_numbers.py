"""Every number the report uses, computed from the run files. Writes paper/numbers.json and prints a summary.
The report and the claims ledger quote these; nothing is typed by hand.   python3 scripts/report_numbers.py"""
import json, pathlib, statistics as st, collections, glob, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import results

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARMS = ["none", "rea", "rea-directed"]
called = lambda r: any(k.startswith("mcp__rea") for k in r["tools_used"])
rnd = lambda x, n=1: None if x is None else round(x, n)

def load():
    rows = results.collect(ROOT / "results" / "raw")
    excl = {(e["target"], e["arm"], e["repeat"]) for e in json.loads((ROOT / "results" / "exclusions.json").read_text())}
    rows_all = rows
    rows = [r for r in rows if (r["target"], r["arm"], r["repeat"]) not in excl]
    raw = {}
    for f in glob.glob(str(ROOT / "results" / "raw" / "*" / "*" / "*.json")):
        j = json.loads(pathlib.Path(f).read_text()); raw[(j["target"], j["arm"], j.get("repeat", 1))] = j
    return rows_all, rows, excl, raw

def acc(rs): c = collections.Counter(r["grade"] for r in rs); return {"n": len(rs), "right": c["right"], "partial": c["partial"], "wrong": c["wrong"], "failed": c["failed"]}
def cost(rs, raw): 
    v = [raw[(r["target"], r["arm"], r["repeat"])]["raw"].get("total_cost_usd") for r in rs]; v = [x for x in v if x is not None]
    return {"mean_usd": rnd(st.mean(v), 3), "total_usd": rnd(sum(v), 2)} if v else {}
def speed(rs):
    w = [r["wall_s"] for r in rs]; t = [r["turns"] for r in rs if r["turns"]]
    return {"mean_s": rnd(st.mean(w)), "median_s": rnd(st.median(w)), "min_s": min(w), "max_s": max(w),
            "mean_turns": rnd(st.mean(t), 2), "median_turns": st.median(t), "min_turns": min(t), "max_turns": max(t)}

def main():
    rows_all, rows, excl, raw = load()
    dev = [r for r in rows if r["split"] == "dev"]; held = [r for r in rows if r["split"] == "heldout"]
    N = {}
    N["runs"] = {"valid_dev": len(dev), "valid_heldout": len(held), "valid_total": len(dev) + len(held),
                 "excluded_stalls": len(excl), "failed_before_model_heldout": len(glob.glob(str(ROOT / "results" / "failed-heldout" / "*" / "*.json"))),
                 "dev_targets": len({r["target"] for r in dev}), "heldout_targets": len({r["target"] for r in held}),
                 "runs_per_dev_cell": 3, "heldout_runs_per_cell": 1}
    N["environment"] = {"models": sorted({r["model"] for r in rows}), "machines": sorted({r["machine"] for r in rows})}
    for split, rs in (("dev", dev), ("heldout", held)):
        N[split] = {arm: {**acc([r for r in rs if r["arm"] == arm]), **speed([r for r in rs if r["arm"] == arm]), **cost([r for r in rs if r["arm"] == arm], raw),
                          "called_rea": sum(called(r) for r in rs if r["arm"] == arm)} for arm in ARMS}
    # tiers (dev): easy t-targets, harder p-targets, phase 2b on its own
    tiers = {"easy_t": lambda t: t.startswith("t"), "harder_p": lambda t: t.startswith("p") and t != "p09b", "p09b_buildinfo": lambda t: t == "p09b"}
    N["dev_by_tier"] = {name: {arm: {**acc([r for r in dev if r["arm"] == arm and f(r["target"])]),
                                     "called_rea": sum(called(r) for r in dev if r["arm"] == arm and f(r["target"]))} for arm in ARMS} for name, f in tiers.items()}
    # direction rule on dev, per-target means, 15 targets
    T = sorted({r["target"] for r in dev}); N["direction_rule_dev"] = {"targets": len(T), "needed": 12}
    for key, nm in (("wall_s", "seconds"), ("turns", "turns")):
        d = collections.defaultdict(list)
        for r in dev:
            if r[key]: d[(r["target"], r["arm"])].append(r[key])
        m = {k: st.mean(v) for k, v in d.items()}
        N["direction_rule_dev"][nm] = {f"{a}_higher_than_{b}": sum(m[(t, a)] > m[(t, b)] for t in T) for a, b in (("rea", "none"), ("rea-directed", "none"), ("rea-directed", "rea"))}
    # held-out direction, descriptive only
    TH = sorted({r["target"] for r in held}); N["direction_heldout"] = {}
    for key, nm in (("wall_s", "seconds"), ("turns", "turns")):
        m = {(r["target"], r["arm"]): r[key] for r in held}
        N["direction_heldout"][nm] = {f"{a}_higher_than_{b}": sum(m[(t, a)] > m[(t, b)] for t in TH) for a, b in (("rea", "none"), ("rea-directed", "none"))}
    # per-question means over the valid dev runs (for the figures)
    pq = collections.defaultdict(lambda: collections.defaultdict(lambda: {"s": [], "t": []}))
    for r in dev:
        pq[r["target"]][r["arm"]]["s"].append(r["wall_s"])
        if r["turns"]: pq[r["target"]][r["arm"]]["t"].append(r["turns"])
    N["dev_per_target"] = {t: {arm: {"mean_s": rnd(st.mean(v["s"])), "mean_turns": rnd(st.mean(v["t"]), 2), "runs": len(v["s"])} for arm, v in sorted(arms.items())} for t, arms in sorted(pq.items())}
    # adoption detail
    byt = collections.defaultdict(lambda: [0, 0])
    for r in dev:
        if r["arm"] == "rea": byt[r["target"]][0] += called(r); byt[r["target"]][1] += 1
    N["adoption_dev_rea_by_target"] = {t: f"{a}/{b}" for t, (a, b) in sorted(byt.items())}
    tools = collections.Counter(k for r in rows if r["arm"] != "none" for k in r["tools_used"] if k.startswith("mcp__rea"))
    N["rea_tools_most_used"] = [(k.replace("mcp__rea__", ""), v) for k, v in tools.most_common(8)]
    N["rea_tool_inspect_go_binary_runs"] = sum("mcp__rea__inspect_go_binary" in r["tools_used"] for r in rows)
    # honesty on real-unknown targets
    N["honesty"] = {}
    for split, rs in (("dev", dev), ("heldout", held)):
        N["honesty"][split] = {arm: {"runs": sum(r["admitted_relevant"] is not None for r in rs if r["arm"] == arm),
                                     "admitted": sum(r["admitted_relevant"] is True for r in rs if r["arm"] == arm),
                                     "overclaimed": sum(bool(r["forbidden_hits"]) for r in rs if r["arm"] == arm and r["admitted_relevant"] is not None)} for arm in ARMS}
    conf = [r["confidence"] for r in rows if r["confidence"] is not None]
    N["confidence"] = {"min": min(conf), "max": max(conf), "runs": len(conf), "footer_missing": sum(not r["footer_ok"] for r in rows)}
    # phase 2b
    p = [r for r in dev if r["target"] == "p09b"]
    N["phase2b"] = {arm: {"right": sum(r["grade"] == "right" for r in p if r["arm"] == arm), "runs": sum(r["arm"] == arm for r in p),
                          "mean_s": rnd(st.mean(r["wall_s"] for r in p if r["arm"] == arm)), "mean_turns": rnd(st.mean(r["turns"] for r in p if r["arm"] == arm and r["turns"]), 1)} for arm in ARMS}
    # held-out audit
    a = json.loads((ROOT / "results" / "heldout-eye-audit.json").read_text())
    N["heldout_audit"] = {"disagreements": a["disagreements"], "by_arm": {arm: {"script": dict(collections.Counter(x["script"] for x in a["runs"] if x["arm"] == arm)),
                                                                              "eye": dict(collections.Counter(x["eye"] for x in a["runs"] if x["arm"] == arm))} for arm in ARMS}}
    N["stall_runs"] = {"wall_s": [r["wall_s"] for r in rows_all if (r["target"], r["arm"], r["repeat"]) in excl]}
    # facts the report states about how the runs were set up, checked in every run record
    import re
    rea_runs = [raw[(r["target"], r["arm"], r["repeat"])] for r in rows if r["arm"] != "none"]
    none_runs = [raw[(r["target"], r["arm"], r["repeat"])] for r in rows if r["arm"] == "none"]
    refusal_words = re.compile(r"\b(I can(?:'|no)t (help|assist|do that)|I(?:'m| am) unable to (help|assist)|I won(?:'|)t (help|assist)|I must decline)\b", re.I)
    N["checks"] = {
        "runs_checked": len(rows),
        "rea_arm_runs": len(rea_runs),
        "rea_arm_runs_with_rea_skill_listed": sum("reverse-engineer-anything" in (j.get("skills_loaded") or []) for j in rea_runs),
        "rea_arm_runs_with_207_rea_tools": sum(j.get("rea_tools_available") == 207 for j in rea_runs),
        "rea_arm_runs_rea_server_connected": sum(any(m.get("name") == "rea" and m.get("status") == "connected" for m in (j.get("mcp_servers") or [])) for j in rea_runs),
        "none_arm_runs": len(none_runs),
        "none_arm_runs_with_rea_skill_listed": sum("reverse-engineer-anything" in (j.get("skills_loaded") or []) for j in none_runs),
        "none_arm_runs_with_rea_tools": sum((j.get("rea_tools_available") or 0) > 0 for j in none_runs),
        "runs_with_refusal_wording_in_answer": sum(bool(refusal_words.search(r2["raw"].get("result", ""))) for r2 in [raw[(r["target"], r["arm"], r["repeat"])] for r in rows]),
        "runs_with_is_error_true": sum(bool(raw[(r["target"], r["arm"], r["repeat"])]["raw"].get("is_error")) for r in rows),
        "runs_with_permission_denials": sum(bool(raw[(r["target"], r["arm"], r["repeat"])]["raw"].get("permission_denials")) for r in rows),
        "runs_with_safety_stops": sum(bool(raw[(r["target"], r["arm"], r["repeat"])]["raw"].get("safety_stops")) for r in rows),
        "claude_code_versions": sorted({raw[(r["target"], r["arm"], r["repeat"])]["claude_version"] for r in rows}),
        "rea_versions": sorted({str(raw[(r["target"], r["arm"], r["repeat"])]["rea_version"]) for r in rows if r["arm"] != "none"}),
    }
    pathlib.Path(ROOT / "paper" / "numbers.json").write_text(json.dumps(N, indent=1, default=list))
    print(json.dumps(N, indent=1, default=list))

if __name__ == "__main__":
    main()
