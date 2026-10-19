# REA's own instruction file (skill), vendored

Copied unchanged from the npm package `rea-agents@6.7.0` (path `package/skills/reverse-engineer-anything/`), MIT licence, Copyright (c) 2026 morluto (see LICENSE). It is loaded in the REA arm only, by copying it into that run's throwaway working folder at `.claude/skills/`. The no-tool arm never sees it.

Why it is here: without it the agent is not told to use REA and, in our first test, used only Bash. The published benchmark's REA arm also used REA's skill.

SKILL.md sha256: fbcd39d6abe803cf7aa49c1880815bc8e22ba2af87a23681944f687bb7629eb1
Skill metadata: version 42, tool_count 207 (matches what `rea doctor` reports for 6.7.0).
