# Host PC Documentation Completion Plan

Status: implemented and Terra-approved
Planning model: `gpt-5.6-sol`
Implementation model: `gpt-5.6-luna`
Review model: `gpt-5.6-terra`
Destination: `docs/source/subsystems/host_pc/`

## Objective

Populate the Host PC behavior contracts as a complete first-run specification
for host-side acquisition coordination, measurement processing, operator
workflows, visualization, settings, session retention, and export. The pass
must not infer intended behavior from `PythonGUI`.

## Source authority

1. `docs/source/Requirements And Metrics.rst`
2. `docs/source/System Overview.rst`
3. `docs/source/Calibration And Characterization.rst`
4. Existing Host PC overview and behavior-index pages
5. Authoritative Embedded and Integration documentation statements
6. Technical requirements and test sections of
   `General/SDDEC26-06_Team_Spectro_Design_Document.docx` as supporting evidence
7. CIE 233 as calibration and test-method context only

Do not inspect `PythonGUI`, firmware, communications-inspector implementation,
tests, logs, captures, or runtime behavior.

## Current-state inventory

- 102 RST files.
- 14 behavior contracts using the seven-page documentation structure.
- 83 files contain explicit generic placeholders:
  - 14 `calculations.rst`
  - 14 `diagnostics.rst`
  - 14 `procedure.rst`
  - 14 `testing.rst`
  - 14 `validation.rst`
  - 13 `inputs_and_outputs.rst`
- 19 overview/index/substantive pages should be preserved unless a minimal
  cross-reference correction is necessary.

## Common seven-page contract

For each behavior directory:

- `index.rst`: preserve scope, overview, and toctree.
- `inputs_and_outputs.rst`: define inputs, outputs, expected values, structure,
  purpose, and ownership.
- `procedure.rst`: define ordered behavior or transitions. Do not force a state
  machine onto a stateless transformation.
- `calculations.rst`: include only requirements-supported equations. State that
  no required numeric calculation exists when appropriate.
- `diagnostics.rst`: define observable condition, expected state, failure
  indication, and operator response.
- `testing.rst`: define behavior-local planned tests and criteria.
- `validation.rst`: define evidence steps and local traceability.

Replace generic placeholders with requirements-backed content or a specific
`Open requirement` admonition. Do not invent numeric limits, retry policies,
storage rules, formulas, or UI layout.

## Primary Data Pipeline

### Ingress and ADC Reconstruction

Populate complete-frame intake, identity/geometry checks, frame ID and status
observation, raw ADC preservation, incomplete/malformed input behavior, and
handoff to downstream stages.

Requirements support 3648 effective pixels. Keep total transported samples,
resynchronization, timeouts, frame-gap response, checksum, and recovery policy
open. Integration owns the normative wire contract.

### Bias and Dark Correction

Populate stored bias, frame-wise dark reference, optional per-pixel dark
offsets, covered-input acquisition, correction output, and comparative noise
evaluation. Treat specific estimator, averaging count, shielded-pixel indices,
integration-time/temperature selection, clipping, and ordering details as open
unless the requirements explicitly define them.

### Bad Pixel Masking

Populate known-bad-pixel mask intake, output qualification, prevention of
invalid-value propagation, and synthetic-mask tests. Keep mask provenance,
invalid representation, replacement/interpolation algorithm, and edge behavior
open.

### Wavelength Mapping

Populate pixel-to-wavelength mapping using known reference wavelengths,
400-1000 nm coverage, residual evaluation, and known-peak validation. Do not
fix a polynomial order, coefficient format, extrapolation rule, or uncertainty
threshold without an approved requirement.

### Spectral Corrections

Populate flat-field/PRNU correction, wavelength-dependent response/QE
correction, intensity normalization, fixed-integration linearity testing, and
reference-source comparison. Keep factor convention, exact stage ordering,
normalization basis, and tolerances open.

### Processed Spectrum Output and Retention

Populate the processed-spectrum record for visualization and export while
preserving raw ADC data. Required CSV outputs are:

- raw ADC counts
- processed counts
- wavelength
- volts
- processed intensity

Keep volts conversion, record schema, metadata, retention duration, memory
limits, and binary-artifact ownership open.

## Device Control and Acquisition Coordination

### Connection Management

Populate attach, detach, readiness gating, unavailable-device behavior, and
safe disconnect. Keep discovery, port selection, automatic reconnect, timeout,
and retry policy open.

### Acquisition Session Control

Populate start/stop continuous acquisition, complete-frame handling, real-time
capture, and operator-visible session status. Keep pause, buffering,
backpressure, dropped-frame, and stop/drain behavior open. Do not merge
transport, display, and design-target rates.

### Integration-Time Control

Populate user-configurable integration time, validation before request,
application to a subsequent acquisition boundary, and visible accepted/rejected
outcome. Keep units, range, quantization, default, acknowledgment, and exact
application timing open.

### Command and Status Handling

Populate success, failure, rejected, and unavailable-device outcomes plus
operator-visible status and acquisition gating. Keep the command vocabulary,
status vocabulary, timeout, retry, and recovery rules open.

## Operator Application

### Session Control

Populate routine connect, acquire, adjust, inspect, and export workflows that
do not require source-code or hardware reconfiguration. Keep session identity,
disconnect recovery, resume behavior, and setup-time criterion open.

### Visualization

Populate the live intensity-versus-wavelength view and existing intended
spectrogram behavior, plus connection, device, and session indicators. Keep
axis scaling, history depth, color mapping, decimation, saturation behavior,
and the approved display-rate profile open where not specified.

### Calibration and User Settings

Populate selection and loading of dark, wavelength, flat-field/PRNU, and
spectral-response corrections; saving and recalling user settings; and
handling missing or incompatible calibration inputs. Keep formats, versions,
defaults, persistence locations, and startup-self-test behavior open.

### Export Initiation and Session Retention

Populate one-action or one-command CSV export, the five required data products,
retained session readiness, and success/failure feedback. Keep filename,
location, overwrite, precision, metadata, retention duration, and incomplete
session policy open. Do not create a binary-export requirement.

## Terminology

Use consistently:

- `effective detector pixels` separately from total transported samples.
- `raw ADC counts`, `processed counts`, `wavelength`, `volts`, and `processed
  intensity` as separate products.
- `bias`, `frame-wise dark reference`, `per-pixel dark offset`,
  `flat-field/PRNU correction`, and `spectral-response/QE correction` as
  separate operations.
- `acquisition session` for device streaming and `operator session` for the
  user workflow.
- `integration time` without unsupported units, range, or encoding.

## Traceability

Preserve standard UUIDs. Add medium-granularity local traceability records to
each behavior's `validation.rst`. Each record contains:

- behavior claim
- alignment state (`Not Started` or `Not In Docs`)
- defining page
- future implementation location
- requirements/reference evidence

Do not add a duplicate centralized live-status register.

## Planned file operations

- Modify the 83 explicit-placeholder files.
- Preserve the other 19 pages except for minimal broken-link correction.
- Create no files.
- Move, rename, or delete no files.
- Preserve titles, paths, anchors, toctrees, and substantive existing content.
- Keep rollback limited to the Host PC subtree.

## Dependencies and risks

- Integration owns packet, command, acknowledgment, status, and malformed-input
  contracts.
- Embedded owns supported integration-time constraints and device status
  meanings when those are specified.
- Test and Verification owns system-level methods and evidence.
- Optics remains out of scope; Host PC consumes approved calibration inputs.
- Requirements are silent on many operational policies; explicit open
  requirements are required for honest first-run completeness.

## Implementation order

1. Reconfirm authority and the unchanged Host PC file inventory.
2. Populate Primary Data Pipeline behavior contracts.
3. Populate Device Control and Acquisition Coordination contracts.
4. Populate Operator Application contracts.
5. Add behavior-local testing, validation, and traceability.
6. Remove generic scaffold markers.
7. Convert remaining gaps to specific open requirements.
8. Audit terminology and ownership against Integration and Embedded plans.

## Verification

```powershell
python -m sphinx -W --keep-going -b html -c docs docs/source docs/build/html
git diff --check
git diff -- docs/source/subsystems/host_pc
```

Confirm:

- No generic scaffold markers remain.
- Every remaining gap names the decision required.
- Traceability IDs are unique.
- No implementation paths or implementation-derived claims were added.
- All `:doc:` targets and toctrees resolve.
- Changes remain inside the approved Host PC scope.

## Approval checklist

- [ ] Fourteen-contract scope approved.
- [ ] 83-file in-place population approved.
- [ ] Required CSV data products approved.
- [ ] Open-requirement treatment approved.
- [ ] Terminology and responsibility boundaries approved.
- [ ] Local traceability approach approved.
