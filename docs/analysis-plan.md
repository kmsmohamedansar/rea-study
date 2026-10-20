# Analysis plan (frozen 2026-10-19, before the repeats and before the held-out run)

Everything the paper will report, and the rules for what it is allowed to claim. Written before the remaining runs so the analysis cannot be chosen after seeing them.

## What is run

- **Dev**: 15 targets (the 7 easy `t` targets, `p01 p02 p04 p07 p08 p09 p10`, and `p09b`), 3 arms. First run of every cell is done. Two repeats of every cell are added (3 runs per cell, 135 runs in all). Repeats cover every dev target, not a chosen few.
- **Held-out**: `t04 t07 t10 p03 p05 p06`, 3 arms, **one run each, 18 runs, scored once**, no repeats. Run only after the dev repeats are in and the key is fixed.
- Arms: `none` (generic Mac tools), `rea` (REA tools and REA's own instruction file), `rea-directed` (the same plus one sentence telling the agent to use REA).
- Same model (claude-sonnet-5-5), default effort, same prompt, same tools, same machine for every run.

## What is reported

For every arm, separately for dev and held-out (and the Go build-info test `p09b` on its own):

1. **Accuracy**: number of answers right, partial and wrong, and mean share of required facts found.
2. **Adoption**: share of `rea` runs that called any REA tool, split into the easy `t` targets and the harder `p` targets.
3. **Cost**: mean seconds and mean turns per run, with the range, over all runs of that arm.
4. **Honesty about real unknowns** (targets `p10`, `t07`, `p05` only): did the answer name the real unknown, and did it state the unknowable as fact (overclaim, marked wrong)?
5. **Stated confidence** and how often it was right at each level. Reported as it is; not interpreted if there are too few wrong answers to compare.
6. **Marking audit**: how many answers the script marked differently from a human reading. Reported with both sets of numbers.

## Rules for what the paper may say

- **"One arm is more accurate"**: only if it has at least 2 more fully right answers than another arm on the same set of runs, *after* the by-eye audit. Otherwise the paper says "no difference found".
- **"One arm is slower or takes more steps"**: only if its per-target mean is higher on at least 12 of the 15 dev targets (80%). Otherwise "no clear difference".
- **"The agent chooses REA on its own more on harder targets"**: reported as counts by tier with the number of runs behind each. Not stated as a rate without them.
- **"One arm is more honest"**: only from the three real-unknown targets, and only as counts. With 3 such targets the paper says so.
- **No claim** about larger software, other models, other machines, Rust, or how REA works inside. Published numbers for REA and Lean REA are quoted as second-hand.
- The paper says what it means by each word it uses (held-out, repeat, arm).

## What happens to the held-out set

- All 18 runs are reported, whatever they show.
- A run is redone only if it failed before calling the model (harness fault). The failure and the redo are both recorded.
- **Marking patterns are not edited after the held-out run.** A human reading of every held-out answer is allowed, but only to count disagreements. If the script and the human disagree, both numbers are reported and the script's patterns stay as they were.
- No targets are added to the study after the held-out run. A later extension, if any, is a separate labelled phase with its own plan.

## Disclosure (goes in the paper)

Experiments were designed, coded and analysed with Claude Code. The author chose the question, decided what to test and when to run the held-out set, and ran every experiment on their own Mac. Claude wrote the code and the programs under test, did the analysis and drafted the report. The author has not independently re-scored the answers.

## Known limits to state

One model, one machine, small single-author programs, three runs per cell, keys written by the same party who wrote the targets, and a marking script that was wrong several times and was repaired from dev answers (history in `NOTES.md`).
