import json

from inspect_finance_trace import summarize, visible_cells


def test_duplicate_within_request_not_across_requests():
    payload = {"source": "sample", "cells": [{"cell_id": "alphabet-17/1/1", "value": "$10,021"}]}
    tool = {"role": "tool", "content": json.dumps(payload)}
    assert len(visible_cells({"messages": [tool]})) == 1
    seen = visible_cells({"messages": [tool, tool]})
    assert len(seen) == 2 and len(set(seen)) == 1
    assert visible_cells("truncated data") is None


def test_missing_inner_chat_is_unknown(capsys):
    summarize({"type": "chat", "session_id": "sample", "turns": [{"messages": {"steps": []}}]})
    assert "no inner cell payload observed" in capsys.readouterr().out


def test_graph_follows_conversation_edges_without_double_counting_identical_nodes(capsys):
    from inspect_finance_trace import summarize_graph

    p = {"source": "example", "cells": [{"cell_id": "t/1/1", "value": "3"}]}
    graph = {
        "nodes": [
            {"id": "first", "type": "agent_reply"},
            {"id": "second", "type": "agent_reply"},
            {"id": "third", "type": "agent_reply"},
            {"id": "a", "type": "tool_result", "value": p},
            {"id": "b", "type": "tool_result", "value": json.dumps(p)},
        ],
        "edges": [
            {"from": "first", "to": "second", "relation": "continued"},
            {"from": "a", "to": "second", "relation": "used"},
            {"from": "second", "to": "third", "relation": "continued"},
            {"from": "b", "to": "third", "relation": "used"},
        ],
    }
    summarize_graph(graph)
    results = capsys.readouterr().out
    assert "second 1 cell appearances" in results and "third 2 cell appearances" in results and "1 duplicate" in results
