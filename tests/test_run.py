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
        self.assertFalse({t for t, _, _ in full} & held)
        (raw / "dev" / "rea").mkdir(parents=True); (raw / "dev" / "rea" / "t01.json").write_text("{}")
        self.assertEqual(len(sweep.plan(raw)), len(full) - 1); self.assertNotIn(("t01", "rea", 1), sweep.plan(raw))


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
    def test_p09b_really_finds_the_p09_binary(self):
        # run.main prints the command in a dry run and exits 0 only if it found a binary (it exits with a message otherwise)
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = run.main(["p09b", "rea-directed", "--dry-run"])
        self.assertEqual(code, 0)
        self.assertIn(run.BUILD_INFO, buf.getvalue()); self.assertIn(run.DIRECTED, buf.getvalue())
    def test_p09b_uses_p09_binary_and_is_in_dev(self):
        self.assertEqual(run.SAME_BINARY["p09b"], "p09")
        self.assertIn("p09b", json.loads((ROOT / "targets" / "split.json").read_text())["dev"])

class Stdin(unittest.TestCase):
    def test_agent_run_gets_closed_stdin_so_programs_reading_it_see_eof(self):
        from unittest import mock
        seen = {}
        def fake_run(cmd, **kw):
            seen.update(kw)
            class P: stdout = ""; stderr = ""; returncode = 0
            return P()
        with mock.patch.object(run.subprocess, "run", side_effect=fake_run):
            tmp = pathlib.Path(tempfile.mkdtemp())
            run.main(["t01", "none", "--raw-dir", str(tmp)])
        self.assertIs(seen.get("stdin"), run.subprocess.DEVNULL)

class AnswerIsLastMessageWithFooter(unittest.TestCase):
    FOOT = '{"confidence": 0.9, "could_not_determine": []}'
    def test_stream_keeps_every_assistant_text(self):
        lines = "\n".join(json.dumps(e) for e in [
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "the real answer\n" + self.FOOT}]}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "reply to a stale notification"}]}},
            {"type": "result", "result": "reply to a stale notification"}])
        result, tools, init, texts = run.parse_stream(lines)
        self.assertEqual(len(texts), 2)
    def test_late_junk_message_does_not_replace_the_answer(self):
        rec = {"raw": {"result": "reply to a stale notification"}, "assistant_texts": ["the real answer\n" + self.FOOT, "reply to a stale notification"]}
        text, earlier = results.answer_text(rec)
        self.assertTrue(earlier); self.assertIn("the real answer", text)
    def test_normal_run_uses_the_final_result(self):
        rec = {"raw": {"result": "answer\n" + self.FOOT}, "assistant_texts": ["thinking out loud", "answer\n" + self.FOOT]}
        self.assertEqual(results.answer_text(rec), ("answer\n" + self.FOOT, False))
    def test_old_records_without_texts_fall_back_to_the_final_result(self):
        self.assertEqual(results.answer_text({"raw": {"result": "x"}}), ("x", False))

class HeldOutRunner(unittest.TestCase):
    def test_plan_is_only_held_out_targets_and_skips_done(self):
        import heldout
        raw = pathlib.Path(tempfile.mkdtemp())
        held = json.loads((ROOT / "targets" / "split.json").read_text())["heldout"]
        full = heldout.plan(raw)
        self.assertEqual(len(full), len(held) * 3); self.assertEqual({t for t, _ in full}, set(held))
        (raw / "heldout" / "rea").mkdir(parents=True); (raw / "heldout" / "rea" / "t04.json").write_text("{}")
        self.assertEqual(len(heldout.plan(raw)), len(held) * 3 - 1)
    def test_nothing_runs_without_the_explicit_flag(self):
        import heldout, io, contextlib
        from unittest import mock
        raw = pathlib.Path(tempfile.mkdtemp())
        with mock.patch.object(heldout.subprocess, "run") as m, contextlib.redirect_stdout(io.StringIO()) as out:
            code = heldout.main(["--raw-dir", str(raw)])
        self.assertEqual(code, 0); m.assert_not_called(); self.assertIn("Nothing run", out.getvalue())
    def test_with_the_flag_every_run_is_marked_heldout_and_never_a_repeat(self):
        import heldout, io, contextlib
        from unittest import mock
        raw = pathlib.Path(tempfile.mkdtemp())
        class P: returncode = 0
        with mock.patch.object(heldout.subprocess, "run", return_value=P()) as m, contextlib.redirect_stdout(io.StringIO()):
            heldout.main(["--run-held-out-once", "--raw-dir", str(raw)])
        self.assertEqual(m.call_count, 18)
        for call in m.call_args_list:
            cmd = call.args[0]
            self.assertIn("--heldout", cmd); self.assertNotIn("--repeat", cmd)
    def test_sweep_never_touches_held_out(self):
        import sweep
        held = set(json.loads((ROOT / "targets" / "split.json").read_text())["heldout"])
        self.assertFalse({t for t, _, _ in sweep.plan(pathlib.Path(tempfile.mkdtemp()), 3)} & held)

class Exclusions(unittest.TestCase):
    @NEEDS_KEY
    def test_excluded_run_is_left_out_of_the_tables_but_listed(self):
        tmp = pathlib.Path(tempfile.mkdtemp()); raw = tmp / "raw"
        fake = tmp / "fake-claude"; fake.write_text(FAKE); fake.chmod(0o755)
        for rep in ("1", "2"):
            run.main(["t01", "none", "--repeat", rep, "--claude-cmd", str(fake), "--raw-dir", str(raw)])
        ex = tmp / "ex.json"; ex.write_text(json.dumps([{"target": "t01", "arm": "none", "repeat": 2, "reason": "stalled"}]))
        out = tmp / "out"; results.main(["--raw-dir", str(raw), "--out-dir", str(out), "--excl", str(ex)])
        md = (out / "summary.md").read_text()
        self.assertIn("## excluded runs", md); self.assertIn("stalled", md)
        self.assertEqual(json.loads((out / "dev.json").read_text())["summary"]["none"]["n"], 1)

class Repeats(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp()); self.raw = self.tmp / "raw"
        self.fake = self.tmp / "fake-claude"; self.fake.write_text(FAKE); self.fake.chmod(0o755)
    def go(self, *args):
        return run.main(list(args) + ["--claude-cmd", str(self.fake), "--raw-dir", str(self.raw)])
    def test_repeat_is_saved_under_its_own_name_and_marked(self):
        self.assertEqual(self.go("t01", "none"), 0)
        self.assertEqual(self.go("t01", "none", "--repeat", "2"), 0)
        a = json.loads((self.raw / "dev" / "none" / "t01.json").read_text())
        b = json.loads((self.raw / "dev" / "none" / "t01.r2.json").read_text())
        self.assertEqual((a["repeat"], b["repeat"]), (1, 2))
    def test_held_out_refuses_repeats(self):
        with self.assertRaises(SystemExit): self.go("t04", "none", "--heldout", "--repeat", "2")
    def test_sweep_plans_the_repeats_and_skips_done(self):
        import sweep
        dev = json.loads((ROOT / "targets" / "split.json").read_text())["dev"]
        self.assertEqual(len(sweep.plan(self.raw, 3)), len(dev) * 3 * 3)
        (self.raw / "dev" / "rea").mkdir(parents=True); (self.raw / "dev" / "rea" / "t01.r2.json").write_text("{}")
        self.assertEqual(len(sweep.plan(self.raw, 3)), len(dev) * 3 * 3 - 1)
        self.assertNotIn(("t01", "rea", 2), sweep.plan(self.raw, 3))
    @NEEDS_KEY
    def test_main_tables_use_first_runs_and_repeats_get_their_own_section(self):
        for rep in ("1", "2", "3"): self.go("t01", "rea", "--repeat", rep)
        out = self.tmp / "out"; results.main(["--raw-dir", str(self.raw), "--out-dir", str(out)])
        s = json.loads((out / "dev.json").read_text())["summary"]["rea"]
        self.assertEqual(s["n"], 1)
        md = (out / "summary.md").read_text()
        self.assertIn("## repeats", md); self.assertIn("| rea | 1 | 3 | 3 |", md)

unittest.main() if __name__ == "__main__" else None
