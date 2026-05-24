# Ex5 — Edinburgh research loop scenario

## Your answer

The planner produced two subgoals: sg_1 (research venues near Haymarket
for a party of 6) and sg_2 (produce an HTML flyer), both assigned to
the loop half. In offline mode (sess_b79ef5c953c5) the FakeLLMClient
scripted the correct tool sequence.

Turn 1 called venue_search, get_weather, and calculate_cost — all
parallel_safe=True because they only read JSON fixtures. Turn 2 called
generate_flyer (parallel_safe=False, writes a file). Turn 3 called
complete_task. The loop half outcome was "complete" with the flyer
written to workspace/flyer.html (1410 bytes).

The dataflow integrity check verified 4 facts against _TOOL_CALL_LOG:
the £ amounts, temperature, and weather condition in the flyer all
matched tool outputs exactly. In real mode (sess_fddbe53e87c5), Qwen
spiralled — calling venue_search 8 times with party_size=10 instead
of 6, never finding results, exhausting max_turns=8. The integrity
check never ran because no flyer was written. This shows the offline
scripted mode is essential for reliable grading.

## Citations

- sess_b79ef5c953c5 (Ex5 offline, dataflow OK, 4 facts verified)
- sess_fddbe53e87c5/logs/trace.jsonl (Ex5 real, 8 spiral calls)