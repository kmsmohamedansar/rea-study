"""Draws the report's figures as SVG into paper/figures/.   python3 scripts/make_figures.py

Numbers come from paper/numbers.json (rebuilt from the run files by scripts/report_numbers.py), except the
'first marking' counts in figure 5, which are the counts written in NOTES.md at the time (the first-pass keys
are not kept). Colours: the three set-ups always use the same three categorical slots of the reference palette
(validated: all pairs pass colour-vision separation; aqua is below 3:1 on white, so every series is direct-labelled
and the report carries the same numbers as tables). Light surface only."""
import json, pathlib
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "figures"
N = json.loads((ROOT / "paper" / "numbers.json").read_text())

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
ARMS = ["none", "rea", "rea-directed"]
COLOR = {"none": "#2a78d6", "rea": "#eb6834", "rea-directed": "#1baf7a"}
LABEL = {"none": "Ordinary tools only", "rea": "With REA, left alone", "rea-directed": "With REA, told to use it"}
SHORT = {"none": "ordinary tools", "rea": "REA, left alone", "rea-directed": "REA, told to use it"}
FONT = "Inter, system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

class Svg:
    def __init__(self, w, h, title, desc):
        self.w, self.h, self.parts = w, h, []
        self.title, self.desc = title, desc
    def add(self, s): self.parts.append(s)
    def rect(self, x, y, w, h, fill, rx=0, stroke=None, sw=1):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{st}/>')
    def line(self, x1, y1, x2, y2, stroke=GRID, sw=1, extra=""):
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{extra}/>')
    def circle(self, cx, cy, r, fill, ring=True, stroke=None, sw=2):
        if ring: self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r + 2}" fill="{SURFACE}"/>')
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{st}/>')
    def text(self, x, y, s, size=12, fill=INK, anchor="start", weight="400", extra=""):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}"{extra}>{escape(s)}</text>')
    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
                f'font-family="{FONT}" role="img" aria-labelledby="t d"><title id="t">{escape(self.title)}</title>'
                f'<desc id="d">{escape(self.desc)}</desc><rect width="{self.w}" height="{self.h}" fill="{SURFACE}"/>')
        (OUT / name).write_text(head + "".join(self.parts) + "</svg>\n")

def legend(svg, x, y, arms=ARMS, gap=190):
    for i, a in enumerate(arms):
        svg.rect(x + i * gap, y - 9, 14, 10, COLOR[a], rx=2)
        svg.text(x + i * gap + 20, y, LABEL[a], 12, INK2)

def axis_pct(svg, x0, x1, y0, y1, ticks=(0, 25, 50, 75, 100)):
    for t in ticks:
        x = x0 + (x1 - x0) * t / 100
        svg.line(x, y0, x, y1, GRID)
        svg.text(x, y1 + 15, f"{t}%", 11, MUTED, "middle")

# ---------------------------------------------------------------- figure 1: how one run works
def fig1():
    s = Svg(760, 372, "How one run works", "Flow from a program with a known answer, through three set-ups, an agent in an empty folder, a saved record, to scoring against an answer key kept off the study machine.")
    s.text(24, 28, "Figure 1. How one run works", 15, INK, weight="600")
    s.text(24, 46, "Every run: one program, one fixed question, one set-up, one agent, one saved record.", 12, INK2)
    def box(x, y, w, h, title, lines, fill="#f1f0ec", stroke=GRID):
        s.rect(x, y, w, h, fill, rx=6, stroke=stroke)
        s.text(x + 10, y + 20, title, 12.5, INK, weight="600")
        for i, l in enumerate(lines): s.text(x + 10, y + 38 + i * 15, l, 11.5, INK2)
    def arrow(x1, y1, x2, y2):
        s.line(x1, y1, x2, y2, MUTED, 1.5, ' marker-end="url(#a)"')
    s.add(f'<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{MUTED}"/></marker></defs>')
    box(24, 70, 150, 92, "Program", ["Written by me, or open", "source. Names stripped.", "I know every right", "answer."])
    box(24, 178, 150, 70, "Question", ["The same text for", "every program and", "every set-up."])
    # three set-ups
    ys = {"none": 64, "rea": 140, "rea-directed": 216}
    notes = {"none": ["The Mac's ordinary", "command-line tools"], "rea": ["Plus REA (207 tools)", "and REA's own", "instructions"], "rea-directed": ["Same as above, plus", "one sentence: use REA"]}
    for a in ARMS:
        y = ys[a]; s.rect(214, y, 190, 66, "#ffffff", rx=6, stroke=COLOR[a], sw=2)
        s.rect(214, y, 6, 66, COLOR[a])
        s.text(230, y + 20, LABEL[a], 12.5, INK, weight="600")
        for i, l in enumerate(notes[a]): s.text(230, y + 37 + i * 14, l, 11.5, INK2)
        arrow(174, 116, 214, y + 33)
    box(446, 100, 136, 128, "Agent", ["Claude Sonnet 5.5,", "default effort.", "Empty folder holding", "only the program.", "Input closed."])
    for a in ARMS: arrow(404, ys[a] + 33, 446, 164)
    box(616, 70, 120, 96, "Saved record", ["The answer, the tools", "it called, seconds,", "turns, machine,", "versions."])
    arrow(582, 164, 616, 118)
    box(616, 186, 120, 70, "Scoring", ["In the cloud, against", "the answer key."])
    arrow(676, 166, 676, 186)
    s.rect(452, 272, 292, 70, "#ffffff", rx=6, stroke=GRID)
    s.text(464, 292, "The answer key is never on the study machine.", 12, INK, weight="600")
    s.text(464, 309, "Marks: right, partial or wrong; did it name a real", 11.5, INK2)
    s.text(464, 324, "unknown; did it state something unknowable.", 11.5, INK2)
    s.text(464, 339, "Then a person reads the answers behind any gap.", 11.5, INK2)
    arrow(676, 256, 676, 272)
    s.text(24, 290, "Repeated 3 times per question in development (135 runs).", 11.5, INK2)
    s.text(24, 306, "Held-out: 6 questions, once each (18 runs), at the very end.", 11.5, INK2)
    s.save("fig1-how-a-run-works.svg")

# ---------------------------------------------------------------- figure 2: accuracy
def fig2():
    h = N["heldout"]; au = N["heldout_audit"]["by_arm"]; d = N["dev"]
    panels = [("Development, marked by script", 45, {a: d[a]["right"] for a in ARMS}),
              ("Held-out, marked by script", 6, {a: h[a]["right"] for a in ARMS}),
              ("Held-out, after a person|read every answer", 6, {a: au[a]["eye"].get("right", 0) for a in ARMS})]
    s = Svg(760, 500, "Right answers by set-up", "Share of answers that were right, in three panels: development by script, held-out by script, and held-out after reading.")
    s.text(24, 28, "Figure 2. Share of answers that were fully right", 15, INK, weight="600")
    s.text(24, 46, "Each bar is one set-up. Labels give the count out of the runs in that panel.", 12, INK2)
    legend(s, 24, 70)
    x0, x1 = 230, 640; y = 100
    for title, n, vals in panels:
        parts = title.split("|")
        for k, part in enumerate(parts): s.text(24, y + 14 + k * 15, part, 12.5, INK, weight="600")
        s.text(24, y + 14 + len(parts) * 15, f"{n} runs per set-up", 11.5, MUTED)
        top = y; bot = y + 3 * 26 + 6
        axis_pct(s, x0, x1, top, bot)
        for i, a in enumerate(ARMS):
            by = y + 4 + i * 26; w = (x1 - x0) * vals[a] / n
            s.rect(x0, by, w, 16, COLOR[a], rx=3)
            s.text(x0 + w + 8, by + 12.5, f"{vals[a]} of {n}", 12, INK, weight="600")
        last_bot = bot; y = bot + 40
    s.text(24, last_bot + 46, "Held-out: three script misses were the script being too strict; none was too lenient (results/heldout-eye-audit.json).", 11, MUTED)
    s.save("fig2-accuracy.svg")

# ---------------------------------------------------------------- figure 3: does the agent choose REA
def fig3():
    t = N["dev_by_tier"]; rows = [
        ("7 easy questions (development)", t["easy_t"]["rea"]["called_rea"], t["easy_t"]["rea"]["n"]),
        ("7 harder questions (development)", t["harder_p"]["rea"]["called_rea"], t["harder_p"]["rea"]["n"]),
        ("Go build information (development)", t["p09b_buildinfo"]["rea"]["called_rea"], t["p09b_buildinfo"]["rea"]["n"]),
        ("6 questions (held-out)", N["heldout"]["rea"]["called_rea"], N["heldout"]["rea"]["n"])]
    s = Svg(760, 300, "How often the agent chose REA on its own", "Share of runs, with REA and its instructions available but not mentioned in the prompt, in which the agent called a REA tool.")
    s.text(24, 28, "Figure 3. How often the agent chose REA when left alone", 15, INK, weight="600")
    s.text(24, 46, "Runs where it called any REA tool, with REA and its instructions available but not mentioned in the prompt.", 12, INK2)
    x0, x1 = 270, 600; y = 78
    axis_pct(s, x0, x1, y, y + len(rows) * 40 + 6)
    for i, (lab, k, n) in enumerate(rows):
        by = y + 8 + i * 40
        s.text(24, by + 13, lab, 12.5, INK)
        w = (x1 - x0) * k / n
        s.rect(x0, by, w, 16, COLOR["rea"], rx=3)
        s.text(x0 + w + 8, by + 12.5, f"{k} of {n}", 12, INK, weight="600")
    s.text(24, y + len(rows) * 40 + 40, "When the prompt told it to use REA, it did in every run: 45 of 45 in development, 6 of 6 held-out.", 11.5, INK2)
    s.text(24, y + len(rows) * 40 + 58, "The Go question asked for compiler and library versions, which REA advertises it can read.", 11.5, INK2)
    s.save("fig3-adoption.svg")

# ---------------------------------------------------------------- figure 4: time and steps per question
def fig4():
    pt = N["dev_per_target"]; order = sorted(pt, key=lambda q: pt[q]["none"]["mean_s"])
    s = Svg(760, 640, "Seconds and turns per question", "Per-question mean seconds and mean turns for the three set-ups across the 15 development questions.")
    s.text(24, 28, "Figure 4. Time and steps on each of the 15 development questions", 15, INK, weight="600")
    s.text(24, 46, "Each dot is the mean of 3 runs (dots are nudged up and down so equal values stay visible). Sorted by ordinary-tools time; p09b is the Go build-information question.", 12, INK2)
    legend(s, 24, 70)
    top = 98; rowh = 28; bot = top + len(order) * rowh
    for title, key, x0, x1, mx, ticks, unit in (("Seconds per run", "mean_s", 70, 360, 100, (0, 25, 50, 75, 100), ""),
                                                 ("Turns per run", "mean_turns", 440, 730, 20, (0, 5, 10, 15, 20), "")):
        s.text(x0, top - 6, title, 12.5, INK, weight="600")
        for tk in ticks:
            x = x0 + (x1 - x0) * tk / mx
            s.line(x, top, x, bot, GRID); s.text(x, bot + 16, str(tk), 11, MUTED, "middle")
        for i, q in enumerate(order):
            cy = top + i * rowh + rowh / 2
            if key == "mean_s": s.text(24, cy + 4, q, 12, INK2)
            s.line(x0, cy, x1, cy, "#f1f0ec")
            for k, a in enumerate(ARMS):   # offset the three dots a little so equal values never hide each other
                v = pt[q][a][key]; x = x0 + (x1 - x0) * min(v, mx) / mx
                s.circle(x, cy + (k - 1) * 6, 4.5, COLOR[a])
    s.text(24, bot + 44, "The directed set-up took more turns than ordinary tools on all 15 questions and more than the left-alone set-up on 14.", 11.5, INK2)
    s.text(24, bot + 62, "The left-alone set-up was slower than ordinary tools on 13 of 15 questions, and about equal in turns (higher on 9 of 15).", 11.5, INK2)
    s.save("fig4-time-and-steps.svg")

# ---------------------------------------------------------------- figure 5: my marking was wrong
def fig5():
    # first marking counts are from NOTES.md at the time (first-pass keys are not kept); the final ones are from the run files
    first = {("Easy questions, development", 7): {"none": 6, "rea": 5, "rea-directed": 6},
             ("Harder questions, development", 6): {"none": 4, "rea": 5, "rea-directed": 4}}
    final_dev = {("Easy questions, development", 7): {a: 7 for a in ARMS}, ("Harder questions, development", 6): {a: 6 for a in ARMS}}
    au = N["heldout_audit"]["by_arm"]
    held_first = {a: au[a]["script"].get("right", 0) for a in ARMS}; held_final = {a: au[a]["eye"].get("right", 0) for a in ARMS}
    groups = [(k[0], k[1], first[k], final_dev[k], "First marking", "After reading and repairing") for k in first] + \
             [("Held-out questions", 6, held_first, held_final, "Script", "After a person read every answer")]
    s = Svg(760, 476, "My marking was wrong", "For each group and set-up, the share of answers marked right by the first marking, and after the answers were read and the marking repaired.")
    s.text(24, 28, "Figure 5. The marking was wrong, and only reading the answers showed it", 15, INK, weight="600")
    s.text(24, 46, "Share of answers marked right. Hollow dot: the first marking. Filled dot: after reading the answers.", 12, INK2)
    x0, x1 = 250, 600; y = 74
    top = y; bot = y + 3 * 112 - 18
    axis_pct(s, x0, x1, top, bot, (50, 60, 70, 80, 90, 100)) if False else None
    for tk in (50, 75, 100):
        x = x0 + (x1 - x0) * (tk - 50) / 50
        s.line(x, top, x, bot, GRID); s.text(x, bot + 15, f"{tk}%", 11, MUTED, "middle")
    for gi, (title, n, a_first, a_final, l1, l2) in enumerate(groups):
        gy = y + gi * 112
        s.text(24, gy + 14, f"{title} ({n} questions)" if gi < 2 else f"{title} ({n} questions, scored once)", 12.5, INK, weight="600")
        for i, a in enumerate(ARMS):
            cy = gy + 40 + i * 26
            s.text(24, cy + 4, SHORT[a], 12, INK2)
            f1 = 100 * a_first[a] / n; f2 = 100 * a_final[a] / n
            xa = x0 + (x1 - x0) * (f1 - 50) / 50; xb = x0 + (x1 - x0) * (f2 - 50) / 50
            if abs(xa - xb) > 0.5: s.line(xa, cy, xb, cy, MUTED, 2)
            s.circle(xa, cy, 5.5, SURFACE, ring=False, stroke=INK2, sw=2)
            s.circle(xb, cy, 5.5, COLOR[a], ring=False)
            s.text(x1 + 22, cy + 4, f"{a_first[a]} of {n} to {a_final[a]} of {n}" if a_first[a] != a_final[a] else f"{a_final[a]} of {n}, unchanged", 11.5, INK2)
    s.text(24, bot + 40, "Held-out: the script was too strict on 3 of 18 answers and never too lenient. Axis starts at 50%.", 11.5, INK2)
    s.text(24, bot + 58, "Development first-marking counts are the ones written in NOTES.md at the time; the key versions are not kept.", 11.5, MUTED)
    s.save("fig5-marking.svg")

# ---------------------------------------------------------------- figure 6: cost
def fig6():
    d, h = N["dev"], N["heldout"]
    s = Svg(760, 330, "Cost per run", "Mean cost per run, as the command-line tool reports it at API prices, for the three set-ups in development and in the held-out set.")
    s.text(24, 28, "Figure 6. Cost per run, as the tool reports it", 15, INK, weight="600")
    s.text(24, 46, "What each run would cost at API prices. I pay a flat Pro fee, so this measures work, not a bill.", 12, INK2)
    legend(s, 24, 70)
    x0, x1 = 230, 600; mx = 0.25; y = 100
    for tk in (0, 0.05, 0.10, 0.15, 0.20, 0.25):
        x = x0 + (x1 - x0) * tk / mx
        s.line(x, y, x, y + 2 * 96 + 8, GRID); s.text(x, y + 2 * 96 + 24, f"${tk:.2f}", 11, MUTED, "middle")
    for gi, (title, src, n) in enumerate((("Development", d, "45 runs each"), ("Held-out", h, "6 runs each"))):
        gy = y + gi * 96
        s.text(24, gy + 14, title, 12.5, INK, weight="600"); s.text(24, gy + 30, n, 11.5, MUTED)
        for i, a in enumerate(ARMS):
            by = gy + 6 + i * 26; v = src[a]["mean_usd"]; w = (x1 - x0) * v / mx
            s.rect(x0, by, w, 16, COLOR[a], rx=3)
            s.text(x0 + w + 8, by + 12.5, f"${v:.3f}", 12, INK, weight="600")
    s.save("fig6-cost.svg")

if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6): f()
    print("wrote", len(list(OUT.glob("*.svg"))), "figures to", OUT)
