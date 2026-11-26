"""Read-only financial table tools on the pinned SnorkelFinance snapshot."""

import json
import operator
import re
from decimal import Decimal
from functools import cache
from pathlib import Path

from contract import CalcOutput, CatalogOutput, Cell, Operation, ReadOutput, TableOutput, TableSummary


@cache
def tables():
    return json.loads((Path(__file__).parent / "data" / "tables.json").read_text(encoding="utf-8"))


def list_tables(request):
    return CatalogOutput(
        [
            TableSummary(key, t["source"], t["description"])
            for key, t in tables().items()
            if t["company"] == request.company.value
        ]
    )


def describe_table(request):
    table = tables()[request.table]
    return TableOutput(request.table, table["description"], [row[0] for row in table["rows"]], table["columns"])


def selected(indices, size):
    if len(set(indices)) != len(indices) or any(i < 0 or i >= size for i in indices):
        raise ValueError("Select distinct indices within the range shown by describe_table.")
    return indices or range(size)


def read_cells(request):
    table = tables()[request.table]
    rows = selected(request.rows, len(table["rows"]))
    columns = selected(request.columns, len(table["columns"]))
    cells = []
    for r in rows:
        row = table["rows"][r]
        for c in columns:
            cells.append(Cell(f"{request.table}/{r}/{c}", row[0], table["columns"][c], row[c]))
    return ReadOutput(request.table, table["source"], table["description"], cells)


def calculate(request):
    op = {
        Operation.ADD: operator.add,
        Operation.SUBTRACT: operator.sub,
        Operation.MULTIPLY: operator.mul,
        Operation.DIVIDE: operator.truediv,
    }[request.operation]
    for value in (request.left, request.right):
        if not re.fullmatch(r"[+-]?(?:[0-9]{1,40}(?:\.[0-9]{1,40})?|\.[0-9]{1,40})", value):
            raise ValueError("Use a signed plain decimal with at most 40 integer and 40 fractional digits.")
    left, right = Decimal(request.left), Decimal(request.right)
    if request.operation == Operation.DIVIDE and right == 0:
        raise ValueError("Division by zero.")
    return CalcOutput(format(op(left, right), "f"))
