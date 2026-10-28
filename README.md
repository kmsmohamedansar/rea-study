# REA study

An independent test of [REA](https://github.com/morluto/rea) ("Reverse Engineer Anything"), a free tool that lets an AI agent inspect programs it has no source code for. Two questions:

1. When an agent explains a program it has no source for, does REA make the explanation more correct?
2. When the agent cannot tell something from the program, does it say so, or make something up?

**Status (2026-10-20):** the experiments are complete and scored; the study is closed. The written report remains a draft.

## What was found, in one paragraph

On these small and medium programs, the study did not detect an accuracy benefit from REA (development 45, 44 and 45 of 45; held-out 5, 6 and 6 of 6 after the answers were read). Those near-ceiling scores do not establish equal accuracy on other programs. Left alone, the agent rarely chose REA. Told to use it, it took longer and more steps. When the prompt asked what could not be determined, every set-up said it could not recover a hidden secret; the study did not test whether agents would volunteer that uncertainty unprompted. See `CASE_STUDY.md` for the short version and `paper/report.md` for the full report.

## Read this first

| File | What it is |
|---|---|
| `CASE_STUDY.md` | Two-chapter short version with the claims ledger |
| `paper/report.md` | The full report (draft) |
| `HANDOFF.md` | Historical pre-study plan; its status and approval steps are no longer current |
| `paper/claims.md` | Every claim, the number behind it, where it comes from, how it was checked |
| `docs/analysis-plan.md` | What would be reported and what could be claimed, written before the repeats and the held-out run |
| `NOTES.md` | Dated log of every decision, mistake and repair |
| `docs/licences.md` | Every tool's licence and where it was read |

## Layout

```
targets/src/         the 20 programs (their comments state the answers; keep them off the machine that runs the agents)
targets/prebuilt/    the Go program, cross-built once
targets/THIRD_PARTY.md   code from other projects, with licences and file fingerprints
targets/split.json   which questions are development and which are held-out (contains no answers)
scripts/             build_targets.sh, run.py, sweep.py, heldout.py, score.py, results.py,
                     report_numbers.py, make_figures.py
results/raw/         one JSON record per run: answer, tools called, seconds, turns, machine, versions
results/exclusions.json, results/failed-heldout/   runs set aside, with the reason
results/heldout-eye-audit.json   a person's reading of all 18 held-out answers
paper/               report, claims ledger, figures (SVG), numbers.json
vendor/rea-skill/    REA's own instruction file, unchanged, with its MIT licence
tests/               72 tests
```

## What is not in this repo, and why

- **Nothing that needs the answer key kept private any more.** `targets/keys.json` was kept off the machine that ran the agents so they could not read it. It is included from the close of the study; `targets/keys-history.md` gives the fingerprints of every earlier version.
- **Built programs.** Build them with `scripts/build_targets.sh`.

## Reproducing

Needs a Mac (Apple silicon), Node 22 or newer, Java 21, Ghidra 12.1.4 with a decompiler for your architecture, Claude Code, and REA 6.7.0 (`npx -y rea-agents@6.7.0 mcp`). Do **not** run `rea setup`: REA is attached per run so the other set-up cannot see it.

1. Move `targets/src` out of the repo folder, then `SRC=/path/to/sources ./scripts/build_targets.sh`.
2. Development: `python3 scripts/sweep.py --repeats 3`.
3. Held-out, once: `python3 scripts/heldout.py --run-held-out-once`.
4. Score (needs the key): `python3 scripts/results.py`; rebuild every number: `python3 scripts/report_numbers.py`; redraw the figures: `python3 scripts/make_figures.py`.
5. Tests: `python3 -m unittest discover -s tests`.

`NOTES.md` explains the one deviation from the official tools: Ghidra's Mac download has no decompiler for Apple silicon, so it was built from source.

## Licence

Shared for viewing only, as in my Jev repo: see `LICENSE`. Third-party code keeps its own licence (`targets/THIRD_PARTY.md`, `vendor/rea-skill/LICENSE`).
