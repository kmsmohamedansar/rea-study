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
unittest.main() if __name__ == "__main__" else None
