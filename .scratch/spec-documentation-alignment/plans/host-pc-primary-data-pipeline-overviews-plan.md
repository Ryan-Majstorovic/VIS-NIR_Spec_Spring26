# Host PC Primary Data Pipeline Overview Rework Plan

Status: Execution authorized
Planning model: `gpt-5.6-sol`
Implementation model: `gpt-5.6-luna`
Review model: `gpt-5.6-terra`

## Purpose and authority

Rework the seven Host PC Primary Data Pipeline overview/index pages so they
follow the finalized `docs/source/subsystems/host_pc/overview.rst` format while
remaining requirements-first.

Use only the current seven index pages and their linked detail pages under
`docs/source/` as behavioral sources. The finalized Host PC overview is the
format reference. Do not inspect or derive intended behavior from code, tests,
logs, captures, measurements, or runtime behavior.

## Exact seven-file scope

Modify only:

1. `docs/source/subsystems/host_pc/primary_data_pipeline/index.rst`
2. `docs/source/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/index.rst`
3. `docs/source/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/index.rst`
4. `docs/source/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/index.rst`
5. `docs/source/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/index.rst`
6. `docs/source/subsystems/host_pc/primary_data_pipeline/spectral_corrections/index.rst`
7. `docs/source/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/index.rst`

Do not modify the format-reference overview, any of the 36 linked detail pages,
or any other repository artifact during implementation.

## Common page contract

Use this order on all seven pages:

1. Existing page title.
2. Existing diagram placeholder, moved directly below the title.
3. UUID-tagged `System Role` containing one `**Summary:**` field only.
4. UUID-tagged `System Objectives`.
5. UUID-tagged two-column relationship section.
6. UUID-tagged boundary section containing one `**Summary:**` field only.
7. Unheaded hidden toctree that preserves every current navigation target and
   its current order.

Every objective shall use this form:

```rst
**Objective N:** The <specific named system> shall <behavior> <condition> <output>.

   Rationale: <functional reason or failure prevented>.
```

Rationales are plain indented paragraphs, not bold fields. Do not use them to
explain page organization or documentation authority. Use concise two-column
`list-table` directives and keep each cell to one logical statement. Remove all
`Related Pages` headings.

Retain explicit `Not In Docs` boundaries for unresolved wire/parser behavior,
correction math not already defined, estimator and selection rules, bad-pixel
replacement methods, wavelength-map representation, thresholds, record schema,
and retention policy.

## UUID and link preservation

Preserve these existing UUIDs exactly, including anchor spelling, case in the
displayed UUID, and reference target:

| Page and section | UUID |
|---|---|
| Primary Data Pipeline - System Role | `2D3495CB-05F7-4990-9126-110D5070E578` |
| Primary Data Pipeline - System Objectives | `CA0B9906-C320-4D0D-A856-BF8F3ADFB7FD` |
| Primary Data Pipeline - System Relationship | `82DDD480-EFC3-48B7-BEB6-E3ED17755F65` |
| Ingress And ADC Reconstruction - System Role | `7F8AC58C-1708-486C-AF4F-2D690F3CE607` |
| Bias And Dark Correction - System Role | `CAE75BDE-39EC-404B-B6D3-8730182E9E2F` |
| Bad Pixel Masking - System Role | `3F21EFCE-BC97-43E0-9186-7EF999385BA0` |
| Wavelength Mapping - System Role | `EA7814F1-819A-4C2F-A709-6B4C829C8EB5` |
| Spectral Corrections - System Role | `84D8A9F5-623C-4394-B3DD-128259F5BABF` |
| Processed Spectrum Output And Retention - System Role | `CD57310A-A435-497C-9C33-9CF5CD8DA7C3` |

Generate fresh UUIDv4 values only for newly introduced headed blocks. Never
reuse or repurpose an existing UUID. All UUIDs in untouched detail pages remain
unchanged.

Preserve every existing toctree target exactly. Relationship-table links shall
use `:doc:` while an unheaded `.. toctree::` with `:hidden:` retains the current
Sphinx hierarchy. The visible table does not replace the hidden toctree.

## Page-by-page implementation

### Primary Data Pipeline

Use the current category index, the six child indexes, and the 36 linked detail
pages as its source boundary.

- Move the pipeline overview/I/O diagram placeholder below the title.
- Reduce `System Role` to a Summary stating that the pipeline qualifies
  complete measurement frames, preserves ordered detector data, performs the
  documented correction and mapping stages, and produces an aligned
  session-ready spectrum record.
- Rename `Pipeline Objectives` to `System Objectives` without changing its
  UUID.
- Replace the current four broad objectives with six named-system objectives:
  1. The Host PC ingress-and-ADC-reconstruction system qualifies complete
     measurement content and preserves ordered raw ADC counts, frame identity,
     status, and the 3648-effective-pixel boundary. The rationale protects
     detector-position order and prevents incomplete input from advancing.
  2. The Host PC bias-and-dark-correction system applies only enabled,
     available, compatible bias/dark terms while preserving raw counts and
     correction metadata. The rationale prevents silent use of unavailable or
     incompatible calibration data.
  3. The Host PC bad-pixel-masking system qualifies known unreliable positions
     using a geometry-compatible mask and retains mask provenance. The
     rationale prevents unreliable positions from silently becoming valid.
  4. The Host PC wavelength-mapping system associates each effective detector
     position with wavelength using an approved map and retains coverage and
     residual evidence. The rationale protects wavelength meaning and
     validation traceability.
  5. The Host PC spectral-corrections system supports separately configured
     flat-field/PRNU, response/QE, and normalization operations only when their
     required data are defined and compatible. The rationale prevents distinct
     or undefined corrections from being conflated.
  6. The Host PC processed-spectrum-output-and-retention system assembles
     aligned raw counts, processed counts, wavelength, volts when defined, and
     processed intensity while preserving raw data. The rationale keeps every
     product associated with the same source measurement.
- Rename `Stage Relationship` to `System Relationship` without changing its
  UUID. Replace the grid table with a two-column linked table whose six rows
  are the six child systems and their primary responsibilities.
- Add an `Integration Boundary` Summary: the pipeline receives complete
  transport candidates from the Integration-owned boundary, consumes rather
  than redefines the wire contract, and supplies aligned processed records to
  visualization, retention, and export initiation. Integration retains
  framing, encoding, field-range, resynchronization, malformed-input recovery,
  and transported-geometry ownership beyond 3648 effective detector pixels.
- Preserve the six child-index toctree entries in their current order as a
  hidden toctree.

### Ingress And ADC Reconstruction

Use only its current index and its six linked detail pages.

Create six granular objectives for the Host PC ingress-and-ADC-reconstruction
system:

1. Accept measurement traffic only while the acquisition interface is
   available and accumulate enough content to evaluate a complete frame.
2. Confirm completeness, frame identity, status, and 3648-effective-pixel
   geometry before acceptance.
3. Preserve raw ADC counts in acquisition order with frame context.
4. Reject or hold incomplete or unsupported content without inventing samples.
5. Prevent non-measurement traffic from becoming a usable spectrum frame.
6. Expose malformed/incomplete conditions and identity gaps without redefining
   Integration-owned encodings.

Rationales protect acquisition eligibility, geometry validity, detector order,
data integrity, traffic classification, and diagnostic visibility. Use a
Summary-only `Integration Boundary` that distinguishes the received complete
transport candidate from Integration-owned framing, chunking, encoding,
resynchronization, recovery, and total transported geometry.

### Bias And Dark Correction

Use only its current index and its six linked detail pages.

Create six objectives for the Host PC bias-and-dark-correction system:

1. Receive preserved raw ADC counts and enabled stored-bias, covered-input
   dark, and optional per-pixel terms.
2. Apply `C_corr(p) = C_raw(p) - B(p) - D(p)` only for enabled and available
   applicable terms.
3. Use approved covered-input data for the configured frame-wise dark
   reference without inventing an estimator.
4. Apply optional per-pixel offsets only when enabled and compatible.
5. Preserve raw counts and record every applied or bypassed correction.
6. Identify missing references, disabled corrections, and non-finite outputs
   rather than silently qualifying affected data.

Rationales protect correction validity, raw-data recoverability, and operator
awareness. Use a Summary-only `Pipeline Boundary` placing the system after
ingress and before bad-pixel/wavelength processing. Estimator, averaging count,
selection, clipping, and optional-term ordering remain `Not In Docs`.

### Bad Pixel Masking

Use only its current index and its six linked detail pages.

Create six objectives for the Host PC bad-pixel-masking system:

1. Receive corrected counts with the applicable mask and geometry identity.
2. Confirm mask compatibility with active detector geometry.
3. Mark or exclude known-bad positions before wavelength or spectral use.
4. Carry mask identity and affected positions with the processed record.
5. Surface missing, mismatched, or invalid-propagation conditions rather than
   silently applying the mask.
6. Avoid prescribing invalid-value, interpolation, replacement, or edge
   behavior while those choices remain `Not In Docs`.

Rationales protect geometry alignment, downstream validity, provenance, and
the unresolved-method boundary. Use a Summary-only `Pipeline Boundary` placing
masking after bias/dark correction and before mapping/correction.

### Wavelength Mapping

Use only its current index and its six linked detail pages.

Create five objectives for the Host PC wavelength-mapping system:

1. Receive ordered effective-pixel positions, corrected values, and an
   approved pixel-to-wavelength map.
2. Associate one wavelength with each effective detector position using the
   general relationship `lambda(p) = f(p)`.
3. Evaluate intended coverage against the documented 400-1000 nm target.
4. Retain known-reference residual evidence with the mapped product.
5. Block or qualify output when the map is unavailable, coverage is limited,
   or residual evidence is unaccepted.

Rationales protect one-to-one detector/wavelength correspondence, coverage
interpretation, validation evidence, and prevention of unvalidated wavelength
claims. Use a Summary-only `Pipeline Boundary`. Function form, polynomial
order, coefficient format, extrapolation, uncertainty, and residual thresholds
remain `Not In Docs`.

### Spectral Corrections

Use only its current index and its six linked detail pages.

Create six objectives for the Host PC spectral-corrections system:

1. Receive wavelength-associated, bias/dark-corrected,
   bad-pixel-qualified data.
2. Apply flat-field or PRNU correction only when enabled and compatible.
3. Apply spectral-response or QE correction only when enabled and compatible.
4. Apply normalization only when its basis is defined.
5. Preserve correction inputs and record each applied or bypassed operation.
6. Identify missing factors, saturation, and invalid results and prevent
   affected outputs from silently qualifying.

Rationales protect stage prerequisites, independent configurability,
reproducibility, and invalid-result containment. Use a Summary-only `Pipeline
Boundary`. Factor convention, equations, operation order, normalization basis,
and tolerances remain `Not In Docs`.

### Processed Spectrum Output And Retention

Use only its current index and its six linked detail pages.

Create six objectives for the Host PC
processed-spectrum-output-and-retention system:

1. Associate raw ADC counts, processed counts, wavelength, volts when defined,
   and processed intensity with the same source measurement.
2. Preserve raw ADC counts independently of derived values.
3. Maintain one-to-one correspondence among available product arrays.
4. Mark a record ready only when required products are complete and aligned.
5. Retain the session-ready record and provide it to visualization, retention,
   and export initiation without owning the export UI.
6. Report missing products, incompatible identities or lengths, and retention
   failures and gate affected outputs.

Rationales protect measurement identity, raw-data recovery, product alignment,
readiness integrity, application handoff, and failure visibility. Use a
Summary-only `Application Boundary`. Volts conversion, schema, metadata,
retention duration, memory limits, and incomplete-record policy remain
`Not In Docs`.

## Leaf documentation relationship table

Each leaf page shall use a two-column `Documentation Relationship` table rather
than naming false peer systems:

| Documentation | Responsibility |
|---|---|
| Linked `Inputs and Outputs` | Accepted inputs, produced outputs, metadata, and unavailable/incompatible conditions. |
| Linked `Procedure` | Ordered behavior, decisions, and processing conditions. |
| Linked `Diagnostics` | Observable failure or qualification conditions and operator gating. |
| Linked `Testing` | Behavior-local scenarios and the current acceptance basis. |
| Linked `Calculations` | Supported equation or explicit absence of a normative calculation, plus open requirements. |
| Linked `Validation` | Behavior claim, local traceability state, open decisions, and evidence method. |

Use relative `:doc:` links. Follow the table and boundary section with the
unchanged six-entry hidden toctree in this order:

1. `inputs_and_outputs`
2. `procedure`
3. `diagnostics`
4. `testing`
5. `calculations`
6. `validation`

## File operations

| Operation | Authorization |
|---|---|
| Modify the exact seven index files | Authorized |
| Create documentation files | Not authorized |
| Modify linked detail pages | Not authorized |
| Modify the Host PC format-reference overview | Not authorized |
| Move, rename, or delete files | Not authorized |
| Inspect code, tests, logs, or runtime output | Not authorized |

Before editing, Luna shall recheck `git status` for the seven targets and the
format-reference overview. Stop and report any new overlapping target-page
changes.

## Luna implementation gate

Luna may implement because this plan's status is `Execution authorized`.

Luna shall:

1. Re-read the seven targets and their 36 linked detail pages.
2. Modify only the seven authorized index files.
3. Preserve all existing UUID and navigation targets.
4. Generate new UUIDs only for newly introduced headed blocks.
5. Keep every claim within the documentation-only source boundary.
6. Run all audits and verification below.
7. Report the exact changed-file list and command results before Terra review.

## Terra independent review gate

Terra shall review the completed diff independently against the current Host PC
overview format and the same documentation-only evidence set. Review must
confirm:

- Every objective names the actual Host PC behavior system and uses `shall`.
- Every objective is granular and supported by a linked detail page.
- Every rationale protects the objective's function or prevents a specific
  failure.
- Role and boundary sections contain Summary only.
- Leaf pages do not invent architectural peer systems.
- Unresolved behavior remains explicitly `Not In Docs`.
- The 3648-effective-pixel boundary is not expanded into unsupported transport
  geometry.
- No unsupported correction equation, order, format, or threshold is added.
- Existing UUIDs and link targets are unchanged; new UUIDs are unique.
- Tables have two columns and working links.
- No `Related Pages` heading remains.
- Hidden toctrees preserve every former entry and order.
- Only the seven authorized documentation files changed.

Any finding returns to Luna for correction. Repeat Terra review and all checks
after each correction. Completion requires a finding-free Terra review.

## Audits and verification

### Scope and file audit

- `git diff --name-only` reports only the seven authorized indexes for the
  implementation workstream.
- The Host PC format-reference overview receives no new workstream changes.
- The 36 detail pages remain byte-for-byte untouched.
- No file is created, moved, renamed, or deleted.

### Structure and content audit

- Diagram placeholder is the first content after each title.
- Page sections follow the common order.
- System Role and boundary sections contain Summary only.
- Every objective uses a named system, `shall`, and a plain indented rationale.
- Every relationship table has two columns and all expected linked rows.
- No `Related Pages` heading remains.
- Hidden toctrees retain their former targets and order.
- Every behavioral claim traces to the page's linked documentation.
- Unsupported parser, correction, masking, mapping, threshold, schema, or
  retention details remain `Not In Docs`.
- No implementation evidence appears.

### UUID and link audit

- Compare all nine existing UUID label/reference pairs before and after.
- Scan `docs/source` for duplicate full UUID anchors.
- Confirm every newly added headed block has one visible UUID.
- Confirm no detail-page UUID changed.
- Confirm every `:doc:` target and hidden-toctree entry resolves.

### Strict Sphinx build

```powershell
python -m sphinx -E -a -W --keep-going -b html -c docs docs/source docs/build/html-primary-data-pipeline-overviews
```

Required result: exit code 0 with warnings treated as errors.

### Diff hygiene

```powershell
git diff --check
```

Required result: exit code 0 with no whitespace errors.

## Definition of done

- Exactly the seven authorized index pages are reworked.
- Existing UUIDs and navigation targets are preserved.
- Every new headed block has a unique visible UUID.
- The category page has six named-system objectives and a linked two-column
  system relationship table.
- Every leaf page has four to seven source-grounded objectives and a six-row
  linked documentation relationship table.
- Every page has a first-position diagram placeholder and Summary-only role and
  boundary sections.
- No separate `Related Pages` section remains.
- Hidden toctrees preserve all current navigation entries.
- Luna's audits pass.
- Terra reports no remaining findings.
- Strict Sphinx exits 0.
- `git diff --check` exits 0.
