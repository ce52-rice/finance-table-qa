"""Deterministic checks for tool calls and the five scoped answer-and-evidence tasks."""

import re
from decimal import Decimal

from contract import Tool

from .references import EXPECTED


def verdict(valid, message):
    return {"valid": valid, "score": float(valid), "message": message, "details": {}}


def verify_input(tool, value):
    kind = Tool(tool)
    if kind in (Tool.DESCRIBE, Tool.READ) and not re.fullmatch(r"(alphabet|disney|gm|gs|walmart)-[0-9]+", value.table):
        return verdict(False, "Use a table ID returned by list_tables.")
    if kind == Tool.READ:
        for indices in (value.rows, value.columns):
            if len(indices) != len(set(indices)) or any(i < 0 for i in indices):
                return verdict(False, "Indices must be distinct and nonnegative.")
    return verdict(True, "Input accepted.")


def verify_output(tool, input_value, output_value, workspace):
    kind = Tool(tool)
    if kind == Tool.LIST:
        tables = output_value.tables
        ok = bool(tables) and all(t.source.startswith(input_value.company.value + "/") for t in tables)
    elif kind == Tool.DESCRIBE:
        ok = output_value.table == input_value.table and bool(output_value.columns) and bool(output_value.row_labels)
    elif kind == Tool.READ:
        cells = output_value.cells
        ok = (
            output_value.table == input_value.table
            and bool(cells)
            and len({cell.cell_id for cell in cells}) == len(cells)
            and all(cell.cell_id.startswith(input_value.table + "/") for cell in cells)
        )
    else:
        ok = Decimal(output_value.value).is_finite()
    return verdict(ok, "Tool output checked.")


def verify_task(task, arguments, output, reference, workspace):
    expected, alternatives = EXPECTED[task]
    raw = output.answer.strip().lower()
    if expected == "Yes":
        correct = raw == "yes"
    else:
        if len(raw) > 90 or not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)\s*%?", raw):
            return verdict(False, "Submit one finite decimal or explicit percentage.")
        prediction = Decimal(raw.rstrip("%").strip())
        if raw.endswith("%"):
            prediction /= 100
        target = Decimal(expected)
        # Half of the last published decimal place, including endpoints.
        tolerance = Decimal(1).scaleb(target.as_tuple().exponent) / 2
        correct = abs(prediction - target) <= tolerance
    if not correct:
        return verdict(False, "Answer differs from the reference.")
    evidence = set(output.evidence)
    supported = len(evidence) == len(output.evidence) and any(evidence == set(group) for group in alternatives)
    return verdict(supported, "Verified answer and operands." if supported else "Check the supporting cell IDs.")
