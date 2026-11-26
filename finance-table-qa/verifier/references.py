"""Published benchmark references and accepted supporting operands by task."""

EXPECTED = {
    "lookup-rate": ("0.067", [["walmart-19/9/1"]]),
    "income-ratio": ("6.118", [["alphabet-17/0/1", "alphabet-17/1/1"]]),
    "borrowing-change": (
        "-0.01724",
        [
            ["gs-17/2/1", "gs-17/2/2"],
            ["gs-17/0/1", "gs-17/1/1", "gs-17/0/2", "gs-17/1/2"],
            ["gs-17/2/1", "gs-17/0/2", "gs-17/1/2"],
            ["gs-17/2/2", "gs-17/0/1", "gs-17/1/1"],
        ],
    ),
    "reconcile-shares": ("Yes", [["disney-26/0/1", "disney-26/1/1", "disney-26/2/1"]]),
    "hedge-ratio": ("0.558", [["gm-04/1/1", "gm-04/2/1"]]),
}
