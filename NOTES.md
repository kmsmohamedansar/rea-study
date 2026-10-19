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
- (Superseded 2026-10-19, see below.) The REA arm used REA's MCP server only, without REA's instruction file ("skill").
- The `none` arm still has Bash, so it can run any tool installed on the Mac (objdump, strings, Ghidra if on PATH). Both arms share the machine; "no tool" means no REA, not no tools.
- The agent's Bash tool can in principle read the repo folder. Mitigation (done 2026-10-19): `targets/keys.json` is git-ignored and never pushed. BUT the source comments in `targets/src/*.c` state each program's behaviour (t07's comment even gives the password), so the run machine does hold the answers unless the sources are moved away after building: build, then move `targets/src` out of the cloned folder (e.g. `mv targets/src ~/rea-study-src`) before any run. The dev/held-out list moved to `targets/split.json`, which has none. Scoring happens where the key lives (the cloud session); raw results are committed on the Mac, carry no answers, and are pulled back. Tests that need the key skip when it is absent (9 of 13); fairness, prompt-leak, held-out-guard and unknown-target tests still run without it.
- Effort is recorded as "default": the CLI does not report which level it applied.

### How to run on the Mac (owner)
1. Move the sources out of the folder (their comments are the answers) and build from there: `mv targets/src ~/rea-study-src; SRC=~/rea-study-src ./scripts/build_targets.sh`.
2. Install Ghidra and Node 22+; do NOT run `rea setup`. Confirm `npx -y rea-agents@6.7.0 mcp` starts.
3. Run commands from inside the cloned folder. One dev target, both arms: `python3 scripts/run.py t01 none` then `python3 scripts/run.py t01 rea`; then read both answers by eye (`results/raw/dev/*/t01.json`, field `raw.result`) before running the rest. `results.py` needs the key, so it runs in the cloud session after you commit and push `results/raw`.

### 2026-10-19: Mac build verified (owner's run)
- Machine for all runs: Darwin 27.0.0 arm64 (the owner's Mac), Apple clang 21.0.0 (clang-2100.3.34.2).
- First build used `-s`, which macOS's linker ignores ("ld: warning: -s is obsolete"), so the programs still carried their function names. Caught from the warnings, fixed by a separate `strip` step plus `codesign -s -` on Darwin.
- After the fix, on the Mac: `nm targets/bin/t07_pwhash` lists only `__mh_execute_header` and the imported `_puts`; `strings ... | grep -i djb2` prints nothing; `t01_licence ABCD-EFGH-IJKD` prints `licence ok` (the re-signed program runs).
- Sources live outside the repo on the Mac (`~/rea-study-src`), built with `SRC=~/rea-study-src ./scripts/build_targets.sh`.
- Not done yet: Ghidra, Node 22+, REA launch check, first real run.

### 2026-10-19: Ghidra and REA set up on the Mac (owner's run)
- Installed: Node 26.8.1, Temurin JDK 21.0.12.1 (native arm64), Ghidra 12.1.4 PUBLIC (unzipped to ~/Downloads/ghidra_12.1.4_PUBLIC), REA 6.7.0 via `npx`. `rea setup` was NOT run; REA is attached per run through `--mcp-config`.
- Env vars in ~/.zshrc: `GHIDRA_INSTALL_DIR`, `JAVA_HOME` (the harness inherits them).
- **Deviation to state in the paper:** Ghidra's official 12.1.4 download ships decompilers for Linux x86_64 and Windows x86_64 only. REA's check failed ("Matching native decompiler for darwin/arm64 was not found"). Fix: built the decompiler from the source included in the same download, `make ghidra_opt ARCH_TYPE="-arch arm64" ADDITIONAL_FLAGS="-w" CXX="clang++ -std=c++11"` in `Ghidra/Features/Decompiler/src/decompile/cpp`, with Apple clang, then copied to `os/mac_arm_64/decompile`. Ghidra's Makefile hard-codes macOS as x86_64 (it has a TODO about arm64), hence the overrides. `file` reports Mach-O 64-bit executable arm64. This is not Ghidra's shipped binary; any difference in decompiler output on Apple silicon is a limit on the results. Build output: 3,262,120 bytes, 2026-10-19 15:22.
- `npx -y rea-agents@6.7.0 doctor --provider ghidra --json` after the build: `healthy: true`, Ghidra provider `available: true`, all Ghidra checks ok (platform darwin, arch arm64, version 12.1.4, headless, native decompiler arm64, JDK 21 accepted). Other engines (Hopper, IDA, JADX, Kuna) and client registrations report as missing: expected and intended.
- Not done yet: `claude` version/login check on the Mac, first real run (this also exercises Ghidra for the first time; REA notes the first Ghidra query starts the import lazily and has a startup deadline, `REA_GHIDRA_STARTUP_TIMEOUT_MS`).

### 2026-10-19: first real runs of t01 (owner's Mac); harness change from what they showed
- Smoke runs, not results: `t01` through both arms with the real `claude` 2.1.295. Both answers were fully correct (the scorer marks the no-tool one "right", 4 of 4 facts). The `rea` arm took 24.0 s and 3 turns, and its answer says it read the program with `otool -tvV`, so it is unclear that REA was available or used.
- Cause of the doubt: the first harness saved only the final text, so tool use was invisible. Changed `scripts/run.py` to read `--output-format stream-json --verbose` and save per run: which tools were called (`tools_used`), the MCP server status from the init event (`mcp_servers`) and how many REA tools were available (`rea_tools_available`). `results.py` now reports "runs that called REA" and "available in" per arm. Event shape checked against a real call to the CLI in this container (init event has `tools` and `mcp_servers`; result event has `result`, `num_turns`, `total_cost_usd`, `permission_denials`).
- Why it matters: without REA's instruction file ("skill"), the agent is not told to use REA and may just use Bash tools it already knows. If the `rea` arm rarely calls REA, the comparison measures nothing. That was flagged as a weakness earlier; this is the first evidence it may be real.
- Both arms' answers are near-identical on this easy target: expect ceiling effects (ties at full marks) on easy targets.

### 2026-10-19: REA arm now also gets REA's own skill
- Evidence from the Mac: `t01` rea arm with the new recording: REA connected (207 tools available, server `connected`, nothing denied) but `tools_used` was `{'Bash': 2}`: the agent never called REA. With only the MCP server and no instructions, the agent has no reason to prefer it over tools it already knows.
- Change: REA's own skill is vendored in `vendor/rea-skill/` (copied unchanged from npm `rea-agents@6.7.0`, `package/skills/reverse-engineer-anything/`, MIT, version 42, 207 tools, matches `rea doctor`). `run.py` copies it into the REA arm's throwaway run folder at `.claude/skills/` only; the no-tool arm never sees it, so nothing leaks through the global Claude config and `rea setup` is still not needed. Checked with the real CLI here: a skill in the working folder shows up in the init event's `skills` list. Tests: 14 pass, including one that the skill folder exists for `rea` and not for `none`.
- What the REA arm now means: REA's MCP server plus REA's own instructions, which is how its authors and the published benchmark use it. Same model, prompt, built-in tools and machine in both arms.
- Still true: the agent may still choose Bash tools over REA even with the skill. That is a result, and `tools_used` records it.

### 2026-10-19: skill loaded, agent still did not use REA; third arm added (before any scored run)
- Evidence from the Mac, `t01`, REA arm with MCP + skill: skill listed (`reverse-engineer-anything`), REA connected with 207 tools, nothing denied, 3 turns, 39.1 s, `tools_used` = `{'Bash': 2}`. The agent never called REA and never opened the skill. Two REA-arm smoke runs so far, both with zero REA calls (n = 2, one easy target: an anecdote, not a rate).
- Design change: two separate questions need two arms. `rea` measures whether the agent chooses REA on its own (adoption). New `rea-directed` measures what REA adds when used: identical to `rea` plus one sentence in the prompt ("Use the REA tools (the `rea` MCP server) to inspect the program."), inserted before the JSON-line instruction. `none` and `rea` prompts are unchanged and never contain it. Decided before any scored run, so it does not break "rules fixed before the first scored run".
- Phase 1 is now 10 targets x 3 arms = 30 runs.
- Bug caught by a test while adding it: the first version of docs/prompt.md quoted the new sentence, and the harness builds the base prompt from all quoted lines, so it leaked into every arm. Fixed by showing it indented. A test now checks the sentence appears in `rea-directed` only and that all three arms use the same tools and flags.
- Tests: 15 pass.

### 2026-10-19: rea-directed arm works on t01 (owner's Mac)
- `t01` rea-directed: exit 0, 37.4 s, 6 turns, nothing denied. `tools_used`: ToolSearch 1, `mcp__rea__open_binary`, `list_strings`, `list_procedures`, `procedure_assembly` (1 each). The agent had to find REA's tools through Claude Code's on-demand tool search (207 tools are deferred), which probably also dampens how often the `rea` arm picks REA. Answer correct (its text cites main at 0x100000460 and decodes the multiply-by-magic-constant modulo from the assembly).
- It asked for assembly only, not decompiled code, so this run did not exercise the Mac-built Ghidra decompiler. Provider used is not recorded in the run file; Ghidra is the only provider configured, so presumably Ghidra, but that is an inference.
- `scripts/sweep.py` runs every dev target through all three arms (21 runs), skipping saved ones. Held-out is never run by it.
