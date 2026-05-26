# Ex5 — Edinburgh research loop scenario

## Your answer

The planner produced two subgoals: sg_1 (research venues near Haymarket
for a party of 6) and sg_2 (produce an HTML flyer), both assigned to
the loop half. In offline mode (FakeLLMClient) the scripted tool
sequence ran cleanly: venue_search, get_weather, calculate_cost in
parallel (all parallel_safe=True), then generate_flyer
(parallel_safe=False), then complete_task.

In real mode (sess_4928cdae3a61, Llama-3.3-70B executor), the planner
produced 3 subgoals and the executor called venue_search, get_weather,
calculate_cost, and generate_flyer across sg_1 through sg_3. The
dataflow integrity check verified 4 facts against _TOOL_CALL_LOG:
£437 total, £87 deposit, 12°C temperature, and "cloudy" condition —
all matching tool outputs exactly.

During development the spiral defense caught Qwen/Qwen3-32B looping
on venue_search 8 times (sess_fddbe53e87c5) with wrong parameters
(party_size=10, area="Edinburgh City Center"). The tool-level counter
returns an error after 3 calls forcing the LLM to use haymarket_tap
directly. The type coercion fix (int(party_size)) was needed because
the LLM passed "6" as a string, causing a TypeError in calculate_cost.

## Citations

- sess_4928cdae3a61/logs/trace.jsonl (Ex5 real, 4 facts verified)
- sess_fddbe53e87c5/logs/trace.jsonl (spiral: 8 venue_search calls)