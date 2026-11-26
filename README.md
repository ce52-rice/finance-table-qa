# Finance Table QA

A RUSH Lab plugin for five independently executable financial QA tasks. Each task fixes the company, financial question and period and accepts an empty input object. The agent can explore 151 nonempty tables from the five companies in one pinned SnorkelFinance snapshot. The same tools, data and verifier serve every trial. The first release is a baseline workload for evaluating harness changes.

## Tools

| Tool | Agent access |
|---|---|
| `list_tables` | Discover a company's table IDs, source names and descriptions. |
| `describe_table` | Look up a table's row labels and column headings. Lists are zero-indexed. |
| `read_cells` | Retrieve selected rows and columns. An empty list selects the entire corresponding dimension. Each output gives the original value, labels and a stable cell ID. |
| `calculate` | Perform one arithmetic operation on two signed decimal inputs. |

### Tasks

| Task | Source question | What to ask |
|---|---:|---|
| `income-ratio` | 2 | For Alphabet, what was the ratio of domestic to foreign income from continuing operations before income taxes in 2022? |
| `lookup-rate` | 124 | What was Walmart's weighted-average finance lease discount rate as of January 31, 2025? |
| `borrowing-change` | 553 | What was the year-over-year percentage change in Goldman Sachs total unsecured borrowings from 2023 to 2024? |
| `reconcile-shares` | 73 | For Disney in 2024, did basic shares plus weighted-average dilutive awards equal diluted shares? |
| `hedge-ratio` | 172 | What was GM's 2024 interest-rate-swap hedge effectiveness ratio using the absolute changes in the hedged item and hedging instrument? |

Each task uses the agent runner and ends with NanoAgent's built-in submission of `answer` and `evidence`. The evaluator requires the specified numeric result or Boolean and the set of cell IDs used as operands. For the borrowing-change task it accepts the totals or the sum of their short-term and long-term components independently for each year. Answer checking accepts explicit percentages and decimal ratios, with half the last decimal place of the published reference as absolute tolerance. Blank, non-finite, ambiguous, wrong-sign, wrong-period and unsupported answers fail. Evidence order is immaterial and duplicate citations fail. This grades the five fixed cases and supported evidence sets. Additional valid derivations or new questions require new verifier cases. The stricter evidence requirement differs from the earlier answer-only Google pilots. Keep their results separate.

## Layout

`nanoagent.yaml` registers the tasks and tools. `contract.py` declares the inputs and outputs. `src/plugin/` serves the tools and bundles the tables. `verifier/` contains the fixed expected answers and evidence. The normal Session agent sees the task instructions and public tools. Never put verifier code, the answer CSV or completed predictions in its prompt or in a workspace exposed to a general shell agent. A baseline grounded in this plugin should use the same tool access as the modified harness.

`product/` and `ui/` provide the listing and result presentation. `tests/` checks all five cases. `src/inspect_finance_trace.py` reads exported JSON Lines offline from the command line.

## Develop and run

Use Python 3.12+ and uv. From the folder containing this README:

```powershell
uv sync --frozen --extra dev
uv run --frozen pytest -q
```

Publish this directory at the root of a team GitHub repository. Include the tracked `.env` file supplied here, which contains only explanatory comments. Add the GitHub repository URL to the course workspace through the Rush plugin submission flow. Once loaded, start a fresh Session in Finance Table QA and ask one of the questions above. For the first trial use only the question, without hints about the table or forced tool calls. Check the submitted answer, cited cells and verdict.

On the Dashboard choose **Download traces (JSON)**. The supplied NanoAgent production version exports JSON Lines, one run or chat per line. Keep raw exports and run sheets outside the plugin repo. For a file in the Windows Downloads folder:

```powershell
python .\src\inspect_finance_trace.py "$HOME\Downloads\traces-finance-table-qa.jsonl"
```

The reader recognizes financial cells returned as structured tool results. On a run with model request bodies it counts repeated cell ID and value pairs within each request. On a chat trajectory it summarizes repeated cells in observed tool results. A chat may expose only the outer task call, or the request may be truncated. If the reader cannot observe inner cells, open the nested task graph in the Session and inspect its tool results and subsequent model calls. If you can save the turn’s graph.json, the same reader accepts its path and follows the recorded used and continued links to reconstruct repeated cells per model request. If those are unavailable, collect the inner task transcript or instrument the harness at the point where it constructs each model request. A missing payload is an unknown observation. Use measured input tokens from matched live trials to report any savings.

Data source: [SnorkelFinance](https://huggingface.co/datasets/snorkelai/finqa-data/tree/9bd176a31004478a5250078872d893fd5fb0736b). The subset and question prompts are from revision `9bd176a31004478a5250078872d893fd5fb0736b`; its Apache 2.0 license and attribution are in `src/plugin/data/`. Snorkel designates its dataset for evaluation. The plugin code uses the MIT license. RUSH Lab and NanoAgent run separately.
