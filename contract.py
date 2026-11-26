"""Shared task and tool schemas for Finance Table QA."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Task(Enum):
    LOOKUP = "lookup-rate"
    INCOME = "income-ratio"
    CHANGE = "borrowing-change"
    SHARES = "reconcile-shares"
    HEDGE = "hedge-ratio"


class Tool(Enum):
    LIST = "list_tables"
    DESCRIBE = "describe_table"
    READ = "read_cells"
    CALCULATE = "calculate"


class Operation(Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


class Company(Enum):
    ALPHABET = "alphabet"
    DISNEY = "disney"
    GM = "gm"
    GOLDMAN_SACHS = "gs"
    WALMART = "walmart"


@dataclass
class QuestionInput(Output):
    """Each named task specifies its company, question and period."""


@dataclass
class AnswerOutput(Output):
    answer: Annotated[str, "One decimal ratio or rate, explicit percent, or yes/no as requested"]
    evidence: Annotated[list[str], "Exactly the cell IDs underlying the answer, one per operand"]


@dataclass
class CatalogInput(Output):
    company: Company


@dataclass
class TableSummary(Output):
    table: str
    source: str
    description: str


@dataclass
class CatalogOutput(Output):
    tables: list[TableSummary]


@dataclass
class TableInput(Output):
    table: Annotated[str, "Short table ID from list_tables"]


@dataclass
class TableOutput(Output):
    table: str
    description: str
    row_labels: Annotated[list[str], "Zero-based positions correspond to row numbers"]
    columns: Annotated[list[str], "Zero-based positions correspond to column numbers"]


@dataclass
class ReadInput(Output):
    table: Annotated[str, "Short table ID from list_tables"]
    rows: Annotated[list[int], "Zero-based row indices. Empty list selects every row."]
    columns: Annotated[list[int], "Zero-based column indices. Empty list selects every column."]


@dataclass
class Cell(Output):
    cell_id: Annotated[str, "Stable table/row/column citation within this dataset version"]
    row_label: str
    column_label: str
    value: Annotated[str, "Verbatim filing cell, including any sign or percentage"]


@dataclass
class ReadOutput(Output):
    table: str
    source: str
    description: str
    cells: list[Cell]


@dataclass
class CalcInput(Output):
    left: Annotated[str, "Signed plain decimal, without commas, currency or percent symbols"]
    operation: Operation
    right: Annotated[str, "Signed plain decimal"]


@dataclass
class CalcOutput(Output):
    value: str


TOOLS = {
    Tool.LIST: (CatalogInput, CatalogOutput),
    Tool.DESCRIBE: (TableInput, TableOutput),
    Tool.READ: (ReadInput, ReadOutput),
    Tool.CALCULATE: (CalcInput, CalcOutput),
}
TASKS = {
    Task.LOOKUP: (QuestionInput, AnswerOutput),
    Task.INCOME: (QuestionInput, AnswerOutput),
    Task.CHANGE: (QuestionInput, AnswerOutput),
    Task.SHARES: (QuestionInput, AnswerOutput),
    Task.HEDGE: (QuestionInput, AnswerOutput),
}
