# Host PC Operator Application Overview Rework Plan

Status: Execution authorized

Planning model: Sol

## Objective

Rework the Operator Application category index and its four leaf index pages so
they match the finalized `docs/source/subsystems/host_pc/overview.rst` format.
The rework is requirements-first and may use only the current Sphinx
documentation under `docs/source` as behavioral evidence. It must not inspect
or derive intent from code, tests, logs, or runtime behavior.

The pages will specify operator-facing behavior without freezing a user
interface layout or inventing calibration, settings, export, or retention
formats.

## Exact Five-File Scope

Modify only:

1. `docs/source/subsystems/host_pc/operator_application/index.rst`
2. `docs/source/subsystems/host_pc/operator_application/session_control/index.rst`
3. `docs/source/subsystems/host_pc/operator_application/visualization/index.rst`
4. `docs/source/subsystems/host_pc/operator_application/calibration_and_user_settings/index.rst`
5. `docs/source/subsystems/host_pc/operator_application/export_initiation_and_session_retention/index.rst`

Do not modify `docs/source/subsystems/host_pc/overview.rst`, any linked detail
page, or any other artifact. The Host PC overview may contain unrelated
working-tree changes and must be preserved.

## Authoritative Sources

- `docs/source/subsystems/host_pc/overview.rst` controls the target page format.
- Each current Operator Application index page supplies its existing role and
  boundary statement.
- The six linked detail pages under each leaf system supply the allowed
  objectives, open decisions, diagnostics, tests, and local traceability.
- Existing `Not In Docs` statements remain unresolved; they are not invitations
  to infer missing behavior.

## Common Page Format

Each target page shall use this exact order:

1. Page title
2. Existing diagram note
3. `System Role`
4. `System Objectives`
5. `System Relationship`
6. `Integration Boundary`
7. Heading-free hidden toctree

Formatting requirements:

- Move the existing diagram note directly below the page title.
- Rename `Overview` to `System Role` and reuse its existing label and UUID.
- Limit `System Role` to one `**Summary:**` paragraph.
- Add a unique standard UUID label and visible UUID line to each new substantive
  section: `System Objectives`, `System Relationship`, and
  `Integration Boundary`.
- Write four to seven granular objectives per page.
- Begin every objective with `**Objective N:**` and include `shall`.
- Follow every objective with one plain indented `Rationale:` paragraph. Do not
  bold the rationale label.
- Use a two-column `.. list-table::` in `System Relationship`.
- Make every first-column item a working `:doc:` link.
- Limit `Integration Boundary` to one `**Summary:**` paragraph.
- Remove the visible `Related Pages` heading.
- Preserve Sphinx hierarchy with a heading-free hidden toctree:

  ```rst
  .. toctree::
     :hidden:
  ```

- Do not add implementation names, widgets, controls, screen positions,
  filename rules, persistence locations, numeric precision, calibration file
  formats, compatibility formats, or other unsupported details.

## UUID And Link Preservation

Preserve these existing labels and UUID values byte-for-byte and attach them to
the renamed `System Role` sections:

- Operator Application: `71D2ED58-E8DB-4E12-BA3F-D9AB7883C5E6`
- Session Control: `902664D2-B91E-4A01-8911-A7A12C89657B`
- Visualization: `7B78AE61-551F-4FD2-BA0E-79877FFB8163`
- Calibration And User Settings: `99D3B5E7-275E-4B3B-B833-6D73656602B1`
- Export Initiation And Session Retention:
  `4718CC11-20B8-4AB0-BF7A-398BE00E1C99`

Generate new, unique standard UUIDs for the three added substantive sections
on each page. Do not reuse detail-page UUIDs or local eight-character
traceability IDs.

Move existing child paths into the hidden toctree without changing their path
text. Duplicate those destinations as linked rows in the relationship table so
the pages remain both navigable and included in the Sphinx hierarchy.

## Page 1: Operator Application

### System Role Theme

The Operator Application shall provide session control, visualization,
calibration and user settings, and export initiation and session retention for
the current Host PC acquisition session without defining a particular UI
layout.

### Objective Themes

1. **Session Control** shall coordinate connection, acquisition, inspection,
   stop or pause, retention, and disconnect actions with visible session state.
   Rationale: State association prevents unavailable or out-of-sequence actions
   from appearing valid.
2. **Visualization** shall present qualified wavelength-associated spectra,
   rolling history when enabled, and connection, device, and session status.
   Rationale: Measurement output requires operating context for correct
   interpretation.
3. **Calibration And User Settings** shall validate selections and setting
   changes before activation and report save or recall outcomes.
   Rationale: Validation prevents missing or incompatible configuration from
   silently affecting later processing.
4. **Export Initiation And Session Retention** shall create required CSV output
   from an eligible retained session and report the outcome without discarding
   reviewable data.
   Rationale: Retention protects the source measurement when export is
   incomplete or unsuccessful.
5. **Operator Application** shall preserve the association among session state,
   processed output, active configuration, and exportable retained data.
   Rationale: Consistent association prevents data or settings from becoming
   detached from the acquisition they govern.
6. **Operator Application** shall expose unavailable, stale, invalid,
   incomplete, or failed conditions without presenting them as successful
   operation.
   Rationale: Visible failure state prevents reliance on invalid workflow
   results.

### Relationship Rows

- `Session Control <session_control/index>` - operator-session workflow and
  state
- `Visualization <visualization/index>` - live and rolling measurement
  presentation
- `Calibration And User Settings <calibration_and_user_settings/index>` -
  calibration selection and user-setting management
- `Export Initiation And Session Retention
  <export_initiation_and_session_retention/index>` - retained-session export
  and outcome reporting

### Boundary Theme

The category consumes connection and acquisition state from Device Control And
Acquisition Coordination and qualified processed and retained spectrum products
from the Primary Data Pipeline. Integration owns the low-level MCU-to-Host PC
contract, and the Primary Data Pipeline owns calibration mathematics and
measurement processing.

## Page 2: Session Control

### System Role Theme

Session Control shall establish readiness, start acquisition, make accepted
processed data available for inspection, stop or pause according to the
approved policy, retain eligible data, and disconnect while presenting current
session state.

### Objective Themes

1. Gate connection and acquisition actions using current connection and
   acquisition status.
2. Establish readiness before acquisition actions become available.
3. Start a session and present its current state.
4. Make accepted processed data available for inspection during the session.
5. Stop or pause according to the approved acquisition policy and retain
   eligible session data.
6. Expose connection loss and unavailable actions and disconnect safely.

Each rationale shall explain respectively: prevention of invalid actions,
readiness before acquisition, association between actions and acquisition,
inspection of qualified data, controlled finalization and retention, and
avoidance of a disconnected session appearing active.

### Relationship Rows

Link the existing `inputs_and_outputs`, `procedure`, `diagnostics`, `testing`,
`calculations`, and `validation` pages. Describe them respectively as action and
status boundaries, workflow and states, invalid-action and connection-loss
conditions, behavior tests, the absence of numeric calculation plus open
policy requirements, and local traceability.

### Boundary Theme

Session Control consumes connection and acquisition state from Device Control
And Acquisition Coordination and processed-data readiness from the Primary Data
Pipeline. It provides session context to Visualization and Export Initiation And
Session Retention. Low-level device commands remain outside this system.

## Page 3: Visualization

### System Role Theme

Visualization shall present qualified wavelength-associated processed spectra,
rolling spectral history when enabled, and connection, device, and session
status while identifying unavailable or stale display data.

### Objective Themes

1. Accept only qualified wavelength-and-intensity records.
2. Present the current intensity-versus-wavelength spectrum while preserving
   wavelength and intensity correspondence.
3. Append accepted records to rolling spectrogram history when enabled.
4. Present connection, device, and session indicators independently of
   spectrum rendering.
5. Identify no-record, stale, unavailable, or invalid-value conditions.
6. Consume processed values without introducing a new measurement calculation.

Each rationale shall explain respectively: rejection of invalid data, required
wavelength/value pairing, ordered temporal context, visibility of operating
state without a spectrum, avoidance of stale data appearing current, and
preservation of Primary Data Pipeline calculation ownership.

### Relationship Rows

Link the six existing detail pages and describe them as qualified data and
status boundaries, display update flow, unavailable/stale diagnostics,
requirements-based display tests, the absence of new measurement calculations,
and local traceability.

### Boundary Theme

Visualization consumes wavelength-associated processed values from the Primary
Data Pipeline and device/session status from adjacent Host PC systems. It owns
operator-facing presentation, not acquisition control, spectral processing, or
a fixed screen layout.

## Page 4: Calibration And User Settings

### System Role Theme

Calibration And User Settings shall let the operator select calibration inputs
and save or recall user settings, validate requested selections, activate only
accepted configuration, and report outcomes without defining calibration
mathematics or storage formats.

### Objective Themes

1. Present bias/dark, wavelength, flat-field or PRNU, and spectral-response or
   QE selection categories.
2. Validate requested selections against the active detector and processing
   context.
3. Activate accepted selections for subsequent processing.
4. Prevent missing or incompatible selections from being silently activated.
5. Save or recall user settings and report the outcome.
6. Preserve the current active configuration when selection, save, or recall
   fails.

Each rationale shall explain respectively: visible configuration categories,
compatibility protection, establishment of the governing configuration,
avoidance of silent substitution, confirmation of requested change, and
preservation of a known active configuration after failure.

### Relationship Rows

Link the six existing detail pages and describe them as configuration
boundaries, selection and recall workflow, incompatibility diagnostics,
behavior tests, the absence of calibration math, and local traceability.

### Boundary Theme

This system manages operator selection and configuration outcomes. The Primary
Data Pipeline owns calibration calculations and application order. Formats,
versions, defaults, persistence locations, compatibility rules, and startup
self-test remain unspecified.

## Page 5: Export Initiation And Session Retention

### System Role Theme

Export Initiation And Session Retention shall accept export requests for
eligible retained sessions, preserve correspondence among required raw and
processed products, create required CSV output, report the result, and retain
reviewable session data according to the approved policy.

### Objective Themes

1. Accept export requests only for retained acquisition sessions.
2. Confirm aligned raw ADC counts, processed counts, wavelength, volts, and
   processed intensity.
3. Create CSV output containing the five required data products.
4. Report successful, failed, or incomplete export outcomes.
5. Preserve retained data needed for review when export fails.
6. Keep the session available according to the approved retention policy.

Each rationale shall explain respectively: session-context preservation,
row/value alignment, downstream availability of raw and derived data, avoidance
of false success, recovery after write failure, and later export or review
without inventing a duration or storage mechanism.

### Relationship Rows

Link the six existing detail pages and describe them as retained inputs and CSV
outputs, export workflow, incomplete/write/schema diagnostics, export tests,
the five-product correspondence requirement, and local traceability.

### Boundary Theme

This system consumes eligible retained products from the Primary Data Pipeline
and session context from Session Control. It produces required CSV content and
outcome status without adding measurement calculations or defining filename,
destination, overwrite, precision, metadata, retention duration, or storage
policy.

## File Operations

- Modify the exact five index pages in place using `apply_patch`.
- Do not create, move, rename, or delete documentation files.
- Do not modify linked detail pages.
- Preserve all existing path spellings, titles, labels, UUIDs, and child
  destinations.
- Generate new UUIDs only for newly introduced substantive sections.
- Review the shared worktree before and after editing so unrelated changes are
  neither incorporated nor reverted.

## Luna Implementation Gate

Use Luna for implementation after this plan is accepted.

Luna shall:

1. Re-read the five target pages, their linked detail pages, and the finalized
   Host PC overview.
2. Confirm the five target files are not concurrently modified.
3. Apply minimal patches to the five files only.
4. Preserve existing UUIDs and destinations exactly.
5. Run the page-format and source-grounding audits below.
6. Run strict Sphinx and path-scoped diff verification.

## Terra Review Gate

Use Terra for an independent read-only review after Luna's first implementation
pass.

Terra shall compare the diff against the Host PC overview and all linked detail
pages and report only concrete findings concerning:

- unsupported or invented behavior
- incorrect section order or field style
- missing `shall` language or functional rationale
- UUID or label changes
- broken or missing `:doc:` links
- missing hidden-toctree membership
- UI-layout coupling
- invented calibration, settings, export, or retention formats
- loss of an existing `Not In Docs` boundary

Luna may then make a correction pass limited to Terra's confirmed findings.

## Audits

### Scope Audit

- Exactly the five authorized files changed.
- `docs/source/subsystems/host_pc/overview.rst` and all detail pages are
  untouched.
- No files were created, moved, renamed, or deleted.

### Structure Audit

- The diagram note immediately follows each page title.
- Each page contains `System Role`, `System Objectives`,
  `System Relationship`, and `Integration Boundary` in that order.
- No `Overview` or `Related Pages` heading remains.
- A hidden toctree contains every former child path exactly once.

### Content Audit

- `System Role` and `Integration Boundary` contain only `**Summary:**`.
- Every objective includes `shall` and one plain indented `Rationale:`.
- Each relationship table has exactly two columns and linked first-column
  entries.
- Category objectives name the responsible child system.
- Leaf objectives are grounded in their existing detail pages.
- Open requirements remain explicit and unresolved.
- No implementation, screen layout, storage format, or calibration format was
  introduced.

### UUID And Link Audit

- All five existing role UUIDs and labels are unchanged.
- All new standard UUIDs are unique within `docs/source`.
- Every `:doc:` target resolves.
- No child documentation page becomes orphaned.

## Verification Commands

Run the strict Sphinx build:

```powershell
python -m sphinx -W --keep-going -b html -c docs docs/source docs/build/html
```

Run path-scoped diff verification:

```powershell
git diff --check -- docs/source/subsystems/host_pc/operator_application/index.rst `
  docs/source/subsystems/host_pc/operator_application/session_control/index.rst `
  docs/source/subsystems/host_pc/operator_application/visualization/index.rst `
  docs/source/subsystems/host_pc/operator_application/calibration_and_user_settings/index.rst `
  docs/source/subsystems/host_pc/operator_application/export_initiation_and_session_retention/index.rst

git diff -- docs/source/subsystems/host_pc/operator_application/index.rst `
  docs/source/subsystems/host_pc/operator_application/session_control/index.rst `
  docs/source/subsystems/host_pc/operator_application/visualization/index.rst `
  docs/source/subsystems/host_pc/operator_application/calibration_and_user_settings/index.rst `
  docs/source/subsystems/host_pc/operator_application/export_initiation_and_session_retention/index.rst
```

If the strict build reports unrelated baseline warnings, Terra must confirm
that none originate from these five pages and that the change introduces no new
warning.

## Definition Of Done

- Luna has updated exactly the five authorized pages.
- Terra has completed an independent source-grounding and format review.
- All confirmed Terra findings are resolved.
- The existing five role UUIDs and all child links are preserved.
- Every page follows the finalized overview format and retains hidden toctree
  membership without a visible `Related Pages` section.
- Objectives and rationales are granular, requirements-first, and supported by
  existing detail pages.
- No UI layout, implementation behavior, storage format, or calibration format
  has been invented.
- Strict Sphinx verification passes, or any unrelated baseline warning is
  documented and no target-page warning remains.
- `git diff --check` passes for all five files.
