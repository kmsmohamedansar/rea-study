# Build notes

Dated log of what was done, what broke and what was measured.

## 2026-10-19

Plan drafted in HANDOFF.md. Nothing measured yet.

### Decisions
- Model: Sonnet 5.5 for every arm, so results sit next to the one published REA benchmark (by the author of Lean REA, run on Sonnet 5.5). Effort left at the default, and the default is recorded in each result because defaults change between versions.
- Scope: phase 1 only. 10 targets, two arms (REA, no tool), one run each. Third arm (Lean REA) and repeats only if phase 1 looks interesting.

### Step 1: targets and answer keys (drafted, owner review needed)
- 10 small C programs in `targets/src/`, each with one definite answer. `scripts/build_targets.sh` builds them stripped with identical flags; build on the Mac that runs the study.
- Checked here (Linux x86_64, gcc 13.3, this cloud container) that each program does what its comment says: licence ok and invalid cases, retry waits of 200/400/800/1600/2000 ms then give up, QSTK header parse, hidden QS_DIAG=7 switch, XOR 0x5A message decodes to `update.example.invalid`, rate limit 5 per 60 s, djb2 hash of the password is 0x16c91852, state order and exit code 3, timeout clamp to 300, Adler-32 of "Wikipedia" is 11e60398 (the well known value).
- `targets/keys.json`: required facts per target (regex alternatives), forbidden claims, things the binary cannot reveal. Split fixed now: 7 dev, 3 held-out (t04 hidden switch, t07 one-way hash, t10 standard algorithm). Held-out stays unread by the agent arms until the end.
- `scripts/score.py` marks an answer: fraction of required facts, forbidden hits, stated confidence, whether it admitted unknowns. `tests/test_score.py`: 7 tests pass (full marks, partial, forbidden claim, naming the password flat is wrong, admitting one-way hash is right, missing footer, key and split consistency).

### Known weaknesses (recorded before any run)
- Marking is by regex over free text. It can credit a fact mentioned in passing and miss a paraphrase. Mitigation: the owner reads a sample of marked answers by eye and we report how often the script and the eye disagree.
- All 10 programs are one author's, small and single-file; real software is messier. Open-source binaries are phase 2.
- One run per target per arm: no measure of run-to-run noise.
- Programs are C built with gcc -O1; results say nothing about Go, Rust or Electron targets.
- t07's "named the password flat" rule is a judgement call on what counts as admitting a guess.
- Held-out uses n = 3, so held-out numbers are an anecdote, not a statistic.

### Step 2: run harness and results (done, tested with a stub; not yet run against the real CLI)
- `scripts/run.py TARGET ARM` runs one target through `none` or `rea` with headless Claude Code (`claude -p`), model `claude-sonnet-5-5`, effort left at default, same built-in tools (Bash, Read, Glob, Grep) in both arms. The `rea` arm adds REA's MCP server, pinned to `rea-agents@6.7.0` (launch line `npx -y rea-agents@6.7.0 mcp`, from REA's own docs/installation.md). Each run happens in an empty temp folder with the binary copied as `target`, so the repo's CLAUDE.md, key and source are not in the agent's working folder. Raw result saved with machine, date, versions and wall time in `results/raw/` (not committed).
- Held-out guard: held-out targets are refused without `--heldout`, dev targets are refused with it, and a held-out result that already exists is never overwritten.
- `scripts/results.py` scores every raw run and writes `results/summary.md` and `results/<split>.json`. A run that crashed or returned unparseable output is graded `failed` and kept out of right/wrong counts, so a harness fault is never blamed on the agent. Found by a test: first version scored a broken run as "wrong".
- `python3 -m unittest discover -s tests`: 13 tests pass (this cloud container, Linux x86_64). They use a stub in place of `claude`, so they prove the harness logic, not the real CLI. First real run will be the real check.

### Known weaknesses added with the harness
- The REA arm uses REA's MCP server only. REA's own instruction file ("skill"), which the published benchmark's REA arm also used, is not loaded, because `rea setup` installs it globally and would leak into the `none` arm. Phase 2 can add it back with a separate config folder.
- The `none` arm still has Bash, so it can run any tool installed on the Mac (objdump, strings, Ghidra if on PATH). Both arms share the machine; "no tool" means no REA, not no tools.
- The agent's Bash tool can in principle read the repo folder. Mitigation (done 2026-10-19): `targets/keys.json` is git-ignored and never pushed. BUT the source comments in `targets/src/*.c` state each program's behaviour (t07's comment even gives the password), so the run machine does hold the answers unless the sources are moved away after building: build, then move `targets/src` out of the cloned folder (e.g. `mv targets/src ~/rea-study-src`) before any run. The dev/held-out list moved to `targets/split.json`, which has none. Scoring happens where the key lives (the cloud session); raw results are committed on the Mac, carry no answers, and are pulled back. Tests that need the key skip when it is absent (9 of 13); fairness, prompt-leak, held-out-guard and unknown-target tests still run without it.
- Effort is recorded as "default": the CLI does not report which level it applied.

### How to run on the Mac (owner)
1. `./scripts/build_targets.sh`, then move the sources out of the folder: `mv targets/src ~/rea-study-src` (the comments in them are the answers).
2. Install Ghidra and Node 22+; do NOT run `rea setup`. Confirm `npx -y rea-agents@6.7.0 mcp` starts.
3. Run commands from inside the cloned folder. One dev target, both arms: `python3 scripts/run.py t01 none` then `python3 scripts/run.py t01 rea`; then read both answers by eye (`results/raw/dev/*/t01.json`, field `raw.result`) before running the rest. `results.py` needs the key, so it runs in the cloud session after you commit and push `results/raw`.
