"""Inspect a Rush Dashboard export locally. Raw tool-result payloads only."""

import json
import sys
from collections import Counter
from pathlib import Path


def cells_from_result(payload):
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except ValueError:
            return []
    if isinstance(payload, list):
        cells = []
        for block in payload:
            if isinstance(block, dict) and block.get("type") in {"text", "input_text", "output_text"}:
                cells.extend(cells_from_result(block.get("text")))
        return cells
    if not isinstance(payload, dict) or not isinstance(payload.get("cells"), list):
        return []
    return [
        (payload.get("source"), c["cell_id"], c["value"])
        for c in payload["cells"]
        if isinstance(c, dict) and isinstance(c.get("cell_id"), str) and isinstance(c.get("value"), str)
    ]


def visible_cells(body):
    if not isinstance(body, dict):
        return None
    messages = body.get("messages", body.get("input"))
    if not isinstance(messages, list):
        return None
    items = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        if message.get("role") == "tool":
            items.extend(cells_from_result(message.get("content")))
        elif message.get("type") == "function_call_output":
            items.extend(cells_from_result(message.get("output")))
        elif isinstance(message.get("content"), list):
            for block in message["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    items.extend(cells_from_result(block.get("content")))
    return items


def summarize(record):
    if record.get("type") == "run":
        print("Run", record.get("run_id"), "task", record.get("task_id"))
        for attempt in record.get("attempts", []):
            for call in attempt.get("model_calls", []):
                req = call.get("request") or {}
                observed = visible_cells(req.get("body"))
                label = f"  Request {call.get('call_id')}:"
                if observed is None or req.get("redaction") == "truncated":
                    print(label, "request missing, truncated or unsupported")
                elif not observed:
                    print(label, "no structured finance cell payload identified")
                else:
                    dup = sum(n - 1 for n in Counter(observed).values())
                    print(label, len(observed), "cell appearances,", dup, "duplicate copies within this request")
    elif record.get("type") == "chat":
        print("Session", record.get("session_id"))
        for i, turn in enumerate(record.get("turns", []), 1):
            observed = []
            trajectory = turn.get("messages") or {}
            for step in trajectory.get("steps", []):
                for result in (step.get("observation") or {}).get("results", []):
                    observed.extend(cells_from_result(result.get("content")))
            if observed:
                dup = sum(n - 1 for n in Counter(observed).values())
                print(
                    f"  Turn {i}: {len(observed)} returned cells, {dup} repeated across recorded results;"
                    " confirm simultaneous visibility in the inner task before counting prompt savings."
                )
            else:
                print(f"  Turn {i}: no inner cell payload observed. Check the task graph or an instrumented run.")
    else:
        print("Unsupported record type", record.get("type"))


def summarize_graph(graph):
    """Follow only recorded used/continued edges within a conversation."""
    nodes = {node["id"]: node for node in graph["nodes"]}
    inputs = {}
    for edge in graph["edges"]:
        if edge["relation"] in {"continued", "used"}:
            inputs.setdefault(edge["to"], []).append((edge["relation"], edge["from"]))
    found = False
    for node in nodes.values():
        if node["type"] != "agent_reply":
            continue
        pending = [node["id"]]
        visited = set()
        result_ids = set()
        while pending:
            at = pending.pop()
            if at in visited:
                continue
            visited.add(at)
            for relation, source in inputs.get(at, []):
                if relation == "continued":
                    pending.append(source)
                elif nodes[source]["type"] == "tool_result":
                    result_ids.add(source)
        cells = [cell for source in result_ids for cell in cells_from_result(nodes[source].get("value"))]
        if cells:
            found = True
            print(
                node["id"],
                len(cells),
                "cell appearances on recorded conversation edges,",
                len(cells) - len(set(cells)),
                "duplicate copies (graph reconstruction)",
            )
    if not found:
        print("No structured financial cells linked to model requests in this graph; visibility unconfirmed.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python src/inspect_finance_trace.py path/to/traces-finance-table-qa.jsonl")
    path = Path(sys.argv[1])
    if path.suffix.lower() == ".json":
        with path.open(encoding="utf-8-sig") as stream:
            graph = json.load(stream)
        if "nodes" not in graph or "edges" not in graph:
            sys.exit("Expected a turn graph.json with nodes and edges, or a Dashboard .jsonl export.")
        summarize_graph(graph)
        sys.exit(0)
    matched = False
    with path.open(encoding="utf-8-sig") as stream:
        for line in stream:
            if line.strip():
                record = json.loads(line)
                if (record.get("plugin") or {}).get("id") == "finance-table-qa":
                    matched = True
                    summarize(record)
    if not matched:
        print("No finance-table-qa sessions or runs in this export.")
