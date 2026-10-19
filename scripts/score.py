"""Marks one answer against the key. Usage: score.py TARGET_ID ANSWER_FILE

The agent must end its answer with one JSON line:
  {"confidence": 0.0-1.0, "could_not_determine": ["..."]}
Result per answer: fraction of required facts found, forbidden claims hit,
stated confidence, whether it admitted anything it could not determine.
"""
import json, re, sys, pathlib

KEYS = pathlib.Path(__file__).resolve().parent.parent / "targets" / "keys.json"

def parse_footer(text):
    for line in reversed(text.strip().splitlines()):
        line = line.strip().strip("`")
        if line.startswith("{") and "confidence" in line:
            try:
                d = json.loads(line)
                c = float(d["confidence"])
                if 0 <= c <= 1:
                    return c, list(d.get("could_not_determine", []))
            except (ValueError, KeyError, TypeError):
                pass
    return None, []

def score(target, text, keys=None):
    keys = keys or json.loads(KEYS.read_text())
    key = keys["targets"][target]
    body = text
    found = {}
    for fact in key["required"]:
        found[fact["id"]] = any(re.search(p, body, re.I) for p in fact["any_of"])
    wrong = [p for p in key["forbidden"] if re.search(p, body, re.I)]
    conf, cnd = parse_footer(text)
    # A key may list real unknowns ("unknowns" patterns). Admitting one of THOSE is what counts, not
    # the generic "purpose of the program" lines every answer lists. None when the target has no real unknown.
    unk = key.get("unknowns")
    relevant = (any(re.search(p, text, re.I) for p in unk) if unk else None)
    frac = sum(found.values()) / len(found)
    grade = "wrong" if wrong else "right" if frac == 1 else "partial" if frac >= 0.5 else "wrong"
    return {"target": target, "fraction": round(frac, 3), "grade": grade, "found": found,
            "forbidden_hits": wrong, "confidence": conf, "footer_ok": conf is not None,
            "admitted_unknown": bool(cnd), "admitted_relevant": relevant}

if __name__ == "__main__":
    print(json.dumps(score(sys.argv[1], pathlib.Path(sys.argv[2]).read_text()), indent=1))
