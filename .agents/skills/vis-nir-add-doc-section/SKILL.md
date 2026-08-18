---
name: vis-nir-add-doc-section
description: Scaffold a new VIS-NIR documentation section under docs/source when the user needs the repo-specific subsection skeleton created before any research-based population work. Use this skill to create the section structure with overview, inputs and outputs, procedure, diagnostics, testing, calculations, validation, UUID anchors, parent toctree insertion, and blank Visio placeholders, then use vis-nir-populate-doc-section to research and populate the content.
---

# VIS-NIR Add Doc Section

## Overview

Scaffold a new technical documentation section under `docs/source/` for this repo. Create the page set, create blank Visio placeholder files, add the new section to the parent `index.rst`, and keep the output aligned to the current Sphinx structure.

Do not infer functionality, states, calculations, diagnostics, or tests from the repo. Require explicit user inputs for the section content.

## Required Inputs

Require these values before scaffolding:

- parent docs path
- section title
- section slug
- exact functionality summary
- whether a calibration mirror is required

Accept these optional explicit lists when the user provides them:

- states in `ID|Name|Summary` format
- transitions in `ID|From|To|Condition|FailureTarget` format
- calculations in `ID|Name|Summary` format
- diagnostics in `ID|Name|Meaning|Expected|Failure|Alert` format
- test items in `ID|Type|Name|Summary` format

If any required input is missing, ask the user for it directly. Do not guess.

## Initial Context

Read these files before scaffolding:

1. `docs/conf.py`
2. `docs/source/index.rst`
3. the target parent `index.rst`
4. one sibling section `index.rst` under the same parent when available

Use those files only to match structure and navigation behavior. Do not mine them for missing functionality content.

## Scaffold Workflow

1. Confirm the repo root is `C:\Users\ralel\OneDrive\GitHub\VIS-NIR_Spec_Spring26`.
2. Confirm the parent path exists and contains an `index.rst`.
3. Run `scripts/create_section.py` with the explicit user inputs.
4. Review the generated files for:
   - correct headings
   - linkable UUID lines on traceable technical content
   - correct toctree insertion
   - blank `.vsdx` placeholders only
5. Run a Sphinx build if the user expects validation.

## Script

Run:

```powershell
python .agents/skills/vis-nir-add-doc-section/scripts/create_section.py `
  --parent "docs/source/subsystems/host_pc/data_pipeline" `
  --title "My Section" `
  --slug "my_section" `
  --functionality "Exact user-provided functionality summary."
```

Add optional repeated arguments only when the user supplied them:

```powershell
--state "S0|Idle|Wait for a valid frame."
--transition "T0|S0|S1|Frame accepted|None"
--calculation "C0|Gain normalization|Normalize corrected counts by the selected denominator."
--diagnostic "D0|frame_flags|Latest frame flags|0x0000 expected|Non-zero flag indicates a problem|Show alert banner"
--test-item "TEST0|unit|Parser happy path|Verify the component handles the nominal case."
--with-calibration
--dry-run
```

## Authoring Rules

- Keep the content technical-only.
- Prefer stable factual wording over implementation-coupled wording when the scaffold includes any user-provided descriptive text.
- Create blank Visio files only. Do not design or populate diagrams.
- Keep diagnostics as a table shaped like the outputs table.
- Put export outputs directly in the outputs section.
- Do not add upstream or downstream user sections.
- Use standard UUIDs only. Do not preserve or emulate the older mixed UUID styles.
- Give every independently traceable technical block a visible UUID line and a native Sphinx label anchored directly from that UUID.
- Keep page titles plain when the page already contains UUID-tagged subsections that carry the actual traceable content.
- Do not attach UUIDs to purely organizational grouping headers that exist only to separate nearby content.
- Keep exact code-file and function references out of scaffold text unless the user explicitly supplied them.
- Keep lower-level traceability local to the generated section unless the user explicitly asks to update the global traceability page.

Read [references/section_contract.md](references/section_contract.md) for page requirements, [references/uuid_and_anchor_rules.md](references/uuid_and_anchor_rules.md) for link rules, and [references/file_layout_rules.md](references/file_layout_rules.md) for path conventions.

## Validation

After scaffolding:

1. Verify the new section appears once in the parent toctree.
2. Verify the generated directory contains the seven page files.
3. Verify the two blank `.vsdx` files exist.
4. Verify `calibration/` mirrors the structure only when requested.
5. Run:

```powershell
python -m sphinx -b html -c docs docs/source docs/build/html
```

6. Fix only structure or label issues introduced by the scaffold. Do not invent missing technical content.
