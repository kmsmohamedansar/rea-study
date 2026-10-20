# Held-out runs that failed before the model was called

12 of the 18 held-out runs (t10, p03, p05, p06, each in three arms) were made on 2026-10-19 at 19:22 to 19:23, right after t04 and t07 ran normally. Every one of them recorded:

    You've hit your session limit · resets 10:20pm (America/Toronto)

with API time 0, no tool calls, `is_error` true and exit code 1. The model was never called, so no answer exists and nothing was learned about any arm from them. This is the owner's Claude Pro usage limit running out, not an agent result.

Under docs/analysis-plan.md ("a run is redone only if it failed before calling the model") these cells are redone. The failed records are kept here, unchanged apart from their location, and are not counted anywhere. The redo goes in results/raw/heldout as the one scored run for each cell.

The six runs that did complete (t04 and t07, three arms each) stay where they were made and are not redone.
