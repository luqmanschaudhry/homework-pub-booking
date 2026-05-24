# Ex9 — Reflection

## Q1 — Planner handoff decision

### Your answer

In my Ex7 run (session sess_94fd867e614b), the bridge completed in 2
rounds with "structured confirmed in round 2". The handoff decision
works because the DefaultPlanner assigns subgoals to halves based on
the nature of the work described: open-ended research goes to the loop
half (which can call tools iteratively), while commitment/confirmation
goes to the structured half (which has deterministic rules encoded in
Python).

This is advisory, not physical — the orchestrator respects the
assignment only because both halves are wired up in the bridge. The
key insight from my run is that "round 2" means the loop half ran
first, produced a result, and the structured half then confirmed it.
The handoff is the seam between non-deterministic reasoning and
deterministic policy enforcement.

If the planner mis-assigns a subgoal — say, sends a policy-enforcement
task to the loop half — the LLM might hallucinate a confirmation
instead of applying the actual rules. The structured half's Python
is the source of truth; prose interpretation is just routing.

### Citation

- sess_94fd867e614b (Ex7 offline run, bridge completed 2 rounds)

---

## Q2 — Dataflow integrity catch

### Your answer

In session sess_fddbe53e87c5 (Ex5 real mode), the Qwen executor
spiralled: it called venue_search 8 times with wrong parameters
(party_size=10 instead of 6, area="Edinburgh City Center" instead
of "Haymarket"), never finding results. The trace shows each call
returning "0 result(s)" and the executor retrying with minor
variations rather than moving on to get_weather or calculate_cost.

The dataflow integrity check would have caught any fabrication had
the LLM invented a venue result and proceeded to generate a flyer —
verify_dataflow compares every £ amount and temperature in the flyer
against _TOOL_CALL_LOG. Since no flyer was written the check never
ran, but the spiral itself is a dataflow failure: the executor never
produced the ground-truth data that generate_flyer needs.

The lesson: integrity checks protect against fabrication, but they
cannot protect against the LLM getting stuck before producing data.
Both failure modes (spiral and fabrication) are real; the offline
FakeLLMClient masks the spiral by scripting the correct tool calls.

### Citation

- sess_fddbe53e87c5/logs/trace.jsonl (8 venue_search calls, 0 results each)

---

## Q3 — Removing one framework primitive

### Your answer

I'd keep session directories as the last thing standing. My Ex8 run
(sess_452094cd7463) shows why: the trace.jsonl captured both sides
of the conversation — user utterances and Alasdair's replies — with
timestamps. Without the session directory, that exchange would be
gone the moment the process exited.

The forward-only state machine and tickets are useful but
reconstructable: tickets are .json files inside the session, and
the state machine is just a policy on how to read them. Atomic-rename
IPC is replaceable by polling. But session directories are the
atomic unit of "what happened in this run" — lose them and you lose
the ability to narrate, debug, or grade any session.

In my Ex5 offline run the session was written to a temp directory
that was deleted after the process exited. I could not read the
trace later. The persistent sessions (Ex5 real, Ex8) survived because
they were written to the sovereign-agent data directory. That
difference — ephemeral vs persistent — is exactly why session
directories are the irreplaceable primitive.

### Citation

- sess_452094cd7463/logs/trace.jsonl (Ex8 conversation trace)
- sess_fddbe53e87c5/logs/trace.jsonl (Ex5 real mode spiral)