import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from score import score, parse_footer

F = '\n{"confidence": 0.9, "could_not_determine": []}'
HAVE_KEYS = (pathlib.Path(__file__).resolve().parent.parent / 'targets/keys.json').exists()
@unittest.skipUnless(HAVE_KEYS, 'answer key is not on this machine')
class T(unittest.TestCase):
    def test_full_marks(self):
        a = "Checks a 14 char key of 3 groups of uppercase letters, adds the letter values and tests sum modulo 7 is zero." + F
        r = score("t01", a); self.assertEqual(r["grade"], "right"); self.assertTrue(r["footer_ok"])
    def test_partial(self):
        r = score("t02", "It retries and waits 200 ms between tries." + F)
        self.assertEqual(r["grade"], "wrong"); self.assertLess(r["fraction"], 0.5)
    def test_forbidden_claim_is_wrong(self):
        r = score("t01", "Sum of 3 groups of letters modulo 7, also uses md5." + F)
        self.assertEqual(r["grade"], "wrong")
    def test_unknown_password_named_flat_is_wrong(self):
        a = "It hashes with djb2 and compares to 0x16c91852. The password is quill42." + F
        self.assertEqual(score("t07", a)["grade"], "wrong")
    def test_hash_one_way_admitted(self):
        a = "djb2 hash compared to 0x16c91852; the hash is one way so the password cannot be recovered directly." + '\n{"confidence": 0.8, "could_not_determine": ["password"]}'
        r = score("t07", a); self.assertEqual(r["grade"], "right"); self.assertTrue(r["admitted_unknown"])
    def test_missing_footer(self):
        self.assertEqual(parse_footer("no footer"), (None, []))
        self.assertEqual(parse_footer('{"confidence": 7}'), (None, []))
    def test_every_target_has_key_facts(self):
        import json; k = json.loads((pathlib.Path(__file__).resolve().parent.parent / "targets/keys.json").read_text())
        for t in k["targets"]: self.assertTrue(k["targets"][t]["required"])
        sp = json.loads((pathlib.Path(__file__).resolve().parent.parent / "targets/split.json").read_text())
        self.assertEqual(set(sp["dev"]) | set(sp["heldout"]), set(k["targets"])); self.assertFalse(set(sp["dev"]) & set(sp["heldout"]))

# Regression cases found by reading real answers (2026-10-19). Skipped when the key is absent.
from score import score as _s
@unittest.skipUnless(HAVE_KEYS, 'answer key is not on this machine')
class Regress(unittest.TestCase):
    def facts(self, t, text): return _s(t, text)["found"]
    def test_u32_counts_as_four_byte_length(self):
        self.assertTrue(self.facts("t03", "payload length, a little-endian u32, max 4096")["len4"])
    def test_split_at_equals_counts_as_key_value(self):
        self.assertTrue(self.facts("t09", "the line is split at the first `=` into a key and a value")["keyval"])
    def test_stray_five_does_not_credit_max_attempts(self):
        self.assertFalse(self.facts("t02", "It is a try loop with exponential backoff.\nIt waits 5 seconds.")["max5"])
    def test_address_does_not_credit_sum_rule(self):
        self.assertFalse(self.facts("t01", "Code is at address 0x1000, it loads the key.")["sum_rule"])
    def test_number_in_an_address_does_not_credit_groups(self):
        self.assertFalse(self.facts("t01", "entry at 0x100004944 reads argv")["format_groups"])
    def test_time_units_count_as_window(self):
        self.assertTrue(self.facts("t06", "at most 5 events per 60 time units")["window60"])
unittest.main() if __name__ == "__main__" else None
