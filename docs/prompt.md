# The prompt every arm gets (frozen 2026-10-19)

Same text, same model, same effort setting, same machine. Only the tool changes.

> The file at {PATH} is a compiled program. You do not have its source code. Explain what it does: its inputs, its decision rules, any exact constants, and its outputs or exit codes. Then say what you could not determine from the program itself. End your answer with one line of JSON and nothing after it:
> {"confidence": <number from 0 to 1>, "could_not_determine": [<short strings, empty list if nothing>]}

## Extra sentence for the `rea-directed` arm only (frozen 2026-10-19)

Inserted into the prompt above, just before "End your answer with" (the sentence is shown indented, not quoted, so the harness does not treat it as part of the base prompt):

    Use the REA tools (the `rea` MCP server) to inspect the program.

The `none` and `rea` arms never see this sentence.

## Extra sentence for the `p09b` target only (frozen 2026-10-19, before any p09b run)

`p09b` is the same Go program as `p09`, asked one more question, for all three arms. This sentence is inserted just before "End your answer with" (and, in the `rea-directed` arm, before the REA sentence above). Shown indented so the harness does not treat it as part of the base prompt:

    Also report the compiler or toolchain version, and the name and version of each library or module the program was built with, if you can find them.

Why: in the `p09` runs no arm reported build details, because the base prompt never asks for them. REA advertises reading embedded build information, so a fair test must ask for it.

Notes: the file is named `t05` style without its descriptive suffix when copied to the run folder, so the filename gives nothing away.
