---
name: vis-nir-populate-doc-section
description: Research, populate, revise, or reconcile VIS-NIR Sphinx documentation under docs/source when the user wants factual, implementation-verified content built from current docs, repo code, and historical project materials in General. Use this skill after a subsection already exists, especially for calibration, characterization, host PC, embedded, optics, traceability, or documentation-repair work that must inspect sources first, route PDFs through the PDF MCP, route VSDX files through the Visio MCP, and ask two clarification rounds before writing.
---

# VIS-NIR Populate Doc Section

## Overview

Research the existing documentation, implementation, and historical project materials before proposing or writing VIS-NIR documentation. Treat this skill as the content-authoring sister to `vis-nir-add-doc-section`, which creates the initial subsection skeleton.

Read [references/research_workflow.md](references/research_workflow.md) first. Load the other reference files when their topic becomes active.

## Workflow

1. Confirm the repo root is `C:\Users\ralel\OneDrive\GitHub\VIS-NIR_Spec_Spring26`.
2. Confirm whether the requested target section already exists inside `docs/source`.
3. If the target section does not exist yet, use `$vis-nir-add-doc-section` first and only return here once the structure exists.
4. Build the initial research inventory with:

```powershell
python .agents/skills/vis-nir-populate-doc-section/scripts/manage_doc_section.py inspect `
  --topic "bias dark correction" `
  --candidate-path "docs/source/subsystems/host_pc/data_pipeline/bias_dark_correction"
```

5. Read the live sources identified by the script:
   - current docs and repo code from host paths
   - PDFs from `General` through the PDF MCP with `/workspace/...` paths
   - VSDX files from `General` through the Visio MCP with host Windows paths
   - DOCX and PPTX files from `General` through host-path OOXML inspection
6. Return the research brief before asking for any file edits.
7. Ask Round 1 clarifying questions.
8. After the user replies, ask Round 2 clarifying questions.
9. Only after both rounds complete and the destination path is confirmed, prepare the draft manifest:

```powershell
python .agents/skills/vis-nir-populate-doc-section/scripts/manage_doc_section.py draft `
  --confirmed-path "docs/source/subsystems/host_pc/data_pipeline/bias_dark_correction" `
  --topic "bias dark correction" `
  --round1 "{\"destination_confirmed\": true}" `
  --round2 "{\"terminology_confirmed\": true}"
```

10. Before any move, rename, delete, or overwrite, present the safe file-operation plan.
11. Only apply approved writes with:

```powershell
python .agents/skills/vis-nir-populate-doc-section/scripts/manage_doc_section.py apply `
  --confirmed-path "docs/source/subsystems/host_pc/data_pipeline/bias_dark_correction" `
  --draft-manifest "path/to/manifest.json" `
  --approve-destructive false
```

## Source Routing

Use the tool-specific routing contract in [references/source_intake_rules.md](references/source_intake_rules.md).

- Treat all content under `C:\Users\ralel\OneDrive - Iowa State University\VIS-NIR Spectrum - Documents\General` as first-class evidence with equal base discovery weight.
- Route PDFs from `General` through the PDF MCP using `/workspace/...` paths.
- Route VSDX files from `General` through the Visio MCP using host Windows paths.
- Read DOCX and PPTX files from `General` from host Windows paths.
- Read repo docs and implementation from host Windows paths.

For VSDX evidence, start with `mcp__visio_server.list_shapes` and use the returned shape text as diagram evidence. Do not claim diagram meaning that is not supported by the extracted text and the surrounding project sources.

## Preferred References

Read [references/preferred_references.md](references/preferred_references.md) before calibration or characterization work.

The file `/workspace/Reference PDFs/Calibration Characterization andUse of Spectroradiometers.pdf` is a mandatory preferred reference for:

- calibration documentation
- characterization documentation
- spectroradiometer usage
- radiometric measurement procedures
- optical validation and measurement-traceability content

When one of those topics is active, explicitly say in the research brief whether this PDF was consulted and what it contributed.

## Research Brief Contract

Return a concise research brief containing:

1. files and folders inspected
2. relevant findings from existing documentation
3. relevant findings from implementation
4. relevant findings from `General`
5. applicable documentation-structure rules from the scaffold skill references
6. preferred-reference findings
7. discrepancies or uncertainties
8. missing references or citations still needed
9. incomplete or nonstandard documentation that may need reconstruction

Use the evidence labels from [references/evidence_labels.md](references/evidence_labels.md).

## Clarification Gates

Read [references/question_rounds.md](references/question_rounds.md) before asking questions.

- Round 1 happens after the initial research brief.
- Round 2 happens after the user answers Round 1.
- The documentation destination inside `docs/source` must always be confirmed before writing.
- If the user already supplied a destination path, still ask them to confirm it before writing.

## Writing Rules

- Keep the writing technical, concise, and grounded in verified current behavior.
- Prefer stable factual phrasing over implementation-centric phrasing. For example, write "The binary header is 24 bytes" rather than "The implementation uses a 24-byte header" when the statement is a current verified fact.
- Minimize exact code-file, function, or class references in the final documentation unless they are necessary for traceability, discrepancy resolution, or the user explicitly asks for them.
- Give visible UUIDs to independently traceable technical content such as specifications, device characteristics, I/O definitions, calculations, diagnostics, tests, validation criteria, states, and transitions.
- Do not give a page title its own UUID when that page already contains UUID-tagged subsections that carry the real traceable content.
- Do not add UUIDs to purely organizational grouping headers when they do not carry standalone technical requirements or verification value.
- Prefer bold field labels for dense technical blocks when that improves readability, such as `**Functionality:**`, `**Output:**`, `**Calculation:**`, `**Expected Outcome:**`, and `**Rationale:**`.
- Include a rationale field when it clarifies why a state, transition boundary, calculation, or validation step exists.
- Do not present planned behavior as implemented behavior.
- If a feature is not implemented, document it as planned work or a TODO.
- If current docs and implementation disagree, surface the discrepancy and ask the user how to resolve it.
- Reuse valid existing documentation where possible.
- Reconstruct incomplete or nonstandard sections into the established Sphinx structure when the user approves.
- Do not generate diagrams in this skill.

## File Operations

Read [references/file_operation_policy.md](references/file_operation_policy.md) before applying changes.

- Do not move, rename, delete, or overwrite anything until the file-operation plan is shown and approved.
- Keep destructive operations blocked unless the user has explicitly approved them.
- Use the `apply` subcommand only after the manifest reflects the approved plan.
