import json, os, pathlib, stat, subprocess, sys, tempfile, unittest
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import run, results

FAKE = """#!/bin/sh
case "$1" in --version) echo "fake-claude 0.0"; exit 0;; esac
cat <<'JSON'
{"type": "system", "subtype": "init", "tools": ["Bash", "mcp__rea__x"], "mcp_servers": [{"name": "rea", "status": "connected"}]}
{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash"}, {"type": "tool_use", "name": "mcp__rea__x"}]}}
{"type": "result", "result": "Checks 3 groups of uppercase letters; sum modulo 7.\\n{\\"confidence\\": 0.9, \\"could_not_determine\\": []}", "num_turns": 4, "total_cost_usd": 0.1}
JSON
"""

def setUpModule():
    subprocess.run([str(ROOT / "scripts" / "build_targets.sh")], check=True, capture_output=True)

import score as _score
NEEDS_KEY = unittest.skipUnless(_score.KEYS.exists(), 'answer key is not on this machine')
class T(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.fake = self.tmp / "fake-claude"; self.fake.write_text(FAKE); self.fake.chmod(0o755)
        self.raw = self.tmp / "raw"
    def go(self, *args):
        return run.main(list(args) + ["--claude-cmd", str(self.fake), "--raw-dir", str(self.raw)])

    def test_arms_differ_only_by_rea(self):
        n = run.build_cmd("none", "P", "m.json"); r = run.build_cmd("rea", "P", "m.json")
        self.assertEqual(n[:n.index("--allowedTools")], r[:r.index("--allowedTools")])
        self.assertIn("--mcp-config", r); self.assertNotIn("--mcp-config", n)
        self.assertEqual([x for x in r if x not in n], ["mcp__rea", "--mcp-config", "m.json"])
        self.assertIn("claude-sonnet-5-5", n); self.assertIn("--strict-mcp-config", n)

    def test_directed_arm_adds_one_sentence_and_nothing_else(self):
        base = run.load_prompt("/x/target", "rea")
        d = run.load_prompt("/x/target", "rea-directed")
        self.assertEqual(run.load_prompt("/x/target", "none"), base)
        self.assertIn(run.DIRECTED, d); self.assertNotIn(run.DIRECTED, base)
        self.assertEqual(d.replace(run.DIRECTED + " ", ""), base)
        a, b = run.build_cmd("rea", "P", "m.json"), run.build_cmd("rea-directed", "P", "m.json")
        self.assertEqual(a, b)

    def test_skill_goes_to_rea_arm_only(self):
        binary = next((ROOT / "targets" / "bin").glob("t01_*"))
        for arm, expect in (("none", False), ("rea", True), ("rea-directed", True)):
            w = pathlib.Path(tempfile.mkdtemp()); run.prepare_workdir(w, arm, binary)
            self.assertTrue((w / "target").exists())
            self.assertEqual((w / ".claude" / "skills" / "reverse-engineer-anything" / "SKILL.md").exists(), expect)

    def test_prompt_leaks_nothing(self):
        p = run.load_prompt("/x/target")
        self.assertIn("/x/target", p); self.assertIn("could_not_determine", p)
        self.assertNotIn("{PATH}", p)
        for word in ("licence", "retry", "djb2", "QSTK", "adler"): self.assertNotIn(word, p.lower())

    def test_heldout_guard(self):
        with self.assertRaises(SystemExit): self.go("t04", "none")
        with self.assertRaises(SystemExit): self.go("t01", "none", "--heldout")
        self.assertEqual(self.go("t04", "none", "--heldout"), 0)
        with self.assertRaises(SystemExit): self.go("t04", "none", "--heldout")
        self.assertEqual(self.go("t04", "rea", "--heldout"), 0)

    @NEEDS_KEY
    def test_end_to_end_to_summary(self):
        self.assertEqual(self.go("t01", "none"), 0); self.assertEqual(self.go("t01", "rea"), 0)
        rec = json.loads((self.raw / "dev" / "rea" / "t01.json").read_text())
        self.assertEqual(rec["rea_version"], "6.7.0"); self.assertIn("Linux", rec["machine"])
        self.assertEqual(rec["model"], "claude-sonnet-5-5")
        out = self.tmp / "out"; results.main(["--raw-dir", str(self.raw), "--out-dir", str(out)])
        s = json.loads((out / "dev.json").read_text())["summary"]
        self.assertEqual(s["none"]["right"], 1); self.assertEqual(s["rea"]["n"], 1)
        self.assertEqual(s["none"]["mean_turns"], 4)
        self.assertEqual(rec["tools_used"], {"Bash": 1, "mcp__rea__x": 1}); self.assertEqual(rec["rea_tools_available"], 1)
        self.assertEqual(s["rea"]["runs_that_called_rea"], 1)

    @NEEDS_KEY
    def test_broken_run_is_failed_not_wrong(self):
        bad = self.tmp / "bad-claude"; bad.write_text("#!/bin/sh\ncase \"$1\" in --version) echo v; exit 0;; esac\necho 'not json'; exit 1\n"); bad.chmod(0o755)
        run.main(["t01", "none", "--claude-cmd", str(bad), "--raw-dir", str(self.raw)])
        out = self.tmp / "out"; results.main(["--raw-dir", str(self.raw), "--out-dir", str(out)])
        s = json.loads((out / "dev.json").read_text())["summary"]["none"]
        self.assertEqual((s["failed"], s["right"], s["wrong"], s["not_right_total"]), (1, 0, 0, 0))

    def test_unknown_target_and_missing_binary(self):
        with self.assertRaises(SystemExit): self.go("t99", "none")

class Sweep(unittest.TestCase):
    def test_plan_covers_dev_only_and_skips_done(self):
        import sweep
        raw = pathlib.Path(tempfile.mkdtemp())
        full = sweep.plan(raw)
        dev = json.loads((ROOT / "targets" / "split.json").read_text())["dev"]
        self.assertEqual(len(full), len(dev) * 3)
        held = set(json.loads((ROOT / "targets" / "split.json").read_text())["heldout"])
        self.assertFalse({t for t, _ in full} & held)
        (raw / "dev" / "rea").mkdir(parents=True); (raw / "dev" / "rea" / "t01.json").write_text("{}")
        self.assertEqual(len(sweep.plan(raw)), len(full) - 1); self.assertNotIn(("t01", "rea"), sweep.plan(raw))


class Phase2b(unittest.TestCase):
    def test_build_info_sentence_is_p09b_only_and_in_every_arm(self):
        for arm in ("none", "rea", "rea-directed"):
            self.assertIn(run.BUILD_INFO, run.load_prompt("/x/target", arm, "p09b"))
            self.assertNotIn(run.BUILD_INFO, run.load_prompt("/x/target", arm, "p09"))
            self.assertNotIn(run.BUILD_INFO, run.load_prompt("/x/target", arm))
    def test_directed_arm_keeps_both_sentences_and_none_gets_no_rea_sentence(self):
        d = run.load_prompt("/x/target", "rea-directed", "p09b")
        self.assertIn(run.BUILD_INFO, d); self.assertIn(run.DIRECTED, d)
        self.assertLess(d.index(run.BUILD_INFO), d.index(run.DIRECTED))
        self.assertNotIn(run.DIRECTED, run.load_prompt("/x/target", "none", "p09b"))
        self.assertNotIn(run.DIRECTED, run.load_prompt("/x/target", "rea", "p09b"))
    def test_sentence_leaks_nothing(self):
        for word in ("go1", "uuid", "pflag", "golang", "1.24", "module path"):
            self.assertNotIn(word, run.BUILD_INFO.lower())
    def test_p09b_uses_p09_binary_and_is_in_dev(self):
        self.assertEqual(run.SAME_BINARY["p09b"], "p09")
        self.assertIn("p09b", json.loads((ROOT / "targets" / "split.json").read_text())["dev"])
unittest.main() if __name__ == "__main__" else None
