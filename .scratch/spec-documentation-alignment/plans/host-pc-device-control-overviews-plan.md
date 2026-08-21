# Host PC Device Control Overview Rework Plan

Status: Execution authorized

Planning model: `gpt-5.6-sol`

Implementation model: `gpt-5.6-luna`

Independent review model: `gpt-5.6-terra`

## Authority and exact scope

Use only the current `docs/source/` Host PC overview, the five target pages,
and their linked detail pages as intended-behavior authority. Do not inspect or
derive requirements from code, tests, logs, captures, runtime behavior, or
generated HTML.

Luna may edit exactly these five files:

1. `docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/index.rst`
2. `docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/index.rst`
3. `docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/index.rst`
4. `docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/index.rst`
5. `docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/index.rst`

The 24 linked Inputs and Outputs, Procedure, Diagnostics, Testing,
Calculations, and Validation pages are read-only authority for this pass.

## Common page format

Apply this order to every target page:

1. Existing page title.
2. Existing diagram placeholder note, moved immediately below the title.
3. `System Role`.
4. `System Objectives`.
5. `System Relationship`.
6. `Integration Boundary`.
7. Hidden navigation toctree, with no visible `Related Pages` heading.

For every page:

- Rename the current `Overview` section to `System Role` and preserve its
  current UUID anchor and displayed UUID exactly.
- Keep only `**Summary:**` in `System Role`.
- Use granular `The <named system> shall ...` objectives with a plain indented
  functional `Rationale:` immediately below each objective.
- Use a two-column linked `list-table` under `System Relationship`.
- Keep only `**Summary:**` under `Integration Boundary`.
- Remove `Related Pages`.
- Preserve every current toctree destination in a `:hidden:` toctree so the
  navigation hierarchy remains intact.
- Leave wire, transport, command encoding, acknowledgment, timing, and recovery
  details with Integration. Unsupported specifics remain ``Not In Docs``.

## UUID plan

Preserve each existing UUID as the `System Role` UUID. Add one visible stable
UUID to each of the other three headed sections.

| Page | Preserved System Role | New Objectives | New Relationship | New Boundary |
|---|---|---|---|---|
| Category index | `2168F561-F3A2-4FC1-82D5-9BC67A50B01B` | `3F2992AB-FC13-4F13-8BD3-089102B2636B` | `A75379EB-011D-4A55-A11F-F9EC8A3C480D` | `960065A1-1E9D-4DDF-AFC9-CB37E5C57D47` |
| Connection Management | `97AA0E47-6D1E-460D-850D-41A5C58E3C25` | `317C53B9-CA4E-4DD3-BAEF-9AFCEC4D5CA2` | `17DD02F7-F14C-49FC-A508-A8356A3E0EBC` | `6C564B0A-52AF-463E-AA6A-246B9B60C66F` |
| Acquisition Session Control | `C5B4956E-5695-4DA3-88A6-387879CF6948` | `529D7E4E-7178-42D1-A64A-624397FAC33F` | `48B24259-048C-421D-B6F9-5A4D1CA7EBCA` | `E1252260-9443-43E9-A8AE-295125BDB6A3` |
| Integration-Time Control | `9D1AE020-FA76-4BD5-9C9F-98924BE201C2` | `9BE2B69A-07FA-42E3-8E83-7FDE0675F396` | `B88E3829-F9D3-492A-B983-187076E993F8` | `42D4406F-361A-43A5-B55E-64705ADD0752` |
| Command Status Handling | `396683D9-3A49-4762-8F58-F3CF28B4DC5B` | `DE4415BD-A210-4D0A-AD19-9CC0555CC4DA` | `420FBE4D-A7AE-40E6-BBE6-696A0FDC08E1` | `60C343D4-D0A3-4F70-AD8A-3857E1B3077B` |

Use lowercase UUID text in each reST anchor and uppercase text in its displayed
`UUID:` field.

## Page 1: Device Control and Acquisition Coordination

### System Role

**Proposed summary:** The Host PC device-control and acquisition-coordination
system shall coordinate connection state, acquisition start and stop actions,
complete-frame routing, integration-time requests, and command outcomes so
acquisition-control state remains available to operator and processing
workflows.

### System Objectives

1. **Connection state:** The Host PC device-control system shall maintain the
   connection states Disconnected, Connecting, Ready, and Unavailable and shall
   gate acquisition and command actions until the device is Ready.

   Rationale: Explicit readiness prevents control actions from being issued
   through a connection that is absent, incomplete, or unusable.

2. **Connection loss:** The Host PC device-control system shall gate dependent
   actions and expose an unavailable state when an operator disconnect or
   observed connection loss occurs.

   Rationale: Removing readiness after a disconnect prevents later actions
   from relying on a device that can no longer accept them.

3. **Acquisition start and frame routing:** The Host PC
   acquisition-coordination system shall accept an acquisition-start request
   only while the connection is Ready and shall route complete frames to
   processing and retention while acquisition is active.

   Rationale: Readiness gating and active-session routing keep received frames
   associated with a valid acquisition session.

4. **Acquisition stop and disposition:** The Host PC acquisition-coordination
   system shall accept an acquisition-stop request, prevent new frames from
   entering the session after the approved stop boundary, and expose the
   session as complete, partial, or interrupted.

   Rationale: A visible stop disposition prevents incomplete or interrupted
   data from being mistaken for a complete session.

5. **Integration-time request:** The Host PC integration-time-control system
   shall validate an operator request against approved constraints when those
   constraints are documented, submit the request through the Integration
   control interface, and classify the result as accepted, rejected, or
   unavailable.

   Rationale: Validation and outcome classification prevent an unapproved or
   unsuccessful setting request from being represented as active.

6. **Command outcome:** The Host PC command-status-handling system shall gate
   commands using connection and acquisition preconditions, distinguish
   success, failure, rejection, unavailable, and missing outcomes, and update
   only the dependent actions permitted by the outcome.

   Rationale: Distinguishing unsuccessful outcomes from success prevents
   acquisition state from advancing on a failed or unresolved command.

7. **Visible control state:** The Host PC device-control and
   acquisition-coordination system shall expose connection,
   acquisition-session, integration-time-request, and command-outcome state to
   the operator workflow.

   Rationale: Visible state lets the operator distinguish ready, pending,
   active, rejected, and unavailable control conditions.

### System Relationship

Use a two-column `list-table` with these linked rows:

| System | Primary Responsibility |
|---|---|
| `Connection Management <connection_management/index>` | Device attachment, readiness, connection loss, and action gating. |
| `Acquisition Session Control <acquisition_session_control/index>` | Acquisition start and stop, complete-frame routing, and session disposition. |
| `Integration-Time Control <integration_time_control/index>` | Request validation, outcome classification, and pending or active value state. |
| `Command Status Handling <command_status_handling/index>` | Command-outcome normalization and dependent-action gating. |

Use `:doc:` links in the first column.

### Integration Boundary

**Proposed summary:** The Host PC device-control and acquisition-coordination
system shall exchange supported acquisition-control requests and device
outcomes at the MCU-to-Host PC boundary defined by
the `Integration Interfaces` document at
`../../integration/interfaces/system_boundaries/Integration Interfaces`.
Integration owns wire-level command encoding, status meanings,
acknowledgments, timing, retry, recovery, and request-application details;
unresolved specifics remain ``Not In Docs``.

### Hidden toctree

```rst
.. toctree::
   :maxdepth: 1
   :hidden:

   connection_management/index
   acquisition_session_control/index
   integration_time_control/index
   command_status_handling/index
```

## Page 2: Connection Management

### System Role

**Proposed summary:** The Host PC connection-management system shall respond to
operator connect and disconnect requests, maintain device connection and
readiness state, gate acquisition and command actions until readiness is
confirmed, and expose connection loss or unavailability.

### System Objectives

1. The Host PC connection-management system shall maintain the Disconnected,
   Connecting, Ready, and Unavailable connection states.

   Rationale: Distinct states prevent a connection attempt or failed connection
   from being represented as ready.

2. The Host PC connection-management system shall enter Connecting from
   Disconnected only in response to an operator connection request and shall
   evaluate device availability and interface readiness.

   Rationale: Requiring an explicit request and readiness evaluation prevents
   unintended attachment and premature control access.

3. The Host PC connection-management system shall enter Ready only after the
   connection is confirmed usable for host control.

   Rationale: Confirmed readiness protects acquisition and command workflows
   from using an incomplete connection.

4. The Host PC connection-management system shall gate acquisition and command
   actions while the connection is Disconnected, Connecting, or Unavailable.

   Rationale: Gating dependent actions prevents requests from being applied
   when no usable device connection exists.

5. The Host PC connection-management system shall transition out of Ready,
   gate dependent actions, and expose the unavailable condition after an
   operator disconnect or observed connection loss.

   Rationale: Immediate loss handling prevents stale readiness from allowing
   further control actions.

Discovery, port selection, automatic reconnect, timeout, and retry policy
remain ``Not In Docs``.

### System Relationship

| Page | Primary Responsibility |
|---|---|
| `Inputs and Outputs <inputs_and_outputs>` | Connection requests and availability inputs; visible state and readiness outputs. |
| `Procedure <procedure>` | Connection flow, allowed transitions, and lifecycle states. |
| `Diagnostics <diagnostics>` | Unavailable-device, connection-loss, and incomplete-readiness conditions. |
| `Testing <testing>` | Attach, detach, readiness-gating, and device-loss checks. |
| `Calculations <calculations>` | Readiness evaluation and open connection-policy decisions. |
| `Validation <validation>` | Local behavior claim, traceability, and evidence method. |

Implement these as `:doc:` links in a two-column `list-table`.

### Integration Boundary

**Proposed summary:** The Host PC connection-management system shall determine
availability and readiness at the MCU-to-Host PC boundary defined by
the `Integration Interfaces` document at
`../../../integration/interfaces/system_boundaries/Integration Interfaces`.
Integration owns the low-level attachment and transport boundary; device
discovery, port selection, automatic reconnect, timeout, and retry policy
remain ``Not In Docs``.

### Hidden toctree

Retain `inputs_and_outputs`, `procedure`, `diagnostics`, `testing`,
`calculations`, and `validation`, in that order, under a `:hidden:` toctree.

## Page 3: Acquisition Session Control

### System Role

**Proposed summary:** The Host PC acquisition-session-control system shall
coordinate measurement-session start and stop behavior after connection
readiness, route complete frames during active acquisition, and expose whether
the resulting session is complete, partial, or interrupted.

### System Objectives

1. The Host PC acquisition-session-control system shall accept a Start request
   only while the connection state is Ready.

   Rationale: Start gating prevents an acquisition from beginning without a
   usable device connection.

2. The Host PC acquisition-session-control system shall enter Acquiring only
   after the acquisition-start outcome is accepted.

   Rationale: Waiting for acceptance prevents a pending or failed request from
   being represented as an active acquisition.

3. The Host PC acquisition-session-control system shall route complete
   measurement frames to processing and retention while the acquisition
   session remains active.

   Rationale: Routing only within the active session preserves the association
   between received frames and the session that requested them.

4. The Host PC acquisition-session-control system shall accept a Stop request
   and prevent new frames from entering the session after the approved stop
   boundary.

   Rationale: Closing frame admission at the stop boundary prevents later
   frames from being attributed to a completed session.

5. The Host PC acquisition-session-control system shall expose whether a
   stopped session is complete, partial, or interrupted.

   Rationale: Session disposition prevents incomplete measurements from being
   treated as complete data products.

6. The Host PC acquisition-session-control system shall keep acquisition
   transport rate, display update rate, and the above-100-fps system design
   target as distinct measures.

   Rationale: Separating these measures prevents evidence for one boundary from
   being used as acceptance evidence for another.

Pause, buffering, backpressure, dropped-frame, and stop/drain behavior remain
``Not In Docs``.

### System Relationship

| Page | Primary Responsibility |
|---|---|
| `Inputs and Outputs <inputs_and_outputs>` | Start and stop inputs, readiness and frame inputs, and session outputs. |
| `Procedure <procedure>` | Session flow, transition conditions, and acquisition states. |
| `Diagnostics <diagnostics>` | Missing-frame, identity-gap, and stop-completeness conditions. |
| `Testing <testing>` | Start, stop, complete-frame feed, and not-ready checks. |
| `Calculations <calculations>` | Separation of acquisition, display, and system-target rates. |
| `Validation <validation>` | Local behavior claim, traceability, and evidence method. |

Implement these as `:doc:` links in a two-column `list-table`.

### Integration Boundary

**Proposed summary:** The Host PC acquisition-session-control system shall
exchange supported Start and Stop requests, outcomes, complete frames, and
status at the MCU-to-Host PC boundary defined by
the `Integration Interfaces` document at
`../../../integration/interfaces/system_boundaries/Integration Interfaces`.
Integration owns the low-level request and frame-transfer contract; pause,
buffering, backpressure, dropped-frame response, and stop/drain policy remain
``Not In Docs``.

### Hidden toctree

Retain all six current detail-page entries, in their current order, under a
`:hidden:` toctree.

## Page 4: Integration-Time Control

### System Role

**Proposed summary:** The Host PC integration-time-control system shall receive
an operator-requested integration time, validate it against approved
constraints when available, submit it through the Integration control
interface, expose its outcome, and distinguish pending from active values.

### System Objectives

1. The Host PC integration-time-control system shall receive the
   operator-requested integration time together with the current connection and
   acquisition state.

   Rationale: Retaining request and system state together preserves the context
   in which the change was requested.

2. The Host PC integration-time-control system shall validate a requested
   integration time against approved device constraints when those constraints
   are documented.

   Rationale: Constraint validation prevents a known-invalid request from being
   submitted as an acceptable device setting.

3. The Host PC integration-time-control system shall submit an eligible request
   through the Integration control interface.

   Rationale: Using the shared control boundary keeps host intent and device
   application within one interface contract.

4. The Host PC integration-time-control system shall classify the device
   outcome as accepted, rejected, or unavailable and shall expose that outcome
   to the operator workflow.

   Rationale: Explicit classification prevents rejection or interface
   unavailability from being mistaken for acceptance.

5. The Host PC integration-time-control system shall expose whether an accepted
   value is pending or active and shall apply the value at the documented
   subsequent acquisition boundary.

   Rationale: Distinguishing pending from active prevents measurements from
   being associated with a setting that has not yet taken effect.

6. The Host PC integration-time-control system shall leave the active
   integration-time value unchanged after rejection or interface
   unavailability.

   Rationale: Preserving the prior active value prevents an unsuccessful
   request from changing the measurement context.

Units, range, quantization, default, acknowledgment, and exact application
boundary remain ``Not In Docs``.

### System Relationship

| Page | Primary Responsibility |
|---|---|
| `Inputs and Outputs <inputs_and_outputs>` | Requested value, operating state, device outcome, and pending or active status. |
| `Procedure <procedure>` | Request validation, submission, classification, and application flow. |
| `Diagnostics <diagnostics>` | Invalid-request, rejection, and undefined-boundary conditions. |
| `Testing <testing>` | Accepted, rejected, unavailable, unchanged-frame, and state-visibility checks. |
| `Calculations <calculations>` | Constraint validation and unresolved value definitions. |
| `Validation <validation>` | Local behavior claim, traceability, and evidence method. |

Implement these as `:doc:` links in a two-column `list-table`.

### Integration Boundary

**Proposed summary:** The Host PC integration-time-control system shall submit
supported integration-time requests and receive their outcomes at the
MCU-to-Host PC boundary defined by
the `Integration Interfaces` document at
`../../../integration/interfaces/system_boundaries/Integration Interfaces`.
Integration owns wire-level request encoding, acknowledgment, and
device-application semantics; units, range, quantization, default,
acknowledgment behavior, and the exact application boundary remain
``Not In Docs``.

### Hidden toctree

Retain all six current detail-page entries, in their current order, under a
`:hidden:` toctree.

## Page 5: Command Status Handling

### System Role

**Proposed summary:** The Host PC command-status-handling system shall gate
operator commands using connection and acquisition state, submit eligible
requests through Integration, classify returned outcomes, expose command
status, and permit only the dependent actions authorized by that outcome.

### System Objectives

1. The Host PC command-status-handling system shall gate an operator command
   using the current connection and acquisition preconditions.

   Rationale: Precondition gating prevents a command from being submitted when
   the device or acquisition state cannot support it.

2. The Host PC command-status-handling system shall submit an eligible command
   through the Integration control interface.

   Rationale: Using the shared control interface keeps the request associated
   with the device outcome returned for it.

3. The Host PC command-status-handling system shall classify the returned
   outcome as success, failure, rejection, or unavailable and shall not report
   a missing outcome as success.

   Rationale: Complete classification prevents unsuccessful or unresolved
   commands from advancing the success path.

4. The Host PC command-status-handling system shall expose a normalized command
   status, preserve failure context, and distinguish rejection from transport
   failure.

   Rationale: Preserving the outcome class gives operator and dependent
   workflows the information needed to respond safely.

5. The Host PC command-status-handling system shall update only the dependent
   actions permitted by the classified outcome and shall not advance
   acquisition after failure, rejection, unavailability, or a missing outcome.

   Rationale: Outcome-based gating prevents host state from representing a
   device action that did not succeed.

Command vocabulary, status vocabulary, timeout, retry, and recovery rules
remain ``Not In Docs``.

### System Relationship

| Page | Primary Responsibility |
|---|---|
| `Inputs and Outputs <inputs_and_outputs>` | Operator command, readiness state, Integration outcome, and normalized status. |
| `Procedure <procedure>` | Command gating, submission, classification, and dependent-action flow. |
| `Diagnostics <diagnostics>` | Failure context, rejection distinction, and missing-outcome handling. |
| `Testing <testing>` | Outcome-class, no-advance-on-failure, and status-visibility checks. |
| `Calculations <calculations>` | Outcome classification and unresolved command policies. |
| `Validation <validation>` | Local behavior claim, traceability, and evidence method. |

Implement these as `:doc:` links in a two-column `list-table`.

### Integration Boundary

**Proposed summary:** The Host PC command-status-handling system shall submit
eligible commands and receive command outcomes at the MCU-to-Host PC boundary
defined by
the `Integration Interfaces` document at
`../../../integration/interfaces/system_boundaries/Integration Interfaces`.
Integration owns wire-level command and status definitions; command vocabulary,
status vocabulary, timeout, retry, and recovery rules remain ``Not In Docs``.

### Hidden toctree

Retain all six current detail-page entries, in their current order, under a
`:hidden:` toctree.

## File operations

- Use `apply_patch` to edit only the exact five authorized source files.
- Do not create, move, rename, or delete documentation files.
- Do not edit `docs/source/subsystems/host_pc/overview.rst`; use it only as the
  finalized format reference.
- Do not edit linked detail pages or Integration pages.
- Do not hand-edit generated HTML.
- Preserve page paths, titles, existing UUIDs, and all current toctree targets.
- Preserve unrelated working-tree changes.

## Implementation audits

Before building, assert:

- Exactly the five authorized source files changed for this workstream.
- Every page begins with its title followed immediately by the diagram note.
- Every page has exactly four UUID-tagged headed sections.
- All five original UUID anchors and displayed values are unchanged.
- All 15 new UUIDs are unique across `docs/source/`.
- Every `System Role` and `Integration Boundary` contains only `**Summary:**`.
- The category has seven objectives; each leaf has four to seven.
- Every objective uses `The <named system> shall ...` and has an immediately
  associated, visibly indented functional rationale.
- No rationale discusses page organization, documentation authority,
  implementation review, or code layout.
- Every relationship table has exactly two columns and linked first-column
  entries.
- No `Downstream Or Adjacent Relationship` column or visible `Related Pages`
  heading remains.
- Every former toctree target appears once in a hidden toctree.
- Every boundary summary links the canonical Integration Interfaces page.
- No page invents encoding, acknowledgment, timeout, retry, recovery,
  buffering, stop/drain, application-boundary, range, unit, or quantization
  requirements.
- Unsupported specifics remain explicitly ``Not In Docs``.
- Acquisition transport rate, display update rate, and the above-100-fps
  system target remain separate.
- No implementation evidence appears as intended behavior.

Run focused source audits:

```powershell
rg -n "^(Overview|Related Pages)$|Downstream Or Adjacent|Expected Outcome|^\*\*Rationale:\*\*" docs/source/subsystems/host_pc/device_control_and_acquisition_coordination -g index.rst
rg -n "^\*\*Objective [0-9]+:\*\*" docs/source/subsystems/host_pc/device_control_and_acquisition_coordination -g index.rst
rg -n "uuid-|^UUID:" docs/source/subsystems/host_pc/device_control_and_acquisition_coordination -g index.rst
rg -n "specification shall|page exists|documentation authoritative|current code|implementation" docs/source/subsystems/host_pc/device_control_and_acquisition_coordination -g index.rst
```

## Strict verification

```powershell
python -m sphinx -E -a -W --keep-going -b html -c docs docs/source docs/build/html-structure-parity-section-2
git diff --check
git diff -- docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/index.rst docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/index.rst docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/index.rst docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/index.rst docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/index.rst
git status --short
```

Inspect all five rendered pages and confirm the diagram is first; sections are
in order; rationales render subordinate to objectives; tables have two columns
and valid links; hidden toctrees preserve navigation; no Related Pages section
appears; Integration links resolve; and Sphinx reports no orphan,
duplicate-label, unknown-document, malformed-table, or other warning.

## Luna implementation gate

Luna shall:

1. Read this plan, the finalized Host PC overview, all five target pages, and
   all 24 linked detail pages.
2. Make one bounded `apply_patch` change affecting only the five target files.
3. Preserve existing UUIDs and link destinations and add the planned UUIDs.
4. Implement the proposed summaries, objectives, rationales, linked tables,
   boundary summaries, and hidden toctrees without filling open policies from
   implementation knowledge.
5. Run the source audits, strict Sphinx build, rendered-page inspection,
   scoped diff, and `git diff --check`.
6. Report changed files, objective/UUID/link counts, build result, and the open
   details intentionally retained as ``Not In Docs``.

## Independent Terra review gate

Terra performs a read-only review after Luna finishes. Terra compares the five
diffs with the finalized Host PC overview, this plan, the 24 authoritative
detail pages, and the requirements-first authoring rules.

Terra shall approve only when:

- system facts replace documentation-centric prose;
- summaries are summary-only;
- objectives are granular, complete, nonduplicative, and source-supported;
- every objective uses named-system `shall` language and a functional
  rationale;
- no open behavior has silently become a requirement;
- category objectives accurately roll up the four leaf systems;
- each leaf accurately summarizes its detail pages;
- Integration ownership is clear without duplicated boundary definitions;
- unsupported specifics remain ``Not In Docs``;
- tables are concise, linked, and two-column;
- hidden toctrees preserve all navigation links;
- original UUIDs and paths remain stable;
- scope is limited to the five authorized files; and
- strict Sphinx and `git diff --check` pass.

Terra returns approval or line-specific findings and does not edit files. Any
finding returns to Luna for correction, repeat audits, a fresh strict build and
diff check, and another Terra review.

## Definition of done

This workstream is done only when:

1. The five authorized pages match the finalized Host PC overview structure.
2. The planned UUIDs, summaries, objective sets, rationales, relationship
   tables, boundary summaries, and hidden toctrees are present.
3. Existing UUIDs, page paths, and navigation targets are preserved.
4. All content assertions and focused audits pass.
5. The strict Sphinx build completes with warnings treated as errors.
6. `git diff --check` passes and the diff contains no out-of-scope source edit.
7. Rendered-page inspection passes for all five pages.
8. Terra provides independent approval with no unresolved finding.
