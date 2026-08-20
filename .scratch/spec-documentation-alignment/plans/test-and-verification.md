# Test and Verification Documentation Creation Plan

Status: implemented and Terra-approved
Planning model: `gpt-5.6-sol`
Implementation model: `gpt-5.6-luna`
Review model: `gpt-5.6-terra`
Destination: `docs/source/subsystems/test_and_verification/`

## Objective

Create the missing requirements-first Test and Verification section. It will
define requirement-linked methods, acceptance-criterion readiness, evidence
records, calculations, regression triggers, and unresolved verification work.
It will not report any test as executed, passed, verified, or accepted.

## Source authority

1. `docs/source/Requirements And Metrics.rst`
2. `docs/source/Calibration And Characterization.rst`
3. Approved subsystem intended-behavior documentation
4. `.scratch/spec-documentation-alignment/issues/04-document-intended-tooling-and-integration-behavior.md`
5. Technical requirements, milestones, metrics, and testing sections of
   `General/SDDEC26-06_Team_Spectro_Design_Document.docx` as supporting evidence
6. CIE 233 as calibration/characterization method guidance only

Do not inspect code, tests, logs, captures, measurements, or runtime evidence
when creating this first-run specification.

## Scaffold definition

- Parent documentation area: `docs/source/subsystems/`
- Section title: `Test and Verification`
- Section slug: `test_and_verification`
- Functionality summary: Define requirement-linked verification methods,
  acceptance criteria, evidence records, regression triggers, and unresolved
  verification work without treating implementation behavior as the
  requirements source.
- Calibration mirror: false
- Formal states/transitions: none; do not invent a verification state machine.
- Diagrams: blank placeholders only if retained by the scaffold contract.

The scaffold generator requires a parent `index.rst`, but
`docs/source/subsystems/` has none. Do not create an unnecessary subsystem
wrapper or restructure existing navigation. Create the equivalent seven-page
contract manually, using the scaffold's page, UUID, and navigation rules, and
add the new section directly to `docs/source/index.rst`.

## Planned files

### Create `index.rst`

Define:

- system scope
- requirements-first authority
- ownership boundaries
- status vocabulary
- planned-only first-pass language
- related-page toctree

### Create `inputs_and_outputs.rst`

Verification inputs:

- requirement or intended-behavior claim
- approved acceptance criterion
- test configuration and environmental conditions
- reference source and reference-instrument information
- calibration and configuration versions

Evidence outputs:

- raw observations
- derived metrics
- evidence-artifact location
- pass, fail, or inconclusive disposition
- reviewer and review disposition

### Create `procedure.rst`

Define this lifecycle:

1. Select a local traceability item.
2. Confirm method and criterion readiness.
3. Record setup and environmental conditions.
4. Capture raw evidence.
5. Calculate the specified metrics.
6. Compare results with the documented criterion.
7. Classify the result as pass, fail, or inconclusive.
8. Archive evidence and trigger mismatch review where required.

### Create `diagnostics.rst`

Define failure classifications:

- invalid or uncontrolled setup
- incomplete evidence
- corrupted or incomplete interface data
- missing acceptance threshold
- failed requirement
- expired or unsuitable reference
- calibration/configuration mismatch
- procedure deviation

### Create `testing.rst`

Create the master requirement-to-test matrix and concise planned test
definitions. Do not claim execution status.

### Create `calculations.rst`

Define, where requirements and method guidance support them:

- observed complete-frame rate
- wavelength error
- FWHM
- SNR
- linearity residual
- repeatability statistic
- dark/baseline improvement
- uncertainty reporting

Use explicit TODOs for undefined windows, interpolation methods, aggregation
statistics, environmental profiles, and thresholds.

### Create `validation.rst`

Define the system/client acceptance workflow:

1. Connect the instrument.
2. Begin acquisition.
3. Confirm live spectral presentation.
4. Adjust integration time.
5. Select or apply required calibration.
6. Export the required CSV data products.
7. Review the resulting spectrum and evidence record.

### Create blank diagram placeholders

- `docs/source/_static/diagrams/test_and_verification/test_and_verification-io.vsdx`
- `docs/source/_static/diagrams/test_and_verification/test_and_verification-state-machine.vsdx`

Do not populate or export these diagrams.

### Modify shared pages

Modify:

- `docs/source/index.rst`
- `docs/source/Calibration And Characterization.rst`

Add one root navigation entry for
`subsystems/test_and_verification/index`. Add a cross-reference from
Calibration and Characterization to the new method/evidence section without
promoting implementation details into requirements.

Integration owns reverse links from its own pages.

## Requirement-to-test mapping

| Requirement | Planned verification |
|---|---|
| 400-1000 nm usable coverage | Known reference sources across both ends; exact source set and edge criterion TODO |
| 3648 effective pixels | Frame-geometry and interface check; total transported samples remain open |
| Approximately 5 nm FWHM | Narrow-source measurement and half-maximum width calculation |
| Real-time acquisition and above-100-fps design target | Complete-frame count over elapsed time; observation and lower acceptance profiles TODO |
| Complete USB frames with IDs and flags | Integration-interface test referencing the approved Integration contract |
| Bias and dark correction | Blocked-input and stored-reference comparisons over relevant conditions |
| Pixel-to-wavelength mapping | Known reference-line fit and residual evaluation |
| Flat-field/intensity/response correction | Controlled reference-source comparison; absolute versus relative scope TODO |
| Required CSV fields | Schema/content check for raw ADC counts, processed counts, wavelength, volts, and processed intensity |
| Wavelength accuracy | Reference-peak error; tolerance TODO |
| SNR | Stable-source and dark/noise acquisitions; bands and statistic TODO |
| Linearity | Controlled input variation at fixed integration time |
| Repeatability | Repeated acquisitions without realignment; statistic and duration TODO |
| Stray light and second order | Controlled filtered/unfiltered or blocked-band comparison; exact method TODO |
| Reference comparison | Same-source comparison with a suitable reference instrument when available |
| Routine user workflow | Client demonstration without code or hardware reconfiguration |

## Status language

- `documented`: requirement exists in Sphinx.
- `planned`: method is specified but has not been executed.
- `unknown` or TODO: threshold, condition, method, or evidence is missing.
- Do not use `implemented`, `passed`, `verified`, `accepted`, or measured-result
  language without a reviewed evidence artifact.
- Metrics remain provisional until their method and evidence are available.

## Local traceability proposal

| ID | Behavior |
|---|---|
| `0647B389` | Verification governance and evidence completeness |
| `CD6CB2E1` | Wavelength coverage |
| `B2F02404` | Spectral resolution and FWHM |
| `B8214C8F` | Acquisition and transfer rate |
| `3B3A1204` | Frame geometry and USB integrity |
| `E277595D` | Calibration-function verification |
| `1680B586` | CSV export schema |
| `3C903FDA` | Wavelength accuracy |
| `F39143FD` | SNR |
| `5546B204` | Linearity |
| `3A725623` | Repeatability |
| `3E2147CE` | Stray light and second-order behavior |
| `2E04E226` | Reference-instrument comparison |
| `2ED19D37` | Client acceptance workflow |
| `66D487DD` | Regression triggers |
| `CF2F2048` | Uncertainty and measurement-condition reporting |

Use `Not Started` for documented planned work and `Not In Docs` where the
criterion or method is unresolved. Implementation locations remain TODO until
the later verification phase.

## Ownership boundaries

- Integration defines interface contracts, control/data boundaries, and
  interface checkpoints.
- Test and Verification defines methods, evidence packages, calculations,
  criteria, and disposition.
- Host PC and Embedded retain behavior-local tests and reference this section
  for system-level evidence.
- Calibration and Characterization defines what is calibrated or characterized;
  this section defines how compliance is demonstrated.
- Optics remains outside the current authority effort, although optical
  readiness is a dependency for full-system characterization.

## Implementation order

1. Confirm the seven-page destination and root navigation entry.
2. Create the seven RST pages using the scaffold contract.
3. Create only the two blank VSDX placeholders.
4. Populate governance, I/O, procedure, diagnostics, testing, calculations, and
   validation content.
5. Add local traceability and explicit TODOs.
6. Update root navigation and Calibration and Characterization cross-reference.
7. Coordinate reverse links with Integration after both sections exist.
8. Audit every claim for planned-only language.

## Verification

```powershell
python -m sphinx -W --keep-going -b html -c docs docs/source docs/build/html
git diff --check
git diff -- docs/source/subsystems/test_and_verification docs/source/index.rst "docs/source/Calibration And Characterization.rst"
```

Confirm:

- All seven pages appear once.
- Cross-references and toctrees resolve.
- Blank VSDX files remain empty placeholders.
- No implementation evidence was introduced.
- Every missing criterion is visibly marked TODO.
- No test is presented as executed or accepted.

## Approval checklist

- [ ] Destination and seven-page structure approved.
- [ ] Manual scaffold fallback approved.
- [ ] Root navigation update approved.
- [ ] Calibration and Characterization cross-reference approved.
- [ ] Requirement-to-test mapping approved.
- [ ] Calculations and TODO treatment approved.
- [ ] Local traceability proposal approved.
