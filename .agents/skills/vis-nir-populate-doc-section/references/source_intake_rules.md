# Source Intake Rules

## Roots

- Repo docs root: `C:\Users\ralel\OneDrive\GitHub\VIS-NIR_Spec_Spring26\docs\source`
- Repo code roots:
  - `C:\Users\ralel\OneDrive\GitHub\VIS-NIR_Spec_Spring26\PythonGUI`
  - `C:\Users\ralel\OneDrive\GitHub\VIS-NIR_Spec_Spring26\CCD-Driver-Code`
- Historical host root: `C:\Users\ralel\OneDrive - Iowa State University\VIS-NIR Spectrum - Documents\General`
- Historical PDF MCP root: `/workspace`

## Base Weighting

Treat all files and folders under `General` as first-class evidence with equal base discovery weight.

Named preferred references add mandatory-consult behavior for matching topics, but they do not demote other historical files.

## Routing By Source Type

- `.rst`, `.py`, `.md`, `.txt`, `.c`, `.h`: read from host paths
- `.docx`: read from host path by OOXML extraction
- `.pptx`: read from host path by OOXML extraction
- `.pdf`: read through the PDF MCP using `/workspace/...`
- `.vsdx`: read through the Visio MCP using host Windows paths

## Normalized Source Record

The helper script emits normalized source records with:

- `host_path`
- `pdf_mcp_path` when applicable
- `source_type`
- `topic_tags`
- `preferred_reference`
- `evidence_status`

Use those records to decide which live tool calls are still required.
