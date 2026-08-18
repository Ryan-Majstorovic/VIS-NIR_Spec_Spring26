# Evidence Labels

Use these labels explicitly in the research brief and in later documentation decisions.

## Labels

- `implemented`: confirmed by source code or directly supported runtime behavior
- `documented`: stated in existing docs but not yet confirmed in code this turn
- `user-intended`: stated by the user as desired or intended behavior
- `planned`: not implemented yet, but intended for future work
- `unknown`: not confirmed by code, docs, user clarification, or references

## Rules

- Do not present `planned` or `user-intended` items as `implemented`.
- If an explanation depends on `unknown` behavior, ask a clarification question.
- If a missing feature still belongs in the section, document it as a TODO instead of a finished capability.
