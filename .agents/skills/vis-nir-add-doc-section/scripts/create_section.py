#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from uuid import uuid4

PAGE_FILES = (
    "index.rst",
    "inputs_and_outputs.rst",
    "procedure.rst",
    "diagnostics.rst",
    "testing.rst",
    "calculations.rst",
    "validation.rst",
)
REQUIRED_PAGE_KEYS = (
    "index",
    "inputs_and_outputs",
    "procedure",
    "diagnostics",
    "testing",
    "calculations",
    "validation",
)
DEFAULT_INPUT_ROW = ("[TODO] Input item", "[TODO] Expected values", "[TODO] Structure", "[TODO] Purpose")
DEFAULT_OUTPUT_ROW = ("[TODO] Output item", "[TODO] Expected values", "[TODO] Structure", "[TODO] Purpose")
DEFAULT_DIAGNOSTIC_ROW = (
    "[TODO] Diagnostic item",
    "[TODO] Meaning",
    "[TODO] Expected range or state",
    "[TODO] Failure indication",
    "[TODO] User alert behavior",
    "[TODO] UUID",
)
DEFAULT_TEST_ROW = ("[TODO] test_id", "[TODO] Type", "[TODO] Test name", "[TODO] Summary", "[TODO] UUID")
DEFAULT_VALIDATION_ROW = ("[TODO] validation_id", "[TODO] Validation step", "[TODO] Expected outcome", "[TODO] UUID")


@dataclass(frozen=True)
class StateItem:
    item_id: str
    name: str
    summary: str
    uuid: str


@dataclass(frozen=True)
class TransitionItem:
    item_id: str
    from_state: str
    to_state: str
    condition: str
    failure_target: str
    uuid: str


@dataclass(frozen=True)
class CalculationItem:
    item_id: str
    name: str
    summary: str
    uuid: str


@dataclass(frozen=True)
class DiagnosticItem:
    item_id: str
    name: str
    meaning: str
    expected: str
    failure: str
    alert: str
    uuid: str


@dataclass(frozen=True)
class TestItem:
    item_id: str
    test_type: str
    name: str
    summary: str
    uuid: str


@dataclass(frozen=True)
class ValidationItem:
    item_id: str
    step: str
    expected: str
    uuid: str


def make_uuid() -> str:
    return str(uuid4()).upper()


def normalize_label(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return f"uuid-{normalized}" if not normalized.startswith("uuid-") else normalized


def slug_is_valid(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_-]+", value))


def ensure_docs_source(parent: Path) -> Path:
    for ancestor in (parent, *parent.parents):
        if ancestor.name == "source" and ancestor.parent.name == "docs":
            return ancestor
    raise ValueError("Parent path must be under docs/source.")


def parse_triplet(raw: str, label: str) -> tuple[str, str, str]:
    parts = [part.strip() for part in raw.split("|")]
    if len(parts) != 3 or not all(parts):
        raise ValueError(f"{label} must use the format ID|Name|Summary.")
    return parts[0], parts[1], parts[2]


def parse_transition(raw: str) -> tuple[str, str, str, str, str]:
    parts = [part.strip() for part in raw.split("|")]
    if len(parts) != 5 or not all(parts):
        raise ValueError("transition must use the format ID|StateItem|To|Condition|FailureTarget.")
    return parts[0], parts[1], parts[2], parts[3], parts[4]


def parse_diagnostic(raw: str) -> tuple[str, str, str, str, str, str]:
    parts = [part.strip() for part in raw.split("|")]
    if len(parts) != 6 or not all(parts):
        raise ValueError(
            "diagnostic must use the format ID|Name|Meaning|Expected|Failure|Alert."
        )
    return parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]


def parse_test(raw: str) -> tuple[str, str, str, str]:
    parts = [part.strip() for part in raw.split("|")]
    if len(parts) != 4 or not all(parts):
        raise ValueError("test-item must use the format ID|Type|Name|Summary.")
    return parts[0], parts[1], parts[2], parts[3]


def parse_states(values: Iterable[str]) -> list[StateItem]:
    items: list[StateItem] = []
    for raw in values:
        item_id, name, summary = parse_triplet(raw, "state")
        items.append(StateItem(item_id=item_id, name=name, summary=summary, uuid=make_uuid()))
    return items


def parse_transitions(values: Iterable[str]) -> list[TransitionItem]:
    items: list[TransitionItem] = []
    for raw in values:
        item_id, from_state, to_state, condition, failure_target = parse_transition(raw)
        items.append(
            TransitionItem(
                item_id=item_id,
                from_state=from_state,
                to_state=to_state,
                condition=condition,
                failure_target=failure_target,
                uuid=make_uuid(),
            )
        )
    return items


def parse_calculations(values: Iterable[str]) -> list[CalculationItem]:
    items: list[CalculationItem] = []
    for raw in values:
        item_id, name, summary = parse_triplet(raw, "calculation")
        items.append(CalculationItem(item_id=item_id, name=name, summary=summary, uuid=make_uuid()))
    return items


def parse_diagnostics(values: Iterable[str]) -> list[DiagnosticItem]:
    items: list[DiagnosticItem] = []
    for raw in values:
        item_id, name, meaning, expected, failure, alert = parse_diagnostic(raw)
        items.append(
            DiagnosticItem(
                item_id=item_id,
                name=name,
                meaning=meaning,
                expected=expected,
                failure=failure,
                alert=alert,
                uuid=make_uuid(),
            )
        )
    return items


def parse_tests(values: Iterable[str]) -> list[TestItem]:
    items: list[TestItem] = []
    for raw in values:
        item_id, test_type, name, summary = parse_test(raw)
        items.append(TestItem(item_id=item_id, test_type=test_type, name=name, summary=summary, uuid=make_uuid()))
    return items


def clone_states(items: list[StateItem]) -> list[StateItem]:
    return [StateItem(item_id=item.item_id, name=item.name, summary=item.summary, uuid=make_uuid()) for item in items]


def clone_transitions(items: list[TransitionItem]) -> list[TransitionItem]:
    return [
        TransitionItem(
            item_id=item.item_id,
            from_state=item.from_state,
            to_state=item.to_state,
            condition=item.condition,
            failure_target=item.failure_target,
            uuid=make_uuid(),
        )
        for item in items
    ]


def clone_calculations(items: list[CalculationItem]) -> list[CalculationItem]:
    return [CalculationItem(item_id=item.item_id, name=item.name, summary=item.summary, uuid=make_uuid()) for item in items]


def clone_diagnostics(items: list[DiagnosticItem]) -> list[DiagnosticItem]:
    return [
        DiagnosticItem(
            item_id=item.item_id,
            name=item.name,
            meaning=item.meaning,
            expected=item.expected,
            failure=item.failure,
            alert=item.alert,
            uuid=make_uuid(),
        )
        for item in items
    ]


def clone_tests(items: list[TestItem]) -> list[TestItem]:
    return [
        TestItem(
            item_id=item.item_id,
            test_type=item.test_type,
            name=item.name,
            summary=item.summary,
            uuid=make_uuid(),
        )
        for item in items
    ]


def rst_page_header(title: str) -> str:
    return f"{title}\n{'=' * len(title)}\n\n"


def rst_section_header(title: str, level: str = "-", uuid_value: str | None = None) -> str:
    lines: list[str] = []
    if uuid_value is not None:
        lines.append(f".. _{normalize_label(uuid_value)}:\n")
    lines.append(f"{title}\n{level * len(title)}\n")
    if uuid_value is not None:
        lines.append(f"UUID: :ref:`{uuid_value} <{normalize_label(uuid_value)}>`\n")
    return "\n".join(lines)


def list_table(headers: tuple[str, ...], rows: list[tuple[str, ...]]) -> str:
    lines = [".. list-table::", "   :header-rows: 1", ""]
    header_prefix = "   * - "
    lines.append(header_prefix + headers[0])
    for header in headers[1:]:
        lines.append(f"     - {header}")
    for row in rows:
        lines.append(f"   * - {row[0]}")
        for cell in row[1:]:
            lines.append(f"     - {cell}")
    lines.append("")
    return "\n".join(lines)


def state_anchor(state: StateItem) -> str:
    return normalize_label(state.uuid)


def transition_anchor(item: TransitionItem) -> str:
    return normalize_label(item.uuid)


def calc_anchor(item: CalculationItem) -> str:
    return normalize_label(item.uuid)


def diagnostic_anchor(item: DiagnosticItem) -> str:
    return normalize_label(item.uuid)


def test_anchor(item: TestItem) -> str:
    return normalize_label(item.uuid)


def validation_anchor(item: ValidationItem) -> str:
    return normalize_label(item.uuid)


def build_index_page(title: str, functionality: str, with_calibration: bool) -> str:
    toctree_entries = [
        "inputs_and_outputs",
        "procedure",
        "diagnostics",
        "testing",
        "calculations",
        "validation",
    ]
    if with_calibration:
        toctree_entries.append("calibration/index")
    lines = [rst_page_header(title)]
    lines.append(rst_section_header("Overview", uuid_value=make_uuid()))
    lines.append(f"{functionality}\n")
    lines.append(".. note::\n")
    lines.append("   Insert the user-provided I/O diagram here after the Visio source and image are available.\n")
    lines.append(rst_section_header("Related Pages"))
    lines.append(".. toctree::")
    lines.append("   :maxdepth: 1\n")
    for entry in toctree_entries:
        lines.append(f"   {entry}")
    lines.append("")
    return "\n".join(lines)


def build_io_page(title: str) -> str:
    lines = [rst_page_header(title)]
    lines.append(rst_section_header("Inputs", uuid_value=make_uuid()))
    lines.append(list_table(("Item", "Expected Values", "Structure", "Purpose"), [DEFAULT_INPUT_ROW]))
    lines.append(rst_section_header("Outputs", uuid_value=make_uuid()))
    lines.append(list_table(("Item", "Expected Values", "Structure", "Purpose"), [DEFAULT_OUTPUT_ROW]))
    return "\n".join(lines)


def build_procedure_page(
    title: str,
    states: list[StateItem],
    transitions: list[TransitionItem],
) -> str:
    transition_rows = []
    if transitions:
        for item in transitions:
            transition_rows.append(
                (
                    item.item_id,
                    item.from_state,
                    item.to_state,
                    item.condition,
                    item.failure_target,
                    f":ref:`{item.uuid} <{transition_anchor(item)}>`",
                )
            )
    else:
        transition_rows.append(
            ("[TODO] T0", "[TODO] State item", "[TODO] To", "[TODO] Conditional basis", "[TODO] Failure target", "[TODO] UUID")
        )

    lines = [rst_page_header(title)]
    lines.append(rst_section_header("State Machine", uuid_value=make_uuid()))
    lines.append(".. note::\n")
    lines.append("   Insert the user-provided state-machine image here after the Visio source and image are available.\n")
    lines.append(rst_section_header("Transitions", uuid_value=make_uuid()))
    lines.append(
        list_table(
            ("ID", "State Item", "To", "Conditional Basis", "Failure Target", "UUID"),
            transition_rows,
        )
    )

    lines.append(rst_section_header("States", uuid_value=make_uuid()))
    if states:
        for state in states:
            lines.append(f".. _{state_anchor(state)}:\n")
            state_title = f"State {state.item_id} - {state.name}"
            lines.append(rst_section_header(state_title))
            lines.append(f"UUID: :ref:`{state.uuid} <{state_anchor(state)}>`\n")
            lines.append(f"**Summary:** {state.summary}\n")
            lines.append("**Functionality:** [TODO]\n")
            lines.append("**Output:** [TODO]\n")
            lines.append("**Calculation:** [TODO]\n")
            lines.append("**Rationale:** [TODO]\n")
    else:
        lines.append("[TODO] Add explicit state definitions.\n")

    if transitions:
        for item in transitions:
            lines.append(f".. _{transition_anchor(item)}:\n")
            transition_title = f"Transition {item.item_id}"
            lines.append(rst_section_header(transition_title))
            lines.append(f"UUID: :ref:`{item.uuid} <{transition_anchor(item)}>`\n")
            lines.append(f"**State Item:** ``{item.from_state}``\n")
            lines.append(f"**To State:** ``{item.to_state}``\n")
            lines.append("**Conditional Transitions:**\n")
            lines.append(f"\n* If {item.condition}, advance to ``{item.to_state}``.\n")
            lines.append(f"**Failure Target:** {item.failure_target}\n")
            lines.append("**Rationale:** [TODO]\n")
    else:
        lines.append("[TODO] Add explicit transition definitions.\n")

    return "\n".join(lines)


def build_diagnostics_page(title: str, diagnostics: list[DiagnosticItem]) -> str:
    rows = []
    if diagnostics:
        for item in diagnostics:
            rows.append(
                (
                    item.name,
                    item.meaning,
                    item.expected,
                    item.failure,
                    item.alert,
                    f":ref:`{item.uuid} <{diagnostic_anchor(item)}>`",
                )
            )
    else:
        rows.append(DEFAULT_DIAGNOSTIC_ROW)

    lines = [rst_page_header(title)]
    lines.append(rst_section_header("Diagnostics Table", uuid_value=make_uuid()))
    lines.append(
        list_table(
            ("Item", "Meaning", "Expected Range Or State", "Failure Indication", "User Alert Behavior", "UUID"),
            rows,
        )
    )

    if diagnostics:
        for item in diagnostics:
            lines.append(f".. _{diagnostic_anchor(item)}:\n")
            item_title = f"Diagnostic {item.item_id} - {item.name}"
            lines.append(rst_section_header(item_title))
            lines.append(f"UUID: :ref:`{item.uuid} <{diagnostic_anchor(item)}>`\n")
            lines.append(f"Meaning: {item.meaning}\n")
            lines.append(f"Expected Range Or State: {item.expected}\n")
            lines.append(f"Failure Indication: {item.failure}\n")
            lines.append(f"User Alert Behavior: {item.alert}\n")
    return "\n".join(lines)


def build_testing_page(title: str, tests: list[TestItem]) -> str:
    rows = []
    if tests:
        for item in tests:
            rows.append(
                (
                    item.item_id,
                    item.test_type,
                    item.name,
                    item.summary,
                    f":ref:`{item.uuid} <{test_anchor(item)}>`",
                )
            )
    else:
        rows.append(DEFAULT_TEST_ROW)

    lines = [rst_page_header(title)]
    lines.append(rst_section_header("Testing Matrix", uuid_value=make_uuid()))
    lines.append(list_table(("ID", "Type", "Name", "Summary", "UUID"), rows))

    if tests:
        for item in tests:
            lines.append(f".. _{test_anchor(item)}:\n")
            item_title = f"Test {item.item_id} - {item.name}"
            lines.append(rst_section_header(item_title))
            lines.append(f"UUID: :ref:`{item.uuid} <{test_anchor(item)}>`\n")
            lines.append(f"Type: {item.test_type}\n")
            lines.append(f"Summary: {item.summary}\n")
            lines.append("[TODO] Add setup, execution, and acceptance details.\n")
    return "\n".join(lines)


def build_calculations_page(title: str, calculations: list[CalculationItem]) -> str:
    lines = [rst_page_header(title)]
    if calculations:
        for item in calculations:
            lines.append(f".. _{calc_anchor(item)}:\n")
            calc_title = f"Calculation {item.item_id} - {item.name}"
            lines.append(rst_section_header(calc_title))
            lines.append(f"UUID: :ref:`{item.uuid} <{calc_anchor(item)}>`\n")
            lines.append(f"**Summary:** {item.summary}\n")
            lines.append("**Variables:** [TODO]\n")
            lines.append("**Equation Reasoning:** [TODO]\n")
            lines.append("**Implementation Note:** [TODO]\n")
            lines.append("**Rationale:** [TODO]\n")
    else:
        lines.append("[TODO] Add explicit calculation definitions.\n")
    return "\n".join(lines)


def build_validation_page(title: str, validations: list[ValidationItem]) -> str:
    lines = [rst_page_header(title)]
    lines.append(rst_section_header("Validation Steps", uuid_value=make_uuid()))
    if validations:
        for index, item in enumerate(validations, start=1):
            lines.append(f"**Step {index}:** {item.step}\n")
            lines.append(f"\n   **Expected Outcome:** {item.expected}\n")
            lines.append("")
    else:
        lines.append("**Step 1:** [TODO] Validation step\n")
        lines.append("\n   **Expected Outcome:** [TODO]\n")
        lines.append("")

    lines.append("\n**Rationale:** [TODO]\n")
    return "\n".join(lines)


def page_map(
    title_prefix: str,
    functionality: str,
    with_calibration: bool,
    states: list[StateItem],
    transitions: list[TransitionItem],
    calculations: list[CalculationItem],
    diagnostics: list[DiagnosticItem],
    tests: list[TestItem],
    validations: list[ValidationItem],
) -> dict[str, str]:
    page_titles = {
        "index": title_prefix,
        "inputs_and_outputs": "Inputs and Outputs",
        "procedure": "Procedure",
        "diagnostics": "Diagnostics",
        "testing": "Testing",
        "calculations": "Calculations",
        "validation": "Validation",
    }
    return {
        "index": build_index_page(page_titles["index"], functionality, with_calibration),
        "inputs_and_outputs": build_io_page(page_titles["inputs_and_outputs"]),
        "procedure": build_procedure_page(page_titles["procedure"], states, transitions),
        "diagnostics": build_diagnostics_page(page_titles["diagnostics"], diagnostics),
        "testing": build_testing_page(page_titles["testing"], tests),
        "calculations": build_calculations_page(page_titles["calculations"], calculations),
        "validation": build_validation_page(page_titles["validation"], validations),
    }


def update_parent_index(parent_index: Path, slug: str, dry_run: bool) -> None:
    text = parent_index.read_text(encoding="utf-8")
    entry = f"{slug}/index"
    if re.search(rf"(?m)^\s*{re.escape(entry)}\s*$", text):
        return

    lines = text.splitlines()
    insert_at: int | None = None
    seen_toctree = False
    for index, line in enumerate(lines):
        if line.strip() == ".. toctree::":
            seen_toctree = True
            continue
        if seen_toctree and line.startswith("   ") and line.strip().startswith(":"):
            continue
        if seen_toctree and line.startswith("   ") and line.strip():
            insert_at = index
        if seen_toctree and insert_at is not None and (not line.startswith("   ") or not line.strip()):
            insert_at = index
            break

    if insert_at is None:
        raise ValueError(f"Could not find a writable toctree block in {parent_index}.")

    lines.insert(insert_at, f"   {entry}")
    updated = "\n".join(lines) + "\n"
    if dry_run:
        print(f"[DRY-RUN] Would update {parent_index} with toctree entry {entry}")
        return
    parent_index.write_text(updated, encoding="utf-8")


def write_pages(section_dir: Path, content_map: dict[str, str], dry_run: bool) -> None:
    for key, content in content_map.items():
        path = section_dir / f"{key}.rst"
        if dry_run:
            print(f"[DRY-RUN] Would write {path}")
            continue
        path.write_text(content, encoding="utf-8")


def touch_diagrams(diagram_dir: Path, slug: str, dry_run: bool) -> None:
    files = (
        diagram_dir / f"{slug}-io.vsdx",
        diagram_dir / f"{slug}-state-machine.vsdx",
    )
    for file_path in files:
        if dry_run:
            print(f"[DRY-RUN] Would create blank {file_path}")
            continue
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch(exist_ok=False)


def build_validation_items(states: list[StateItem], transitions: list[TransitionItem], tests: list[TestItem]) -> list[ValidationItem]:
    items: list[ValidationItem] = []
    for state in states:
        items.append(
            ValidationItem(
                item_id=f"VAL-{state.item_id}",
                step=f"Confirm state ``{state.item_id}`` behaves as documented.",
                    expected=f"State ``{state.item_id}`` matches the documented functionality, outputs, and calculations.",
                uuid=make_uuid(),
            )
        )
    for transition in transitions:
        items.append(
            ValidationItem(
                item_id=f"VAL-{transition.item_id}",
                step=f"Trigger transition ``{transition.item_id}`` under the documented conditional basis.",
                expected=f"Flow moves from ``{transition.from_state}`` to ``{transition.to_state}`` as documented.",
                uuid=make_uuid(),
            )
        )
    if not items and tests:
        for test in tests:
            items.append(
                ValidationItem(
                    item_id=f"VAL-{test.item_id}",
                    step=f"Run test ``{test.item_id}`` for validation evidence.",
                    expected=f"Test ``{test.item_id}`` completes with the documented result.",
                    uuid=make_uuid(),
                )
            )
    return items


def ensure_empty_target(section_dir: Path) -> None:
    if section_dir.exists():
        raise FileExistsError(f"Section directory already exists: {section_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold a VIS-NIR documentation section.")
    parser.add_argument("--parent", required=True, help="Parent docs path that already contains index.rst.")
    parser.add_argument("--title", required=True, help="Section title.")
    parser.add_argument("--slug", required=True, help="Section slug.")
    parser.add_argument("--functionality", required=True, help="Exact user-provided functionality summary.")
    parser.add_argument("--with-calibration", action="store_true", help="Create a calibration mirror.")
    parser.add_argument("--state", action="append", default=[], help="State in ID|Name|Summary format.")
    parser.add_argument(
        "--transition",
        action="append",
        default=[],
        help="Transition in ID|StateItem|To|Condition|FailureTarget format.",
    )
    parser.add_argument(
        "--calculation",
        action="append",
        default=[],
        help="Calculation in ID|Name|Summary format.",
    )
    parser.add_argument(
        "--diagnostic",
        action="append",
        default=[],
        help="Diagnostic in ID|Name|Meaning|Expected|Failure|Alert format.",
    )
    parser.add_argument(
        "--test-item",
        action="append",
        default=[],
        help="Test item in ID|Type|Name|Summary format.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without writing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not slug_is_valid(args.slug):
        print("Slug must match [A-Za-z0-9_-]+.", file=sys.stderr)
        return 1

    parent = Path(args.parent).resolve()
    parent_index = parent / "index.rst"
    if not parent_index.exists():
        print(f"Parent index not found: {parent_index}", file=sys.stderr)
        return 1

    docs_source = ensure_docs_source(parent)
    repo_root = docs_source.parent.parent
    section_dir = parent / args.slug
    diagram_dir = docs_source / "_static" / "diagrams" / args.slug

    try:
        states = parse_states(args.state)
        transitions = parse_transitions(args.transition)
        calculations = parse_calculations(args.calculation)
        diagnostics = parse_diagnostics(args.diagnostic)
        tests = parse_tests(args.test_item)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    validations = build_validation_items(states, transitions, tests)
    calibration_states = clone_states(states)
    calibration_transitions = clone_transitions(transitions)
    calibration_calculations = clone_calculations(calculations)
    calibration_diagnostics = clone_diagnostics(diagnostics)
    calibration_tests = clone_tests(tests)
    calibration_validations = build_validation_items(
        calibration_states,
        calibration_transitions,
        calibration_tests,
    )

    try:
        ensure_empty_target(section_dir)
    except FileExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    content = page_map(
        title_prefix=args.title,
        functionality=args.functionality,
        with_calibration=args.with_calibration,
        states=states,
        transitions=transitions,
        calculations=calculations,
        diagnostics=diagnostics,
        tests=tests,
        validations=validations,
    )
    calibration_content = page_map(
        title_prefix=f"{args.title} Calibration",
        functionality=f"Calibration mirror for: {args.functionality}",
        with_calibration=False,
        states=calibration_states,
        transitions=calibration_transitions,
        calculations=calibration_calculations,
        diagnostics=calibration_diagnostics,
        tests=calibration_tests,
        validations=calibration_validations,
    )

    if args.dry_run:
        print(f"[DRY-RUN] Repo root: {repo_root}")
        print(f"[DRY-RUN] Section directory: {section_dir}")

    if not args.dry_run:
        section_dir.mkdir(parents=True, exist_ok=False)
    write_pages(section_dir, content, args.dry_run)

    if args.with_calibration:
        calibration_dir = section_dir / "calibration"
        if not args.dry_run:
            calibration_dir.mkdir(parents=True, exist_ok=False)
        write_pages(calibration_dir, calibration_content, args.dry_run)

    touch_diagrams(diagram_dir, args.slug, args.dry_run)
    update_parent_index(parent_index, args.slug, args.dry_run)

    if not args.dry_run:
        print(f"[OK] Created section scaffold at {section_dir}")
        print(f"[OK] Created blank Visio placeholders in {diagram_dir}")
        print(f"[OK] Updated parent toctree in {parent_index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
