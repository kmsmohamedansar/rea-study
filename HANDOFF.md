# Handoff: start here in a fresh session

Draft plan, 2026-10-19. Nothing built or measured yet. Owner approves before any
step runs.

## The question

When an AI agent explains a program it has no source code for, how often is the
explanation right, does a reverse-engineering tool make it righter, and when the
agent is wrong does it say it was unsure?

Second half matters more than the first. A confident wrong explanation is worse
than no explanation. This is the same question the owner's `decision-models`
project asked about models, asked again about agents.

## Why this is worth doing (checked 2026-10-19)

REA ("Reverse Engineer Anything", `morluto/rea`, MIT licence) is a tool that lets
an AI agent inspect programs without source code. It is popular and new.

One benchmark of it exists. It was run by the author of a competing tool
(`aicodeking/leanrea`) and published in that tool's own repository:

- 4 tasks, 3 repeats, 3 arms (REA, leanrea, no tool). 36 runs.
- Claude Code headless, Sonnet 5.5, macOS arm64.
- Graded against hand-made answer keys in `bench/tasks.json`.
- Scores: REA 75/75, leanrea 74/75, no tool 67/75 (one refusal).
- REA cost most and took longest: 627 s and $3.36, against 388 s and $2.17.

Its own stated limits: 3 repeats, one model, one machine, and **Ghidra, Hopper
and jadx were not installed**, so no task exercised a real decompiler. Answer
keys are tied to specific app versions.

Academic benchmarks for machine code and AI exist (BinMetric, Decompile-Bench,
REBench, REFORGE). They ask narrow questions: name this function, turn this back
into C. REFORGE's own argument is that most such papers are unclear about how
their answer key was built.

So the gaps are:

1. No independent test of REA. The only one is by a competitor.
2. No test with a decompiler actually installed, which is REA's main case.
3. Nothing at all on whether the agent admits what it could not work out.

Gap 3 is the owner's angle and the reason to do this rather than repeat (1).

**Before building:** search again for an independent REA evaluation. If one has
appeared, read it and ask the next question instead of this one.

## Rules

Carried over from the owner's portfolio plan, same as `decision-models`:

1. **No paid API or service.** Claude Pro is a subscription already held. Ghidra
   is free; Hopper and IDA are paid, so neither is used. REA's setup offers to
   install Hopper: decline it.
2. **Targets must be ones we hold the answer to.** Programs written for this
   study, open-source binaries where the source is public, or practice binaries
   with published solutions. No live commercial sites or apps. No retail,
   grocery or CPG setting. Nothing from the owner's employer.
3. **One model, both arms.** Only the tool changes between arms, never the
   model, the prompt or the machine. Otherwise the result measures nothing.
4. **Answer keys and scoring rules written and frozen before the first scored
   run.** Held-out targets scored once, at the end.
5. **Plain words. No em dashes. Jargon explained once.**
6. **Evidence.** Dated `NOTES.md`, screenshot each milestone, real output before
   any claim, failures recorded.
7. **Only numbers from runs in this repo, with the machine named.** Licence of
   every tool checked and recorded before use.
8. **Honesty about REA.** We test what it does in public. Never claim to know
   how it works inside. Same for leanrea.
9. **Don't touch the portfolio site until the owner says so.**

## Steps

1. **Targets and answer keys.** About 15 small programs written for this study,
   plus about 5 open-source binaries where the published source is the key. Each
   gets one question with a definite answer (how does it check the key, how many
   times does it retry, what is the file format's header). Write the answer and
   the marking rules first, in `targets/keys.json`. Strip symbols at build time.
   Split: two thirds for development, one third held out.
   **[owner]** review the keys before anything is run against them.

2. **Harness.** A script that runs one target through one arm and saves the raw
   answer. Arms: REA with Ghidra installed, leanrea, and no tool. Same model,
   same prompt, same machine, named in every result. Runs happen on the owner's
   Mac, since Ghidra and the targets live there.

3. **Marking.** A script that compares an answer against the key: right, partly
   right, wrong. Plus two things the agent must state in a fixed shape so they
   can be marked by code: its confidence, and what it could not determine.
   Marking is by script, not by eye, so it can be re-run and checked.

4. **Measure.** Per arm: score, time, turns, tokens. Then the calibration
   question, the same way `decision-models` did it: group answers by stated
   confidence and check how often each group was right. And the plain count that
   matters most: of the wrong answers, how many admitted uncertainty.

5. **Held-out set, scored once.** After every rule and prompt is frozen.

6. **Write-up.** Same shape as `paper/report.md`: abstract with the numbers,
   method, results, limits stated plainly, claims ledger. Publish the targets
   and the marking script so a reader can re-run it.

7. **[owner]** Approve before anything touches the portfolio site.

## Honest risks

- The method (make your own targets, keep the answer key) is the standard one.
  Someone else may run it first. The uncertainty angle is the part that is ours.
- Claude Pro has usage limits. 20 targets × 3 arms is 60 runs plus repeats. This
  will take days, not an evening. Keep the target count small rather than
  stretching the limits.
- If REA turns out to add little over no tool at all, that is the result and it
  gets published. Same as the keyword baseline in `decision-models`.

## Not decided

- Exact target list and what each program does.
- Whether to include leanrea as a third arm or keep it to two (REA, no tool).
  Three arms is a better paper and a third more runs.
- How the agent should state confidence so a script can read it.
