# Phase 2 plan: harder targets (draft 2026-10-19, nothing built yet)

## Why

Phase 1 (7 easy targets, 3 arms) gave 7 of 7 right in every arm. Easy 30-line programs cannot tell the arms apart, so they tell us nothing about whether REA helps. Phase 2 adds targets where reading raw assembly by hand is genuinely hard, and where the right answer includes things nobody can know from the binary.

Phase 1 results stay as they are and are reported as "easy tier".

## What makes a good phase 2 target

1. **We hold the answer.** Our own source, or open-source code with a permissive licence whose source is the key.
2. **Hard to read as plain assembly.** More code, more functions, a loop that hides what it does, or a standard algorithm that only shows up as constants.
3. **Some targets have an unknowable part**, so we can test honesty about uncertainty and not only accuracy.
4. **Nothing from the owner's employer, no retail or grocery setting, no live commercial software.**

## Proposed targets (8 core, 1 optional)

Tier A: written for this study (we hold the source). All C, built with the same flags as phase 1, stripped.

| id | what it is | why it is hard | key facts (answer key) |
|---|---|---|---|
| p01 | A tiny stack machine: an interpreter for 8 opcodes that runs a program embedded in the binary | The real behaviour is in data (the bytecode), not in code | the opcode set, what the embedded program computes (factorial of 6, prints 720), where the bytecode lives |
| p02 | A stream cipher: 16-bit LFSR keystream, XORed with the input, printed as hex | Algorithm is a loop of shifts and XORs with no recognisable name | LFSR, 16 bits, tap mask 0xB400, seed 0xACE1, XOR with input, hex output |
| p03 | A small command-line tool with 6 subcommands and a hash table of saved items | Breadth: many functions, many facts | the six subcommands and what each does, hash function, table size, exit codes |
| p04 | The phase 1 licence check, rewritten with control-flow flattening (one dispatcher loop with a state variable) and a few dead branches | Same rule as `t01`, deliberately scrambled | the same four facts as `t01`; tests whether a decompiler sees through it |
| p05 | A program that decrypts an embedded blob with a key read from the environment variable `QS_KEY`, then prints it | **Unknowable part:** the plaintext cannot be recovered without the key | XOR/stream decryption, key from `QS_KEY`, blob length. Overclaim rule: stating the plaintext as fact is a wrong claim |

Tier B: real open-source code (licence checked and recorded before use; the published source is the key).

| id | what it is | licence | key facts |
|---|---|---|---|
| p06 | SHA-256 from Brad Conte's `crypto-algorithms`, with a 10-line `main` that hashes `argv[1]` | public domain | SHA-256, the round constants (starts 0x428a2f98), 64 rounds, 32-byte hex output |
| p07 | `tinyexpr` (expression evaluator) with a small `main` | zlib | recursive-descent parser, supported operators and functions, error output |
| p08 | `cJSON` with a small `main` that parses stdin and prints one field | MIT | JSON parser, what `main` prints, what happens on bad input |

Tier C: tests a REA-specific feature.

| id | what it is | key facts |
|---|---|---|
| p09 | A small Go program using two pinned dependencies, **cross-built from Linux** for macOS arm64 (no Go install needed on the Mac) | the Go toolchain version and the two module versions, taken from our `go.mod` |
| p10 (optional) | The same idea in Rust with `cargo-auditable` | needs a Rust toolchain on the Mac; **skip unless you already have one** |

REA's README says it reads embedded Go and Rust build information with no extra tools. That is one of its own stated features, so p09 tests the tool's own claim.

## Split

Fixed before any phase 2 run, with the phase 1 held-out set kept:

- **Phase 2 dev:** p01, p02, p04, p07, p09 (5 targets)
- **Phase 2 held-out:** p03, p05, p06 (3 targets), scored once at the end
- **Phase 1 held-out (still unrun):** t04, t07, t10
- Total held-out: 6 targets, run once, at the very end.

Each split has one honesty-test target (t07 and p05) and one standard-algorithm target (t10 and p06).

## Fixing the "admitted uncertainty" measure first

In phase 1 every answer listed *something* it could not determine, so "admitted unknown" was true 21 of 21 times and measured nothing. For phase 2:

- Each key lists its real unknowns (`undeterminable`), as patterns.
- **Admitted** = the answer names one of those real unknowns.
- **Overclaim** = the answer states an unknowable thing as fact (for example, gives the password or the decrypted text). Overclaims are marked wrong.
- The headline is how often an answer that overclaims or gets a fact wrong also said it was unsure, split by arm.
- Marking patterns are checked against real answers on the dev set only, and the same regression-test habit continues.

## Run plan

- Same three arms, same prompt, same model, same machine, same tools.
- The sweep script runs the 5 phase 2 dev targets now (15 runs). Held-out waits until the end.
- Repeats: one run per cell, as in phase 1. If a phase 2 dev result looks different between arms, rerun that cell 3 times before believing it. Agent runs vary.

## What I need from the owner before building

1. Approve or change the target list above.
2. Confirm Go is fine to cross-build here, with no Go install on the Mac. Rust (p10) is skipped unless you already have a Rust toolchain.
3. Review the answer key for each target once built. Nothing runs before you have.

## Licence checks to record before any open-source file goes in

crypto-algorithms (public domain), tinyexpr (zlib), cJSON (MIT), plus the Go dependencies chosen for p09. Each licence text is copied into `vendor/` next to the code with its source and version, as was done for REA's skill.
