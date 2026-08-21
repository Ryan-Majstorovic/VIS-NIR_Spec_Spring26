# Host PC Branching Objectives Revision Plan

Status: Execution authorized by the user's branching-objective revision request  
Planning model: `gpt-5.6-sol`  
Implementation model: `gpt-5.6-luna`  
Independent review model: `gpt-5.6-terra`

## Outcome

Revise the Host PC overview hierarchy so objectives form a real functional
decomposition rather than a repeated inventory of the next page level.

- The Host PC overview will contain nine consecutively numbered objectives:
  three for Primary Data Pipeline, three for Device Control And Acquisition
  Coordination, and three for Operator Application.
- The Host PC overview objectives will name only those three direct systems.
  They will not name, label, or enumerate any grandchild system.
- Each of the three direct-child indexes will restate its assigned Host PC
  outcomes as behavior of that direct child and decompose them into the
  functional outcomes required to achieve them. Its objectives will not merely
  say that a named child page performs a function.
- Each of the fourteen leaf indexes will remain a functional decomposition of
  its parent outcome. Their existing objective sets already name the leaf
  system and state functional requirements, so all fourteen are read-only
  lineage-audit targets for this revision.

This is a requirements-first documentation change. It is not a conformance
review and shall not use code or runtime behavior to create intended behavior.

## Authority and inspected material

Behavioral authority is limited to `docs/source/`, with special weight given to
`docs/source/Requirements And Metrics.rst`. The current Host PC pages are
authoritative intended-behavior text even where they record an unresolved
boundary. Code, tests, logs, captures, measurements, generated HTML, and
historical implementation notes are excluded from behavioral research.

The planning pass inspected:

- `docs/source/Requirements And Metrics.rst`;
- `docs/source/subsystems/host_pc/overview.rst`;
- all seventeen Host PC `index.rst` pages below the overview: three category
  indexes and fourteen leaf indexes;
- `.scratch/spec-documentation-alignment/plans/host-pc-overview-revision-plan.md`;
- the three branch plans for Primary Data Pipeline, Device Control And
  Acquisition Coordination, and Operator Application; and
- `.scratch/spec-documentation-alignment/host-pc-page-review-checklist.md`.

The earlier plans record how the current format was produced. They are useful
history, but this plan supersedes their objective hierarchy where they direct a
parent page to enumerate its children.

## Current-state findings

The current pages already establish the required presentation contract:

1. a diagram or diagram placeholder immediately below the title;
2. `System Role` with a single `**Summary:**` field;
3. consecutively numbered named-system `shall` objectives, each followed
   immediately by one plain indented `Rationale:` paragraph;
4. a two-column linked relationship table;
5. a Summary-only boundary section;
6. no visible `Related Pages` section; and
7. a heading-free hidden toctree on every current `index.rst` page.

The Host PC overview does not contain a toctree because the root documentation
toctree already owns the overview and the three direct Host PC systems. Preserve
that navigation ownership. The top relationship table remains the overview's
direct-system navigator; do not add a second toctree route from this page.

The objective hierarchy has two defects:

- The Host PC overview reaches below its direct-system boundary by naming bias
  and dark correction, bad-pixel handling, wavelength mapping, spectral
  correction, session control, calibration and settings, visualization, and
  export behavior directly.
- Each category index largely repeats one objective per named child system.
  This creates a directory inventory, not a decomposition of the category's
  assigned functional goals.

The fourteen leaf indexes already use the current leaf system as the named
subject and decompose its behavior into functional outcomes. They therefore do
not need objective-hierarchy edits. Their existing conditional wording and
open-boundary statements for stop/drain behavior, integration-time application,
pause/resume behavior, and retention policy remain source constraints to audit,
not authority to expand in the four modified parent pages.

Accordingly, the exact implementation scope is four pages: the Host PC
overview and the three category indexes. The fourteen leaf indexes are
read-only inputs and verification endpoints.

## Required common format

Preserve this exact headed-block order on every target page:

1. `System Role`
2. `System Objectives`
3. `System Relationship` or the existing leaf-level relationship title
4. the existing boundary title

The diagram remains above `System Role`, and the hidden toctree remains after
the boundary. Do not add grouping subheadings inside `System Objectives`.
Grouping at the Host PC level is expressed by contiguous objective order:
objectives 1-3 are Primary Data Pipeline, 4-6 are Device Control And
Acquisition Coordination, and 7-9 are Operator Application.

Every normative objective shall use this form:

```rst
**Objective N:** The <named system> shall <perform X> <under condition Y> to
<produce Z>.

   Rationale: <why that behavior or boundary is needed, or the failure it prevents>.
```

Rationales remain plain indented paragraphs. Do not bold `Rationale:`. Do not
introduce implementation terminology, UI layout, protocol details, storage
mechanisms, or acceptance values that are not already supported by
`docs/source/`.

## Objective hierarchy

The identifiers below are planning trace labels only. They shall not be added
to the reStructuredText and shall not replace the visible UUIDs.

### Level 0: Host PC overview

Modify `docs/source/subsystems/host_pc/overview.rst`.

Replace the current seven-objective set with the following nine-objective set.
Each objective must name exactly one of the three direct Host PC systems.

| Objective | Direct-system outcome | Rationale intent |
|---|---|---|
| HP-PDP-1 / Objective 1 | The Host PC Primary Data Pipeline shall accept only complete measurement frames from the Integration boundary and preserve all 3648 effective detector samples in acquisition order with their frame context for processing. | Protect detector-position and frame identity from incomplete or reordered input. |
| HP-PDP-2 / Objective 2 | The Host PC Primary Data Pipeline shall apply approved and compatible processing and calibration inputs to qualified detector data to produce corrected, wavelength-associated spectra. | Prevent unavailable, incompatible, or undefined processing inputs from silently changing measurement meaning. |
| HP-PDP-3 / Objective 3 | The Host PC Primary Data Pipeline shall preserve source raw counts and assemble aligned raw and derived measurement products into a session-ready record for operator use. | Keep every derived value traceable to the same source measurement and usable by downstream Host PC workflows. |
| HP-DCA-1 / Objective 4 | The Host PC Device Control And Acquisition Coordination system shall establish and maintain device connection readiness and gate device-dependent actions until the connection is usable. | Prevent unavailable or incomplete connections from authorizing control actions. |
| HP-DCA-2 / Objective 5 | The Host PC Device Control And Acquisition Coordination system shall coordinate setting, acquisition-start, and acquisition-stop requests with current connection and session state and shall advance dependent state only for accepted outcomes. | Prevent requested or failed device actions from being represented as active. |
| HP-DCA-3 / Objective 6 | The Host PC Device Control And Acquisition Coordination system shall associate complete frames with an active acquisition and expose control and session outcomes to processing and operator workflows. | Preserve acquisition context and make incomplete, interrupted, rejected, or unavailable conditions visible. |
| HP-OA-1 / Objective 7 | The Host PC Operator Application shall coordinate operator session actions and accepted configuration with visible connection and acquisition state. | Prevent unavailable or out-of-sequence actions and ambiguous configuration from appearing valid. |
| HP-OA-2 / Objective 8 | The Host PC Operator Application shall present qualified spectra together with device and session status and shall identify unavailable, stale, or invalid presentation data. | Let the operator interpret measurements in their operating context without mistaking invalid data for current data. |
| HP-OA-3 / Objective 9 | The Host PC Operator Application shall retain eligible session-associated data, initiate the required CSV export, report its outcome, and preserve reviewable data after an unsuccessful export. | Protect the source session and prevent failed or incomplete output from appearing successful. |

Top-page prohibitions:

- Do not use the names of any of the fourteen grandchildren in the objective
  block.
- Do not enumerate correction stages, UI subfunctions, or control subfunctions
  in the objective block.
- Do not add section headings for the three objective groups.
- Keep the relationship table limited to the same three direct systems.
- Do not add a top-page toctree; preserve the root documentation toctree as the
  sole navigation owner of the overview and its three direct systems.

### Level 1: Primary Data Pipeline

Modify `docs/source/subsystems/host_pc/primary_data_pipeline/index.rst`.
Replace the child-named objective set with objectives whose named subject is
always `The Host PC primary-data-pipeline system`. The relationship table, not
the objective text, remains the inventory of the six direct child systems.

| Pipeline objective | Decomposes | Functional outcome | Rationale intent |
|---|---|---|---|
| PDP-1 | HP-PDP-1 | Accept only eligible complete measurement content; confirm frame identity, status, and 3648-effective-pixel geometry; preserve ordered raw ADC counts and frame context. | Prevent incomplete, incompatible, or misordered input from advancing. |
| PDP-2 | HP-PDP-2 | Apply enabled, available, and compatible bias and dark terms while preserving raw counts and correction metadata. | Prevent unavailable or incompatible calibration data from silently changing the measurement. |
| PDP-3 | HP-PDP-2 | Qualify known unreliable detector positions using a geometry-compatible mask and retain mask identity and affected positions. | Prevent unreliable positions from silently qualifying as valid and preserve mask provenance. |
| PDP-4 | HP-PDP-2 | Associate each effective detector position with wavelength using an approved map and retain coverage and known-reference residual evidence. | Protect wavelength meaning and retain validation traceability. |
| PDP-5 | HP-PDP-2 | Apply separately configured flat-field or PRNU, spectral-response or QE, and normalization operations only when their required inputs and bases are defined and compatible. | Prevent distinct or undefined corrections from being conflated or applied without prerequisites. |
| PDP-6 | HP-PDP-3 | Preserve raw counts; align raw counts, processed counts, wavelength, volts when defined, and processed intensity; mark the record session-ready only when required products are complete and aligned. | Keep derived products tied to one source measurement and preserve recovery and reprocessing value. |

Do not use the six child-system names as the grammatical subject of these
objectives. Preserve the six linked relationship rows and hidden-toctree
destinations because those structures carry the page hierarchy.

### Level 2: Primary Data Pipeline leaves

The current leaf objectives already decompose the six pipeline outcomes into
functional behaviors. Preserve their wording and ordering unless Luna finds a
direct conflict with the authority boundary stated in this plan.

| Page | Parent objective | Leaf objective map | Implementation action |
|---|---|---|---|
| `primary_data_pipeline/ingress_and_adc_reconstruction/index.rst` | PDP-1 | Availability and accumulation; complete-frame and geometry qualification; ordered raw preservation; no invented samples; nonmeasurement exclusion; malformed/incomplete/identity-gap visibility. | Preserve all six objectives. |
| `primary_data_pipeline/bias_dark_correction/index.rst` | PDP-2 | Receive raw and applicable references; conditional correction equation; approved covered-input dark; compatible optional offsets; raw and metadata preservation; missing/disabled/nonfinite visibility. | Preserve all six objectives. |
| `primary_data_pipeline/bad_pixel_masking/index.rst` | PDP-3 | Receive data, mask, and geometry; confirm compatibility; qualify known-bad positions; retain provenance; expose invalid masks; block undefined replacement behavior. | Preserve all six objectives. |
| `primary_data_pipeline/wavelength_mapping/index.rst` | PDP-4 | Receive ordered positions and approved map; one wavelength per effective position; evaluate 400-1000 nm coverage; retain residual evidence; qualify unavailable or unaccepted mapping. | Preserve all five objectives. |
| `primary_data_pipeline/spectral_corrections/index.rst` | PDP-5 | Require prior qualification; independently gate flat-field/PRNU, response/QE, and normalization; preserve inputs and operation metadata; contain missing, saturated, or invalid results. | Preserve all six objectives. |
| `primary_data_pipeline/processed_spectrum_output_and_retention/index.rst` | PDP-6 | Common source identity; independent raw preservation; one-to-one array correspondence; readiness gating; application handoff; missing/misaligned/retention-failure gating. | Preserve all six objectives. |

### Level 1: Device Control And Acquisition Coordination

Modify
`docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/index.rst`.
Every objective shall name `The Host PC device-control and
acquisition-coordination system`; child names remain only in the relationship
table and hidden toctree.

| Coordination objective | Decomposes | Functional outcome | Rationale intent |
|---|---|---|---|
| DCA-1 | HP-DCA-1 | Maintain Disconnected, Connecting, Ready, and Unavailable states and gate acquisition and command actions until Ready. | Prevent absent, incomplete, or unusable connections from authorizing control. |
| DCA-2 | HP-DCA-1 | Remove readiness, gate dependent actions, and expose unavailability after operator disconnect or observed connection loss. | Prevent stale readiness from allowing later actions. |
| DCA-3 | HP-DCA-2 | Accept acquisition start only while Ready and represent acquisition as active only after an accepted start outcome. | Prevent pending or unsuccessful starts from appearing active. |
| DCA-4 | HP-DCA-2, HP-DCA-3 | Route complete frames only while acquisition is active; expose stop outcome and complete, partial, or interrupted disposition without inventing the stop/drain boundary. | Keep frames associated with a valid session and prevent incomplete data from appearing complete. |
| DCA-5 | HP-DCA-2 | Validate integration-time requests against documented constraints when available; submit eligible requests; distinguish accepted, rejected, unavailable, pending, and active state without defining the activation boundary. | Prevent an invalid or unsuccessful request from being represented as the active measurement setting. |
| DCA-6 | HP-DCA-2 | Gate commands using current preconditions; distinguish success, failure, rejection, unavailable, and missing outcomes; permit only outcome-authorized dependent actions. | Prevent host and acquisition state from advancing after a failed or unresolved command. |
| DCA-7 | HP-DCA-3 | Expose connection, acquisition-session, integration-time-request, command-outcome, and applicable rate-profile state to the operator and processing workflows. | Let dependent workflows distinguish ready, pending, active, rejected, unavailable, and separately measured rate conditions. |

Keep acquisition transport rate, display update rate, and the above-100-fps
system design target distinct. Do not turn one rate into evidence or acceptance
for another.

### Level 2: Device-control leaves

| Page | Parent objective | Leaf objective map | Implementation action |
|---|---|---|---|
| `device_control_and_acquisition_coordination/connection_management/index.rst` | DCA-1, DCA-2 | Four connection states; operator-triggered attempt; confirmed readiness; action gating; disconnect/loss handling. | Preserve all five objectives. |
| `device_control_and_acquisition_coordination/acquisition_session_control/index.rst` | DCA-3, DCA-4, DCA-7 | Ready-gated start; accepted start before Acquiring; active-session frame routing; stop outcome; complete/partial/interrupted disposition; rate separation. | Preserve all six objectives; use the page's stop/drain `Not In Docs` boundary when wording DCA-4. |
| `device_control_and_acquisition_coordination/integration_time_control/index.rst` | DCA-5 | Request plus state; validation against documented constraints; submission; outcome classification; pending versus active; prior value retained after failure. | Preserve all six objectives; do not make the category objective more specific than the leaf's exact-application-boundary `Not In Docs` statement. |
| `device_control_and_acquisition_coordination/command_status_handling/index.rst` | DCA-6 | Precondition gating; shared-interface submission; full outcome classification; normalized visible status with failure context; dependent-action gating. | Preserve all five objectives. |

### Level 1: Operator Application

Modify `docs/source/subsystems/host_pc/operator_application/index.rst`.
Every objective shall name `The Host PC operator-application system`; child
names remain only in the relationship table and hidden toctree.

| Application objective | Decomposes | Functional outcome | Rationale intent |
|---|---|---|---|
| OA-1 | HP-OA-1 | Coordinate connection, acquisition, inspection, stop, retention, and disconnect actions with visible session state and current action availability. | Prevent unavailable or out-of-sequence actions from appearing valid. |
| OA-2 | HP-OA-2 | Present qualified wavelength-associated spectra, rolling history when enabled, and connection, device, and session status. | Keep the presented measurement associated with its operating context. |
| OA-3 | HP-OA-1 | Validate calibration selections and user-setting changes before activation; report save or recall outcomes; preserve the prior active configuration after failure. | Prevent missing, incompatible, or failed configuration changes from silently governing processing. |
| OA-4 | HP-OA-3 | Accept export only for an eligible retained session; verify the five required aligned products; create CSV output; report successful, failed, or incomplete outcome. | Preserve product correspondence and prevent an unsuccessful or partial export from appearing successful. |
| OA-5 | HP-OA-1, HP-OA-3 | Preserve the association among session state, processed output, active configuration, and retained exportable data. | Prevent data or settings from becoming detached from the acquisition they govern. |
| OA-6 | HP-OA-2, HP-OA-3 | Expose unavailable, stale, invalid, incomplete, or failed conditions without presenting them as successful operation. | Prevent operator reliance on invalid workflow results. |

Do not freeze a UI layout or introduce widgets, views, screen positions,
calibration formats, filename rules, or storage policy.

### Level 2: Operator Application leaves

| Page | Parent objective | Leaf objective map | Implementation action |
|---|---|---|---|
| `operator_application/session_control/index.rst` | OA-1, OA-5, OA-6 | State-based action gating; readiness; start and visible state; inspection; controlled stop and retention; loss/unavailable/disconnect handling. | Preserve all six objectives; do not define the leaf's open pause/resume semantics at the category level. |
| `operator_application/visualization/index.rst` | OA-2, OA-6 | Qualified input; current spectrum correspondence; enabled rolling history; independent status; unavailable/stale/invalid visibility; no new measurement calculation. | Preserve all six objectives. |
| `operator_application/calibration_and_user_settings/index.rst` | OA-3, OA-5, OA-6 | Supported selection categories; context validation; accepted activation; rejection of missing/incompatible input; save/recall outcome; prior configuration retained after failure. | Preserve all six objectives. |
| `operator_application/export_initiation_and_session_retention/index.rst` | OA-4, OA-5, OA-6 | Retained-session eligibility; five-product alignment; CSV creation; explicit outcome; reviewable-data preservation after failure; bounded retention behavior. | Preserve all six objectives; do not define retention duration or storage policy at the category level. |

## Supported constraints to preserve

The branching rewrite shall retain these documented constraints without adding
precision:

- 3648 effective detector pixels, preserved in acquisition order;
- intended 400-1000 nm wavelength coverage;
- complete binary measurement frames with frame identity and status at the
  Integration-owned boundary, without copying the wire contract into Host PC;
- distinct acquisition transport, display update, and above-100-fps system
  design-target profiles;
- stored bias, covered-input frame-wise dark reference, optional per-pixel dark
  offsets, pixel-to-wavelength mapping, flat-field or PRNU, spectral-response or
  QE, and normalization only when its basis is defined;
- preservation and alignment of raw ADC counts, processed counts, wavelength,
  volts when defined, and processed intensity;
- CSV as the required export form for those five products;
- Disconnected, Connecting, Ready, and Unavailable connection states;
- success, failure, rejection, unavailable, and missing command outcomes;
- complete, partial, or interrupted acquisition-session disposition; and
- failure visibility and preservation of the prior valid state or reviewable
  data where already documented.

`About 5 nm FWHM`, characterization tests, and other instrument-level metrics
shall not be pulled into Host PC objectives unless a current Host PC page
already assigns the relevant behavior to that Host PC system.

## `Not In Docs` boundaries to preserve

Do not convert any item below into required behavior during the branching
rewrite.

| Page or branch | Keep `Not In Docs` |
|---|---|
| Host PC overview | Detailed optical/electrical/wire definitions, acknowledgment, retry, recovery, UI layout, retention duration, and storage mechanism. |
| Primary Data Pipeline | Framing, encoding, field ranges, resynchronization, malformed-input recovery, and transported geometry beyond 3648 effective pixels. |
| Ingress And ADC Reconstruction | Total transported sample count, payload relationship, parser/chunking details, timeout, checksum, resynchronization, recovery, and nonmeasurement-traffic buffering/presentation. |
| Bias And Dark Correction | Dark estimator, averaging count, reference-selection rules, clipping, and detailed optional-term order. |
| Bad Pixel Masking | Invalid-value representation, interpolation or replacement method, and edge behavior. |
| Wavelength Mapping | Function form beyond `lambda(p) = f(p)`, polynomial order, coefficient format, extrapolation, uncertainty representation, and residual acceptance threshold. |
| Spectral Corrections | Factor convention, equations, operation order, normalization basis, and tolerances. |
| Processed Spectrum Output And Retention | Volts conversion, record schema, metadata, retention duration, memory limits, and incomplete-record policy. |
| Device Control And Acquisition Coordination | Wire command/status encoding and meanings, acknowledgments, timing, retry, recovery, and request-application details. |
| Connection Management | Discovery, port selection, automatic reconnect, timeout, and retry policy. |
| Acquisition Session Control | Pause, buffering, backpressure, dropped-frame response, and stop/drain policy. |
| Integration-Time Control | Units, range, quantization, default, acknowledgment behavior, and exact application boundary. |
| Command Status Handling | Command and status vocabularies, timeout, retry, and recovery rules. |
| Operator Application | Fixed UI layout and any transfer of processing mathematics from Primary Data Pipeline. |
| Session Control | Session identity, pause semantics, resume behavior, disconnect recovery, and setup-time criterion. |
| Visualization | Axis scaling, history depth, color mapping, decimation, saturation rendering, and display-rate profile. |
| Calibration And User Settings | Formats, versions, defaults, persistence locations, compatibility-rule details, and startup self-test behavior. |
| Export Initiation And Session Retention | Filename, destination, overwrite behavior, numeric precision, metadata, retention duration, storage policy, and incomplete-session policy. |

When an objective depends on one of these unresolved items, state the supported
functional boundary and leave the unresolved detail explicitly `Not In Docs`.
Do not use phrases such as `approved policy` or `documented boundary` to imply
that an absent policy or boundary already exists.

## UUID preservation policy

All existing headed blocks remain substantive and keep their current anchor,
visible UUID, and semantic section ownership. Because this revision changes
objective text inside existing `System Objectives` blocks, it requires no new
headed-block UUIDs.

- Preserve all 72 current Host PC overview UUIDs byte-for-byte.
- Do not regenerate, normalize, reuse, or repurpose a UUID.
- Do not add a page-title UUID.
- Do not assign UUIDs to the hidden toctrees.
- If implementation unexpectedly requires a new substantive headed block,
  stop and return to planning; this plan does not authorize one.

| Page | System Role | System Objectives | Relationship | Boundary |
|---|---|---|---|---|
| Host PC System Overview | `42E97793-9F90-4EB8-9757-FDE4D6527DBC` | `90977A32-CB75-4745-B6D0-470F1B5116BE` | `55F3AB31-2428-4459-A33F-4CC03984FD05` | `7E7E9CF8-7577-4DC8-97B7-6730476D1D41` |
| Primary Data Pipeline | `2D3495CB-05F7-4990-9126-110D5070E578` | `CA0B9906-C320-4D0D-A856-BF8F3ADFB7FD` | `82DDD480-EFC3-48B7-BEB6-E3ED17755F65` | `01D4293E-28A0-439F-8DDE-949E0CF4D979` |
| Ingress And ADC Reconstruction | `7F8AC58C-1708-486C-AF4F-2D690F3CE607` | `8A67F948-8087-42D0-A37D-1AA34DB6D15B` | `703CB7D9-EDC2-4560-8A11-4C321FC92D56` | `24659D9A-0778-4E53-9580-C80921452D60` |
| Bias And Dark Correction | `CAE75BDE-39EC-404B-B6D3-8730182E9E2F` | `0498C724-6D5B-4E8F-8E55-3B0CA76CC9B0` | `72023A0D-3EA2-4C32-B64F-7186BEDF58C7` | `36FAFDC0-690B-42AF-98B7-DC22C31E8965` |
| Bad Pixel Masking | `3F21EFCE-BC97-43E0-9186-7EF999385BA0` | `7210EF46-9E87-4FF5-A0B0-67E6BDEA3920` | `32527A47-60C8-41AE-B446-9E3E5118AE17` | `67EFD8D9-A1D1-47DF-A28A-2FB1F94FA06A` |
| Wavelength Mapping | `EA7814F1-819A-4C2F-A709-6B4C829C8EB5` | `500B2C55-787B-4AE7-B6B3-6DD20C6360DF` | `D82FC69A-E22A-43EA-9CE6-50EDDAF3AF89` | `9FDA6ADC-41D8-4C77-9992-C819CA32917C` |
| Spectral Corrections | `84D8A9F5-623C-4394-B3DD-128259F5BABF` | `F46A89E2-57AF-4F66-A6C3-581CCA0A2CFA` | `367106A7-1F63-45F4-A2C6-40249F5D88AE` | `B2B90870-82AD-44E0-979F-FEE99D2947B7` |
| Processed Spectrum Output And Retention | `CD57310A-A435-497C-9C33-9CF5CD8DA7C3` | `1ED83EC4-F108-42F9-AF0B-FA83FB8F431D` | `C17F356A-D747-4A3A-985A-98DEA2055235` | `CC12D520-E64A-449D-89B5-895A9D3984A7` |
| Device Control And Acquisition Coordination | `2168F561-F3A2-4FC1-82D5-9BC67A50B01B` | `3F2992AB-FC13-4F13-8BD3-089102B2636B` | `A75379EB-011D-4A55-A11F-F9EC8A3C480D` | `960065A1-1E9D-4DDF-AFC9-CB37E5C57D47` |
| Connection Management | `97AA0E47-6D1E-460D-850D-41A5C58E3C25` | `317C53B9-CA4E-4DD3-BAEF-9AFCEC4D5CA2` | `17DD02F7-F14C-49FC-A508-A8356A3E0EBC` | `6C564B0A-52AF-463E-AA6A-246B9B60C66F` |
| Acquisition Session Control | `C5B4956E-5695-4DA3-88A6-387879CF6948` | `529D7E4E-7178-42D1-A64A-624397FAC33F` | `48B24259-048C-421D-B6F9-5A4D1CA7EBCA` | `E1252260-9443-43E9-A8AE-295125BDB6A3` |
| Integration-Time Control | `9D1AE020-FA76-4BD5-9C9F-98924BE201C2` | `9BE2B69A-07FA-42E3-8E83-7FDE0675F396` | `B88E3829-F9D3-492A-B983-187076E993F8` | `42D4406F-361A-43A5-B55E-64705ADD0752` |
| Command Status Handling | `396683D9-3A49-4762-8F58-F3CF28B4DC5B` | `DE4415BD-A210-4D0A-AD19-9CC0555CC4DA` | `420FBE4D-A7AE-40E6-BBE6-696A0FDC08E1` | `60C343D4-D0A3-4F70-AD8A-3857E1B3077B` |
| Operator Application | `71D2ED58-E8DB-4E12-BA3F-D9AB7883C5E6` | `1A395633-071F-4CE1-944C-2B9128D28BA0` | `6036BB15-B648-4643-A82F-44BC18209CD1` | `2B60386E-37B5-481E-8406-FB94ECA5A6FD` |
| Session Control | `902664D2-B91E-4A01-8911-A7A12C89657B` | `FB55B99E-7AA5-4582-A2C5-8824EF9D8B32` | `D8B9BB75-D5C6-4EFD-8D3B-D1668C6BEFB4` | `1F508F0C-776A-4183-82DC-FAB83BED83DE` |
| Visualization | `7B78AE61-551F-4FD2-BA0E-79877FFB8163` | `BF942B95-91A2-43A7-BBBC-02D3A26EF151` | `995C0E2C-FB17-4DEB-9E91-B8825654F057` | `EEADA21E-E48D-4E30-9A78-BF5A8EF98805` |
| Calibration And User Settings | `99D3B5E7-275E-4B3B-B833-6D73656602B1` | `88EFFB81-07DA-4B40-ACDA-D750932C774F` | `15ED5613-3A5A-4D14-BB75-0785F7EF044E` | `3EC98C16-6167-4966-875E-CB37D9E537B9` |
| Export Initiation And Session Retention | `4718CC11-20B8-4AB0-BF7A-398BE00E1C99` | `F3449780-965F-4C92-BC90-6CC21F8EF0B0` | `86047674-7D5D-411C-B6C5-929214569601` | `42E50D11-54C5-4644-83D7-B20C3B3D47FF` |

## File operations

### Modify in place

Luna may modify only these four files:

1. `docs/source/subsystems/host_pc/overview.rst`
2. `docs/source/subsystems/host_pc/primary_data_pipeline/index.rst`
3. `docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/index.rst`
4. `docs/source/subsystems/host_pc/operator_application/index.rst`

All fourteen Host PC leaf index pages are read-only verification targets
because their objective sets already provide the required leaf decomposition.

### Prohibited operations

- Create no documentation files.
- Move, rename, or delete no files.
- Modify no linked detail page, Integration page, root navigation page,
  generated HTML, implementation file, test, log, or historical artifact.
- Do not modify the review checklist or the earlier plans as part of
  implementation.
- Preserve unrelated working-tree changes; the Host PC pages already contain
  user-owned edits, so Luna shall patch the current content in place and shall
  not reset or reconstruct files from Git history.

## Luna implementation gate

Luna may begin only after this plan is approved. Luna shall:

1. Re-read `Requirements And Metrics.rst`, the current Host PC overview, all
   seventeen Host PC indexes, and this plan. It shall not inspect code.
2. Capture the pre-edit set of UUID anchors, visible UUIDs, relationship links,
   and hidden-toctree destinations for all eighteen overview pages.
3. Confirm that the four authorized files still match the objective and
   `Not In Docs` findings above. If authority has changed, stop and return to
   planning instead of merging assumptions.
4. Apply minimal patches only to the four authorized files.
5. Keep the diagram, System Role, relationship table, boundary summary, UUIDs,
   and existing navigation text unchanged except for line wrapping required by
   the objective edits.
6. Run the source, hierarchy, UUID, link, build, rendered-page, and diff checks
   below.
7. Report the exact four changed files, objective counts, preserved UUID count,
   hidden-toctree targets, open `Not In Docs` items, and verification results.

No direct-child or leaf page may invent behavior simply to make every branch
look symmetrical. Unequal objective counts are acceptable when they reflect
the documented functional decomposition.

## Verification

### Scope and file-operation audit

- Exactly the four authorized files changed for this plan.
- No file was created, moved, renamed, or deleted.
- All fourteen read-only Host PC index pages and every linked detail page are
  unchanged.
- Existing unrelated working-tree changes are neither incorporated nor
  reverted.

### Structure audit

For all eighteen pages:

- the diagram or placeholder is immediately below the title;
- `System Role` and the boundary contain only `**Summary:**`;
- the objective section contains consecutively numbered objectives;
- every objective is a named-system `shall` requirement followed immediately
  by a plain indented functional rationale;
- the relationship table has two columns and linked first-column entries;
- no `Related Pages` or `Downstream Or Adjacent Relationship` appears;
- all four substantive headed blocks retain visible unique UUIDs; and
- each category and leaf index hidden toctree contains every direct destination
  exactly once and no deeper descendant;
- the Host PC top overview contains no toctree and continues to rely on the root
  documentation toctree for navigation ownership.

The Host PC top page shall have exactly nine objectives. Objectives 1-3 shall
name only Primary Data Pipeline, 4-6 only Device Control And Acquisition
Coordination, and 7-9 only Operator Application. The top objective block shall
contain none of these deeper labels: Ingress And ADC Reconstruction, Bias And
Dark Correction, Bad Pixel Masking, Wavelength Mapping, Spectral Corrections,
Processed Spectrum Output And Retention, Connection Management, Acquisition
Session Control, Integration-Time Control, Command Status Handling, Session
Control, Visualization, Calibration And User Settings, or Export Initiation And
Session Retention.

The three category objective blocks shall use the category system as their
grammatical subject. Their child names shall appear only in their linked
relationship tables and hidden toctrees.

### Authority and content audit

- Every new or revised behavior traces to the current `docs/source/` hierarchy
  and does not cite code as intended-behavior evidence.
- The constraints in `Supported constraints to preserve` remain present at the
  appropriate level.
- Every open item in the `Not In Docs` table remains open.
- No absent policy is implied to exist by wording such as `approved policy` or
  `documented boundary`.
- No leaf objective exceeds the responsibility assigned by its parent branch.
- No parent objective duplicates a grandchild inventory.
- No rationale explains documentation organization, authority, code layout,
  or why a page exists.

### UUID, link, and navigation audit

- The pre-edit and post-edit sets of all 72 anchors and all 72 displayed UUIDs
  are identical.
- Every anchor remains attached to the same semantic headed block.
- The top relationship table contains exactly the three direct systems, and the
  top overview contains no toctree.
- Each category relationship table and hidden toctree contain only its direct
  children in the current order.
- Each leaf relationship table and hidden toctree retain all six detail pages
  in the current order.
- Every `:doc:` target resolves; no duplicate label, unknown document, or orphan
  warning is introduced.

### Strict build and diff checks

Run:

```powershell
python -m sphinx -E -a -W --keep-going -b html -c docs docs/source docs/build/html-structure-parity-section-2
git diff --check
git diff -- docs/source/subsystems/host_pc
git status --short
```

Inspect all eighteen rendered overview pages. Confirm objective/rationale
indentation, two-column table rendering, direct-level link scope, hidden
navigation, UUID visibility, and absence of `Related Pages`.

## Independent Terra review gate

After Luna completes and reports passing verification, Terra performs a
read-only review. Terra shall read this plan, `Requirements And Metrics.rst`,
the complete Host PC overview/index hierarchy, the four-file diff, and the
rendered pages. Terra shall not inspect code and shall not edit files.

Terra shall approve only when:

1. the top overview contains exactly three contiguous objective branches with
   two to three objectives per direct system and no grandchild label;
2. the three category pages express behavior as outcomes of the category
   system rather than as a list of child-system summaries;
3. every leaf objective set is a valid functional decomposition of its mapped
   category objective;
4. every normative statement has supported behavior, condition, output, and a
   functional rationale, or explicitly leaves the unsupported part `Not In
   Docs`;
5. the category rewrites do not broaden the leaf pages' open stop/drain,
   integration-time activation, pause/resume, or retention-policy behavior;
6. all 72 UUIDs, paths, relationship links, and direct-child toctree targets
   are preserved;
7. the required format is visually intact on all eighteen pages;
8. no out-of-scope file changed; and
9. strict Sphinx and `git diff --check` pass.

Terra returns approval or line-specific findings. Any confirmed finding goes
back to Luna for a minimal correction in the authorized files, followed by a
fresh complete audit, strict build, diff check, rendered inspection, and Terra
review.

## Definition of done

The revision is complete only when Luna has implemented the approved
four-file change, the entire eighteen-page Host PC hierarchy passes the
branching and format audits, all supported constraints and `Not In Docs`
boundaries remain intact, the 72-UUID snapshot is unchanged, strict Sphinx and
`git diff --check` pass, and Terra has no unresolved finding.
