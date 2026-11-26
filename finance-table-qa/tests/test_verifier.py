import pytest

from contract import AnswerOutput, CalcInput, CatalogInput, Company, Operation, QuestionInput, ReadInput, TableInput
from plugin.finance import calculate, describe_table, list_tables, read_cells
from verifier import verify_task
from verifier.references import EXPECTED


@pytest.mark.parametrize(
    ("name", "company", "expression", "expected"),
    [
        ("lookup-rate", Company.WALMART, "rate", "6.7%"),
        ("income-ratio", Company.ALPHABET, "ratio", None),
        ("borrowing-change", Company.GOLDMAN_SACHS, "change", None),
        ("reconcile-shares", Company.DISNEY, "equal", "yes"),
        ("hedge-ratio", Company.GM, "absolute ratio", None),
    ],
)
def test_real_filing_path(name, company, expression, expected):
    from decimal import Decimal

    evidence = EXPECTED[name][1][0]
    table = evidence[0].split("/")[0]
    assert table in {t.table for t in list_tables(CatalogInput(company)).tables}
    assert describe_table(TableInput(table)).columns
    numbers = []
    for key in evidence:
        _, r, c = key.split("/")
        (cell,) = read_cells(ReadInput(table, [int(r)], [int(c)])).cells
        assert cell.cell_id == key
        text = cell.value.replace("$", "").replace(",", "").replace("(", "-").replace(")", "").rstrip("%")
        numbers.append(Decimal(text))
    if expression == "rate":
        answer = f"{numbers[0]}%"
    elif expression == "equal":
        answer = "yes" if sum(numbers[:2]) == numbers[2] else "no"
    elif expression == "change":
        answer = str((numbers[0] - numbers[1]) / numbers[1])
    else:
        answer = calculate(CalcInput(str(numbers[0]), Operation.DIVIDE, str(numbers[1]))).value
        if expression == "absolute ratio":
            answer = str(abs(Decimal(answer)))
    assert expected is None or answer == expected
    assert verify_task(name, QuestionInput(), AnswerOutput(answer, evidence), None, None)["valid"]
    for bad in [AnswerOutput("0", evidence), AnswerOutput(answer, []), AnswerOutput(answer, evidence + [evidence[0]])]:
        assert not verify_task(name, QuestionInput(), bad, None, None)["valid"]


def test_overlapping_reads_preserve_stable_ids_and_wrong_period_fails():
    table = EXPECTED["income-ratio"][1][0][0].split("/")[0]
    first = read_cells(ReadInput(table, [1], [1])).cells
    later = read_cells(ReadInput(table, [0, 1], [1])).cells
    assert first[0] == later[1]
    assert not verify_task(
        "income-ratio", QuestionInput(), AnswerOutput("6.118", [first[0].cell_id, f"{table}/0/2"]), None, None
    )["valid"]


@pytest.mark.parametrize("bad", ["NaN", "Infinity", "1e100000000", "2022: 6.118", "6.118 6.118", "0.827", ""])
def test_reject_malformed_or_wrong_ratio(bad):
    assert not verify_task(
        "income-ratio", QuestionInput(), AnswerOutput(bad, EXPECTED["income-ratio"][1][0]), None, None
    )["valid"]


def test_error_cases():
    with pytest.raises(ValueError):
        calculate(CalcInput("10", Operation.DIVIDE, "0"))
    with pytest.raises(ValueError):
        read_cells(ReadInput(EXPECTED["income-ratio"][1][0][0].split("/")[0], [-1], []))
