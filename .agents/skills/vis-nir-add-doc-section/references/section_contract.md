# Section Contract

Every generated section contains these files:

- `index.rst`
- `inputs_and_outputs.rst`
- `procedure.rst`
- `diagnostics.rst`
- `testing.rst`
- `calculations.rst`
- `validation.rst`

If the user requests calibration support, also create:

- `calibration/index.rst`
- `calibration/inputs_and_outputs.rst`
- `calibration/procedure.rst`
- `calibration/diagnostics.rst`
- `calibration/testing.rst`
- `calibration/calculations.rst`
- `calibration/validation.rst`

## Header UUID Rule

Every independently traceable technical block in the generated section should have:

- a Sphinx label derived from a standard UUID
- a visible UUID line directly under that header

This applies to:

- page-level technical sections such as `Overview`, `Inputs`, `Outputs`, or `Validation Steps`
- protocol or payload layout sections
- item-level headed blocks such as states, transitions, calculations, diagnostics, tests, and validation items

Do not add UUIDs to purely organizational grouping headers that do not carry
their own technical requirement, characteristic, or verification criterion.
Do not give a page title its own UUID when the page already contains UUID-tagged
subsections that carry the real traceable content.

## `index.rst`

Include:

- page title
- exact functionality summary from the user
- `Overview` section
- note placeholder for the user-provided I/O diagram
- related-pages toctree

The `Overview` header needs a UUID when it contains substantive technical
summary content. The `Related Pages` grouping header does not.

Do not:

- describe diagram internals that have not been provided
- infer behavior from code

## `inputs_and_outputs.rst`

Include:

- input table
- output table
- export outputs directly inside the outputs table when applicable

The `Inputs` and `Outputs` headers also need UUIDs.

Use columns that keep the content compact and technical:

- item
- expected values
- structure
- purpose

## `procedure.rst`

Include:

- note placeholder for the user-provided state-machine image
- transition summary table
- state sections
- transition sections

The `State Machine`, `Transitions`, and `States` headers need UUIDs because
they define traceable behavior. Do not add a UUID-only grouping header such as
`Transition Details`.

For transitions:

- keep display IDs such as `T0`, `T1`, `TF1`
- give each transition its own UUID
- do not add a separate `ID:` line when the transition header already includes the display ID such as `Transition T0`
- match each transition item to one source state item
- define target state, one or more conditional-transition reasons, and failure target
- include a rationale field when it helps explain why the transition boundary exists

For states:

- give each state its own UUID
- do not add a separate `ID:` line when the state header already includes the display ID such as `State S0 - ...`
- define the state's functionality, output, and calculation
- include a rationale field explaining why the state exists or why its behavior is separated from adjacent states
- do not use entry criteria or exit criteria headings
- do not describe transition destinations inside the state block

## `diagnostics.rst`

Include:

- diagnostics table shaped like the outputs table

The `Diagnostics Table` header needs a UUID. Diagnostic items need UUIDs. Do
not add a UUID-only grouping header such as `Diagnostic Items`.
Do not add a separate `ID:` line when the diagnostic header already includes
the display ID such as `Diagnostic D0 - ...`.

Use these columns:

- item
- meaning
- expected range or state
- failure indication
- user alert behavior
- UUID

## `testing.rst`

Include:

- one page for unit, regression, manual, and acceptance testing
- explicit placeholders when the user has not supplied a given test type

The `Testing Matrix` header needs a UUID. Testing items need UUIDs. Do not add
a UUID-only grouping header such as `Test Item Details`.
Do not add a separate `ID:` line when the test header already includes the
display ID such as `Test TEST0 - ...`.

## `calculations.rst`

Include:

- one subsection per distinct calculation

Each calculation subsection must have a UUID. Avoid adding a second page-level
`Calculations` header below the page title unless it carries distinct technical
content. Nested prose aids such as `Variables` or `Equation Reasoning` do not
need UUIDs unless they are promoted into independently testable specification
blocks.
Do not add a separate `ID:` line when the calculation header already includes
the display ID such as `Calculation C0 - ...`.

Each calculation subsection includes:

- calculation ID
- UUID
- summary
- variables
- equation reasoning
- implementation note
- rationale

## `validation.rst`

Include:

- operator-facing checks
- expected results
- one UUID-backed validation-steps section for user-facing validation

The `Validation Steps` header needs a UUID. Write the validation path as a set
of compact step blocks under that single UUID-backed section:

- `**Step 1:**` style instruction line
- indented `**Expected Outcome:**` line under each step
- one closing `**Rationale:**` paragraph after all steps

Do not create per-step validation UUID blocks unless the user explicitly asks
for independently traceable validation items.

## Readability Style

For dense technical blocks, prefer bold lead-in labels such as:

- `**Summary:**`
- `**Functionality:**`
- `**Output:**`
- `**Calculation:**`
- `**Rationale:**`
- `**Expected Outcome:**`
- `**Step 1:**`
