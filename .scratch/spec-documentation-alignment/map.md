# Spectrometer Specification Documentation Alignment

## Destination

Produce an authoritative documentation path for intended spectrometer behavior,
then verify the current implementation against that specification across the
major code surfaces, then drive the resulting documentation and code fixes from
a clear backlog.

## Notes

- This effort is sequencing work, not completing the implementation changes in one pass.
- Documentation intent should be written before code-verification work starts so the spec stays authoritative.
- Current code-bearing surfaces in this repo are concentrated in `CCD-Driver-Code/`, `PythonGUI/`, and `Spectrometer-COM-Inspector/`.
- Existing Sphinx documentation already provides the technical publication surface in `docs/source/`.
- Verification tickets should compare code to documented intent instead of deriving requirements from the code.

## Decisions so far

- [Define Authoritative Specification Scope](issues/01-define-authoritative-spec-scope.md) - `docs/source/` is the intended-behavior authority for the first verification effort, scoped to `embedded`, `host_pc`, `integration/interfaces`, and `test_and_verification`, with local subsystem traceability and `.scratch/` mismatch reviews.
- [Document Intended Host PC Behavior](issues/03-document-intended-host-pc-behavior.md) - Host PC intent is now organized as one `Host PC System Overview` plus three authoritative systems: `Primary Data Pipeline`, `Device Control And Acquisition Coordination`, and `Operator Application`; the root Host PC sidebar branch was flattened to that new structure and the old runtime/configuration/display-export/validation branches were retired.

## Not yet specified

- The exact intended behavior for each subsystem still needs to be written down by the project owner instead of inferred from the current code.
- It is not yet clear which existing Sphinx pages are authoritative, incomplete, or obsolete.

## Out of scope

- Course-deliverable material and other nontechnical documentation remain outside this effort unless the destination is redrawn.
- `optics` is out of scope for this effort because it is not yet implemented and should be handled as a separate future effort.
