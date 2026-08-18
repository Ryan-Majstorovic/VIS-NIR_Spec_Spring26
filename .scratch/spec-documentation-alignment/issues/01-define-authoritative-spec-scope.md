# Define Authoritative Specification Scope

Type: research
Status: resolved

## Question

What documentation boundary, subsystem inventory, and evidence rules will make the Sphinx docs the authoritative source for intended spectrometer behavior before code verification starts?

## Done When

- The documentation authority is explicit: intended behavior comes from docs, not from reverse-engineering code.
- The subsystem list is named for this effort, including at minimum embedded firmware, host PC software, and communications tooling.
- Each subsystem has a target documentation location under `docs/source/`.
- A simple traceability rule is defined for later comparison work.

## Answer

- `docs/source/` is the authoritative source for intended system behavior for this effort.
- Archived docs, course design documents, PDFs, research notes, source files, tests, logs, exports, captures, bench measurements, and calibration results are supporting evidence only.
- If implementation and documentation differ, the default action is a review in `.scratch/`, not an automatic documentation rewrite or automatic code rewrite.
- The major subsystems in scope for this effort are:
  - `embedded` at `docs/source/subsystems/embedded/`
  - `host_pc` at `docs/source/subsystems/host_pc/`
  - `integration/interfaces` at `docs/source/subsystems/integration/interfaces/`
  - `test_and_verification` at `docs/source/subsystems/test_and_verification/`
- `optics` is out of scope for this effort because it is not yet implemented and should be handled as a separate future effort.
- Traceability is maintained locally in each subsystem's testing or validation section rather than in a duplicated central register.
- Traceability is tracked per major behavior claim, not per page and not per implementation detail.
- A new traceability item is created only when the behavior has its own intent, likely evidence, or possible mismatch with implementation.
- Each traceability item must include:
  - an 8-character uppercase hexadecimal ID
  - the behavior claim
  - the state
  - the defining doc page
  - the implementation location to review
  - the evidence used
- The approved state model is:
  - `Not Started`
  - `Not In Docs`
  - `In Progress`
  - `Review`
  - `Accepted`
- Only items in `Review` or `Accepted` force a formal mismatch review against the implementation.
- Existing documentation is evaluated item by item; no page or subsystem receives a blanket status.
- Archived docs and course design materials may seed `Not In Docs` items and may later serve as supporting evidence, but they do not overrule `docs/source/`.

## Comments
