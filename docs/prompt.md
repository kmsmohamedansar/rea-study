# The prompt every arm gets (frozen 2026-10-19)

Same text, same model, same effort setting, same machine. Only the tool changes.

> The file at {PATH} is a compiled program. You do not have its source code. Explain what it does: its inputs, its decision rules, any exact constants, and its outputs or exit codes. Then say what you could not determine from the program itself. End your answer with one line of JSON and nothing after it:
> {"confidence": <number from 0 to 1>, "could_not_determine": [<short strings, empty list if nothing>]}

Notes: the file is named `t05` style without its descriptive suffix when copied to the run folder, so the filename gives nothing away.
