# Host PC Overview Revision Plan

Status: Awaiting user approval  
Planning model: Sol  
Target: [Host PC overview](../../../docs/source/subsystems/host_pc/overview.rst)  
Checklist: [Host PC page review checklist](../host-pc-page-review-checklist.md)

## Purpose

Revise only the Host PC system overview according to the notes recorded under
the first item in the Host PC page review checklist. The revision shall describe
facts and required behavior of the Host PC system rather than explain the
documentation, its organization, or the current implementation.

`docs/source/` and the user's checklist decisions are the intended-behavior
authority. Python, firmware, tests, logs, captures, measurements, and runtime
behavior shall not be used to create requirements during this revision.

## Checklist decisions

| Checklist note | Planned response |
|---|---|
| System Role does not need separate Summary, Expected Outcome, and Rationale fields. | Retain one `**Summary:**` field and fold the required Host PC behavior into it. |
| Objectives shall state facts about the system, not facts about the documentation. | Replace the current objectives with seven named-system `shall` statements. |
| Remove the standalone-validation-tools statement. | Delete it without replacement. |
| Split the objectives more granularly into six or seven objectives. | Use seven objectives covering control, acquisition, processing, presentation, retention, and export. |
| Integration Boundary shall use the same Summary-only format and link the Integration Interfaces page. | Retain one `**Summary:**` field and delegate boundary definitions through the existing `:doc:` link. |
| System Relationship does not need the downstream or adjacent relationship column. | Replace the current table with a concise two-column table containing System and Primary Responsibility. |
| Fold Related Pages into System Relationship. | Make each system name in the table a `:doc:` link and remove the separate Related Pages section. |

## Scope

### File to modify during implementation

- `docs/source/subsystems/host_pc/overview.rst`

### Files not to modify

- `.scratch/spec-documentation-alignment/host-pc-page-review-checklist.md`
- Host PC child subsystem pages
- Integration pages
- requirements and system-level source pages
- Sphinx configuration and root navigation
- implementation code, tests, logs, or generated HTML

### File operations

- Create, move, rename, and delete no files during implementation.
- Apply the approved revision on top of the current working-tree content.
- Preserve unrelated user changes.
- Use `apply_patch` for the source edit.

## Protected structure

Keep the architecture-diagram placeholder at the top. Retain the following
section order, anchors, and displayed UUIDs exactly:

1. `System Role` — `42E97793-9F90-4EB8-9757-FDE4D6527DBC`
2. `System Objectives` — `90977A32-CB75-4745-B6D0-470F1B5116BE`
3. `System Relationship` — `55F3AB31-2428-4459-A33F-4CC03984FD05`
4. `Integration Boundary` — `7E7E9CF8-7577-4DC8-97B7-6730476D1D41`

Do not add a page-title UUID or regenerate any existing UUID.

## Planned revision

### 1. System Role

Use one factual Summary field. Remove Expected Outcome and Rationale.

Proposed content:

```rst
**Summary:** The Host PC system shall coordinate device connection and
acquisition control, accept and process complete measurement frames, present
processed spectra and acquisition status to the operator, and retain
session-associated outputs for export initiation.
```

This summary states what the Host PC system shall do without discussing why the
page exists, documentation authority, reviewability, or implementation layout.

### 2. System Objectives

Replace the current four objectives with seven granular system objectives. Each
objective shall be followed immediately by a plain, indented functional
rationale.

#### Objective 1 — Connection and command state

```rst
**Objective 1:** The Host PC device-control system shall manage connection
readiness and supported command outcomes so control state remains available to
the acquisition and operator workflows.

   Rationale: Consistent connection and command-outcome state prevents
   acquisition and operator workflows from treating an unavailable device or
   an unsuccessful command as ready or accepted.
```

Do not add undocumented acknowledgment, retry, timeout, or recovery behavior.

#### Objective 2 — Acquisition coordination

```rst
**Objective 2:** The Host PC device-control system shall coordinate acquisition
start and stop actions and integration-time requests with the current connection
and acquisition-session state.

   Rationale: Coordinating requested actions with the current state prevents a
   control change from becoming detached from the acquisition it governs.
```

Do not invent a legal command ordering or command-application boundary.

#### Objective 3 — Frame qualification and reconstruction

```rst
**Objective 3:** The Host PC primary-data-pipeline system shall accept complete
measurement frames at the Integration boundary and qualify and reconstruct
their measurement content into ordered ADC samples before downstream
processing.

   Rationale: Ordered reconstruction preserves the detector-position
   relationship required by correction and wavelength-mapping stages.
```

Do not define packet markers, fields, byte ordering, transported geometry, or
resynchronization behavior on this page.

#### Objective 4 — Correction and wavelength association

```rst
**Objective 4:** The Host PC primary-data-pipeline system shall apply the
approved bias and dark correction, bad-pixel handling, wavelength mapping, and
spectral-correction stages to qualified measurement data to produce corrected,
wavelength-associated spectra.

   Rationale: Applying these transformations supplies the detector correction
   and wavelength meaning required by visualization, retention, and export
   workflows.
```

Do not invent algorithms, calibration formats, numerical thresholds, or stage
parameters.

#### Objective 5 — Session control and settings

```rst
**Objective 5:** The Host PC operator-application system shall provide session
control and calibration and user settings for the current acquisition session.

   Rationale: Associating controls and settings with the current session
   prevents an acquisition from using ambiguous operator configuration.
```

Do not freeze the current user-interface layout into the requirement.

#### Objective 6 — Operator presentation

```rst
**Objective 6:** The Host PC operator-application system shall present processed
spectrum outputs and acquisition status to the operator during the active
session.

   Rationale: Presenting the measurement and its acquisition state together
   allows the operator to interpret the spectrum in the context that produced
   it.
```

Do not introduce an unsupported display or refresh rate.

#### Objective 7 — Retention and export availability

```rst
**Objective 7:** The Host PC system shall retain session-associated processed
spectrum outputs and make the retained session data available for export
initiation.

   Rationale: Preserving the association between a spectrum and its session
   prevents retained or exported measurements from losing their acquisition
   and processing context.
```

Do not claim an undocumented retention duration, automatic export behavior,
storage lifecycle, or storage format.

### 3. System Relationship

Replace the three-column relationship table with a concise two-column
`list-table`. Put each link in the system-name cell so a separate navigation
section is unnecessary.

Proposed content:

```rst
.. list-table::
   :header-rows: 1

   * - System
     - Primary Responsibility
   * - :doc:`Primary Data Pipeline <primary_data_pipeline/index>`
     - Frame reconstruction, spectral processing, and output retention.
   * - :doc:`Device Control And Acquisition Coordination <device_control_and_acquisition_coordination/index>`
     - Connection, acquisition, integration-time, and command coordination.
   * - :doc:`Operator Application <operator_application/index>`
     - Session control, visualization, settings, and export initiation.
```

The responsibility cells shall remain short responsibility labels rather than
repeat each child system's full summary.

Remove:

- the `Downstream Or Adjacent Relationship` column;
- all downstream or adjacent relationship cells;
- the separate `Related Pages` heading and bullet list.

### 4. Integration Boundary

Use one factual Summary field. Remove Expected Outcome and Rationale. Delete the
standalone-validation-tools statement.

Proposed content:

```rst
**Summary:** The Host PC system shall receive measurement frames and exchange
supported control requests and command outcomes at the MCU-to-Host PC boundary
defined by
:doc:`Integration Interfaces <../integration/interfaces/Interfaces>`. The
linked Integration Interfaces section owns the optical-to-CCD, CCD-to-MCU, and
MCU-to-Host PC boundary definitions.
```

The Host PC overview shall delegate boundary ownership without reproducing:

- optical or electrical handoff details;
- packet fields or encoding;
- timing or transport geometry;
- acknowledgment, recovery, or resynchronization behavior;
- command-application rules.

The current Integration Interfaces landing page does not yet enumerate all
three boundary categories. Updating that page is a separate follow-up task and
is outside this Host PC overview revision.

## Content audit

Before building, verify:

- [ ] The four existing UUID anchors and displayed UUID values are unchanged.
- [ ] The diagram placeholder remains immediately below the page title.
- [ ] System Role contains exactly one `**Summary:**` field.
- [ ] System Role contains no Expected Outcome or Rationale field.
- [ ] System Objectives contains exactly seven consecutively numbered objectives.
- [ ] Every objective names the Host PC system or a Host PC subsystem and uses `shall`.
- [ ] Every objective has a plain, visibly indented functional rationale.
- [ ] No rationale explains page organization, documentation authority, reviewability, or code layout.
- [ ] No code-derived requirement, protocol detail, unsupported threshold, UI-layout detail, or retention-policy invention is present.
- [ ] The standalone-validation-tools sentence is absent.
- [ ] System Relationship has exactly two columns and three linked system rows.
- [ ] `Downstream Or Adjacent Relationship` is absent.
- [ ] `Related Pages` is absent.
- [ ] Integration Boundary contains exactly one `**Summary:**` field.
- [ ] The Integration summary links Integration Interfaces.
- [ ] The Integration summary delegates optical-to-CCD, CCD-to-MCU, and MCU-to-Host PC boundary ownership without defining those boundaries.
- [ ] The phrases `specification shall`, `page exists`, `documentation authoritative`, `current code`, `independently reviewable`, and `normal operating path` are absent.

## Verification

Run the strict documentation build:

```powershell
python -m sphinx -E -a -W --keep-going -b html -c docs docs/source docs/build/html-structure-parity-section-2
```

Then run:

```powershell
git diff --check
git diff -- docs/source/subsystems/host_pc/overview.rst
git status --short
```

Inspect the rendered Host PC overview and confirm:

- all four retained sections render beneath the existing title;
- all seven objectives and rationales are visually distinct;
- the relationship table has two columns and no malformed cells;
- all three system links and the Integration Interfaces link resolve;
- no separate Related Pages section remains;
- no Sphinx warning is emitted.

## Execution and review gates

1. User reviews and approves or adjusts this plan.
2. A Luna implementation agent modifies only the Host PC overview source.
3. The implementation agent runs the content audit, strict Sphinx build, and
   `git diff --check`.
4. An independent Terra reviewer compares the source and rendered page against
   this plan and the checklist without editing the file.
5. Any Terra finding is resolved, followed by a repeated audit, build, diff
   check, and review.
6. The Host PC overview checklist item is marked complete only after user
   acceptance.

The Terra review shall explicitly check requirements-first provenance, factual
named-system wording, objective granularity, functional rationales, boundary
delegation, link validity, UUID preservation, and scope containment.
