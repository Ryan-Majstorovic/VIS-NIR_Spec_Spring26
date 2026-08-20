# Integration Documentation Completion Plan

Status: implemented and Terra-approved
Planning model: `gpt-5.6-sol`
Implementation model: `gpt-5.6-luna`
Review model: `gpt-5.6-terra`
Destination: `docs/source/subsystems/integration/`

## Objective

Define the requirements-first host-device boundary, end-to-end measurement and
control flows, interface checkpoints, and the independent role of the
Communications Inspector. Integration documents contracts and handoffs, not
internal implementation sequence or full-system acceptance methods.

## Source authority

1. `docs/source/Requirements And Metrics.rst`
2. Existing authoritative Host PC and Embedded Sphinx statements
3. `.scratch/spec-documentation-alignment/issues/04-document-intended-tooling-and-integration-behavior.md`
4. Technical requirements, architecture, and testing sections of
   `General/SDDEC26-06_Team_Spectro_Design_Document.docx` as supporting evidence

Do not inspect or derive intended behavior from firmware, Python,
communications-inspector code, READMEs, tests, logs, or runtime results.

## Intended boundary

### Measurement plane

1. The detector is illuminated by an external optical input.
2. Embedded timing and acquisition produce measurement samples.
3. Embedded responsibility forms a complete measurement frame carrying frame
   identity and status information.
4. USB CDC transfers the frame across the host-device boundary.
5. The Host PC reconstructs and validates the received measurement.
6. The Host PC applies approved correction and wavelength-association stages.
7. The operator application displays and captures the result.
8. The session retains data required for CSV export.

### Control plane

The Host PC manages connection readiness and requests acquisition start,
acquisition stop, and integration-time changes. Embedded applies supported
requests and returns an outcome or status. Exact encodings and behavior remain
open unless separately approved.

## Responsibility boundaries

| Component | Responsibility |
|---|---|
| Embedded | CCD timing, digitization, frame-formation responsibility, frame identity/status, supported control application |
| Host PC | Connection and acquisition coordination, frame reconstruction/validation, processing, display/capture, retention, export initiation |
| Communications Inspector | Optional independent observation of USB/frame behavior and evidence production |
| Test and Verification | Detailed methods, evidence requirements, calculations, and pass/fail disposition |
| Optics | Upstream illumination context only during this pass |

The Communications Inspector is not the normal operator application and is not
an alternate requirements authority.

## Planned file operations

### Interface branch

Modify:

- `interfaces/Interfaces.rst`
- `interfaces/system_boundaries/System Boundaries Secondary System.rst`
- `interfaces/system_boundaries/Integration Interfaces.rst`

Create:

- `interfaces/system_boundaries/Communications Inspector.rst`

Content includes:

- physical/electrical context at requirement level
- normative host-device responsibility boundary
- measurement-plane contract
- control/status contract
- ownership and handoff table
- support-tool boundary
- explicit open protocol requirements
- local traceability

### Data-flow branch

Modify:

- `data_flow/Data Flow.rst`
- `data_flow/end_to_end/End-To-End Secondary System.rst`
- `data_flow/end_to_end/Integration Data Flow.rst`

Replace implementation-shaped sequencing with the intended measurement and
control flows. Treat optics as upstream context and the required CSV products
as the terminal data handoff. Mark unsupported dense-binary artifacts as open
instead of requirements.

### Integration-test branch

Modify:

- `test_strategy/Test Strategy.rst`
- `test_strategy/acceptance_regression/Acceptance And Regression Secondary System.rst`
- `test_strategy/acceptance_regression/Technical Test Strategy.rst`

Limit this branch to interface and end-to-end integration checkpoints:

- complete-frame transfer
- frame identity and status observation
- sustained-stream rate measurement with separate unresolved profiles
- start, stop, and integration-time round trips
- host display/capture handoff
- CSV-schema handoff
- independent inspector observation
- regression triggers after interface-contract changes
- minimum evidence-record fields

Detailed acceptance procedures and results belong in Test and Verification.

## Communications Inspector page

The new page will define:

- purpose and boundary
- requirement-backed inputs and observations
- complete-frame rate as accepted frames divided by observation duration
- required evidence outputs
- operational constraints
- requirement-silence TODOs
- local traceability

Do not document current command-line options, implementation classes, logging
format, or recovery behavior.

## Requirement mapping

| Requirement | Integration definition |
|---|---|
| Complete binary USB frames with IDs and flags | Interface contract, data flow, inspector observation, integration checkpoint |
| Real-time display and capture | Host handoff in the end-to-end flow |
| Configurable integration time | Control-plane responsibility contract |
| Start and stop acquisition | Control-plane behavior supported by the design requirements |
| Host correction and wavelength mapping | End-to-end handoff only; algorithms remain Host PC-owned |
| Required CSV fields | Terminal data handoff and schema checkpoint |
| Above-100-fps design target | Separate rate profile with criterion TODOs |
| Characterization categories | Cross-reference to Test and Verification |
| Communications Inspector | Independent supporting verification role |

## Open requirements

- Command strings or binary encoding.
- Integration-time units, range, granularity, validation, and application
  timing.
- Acknowledgment, error, retry, timeout, and idempotency rules.
- Legal command ordering and control states.
- Status-flag meanings.
- Text/binary stream coexistence.
- Protocol version, header, checksum, byte order, and resynchronization.
- Total transported sample count beyond 3648 effective pixels.
- Disconnect, reconnect, and partial-frame behavior.
- Concurrent port access by the operator application and inspector.
- Inspector CLI, logging, retention, and recovery details.
- Approved transport and display performance profiles.

## Local traceability proposal

| ID | Behavior |
|---|---|
| `DB0C2800` | Embedded, Host PC, and support-tool responsibility boundary |
| `4000E1CA` | Complete USB CDC frame-transfer responsibility with identity and status |
| `F700CD12` | Start, stop, integration-time, and outcome/status boundary |
| `A252A879` | End-to-end measurement handoff through host display/capture |
| `2BEDC9A3` | Required CSV handoff and fields |
| `7205FDB2` | Communications Inspector as independent verification support |
| `191ACD4F` | Integration verification sequencing and evidence requirements |
| `6805FD49` | Unresolved transport/display acceptance profiles |

Use `Not Started` for documented behavior and `Not In Docs` for unresolved
details. Future implementation locations remain TODO until the later code
verification issue.

## Dependencies and risks

- Embedded and Host PC plans must not silently choose conflicting frame or
  command details.
- Test and Verification must provide the canonical system-verification path.
- Integration owns all files under `docs/source/subsystems/integration/**`.
- The transport-rate target and display-update criterion must not be conflated.
- Cross-references to Test and Verification should be added only to the known
  final destination `../test_and_verification/index` or equivalent resolved
  Sphinx path.

## Implementation order

1. Reconfirm source authority and file ownership.
2. Update the three Interface pages.
3. Create and link the Communications Inspector page.
4. Update the three Data Flow pages.
5. Update the three Integration Test Strategy pages.
6. Add local traceability and explicit open requirements.
7. Add resolved cross-references to Test and Verification.
8. Audit every factual sentence against the requirement mapping.

## Verification

```powershell
python -m sphinx -W --keep-going -b html -c docs docs/source docs/build/html
git diff --check
git diff -- docs/source/subsystems/integration
```

Confirm:

- The Communications Inspector appears once under System Boundaries.
- All `:doc:` links and toctrees resolve.
- No code paths, functions, CLI options, or implementation claims were added.
- Unsupported details are explicit open requirements.
- Optics remains context-only.
- Characterization procedures are not duplicated.
- CSV data products match Requirements and Metrics.
- Transport and display rates remain distinct.

## Approval checklist

- [ ] Measurement/control plane split approved.
- [ ] Responsibility boundaries approved.
- [ ] Communications Inspector page approved.
- [ ] Nine modifications and one creation approved.
- [ ] Open protocol requirements approved.
- [ ] Local traceability proposal approved.
