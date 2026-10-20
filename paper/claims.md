# Claims ledger

Every claim in the report appears here with the numbers behind it, where they come from, and how it was verified. Numbers come from `paper/numbers.json`, which `python3 scripts/report_numbers.py` rebuilds from the run files in `results/raw/`. To check a claim, run that script and open the path named in "Check" (written like `dev.none.right`).

How verified: **script** = produced by the marking script and the numbers script. **eye** = a person read the answers. **both** = both, and they were compared.

All runs: one model (`claude-sonnet-5-5`), default effort, Claude Code 2.1.295, REA 6.7.0, Ghidra 12.1.4, one Mac (`Darwin 27.0.0 arm64`; a MacBook Air, M4, 16 GB, as reported by the author after the runs, not recorded by the harness).

## A. What was run

| ID | Claim | Number | Check | Verified | Limits |
|---|---|---|---|---|---|
| C1 | 153 valid runs were scored: 135 development runs (15 questions, 3 arms, 3 runs each) and 18 held-out runs (6 questions, 3 arms, 1 run each). | 153, 135, 18 | `runs.*` | script | The 15 development questions use 14 programs: the Go program is asked twice (`p09`, `p09b`). |
| C2 | Two further runs were set aside and 12 held-out runs failed before the model was called. All are kept in the repo and listed. | 2, 12 | `runs.excluded_stalls`, `runs.failed_before_model_heldout`, `results/exclusions.json`, `results/failed-heldout/README.md` | script | Replacement runs were made for both set-aside cells. |
| C3 | Every run used the same model, the same Claude Code version and the same REA version. | one value each | `environment.*`, `checks.claude_code_versions`, `checks.rea_versions` | script | One model, one machine. |
| C4 | In all 102 runs of the two REA arms the REA server was connected, all 207 REA tools were available, and REA's own instruction file was listed as loaded. In none of the 51 no-tool runs were any of these present. | 102 of 102; 0 of 51 | `checks.*` | script | "Listed as loaded" means the harness's start-up record names it, not that the agent read it. |
| C5 | No run ended in an error, none had a permission denied, and no answer contains refusal wording. One run's record carries `safety_stops = 1`; it ended normally and its answer is complete and right. | 0, 0, 0; 1 | `checks.runs_with_*` | script | The record does not say what caused the one safety count, and the report makes no claim about it. The refusal check is a word search, not a reading. |

## B. Accuracy

| ID | Claim | Number | Check | Verified | Limits |
|---|---|---|---|---|---|
| C6 | Development: the no-tool arm got 45 of 45 right, the natural REA arm 44 of 45 (one partial), the directed REA arm 45 of 45. | 45, 44+1, 45 | `dev.<arm>.right` | both | The one partial is a `p01` answer that never describes the conditional-jump operation. |
| C7 | Held-out, by script: right in 3, 5 and 6 of 6 (none, rea, rea-directed). After a person read all 18 answers: 5, 6 and 6 of 6. | 3/5/6 then 5/6/6 | `heldout.*.right`, `heldout_audit.by_arm`, `results/heldout-eye-audit.json` | both | The reading was done by the person who wrote the key. Three script misses were the script being too strict. |
| C8 | By the rule written before the run (a gap needs 2 or more fully right answers after the reading), there is **no accuracy difference** between arms. | largest gap 1 | `heldout_audit`, `docs/analysis-plan.md` | both | With the script's own grades the gap would have been 3. The reading is what removes it. |
| C9 | On the 7 easy and 7 harder development programs, accuracy was the same in every arm except one partial answer in the natural REA arm on a harder program. | 21/21, 21/21, 21/21 easy; 21, 20+1, 21 harder | `dev_by_tier.*` | script | Harder means harder than the easy set, not hard. |

## C. Whether the agent chooses REA

| ID | Claim | Number | Check | Verified | Limits |
|---|---|---|---|---|---|
| C10 | With REA's tools and instruction file available, the agent called a REA tool in 11 of 45 development runs and 0 of 6 held-out runs. | 11/45, 0/6 | `dev.rea.called_rea`, `heldout.rea.called_rea` | script | "Called" means any REA tool call appears in the run record. |
| C11 | On the 7 easy development programs it did so in 1 of 21 runs; on the 7 harder ones, 7 of 21; when asked for Go build information (`p09b`), 3 of 3. | 1/21, 7/21, 3/3 | `dev_by_tier.*.rea.called_rea` | script | Small counts. Three runs per cell. |
| C12 | When told in the prompt to use REA, it did in every run: 45 of 45 development, 6 of 6 held-out. | 45/45, 6/6 | `dev.rea-directed.called_rea` | script | That is the prompt working, not a finding about REA. |

## D. Time, steps and cost

| ID | Claim | Number | Check | Verified | Limits |
|---|---|---|---|---|---|
| C13 | Development, seconds per run: mean 26.3 (none), 37.0 (rea), 40.5 (rea-directed); median 24.4, 28.3, 34.8. | as stated | `dev.<arm>.mean_s`, `.median_s` | script | Wall-clock on one machine. Network and service speed vary. |
| C14 | By the rule written beforehand (same direction on at least 12 of 15 questions), the natural REA arm was slower than no-tool (13 of 15) and the directed arm slower than no-tool (15 of 15). Directed against natural: 11 of 15, so no clear difference. | 13, 15, 11 of 15 | `direction_rule_dev.seconds` | script | Per-question means of three runs. |
| C15 | Development, turns per run: mean 4.58, 6.53, 9.80. The directed arm took more turns than no-tool on 15 of 15 questions and than the natural REA arm on 14 of 15. Natural REA against no-tool: 9 of 15, no clear difference. | as stated | `dev.<arm>.mean_turns`, `direction_rule_dev.turns` | script | A turn is one round trip between the agent and the model. |
| C16 | The cost the command line reports per run (what the run would cost at API prices; the owner pays a flat Pro fee) averaged $0.088, $0.14 and $0.204 on development, and $0.074, $0.097 and $0.17 on held-out. | as stated | `dev.<arm>.mean_usd`, `heldout.<arm>.mean_usd` | script | Reported by the tool, not billed. Ratios (about 1.6 and 2.3 times the no-tool arm on development) are my arithmetic on those means. |
| C17 | Held-out, one run per cell, so descriptive only: mean seconds 19.0, 21.1, 30.9; mean turns 3.67, 3.67, 8.33. | as stated | `heldout.*`, `direction_heldout` | script | The natural REA arm never called REA on held-out, so its turns equal no-tool's on every question. |

## E. The Go build-information question

| ID | Claim | Number | Check | Verified | Limits |
|---|---|---|---|---|---|
| C18 | Asked directly for the Go version and the module versions (`p09b`), every arm got all four facts right in all three runs. | 3/3 each | `phase2b.*.right` | both | One program, build information left in. Says nothing about stripped build information or other languages. |
| C19 | The two REA arms took about 1.8 times as long and about 1.7 to 2 times as many turns as the no-tool arm for the same answers: 48.3 s and 9.7 turns (none), 85.4 s and 16.7 (rea), 84.8 s and 19.7 (rea-directed). | as stated | `phase2b.<arm>` | script | The ratios are my arithmetic. The Mac had no Go installed, so the no-tool arm could not use `go version -m`. |
| C20 | REA's own Go build-information tool was called in 4 runs. | 4 | `rea_tool_inspect_go_binary_runs` | script | Counts runs, across both Go questions and all arms. |

## F. Honesty about what cannot be known

| ID | Claim | Number | Check | Verified | Limits |
|---|---|---|---|---|---|
| C21 | On the three questions with a real unknown (a hidden decryption key, a stored hash), each arm named the unknown in all 5 runs and none stated the hidden text or the password. | 5/5 admitted, 0 overclaimed, per arm | `honesty.*`; quotes in section 5.5 are from the `p10` (development) and `p05` (held-out) answers in `results/raw/` | both | Five runs per arm, three questions. The patterns for "named the unknown" were repaired once on development answers; they were frozen before held-out, where a person read all six answers and agreed with the script. |
| C22 | Stated confidence ranged from 0.80 to 0.97 across all 153 runs, and every answer carried the confidence line. | 0.80 to 0.97 | `confidence.*` | script | One incomplete held-out answer (`p06`, no-tool) stated 0.93, the same as complete answers. One case, so it is not a calibration result. |

## G. What went wrong while measuring (process findings)

| ID | Claim | Number | Check | Verified | Limits |
|---|---|---|---|---|---|
| C23 | In every scoring round on development the first marking was wrong when answers were read. First pass against after repair: easy set (7 programs) none 6, rea 5, rea-directed 6 right of 7, then 7, 7, 7; harder set (6 programs) 4, 5, 4 of 6, then 6, 6, 6. | as stated | `NOTES.md`, sections dated 2026-10-19 | eye | Numbers are from the notes written at the time, not rebuilt by the script, because the first-pass keys are not kept in the repo. |
| C24 | In the three-run repeats, 8 of 135 runs were not fully right by script; on reading, 6 of those 8 were marking errors, one was a real partial, and one was the harness fault in C25. | 6, 1, 1 | `NOTES.md` | eye | Part of that reading changed the standard for one fact from "in a table" to "named anywhere in the answer"; this is stated openly in the notes. |
| C25 | Two runs stalled about 12 minutes (733.8 s and 733.4 s) because a program waited on the terminal for input. In one, the recorded final message was a reply to a stale notification, not the answer. Both are kept, listed with the reason, and replaced by new runs under a fixed harness. | 2 | `stall_runs`, `results/exclusions.json` | both | Cause read from the agent's own text and the records' API time (31 s, 23 s). |
| C26 | Twelve of the 18 held-out runs failed before the model was called because the owner's plan usage limit ran out. They were redone, the failed records kept unchanged with the reason. | 12 | `runs.failed_before_model_heldout`, `results/failed-heldout/README.md` | script | Only failure messages were read before the decision. |
| C27 | On held-out answers the script was too strict in 3 of 18 and never too lenient. | 3 of 18 | `heldout_audit.disagreements` | both | Judged by one reader, the author of the key. |

## H. Compared with the published benchmark (second-hand)

All figures in this section are quoted from `bench/BENCHMARK.md` in the repository `aicodeking/leanrea`, dated 2026-10-16, read on 2026-10-20. That benchmark was run by the author of a competing tool, on different targets (a commercial desktop app and the native add-on inside it, and the `gh` Go program), with REA 6.5.0, Claude Code 2.1.301, the same model, and no Ghidra. It is not our data.

| ID | Claim | Source number | Verified | Limits |
|---|---|---|---|---|
| C28 | It reports REA 75 of 75, the lean skill 74 of 75, and no skill 67 of 75, the no-skill gap coming from one refusal on one task. | 75, 74, 67 | read | Second-hand. Our runs had no refusals (C5). |
| C29 | It reports, over 12 runs per arm, REA taking 627 s, 124 turns and $3.36, against 479 s, 81 turns and $2.21 for no skill. | as stated | read | Second-hand. Their cost is theirs; ours is in C16. The ratios (about 1.3 for time, 1.5 for cost) are my arithmetic on their totals; ours were about 1.4 and 1.6 on development. Different programs, versions and set-up. |
| C30 | It reports a Go build-information lookup at 0.56 s with REA against 0.06 s with `go version -m`. | 0.56 s, 0.06 s | read | Second-hand, and measured outside an agent. |

## I. The tools and the code

| ID | Claim | Number | Check | Verified |
|---|---|---|---|---|
| C31 | Every tool's licence is recorded, with where it was read. | n/a | `docs/licences.md` | read |
| C32 | The study's code has 72 tests, all passing at the time of writing. | 72 | `python3 -m unittest discover -s tests` | script |

## Things the report does not claim

- That REA is bad, or good. It matched the no-tool arm on accuracy on these programs, which says nothing about programs much larger or harder.
- Anything about how REA works inside.
- Anything about other models, other machines, other languages (only one Go program was tested), or Rust.
- That confidence is well or badly calibrated. There are too few wrong answers.
- That a result would hold with a different prompt. The prompt was one fixed text.
- That the answer key is correct beyond its listed facts. It checks listed facts only. One answer was seen to state something wrong that the key does not test (a stack machine's print instruction described as not removing the value).
