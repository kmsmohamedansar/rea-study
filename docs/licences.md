# Licences of everything used (checked 2026-10-20)

Rule: the licence of every tool is checked and recorded before it is relied on. Each row says where the text was read. "Publisher's file" means the licence file in the publisher's own repository at the version named, not the copy installed on the study machine.

| What | Used for | Version | Licence | Where read |
|---|---|---|---|---|
| REA (`rea-agents`) | the tool under test | 6.7.0 | MIT, Copyright (c) 2026 morluto | `LICENSE` inside the npm package, and the repo file |
| REA's own instruction file ("skill") | loaded in the two REA arms | 6.7.0 | MIT, same package | copied unchanged to `vendor/rea-skill/` with its LICENSE |
| Ghidra | the decompiler REA drove | 12.1.4 | Apache License 2.0 | publisher's file at tag `Ghidra_12.1.4_build` |
| OpenJDK 21 (built as Eclipse Temurin 21.0.12.1) | Java runtime Ghidra needs | 21.0.12.1 | GPL version 2 with the Classpath Exception | OpenJDK `jdk21u` LICENSE (upstream). Not read from the installed Temurin copy |
| Node.js | runs REA | 26.8.1 | MIT-style licence ("Node.js is licensed for use as follows") | publisher's file on the main branch |
| Claude Code | runs the agent | 2.1.295 | Not open source. Used under the owner's Claude Pro plan terms | not applicable |
| Model | the agent | `claude-sonnet-5-5` | Used through the owner's Claude Pro plan | not applicable |
| Lean REA (`aicodeking/leanrea`) | **not run.** Only its published benchmark is cited, second-hand | n/a | MIT, Copyright (c) 2026 AICodeKing | repo file |
| crypto-algorithms (SHA-256), tinyexpr, cJSON, google/uuid, spf13/pflag | code inside five of the study's programs | see `targets/THIRD_PARTY.md` | public domain, zlib, MIT, BSD-3, BSD-3 | copied beside the code, with SHA-256 fingerprints of every file |

Fingerprints (first 16 hex of SHA-256) of the licence files read on 2026-10-20: Ghidra `c71d239df91726fc`, Node `3ebb7123f4d2b9b9`, OpenJDK `4b9abebc4338048a`, REA `798f9e4d18e49b30`.

## Not checked, and why that is stated

- The Temurin licence was read from OpenJDK upstream, not from the installed JDK folder's `legal/` directory. If the paper needs the installed copy, the owner can run `ls /Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home/legal/` and the file names can be added here.
- Claude Code and the model are commercial products used under the owner's own plan. No licence text was read for them.
