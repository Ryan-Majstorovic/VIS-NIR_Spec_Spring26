from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[4]
DOCS_SOURCE_ROOT = REPO_ROOT / "docs" / "source"
STRUCTURE_RULES_ROOT = REPO_ROOT / ".agents" / "skills" / "vis-nir-add-doc-section" / "references"
PYTHONGUI_ROOT = REPO_ROOT / "PythonGUI"
CCD_DRIVER_ROOT = REPO_ROOT / "CCD-Driver-Code"
HOST_GENERAL_ROOT = Path(
    r"C:\Users\ralel\OneDrive - Iowa State University\VIS-NIR Spectrum - Documents\General"
)
PDF_MCP_ROOT = PurePosixPath("/workspace")

TEXT_SOURCE_EXTENSIONS = {".rst", ".py", ".md", ".txt", ".c", ".h", ".cpp", ".hpp"}
HISTORICAL_EXTENSIONS = {".docx", ".pptx", ".pdf", ".vsdx"}
EXCLUDED_DIR_NAMES = {
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "site-packages",
    "vis_nir_spec_gui.egg-info",
}
DOCX_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
PPTX_NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
TOPIC_KEYWORDS = {
    "calibration": {"calibration", "calibrate", "dark", "bias", "gain", "reference"},
    "characterization": {"characterization", "characterize", "fwhm", "resolution", "response"},
    "spectroradiometer": {"spectroradiometer", "radiometric", "radiance", "irradiance"},
    "optics": {"optics", "optical", "wavelength", "grating", "slit", "detector"},
    "validation": {"validation", "verify", "verification", "test", "acceptance"},
    "host_pc": {"host", "desktop", "gui", "python", "kivy", "export"},
    "embedded": {"embedded", "firmware", "stm32", "timer", "adc", "dma", "usb"},
    "pipeline": {"pipeline", "frame", "correction", "normalize", "normalization"},
    "traceability": {"traceability", "requirement", "metric", "uuid"},
}
PREFERRED_REFERENCES = [
    {
        "id": "spectroradiometer_guide",
        "host_path": HOST_GENERAL_ROOT
        / "Reference PDFs"
        / "Calibration Characterization andUse of Spectroradiometers.pdf",
        "pdf_mcp_path": "/workspace/Reference PDFs/Calibration Characterization andUse of Spectroradiometers.pdf",
        "required_tags": {
            "calibration",
            "characterization",
            "spectroradiometer",
            "optics",
            "validation",
        },
        "usage_note": (
            "Consult extensively for calibration, characterization, radiometric measurement "
            "procedures, and optical validation topics."
        ),
    }
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage VIS-NIR research-driven documentation updates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Build a source inventory and research brief scaffold.")
    inspect_parser.add_argument("--topic", required=True, help="Requested documentation topic.")
    inspect_parser.add_argument("--candidate-path", help="Expected docs/source target path.")
    inspect_parser.add_argument("--subsystem", help="Optional subsystem hint.")
    inspect_parser.add_argument("--max-sources-per-group", type=int, default=6)
    inspect_parser.add_argument("--max-preview-lines", type=int, default=8)

    draft_parser = subparsers.add_parser("draft", help="Build a draft manifest after both question rounds.")
    draft_parser.add_argument("--confirmed-path", required=True, help="Confirmed docs/source target path.")
    draft_parser.add_argument("--topic", required=True, help="Requested documentation topic.")
    draft_parser.add_argument("--round1", required=True, help="Round 1 answers as inline JSON or JSON file path.")
    draft_parser.add_argument("--round2", required=True, help="Round 2 answers as inline JSON or JSON file path.")

    apply_parser = subparsers.add_parser("apply", help="Apply an approved draft manifest.")
    apply_parser.add_argument("--confirmed-path", required=True, help="Confirmed docs/source target path.")
    apply_parser.add_argument("--draft-manifest", required=True, help="Path to a JSON draft manifest.")
    apply_parser.add_argument(
        "--approve-destructive",
        required=True,
        choices=("true", "false"),
        help="Whether deletes and moves were explicitly approved.",
    )

    args = parser.parse_args()
    if args.command == "inspect":
        result = run_inspect(args)
    elif args.command == "draft":
        result = run_draft(args)
    else:
        result = run_apply(args)

    print(json.dumps(result, indent=2))
    return 0


def run_inspect(args: argparse.Namespace) -> dict:
    topic_tokens = make_topic_tokens(args.topic)
    candidate_path = resolve_repo_path(args.candidate_path) if args.candidate_path else None

    docs_records = collect_text_records(
        base_root=DOCS_SOURCE_ROOT,
        extensions={".rst"},
        topic_tokens=topic_tokens,
        max_preview_lines=args.max_preview_lines,
        candidate_path=candidate_path,
        evidence_status="documented",
    )
    code_records = collect_code_records(topic_tokens, args.max_preview_lines)
    historical_records = collect_historical_records(topic_tokens, args.max_preview_lines)

    selected_docs = select_top_records(docs_records, args.max_sources_per_group)
    selected_code = select_top_records(code_records, args.max_sources_per_group)
    selected_historical = select_top_records(historical_records, args.max_sources_per_group)

    preferred_records = []
    for record in selected_historical:
        if record["preferred_reference"]:
            preferred_records.append(record)

    for record in required_preferred_records(topic_tokens):
        if not any(item["host_path"] == record["host_path"] for item in selected_historical):
            selected_historical.append(record)
        if not any(item["host_path"] == record["host_path"] for item in preferred_records):
            preferred_records.append(record)

    pending_pdf = [record for record in selected_historical if record["source_type"] == "pdf"]
    pending_vsdx = [record for record in selected_historical if record["source_type"] == "vsdx"]

    return {
        "topic": args.topic,
        "candidate_path": str(candidate_path) if candidate_path else None,
        "subsystem": args.subsystem,
        "inspected_sources": selected_docs + selected_code + selected_historical,
        "pending_tool_routes": {
            "pdf": [
                {
                    "tool": "pdf_reader",
                    "mcp_path": record["pdf_mcp_path"],
                    "call_sequence": ["read_pdf", "search_pdf", "pdf_evidence"],
                }
                for record in pending_pdf
            ],
            "vsdx": [
                {
                    "tool": "visio_server",
                    "host_path": record["host_path"],
                    "call_sequence": ["list_shapes"],
                }
                for record in pending_vsdx
            ],
        },
        "research_brief": {
            "files_and_folders_inspected": summarize_inspected_roots(candidate_path),
            "documentation_findings": build_findings(selected_docs, "documentation"),
            "implementation_findings": build_findings(selected_code, "implementation"),
            "general_findings": build_findings(selected_historical, "historical"),
            "preferred_reference_findings": build_preferred_findings(preferred_records),
            "applicable_structure_rules": [
                str(STRUCTURE_RULES_ROOT / "file_layout_rules.md"),
                str(STRUCTURE_RULES_ROOT / "section_contract.md"),
                str(STRUCTURE_RULES_ROOT / "uuid_and_anchor_rules.md"),
            ],
            "discrepancies_or_uncertainties": build_uncertainties(candidate_path, pending_pdf, pending_vsdx),
            "missing_references": build_missing_references(topic_tokens, preferred_records),
            "incomplete_documentation": detect_incomplete_docs(candidate_path),
        },
    }


def run_draft(args: argparse.Namespace) -> dict:
    confirmed_path = resolve_repo_path(args.confirmed_path)
    ensure_under_docs_source(confirmed_path)
    round1 = parse_json_argument(args.round1)
    round2 = parse_json_argument(args.round2)

    if confirmed_path.is_file():
        existing_rst_files = [confirmed_path]
    elif confirmed_path.is_dir():
        existing_rst_files = sorted(confirmed_path.rglob("*.rst"))
    else:
        existing_rst_files = []

    target_exists = confirmed_path.exists()
    requires_scaffold = not target_exists
    file_operation_plan = {
        "files_to_create": [] if target_exists else [str(confirmed_path)],
        "files_to_modify": [str(path) for path in existing_rst_files],
        "files_to_move_or_rename": [],
        "files_to_delete": [],
        "rationale": (
            "Target section already exists and can be revised in place."
            if target_exists
            else "Target section does not exist yet and should be scaffolded before content population."
        ),
        "risk_level": "low" if target_exists else "medium",
        "preservation_strategy": "Edit existing files in place and preserve valid documentation unless the user approves restructuring.",
        "rollback_recommendation": "Keep the draft manifest and review diffs before any destructive change.",
    }

    return {
        "topic": args.topic,
        "confirmed_path": str(confirmed_path),
        "location_confirmed": True,
        "requires_scaffold": requires_scaffold,
        "round1": round1,
        "round2": round2,
        "proposed_structure": {
            "target_exists": target_exists,
            "existing_rst_files": [str(path) for path in existing_rst_files],
            "primary_page": str(choose_primary_page(confirmed_path, existing_rst_files)),
        },
        "file_operation_plan": file_operation_plan,
        "writes": [],
        "moves": [],
        "deletes": [],
        "notes": [
            "Populate writes only after the research brief, both question rounds, and destination confirmation are complete.",
            "If requires_scaffold is true, use vis-nir-add-doc-section before applying this manifest.",
        ],
    }


def run_apply(args: argparse.Namespace) -> dict:
    confirmed_path = resolve_repo_path(args.confirmed_path)
    ensure_under_docs_source(confirmed_path)
    approve_destructive = args.approve_destructive == "true"
    manifest_path = resolve_repo_path(args.draft_manifest)
    ensure_under_repo(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    manifest_confirmed_path = resolve_repo_path(manifest["confirmed_path"])
    if manifest_confirmed_path != confirmed_path:
        raise ValueError("Draft manifest confirmed_path does not match the apply command.")

    if manifest.get("requires_scaffold"):
        raise ValueError("Draft manifest still requires scaffolding and cannot be applied.")

    moves = manifest.get("moves", [])
    deletes = manifest.get("deletes", [])
    if (moves or deletes) and not approve_destructive:
        raise ValueError("Destructive operations are present but --approve-destructive is false.")

    writes_applied = []
    for write in manifest.get("writes", []):
        target_path = resolve_repo_path(write["path"])
        ensure_under_repo(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(write["content"], encoding="utf-8")
        writes_applied.append(str(target_path))

    moves_applied = []
    for move in moves:
        source_path = resolve_repo_path(move["from"])
        destination_path = resolve_repo_path(move["to"])
        ensure_under_repo(source_path)
        ensure_under_repo(destination_path)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), str(destination_path))
        moves_applied.append({"from": str(source_path), "to": str(destination_path)})

    deletes_applied = []
    for delete_path_raw in deletes:
        delete_path = resolve_repo_path(delete_path_raw)
        ensure_under_repo(delete_path)
        if delete_path.is_dir():
            shutil.rmtree(delete_path)
        elif delete_path.exists():
            delete_path.unlink()
        deletes_applied.append(str(delete_path))

    return {
        "confirmed_path": str(confirmed_path),
        "writes_applied": writes_applied,
        "moves_applied": moves_applied,
        "deletes_applied": deletes_applied,
    }


def collect_text_records(
    base_root: Path,
    extensions: set[str],
    topic_tokens: set[str],
    max_preview_lines: int,
    candidate_path: Path | None,
    evidence_status: str,
) -> list[dict]:
    records = []
    if not base_root.exists():
        return records

    for path in sorted(base_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue
        if has_excluded_part(path):
            continue
        preview_lines = preview_plain_text(path, max_preview_lines)
        topic_tags = classify_topic_tags(path, preview_lines)
        score = score_source(path, preview_lines, topic_tokens)
        if candidate_path and path.is_relative_to(candidate_path):
            score += 8
        if score <= 0 and not (candidate_path and path.is_relative_to(candidate_path)):
            continue
        records.append(
            build_record(
                path=path,
                source_type=path.suffix.lower().lstrip("."),
                preview_lines=preview_lines,
                topic_tags=topic_tags,
                score=score,
                evidence_status=evidence_status,
            )
        )
    return records


def collect_code_records(topic_tokens: set[str], max_preview_lines: int) -> list[dict]:
    records = []
    for root in (PYTHONGUI_ROOT, CCD_DRIVER_ROOT):
        records.extend(
            collect_text_records(
                base_root=root,
                extensions=TEXT_SOURCE_EXTENSIONS,
                topic_tokens=topic_tokens,
                max_preview_lines=max_preview_lines,
                candidate_path=None,
                evidence_status="implemented",
            )
        )
    return records


def collect_historical_records(topic_tokens: set[str], max_preview_lines: int) -> list[dict]:
    records = []
    if not HOST_GENERAL_ROOT.exists():
        return records

    preferred_lookup = {item["host_path"]: item for item in PREFERRED_REFERENCES}
    for path in sorted(HOST_GENERAL_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in HISTORICAL_EXTENSIONS:
            continue

        preview_lines = []
        if path.suffix.lower() == ".docx":
            preview_lines = extract_docx_preview(path, max_preview_lines)
        elif path.suffix.lower() == ".pptx":
            preview_lines = extract_pptx_preview(path, max_preview_lines)

        topic_tags = classify_topic_tags(path, preview_lines)
        score = score_source(path, preview_lines, topic_tokens)
        preferred = preferred_lookup.get(path)
        if preferred and preferred_applies(preferred, topic_tokens, topic_tags):
            score = max(score, 12)

        if score <= 0 and not preferred:
            continue

        records.append(
            build_record(
                path=path,
                source_type=path.suffix.lower().lstrip("."),
                preview_lines=preview_lines,
                topic_tags=topic_tags,
                score=score,
                evidence_status="documented",
                pdf_mcp_path=host_to_pdf_mcp_path(path) if path.suffix.lower() == ".pdf" else None,
                preferred_reference=bool(preferred),
            )
        )
    return records


def build_record(
    path: Path,
    source_type: str,
    preview_lines: list[str],
    topic_tags: list[str],
    score: int,
    evidence_status: str,
    pdf_mcp_path: str | None = None,
    preferred_reference: bool = False,
) -> dict:
    return {
        "host_path": str(path),
        "pdf_mcp_path": pdf_mcp_path,
        "source_type": source_type,
        "topic_tags": topic_tags,
        "preferred_reference": preferred_reference,
        "evidence_status": evidence_status,
        "score": score,
        "preview": preview_lines,
    }


def required_preferred_records(topic_tokens: set[str]) -> list[dict]:
    records = []
    for preferred in PREFERRED_REFERENCES:
        if not topic_tokens.intersection(preferred["required_tags"]) and not topic_tokens.intersection(
            {"calibration", "characterization", "spectroradiometer", "radiometric", "validation", "optical"}
        ):
            continue
        records.append(
            {
                "host_path": str(preferred["host_path"]),
                "pdf_mcp_path": preferred["pdf_mcp_path"],
                "source_type": "pdf",
                "topic_tags": sorted(preferred["required_tags"]),
                "preferred_reference": True,
                "evidence_status": "documented",
                "score": 12,
                "preview": [],
            }
        )
    return records


def preferred_applies(preferred: dict, topic_tokens: set[str], topic_tags: list[str]) -> bool:
    if topic_tokens.intersection(preferred["required_tags"]):
        return True
    return bool(set(topic_tags).intersection(preferred["required_tags"]))


def build_findings(records: list[dict], label: str) -> list[str]:
    findings = []
    for record in records:
        preview = " ".join(record["preview"][:2]).strip()
        if preview:
            findings.append(f"{label.title()} source {record['host_path']}: {preview}")
        else:
            findings.append(f"{label.title()} source {record['host_path']}: requires live tool inspection.")
    return findings


def build_preferred_findings(records: list[dict]) -> list[str]:
    findings = []
    for record in records:
        status = "pending tool inspection" if record["source_type"] == "pdf" else "host preview available"
        findings.append(f"Preferred reference {record['host_path']}: {status}.")
    return findings


def build_uncertainties(candidate_path: Path | None, pending_pdf: list[dict], pending_vsdx: list[dict]) -> list[str]:
    uncertainties = []
    if candidate_path and not candidate_path.exists():
        uncertainties.append("Target section path does not exist yet and likely requires scaffolding before content population.")
    if pending_pdf:
        uncertainties.append("PDF findings still require live PDF MCP reads before citation-critical drafting.")
    if pending_vsdx:
        uncertainties.append("VSDX findings still require live Visio MCP inspection before diagram-derived claims are written.")
    return uncertainties


def build_missing_references(topic_tokens: set[str], preferred_records: list[dict]) -> list[str]:
    missing = []
    if topic_tokens.intersection({"calibration", "characterization", "spectroradiometer", "radiometric"}):
        if not preferred_records:
            missing.append("Preferred spectroradiometer calibration PDF has not been queued yet.")
    return missing


def detect_incomplete_docs(candidate_path: Path | None) -> list[str]:
    if not candidate_path or not candidate_path.exists():
        return []

    paths = [candidate_path] if candidate_path.is_file() else sorted(candidate_path.rglob("*.rst"))
    incomplete = []
    for path in paths:
        lines = [line.strip() for line in preview_plain_text(path, 40) if line.strip()]
        text = "\n".join(lines).lower()
        if len(lines) < 6 or "todo" in text or "[todo" in text:
            incomplete.append(str(path))
    return incomplete


def summarize_inspected_roots(candidate_path: Path | None) -> list[str]:
    roots = [str(DOCS_SOURCE_ROOT), str(PYTHONGUI_ROOT), str(CCD_DRIVER_ROOT), str(HOST_GENERAL_ROOT)]
    if candidate_path:
        roots.insert(1, str(candidate_path))
    return roots


def choose_primary_page(confirmed_path: Path, existing_rst_files: list[Path]) -> Path:
    if confirmed_path.is_file():
        return confirmed_path
    for path in existing_rst_files:
        if path.name.lower() == "index.rst":
            return path
    return confirmed_path / "index.rst"


def select_top_records(records: list[dict], limit: int) -> list[dict]:
    return sorted(records, key=lambda item: (-item["score"], item["host_path"]))[:limit]


def parse_json_argument(value: str) -> dict:
    candidate = Path(value)
    if candidate.exists():
        return json.loads(candidate.read_text(encoding="utf-8"))
    return json.loads(value)


def resolve_repo_path(raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate.resolve()
    return (REPO_ROOT / candidate).resolve()


def ensure_under_repo(path: Path) -> None:
    if not path.resolve().is_relative_to(REPO_ROOT):
        raise ValueError(f"Path is outside the repo root: {path}")


def ensure_under_docs_source(path: Path) -> None:
    if not path.resolve().is_relative_to(DOCS_SOURCE_ROOT):
        raise ValueError(f"Path is outside docs/source: {path}")


def make_topic_tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) >= 3}


def has_excluded_part(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDED_DIR_NAMES:
            return True
    return False


def classify_topic_tags(path: Path, preview_lines: list[str]) -> list[str]:
    haystack = f"{path.as_posix().lower()} {' '.join(preview_lines).lower()}"
    tags = []
    for tag, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in haystack:
                tags.append(tag)
                break
    return sorted(tags)


def score_source(path: Path, preview_lines: list[str], topic_tokens: set[str]) -> int:
    haystack = f"{path.as_posix().lower()} {' '.join(preview_lines).lower()}"
    score = 0
    for token in topic_tokens:
        if token in haystack:
            score += 2
        if token in path.name.lower():
            score += 2
    return score


def host_to_pdf_mcp_path(path: Path) -> str:
    relative = path.relative_to(HOST_GENERAL_ROOT)
    return str(PDF_MCP_ROOT.joinpath(*relative.parts))


def preview_plain_text(path: Path, max_preview_lines: int) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue
        lines.append(line)
        if len(lines) >= max_preview_lines:
            break
    return lines


def extract_docx_preview(path: Path, max_preview_lines: int) -> list[str]:
    if not zipfile.is_zipfile(path):
        return []

    try:
        with zipfile.ZipFile(path) as archive:
            root = ET.fromstring(archive.read("word/document.xml"))
    except (ET.ParseError, KeyError, OSError, zipfile.BadZipFile):
        return []

    lines = []
    for paragraph in root.findall(".//w:p", DOCX_NS):
        parts = []
        for text_node in paragraph.findall(".//w:t", DOCX_NS):
            if text_node.text:
                parts.append(text_node.text)
        line = re.sub(r"\s+", " ", "".join(parts)).strip()
        if not line:
            continue
        lines.append(line)
        if len(lines) >= max_preview_lines:
            break
    return lines


def extract_pptx_preview(path: Path, max_preview_lines: int) -> list[str]:
    if not zipfile.is_zipfile(path):
        return []

    try:
        with zipfile.ZipFile(path) as archive:
            slide_names = []
            for name in archive.namelist():
                if name.startswith("ppt/slides/slide") and name.endswith(".xml"):
                    slide_names.append(name)
            slide_names.sort(key=slide_sort_key)

            lines = []
            for slide_name in slide_names:
                root = ET.fromstring(archive.read(slide_name))
                for text_node in root.findall(".//a:t", PPTX_NS):
                    if not text_node.text:
                        continue
                    line = re.sub(r"\s+", " ", text_node.text).strip()
                    if not line:
                        continue
                    lines.append(line)
                    if len(lines) >= max_preview_lines:
                        return lines
            return lines
    except (ET.ParseError, KeyError, OSError, zipfile.BadZipFile):
        return []


def slide_sort_key(name: str) -> tuple[int, str]:
    match = re.search(r"slide(\d+)\.xml$", name)
    if not match:
        return (sys.maxsize, name)
    return (int(match.group(1)), name)


if __name__ == "__main__":
    raise SystemExit(main())
