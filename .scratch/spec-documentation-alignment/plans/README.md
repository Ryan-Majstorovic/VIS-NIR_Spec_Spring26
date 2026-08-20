# Requirements-First Documentation Completion Plans

Status: implemented and Terra-approved
Planning model: `gpt-5.6-sol`
Implementation model: `gpt-5.6-luna`
Review model: `gpt-5.6-terra`

## Purpose

These plans define the first requirements-based documentation pass for the
VIS-NIR spectrometer. The pass completes intended-behavior documentation before
implementation verification begins.

The four independently reviewable workstreams are:

1. [Embedded](embedded.md)
2. [Host PC](host-pc.md)
3. [Integration](integration.md)
4. [Test and Verification](test-and-verification.md)

The plans were approved before the lower-cost implementation workstreams began.

## Shared authority and source policy

Use sources in this order:

1. `docs/source/` for intended behavior.
2. `docs/source/Requirements And Metrics.rst` for the current top-level
   technical requirements and targets.
3. The technical requirements, architecture, calibration, and test sections of
   `General/SDDEC26-06_Team_Spectro_Design_Document.docx` as supporting
   requirements evidence.
4. CIE 233 and other technical references as method guidance only. A reference
   does not create a project requirement or acceptance threshold.

Do not derive intended behavior from firmware, Python, communications-inspector
code, tests, logs, captures, measurements, or runtime output during this pass.

## Shared authoring rules

- Write intended behavior as `documented` or `planned`, not `implemented`.
- Mark missing limits, algorithms, states, formats, and policies as explicit
  open requirements or TODOs.
- Use `3648 effective detector pixels` as the supported detector requirement.
  Treat the total transported sample count as unresolved.
- Keep acquisition transport rate, display update rate, the embedded minimum,
  and the above-100-fps design target separate.
- Preserve existing standard UUID anchors.
- Give new independently traceable technical blocks standard UUID anchors.
- Use unique eight-character uppercase hexadecimal IDs for local alignment
  traceability.
- Set documented but unverified alignment items to `Not Started`.
- Set unresolved items to `Not In Docs`.
- Keep detailed traceability local to subsystem validation/testing pages rather
  than expanding the global `Traceability.rst` register.
- Do not create or populate diagrams during content implementation. The new
  Test and Verification scaffold may include only the blank placeholders
  required by the scaffold contract.

## Cross-workstream ownership

| Area | Owns | Does not own |
|---|---|---|
| Embedded | CCD timing, acquisition, frame formation responsibility, supported control application, subsystem validation | Host workflows, wire-format decisions not stated by requirements, calibrated host processing |
| Host PC | Connection/acquisition coordination, host processing, visualization, settings, session retention, export initiation | Embedded timing implementation, normative wire protocol |
| Integration | Host-device control and measurement boundaries, end-to-end handoffs, interface checkpoints, communications-inspector role | Processing algorithms, full-system acceptance methods |
| Test and Verification | Verification methods, evidence records, calculations, criteria readiness, pass/fail disposition | Interface definition, subsystem implementation details |

## Reconciled open decisions

The following remain deliberately unresolved in the first pass:

- Total transported frame sample count beyond 3648 effective pixels.
- Packet header, field widths, byte order, status-bit meanings, checksum, and
  recovery rules.
- Integration-time units, range, resolution, default, validation, and exact
  application boundary.
- Approved transport-rate and display-rate acceptance profiles.
- Retry, timeout, reconnect, buffering, backpressure, and retention policies.
- Calibration file formats, versioning, selection, and persistence rules.
- Most quantitative characterization thresholds beyond 400-1000 nm coverage
  and approximately 5 nm FWHM.

## File-operation summary

| Workstream | Create | Modify | Move/rename/delete |
|---|---:|---:|---:|
| Embedded | 1 RST | 38 RST | None |
| Host PC | None | 83 placeholder RST files | None |
| Integration | 1 RST | 9 RST | None |
| Test and Verification | 7 RST and 2 blank VSDX placeholders | Root index and Calibration and Characterization | None |

Implementation workers must remain inside their assigned ownership roots. The
Test and Verification worker alone may update `docs/source/index.rst` and
`docs/source/Calibration And Characterization.rst`.

## Execution sequence

1. Approve these four plans and the shared rules above.
2. Dispatch lower-cost implementation workstreams with disjoint file ownership.
3. Populate requirements-backed content and explicit open requirements.
4. Run subsystem-scoped structural checks.
5. Reconcile cross-references after all four workstreams finish.
6. Run one strict Sphinx build and `git diff --check` from the coordinating
   workstream.
7. Confirm the diff contains documentation and approved planning artifacts only.

## Review checklist

- [x] Embedded plan approved and implementation reviewed.
- [x] Host PC plan approved and implementation reviewed.
- [x] Integration plan approved and implementation reviewed.
- [x] Test and Verification plan approved and implementation reviewed.
- [x] Requirements-only source boundary approved.
- [x] Open-requirement treatment approved.
- [x] File creation/modification list approved.
- [x] No moves, renames, or deletions approved.
- [x] Lower-cost implementation dispatch completed.
