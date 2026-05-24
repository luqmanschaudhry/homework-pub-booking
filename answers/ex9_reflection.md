# Ex9 — Reflection

## Q1 — Planner handoff decision

### Your answer

In session sess_a648a59eb17d (Ex7 handoff bridge, 2 rounds), the
planner produced one subgoal with assigned_half: "loop" in round 1:
"find venue near haymarket for 12". The executor then called
venue_search(near="Haymarket", party_size=12, budget_max_gbp=2000)
which returned 0 results, then called handoff_to_structured with
reason: "loop half identified a candidate venue; passing to structured
half for confirmation under policy rules".

The trace shows the session.state_changed event at round 1 going from
"loop" to "structured". The structured half (mock Rasa) rejected with
"party_too_large", triggering a reverse handoff back to the loop. In
round 2 the planner received the task_preview: "The structured half
rejected the previous proposal. Reason: sorry, we can't accept this
booking. reason: party_too_large. Produce an alternative." The planner
produced a new subgoal assigned_half: "loop" again — "retry with
larger venue after rejection". The executor searched Old Town for
party_size=6, found royal_oak (1 result), and handed off again. The
structured half confirmed and session.state_changed from "structured"
to "complete" in round 2.

The signal driving the handoff decision is the task description
mentioning "under policy rules" — the planner routes deterministic
constraint enforcement to the structured half, keeping the loop half
focused on open-ended research.

### Citation

- sess_a648a59eb17d/logs/trace.jsonl — handoff_to_structured call,
  session.state_changed events (loop→structured round 1,
  structured→loop round 1, loop→structured round 2,
  structured→complete round 2)

---

## Q2 — Dataflow integrity catch

### Your answer

In session sess_fddbe53e87c5 (Ex5 real mode with Qwen/Qwen3-32B),
the executor spiralled: it called venue_search 8 times with wrong
parameters — party_size=10 instead of the task's specified 6, and
area="Edinburgh City Center" instead of "Haymarket". Every call
returned "0 result(s)". The executor exhausted max_turns=8 without
ever calling get_weather, calculate_cost, or generate_flyer.

This is a dataflow failure the integrity check would have caught had
the LLM fabricated results instead. verify_dataflow works by
comparing every £ amount and temperature in the flyer HTML against
_TOOL_CALL_LOG. If the LLM had invented "Total: £560" in the flyer
without calculate_cost actually returning 560, the check would return
ok=False with unverified_facts=['£560']. The test
test_verify_dataflow_catches_obvious_fabrication confirms this: a
flyer containing £9999 with no tool call producing that value
correctly fails.

The offline FakeLLMClient (sess_b79ef5c953c5) scripted the correct
tool sequence and the check verified 4 facts — £540 total, £0
deposit, 12°C temperature, "cloudy" condition — all matching
_TOOL_CALL_LOG exactly. The contrast between the two sessions shows
the integrity check's value: the offline mode proved the tools and
check work correctly; the real mode exposed what happens when the
LLM ignores the task constraints entirely.

### Citation

- sess_fddbe53e87c5/logs/trace.jsonl (8 venue_search calls, 0 results)
- tests/public/test_ex5_scaffold.py::test_verify_dataflow_catches_obvious_fabrication

---

## Q3 — First production failure

### Your answer

The first production failure I'd expect shipping this agent to a real
pub-booking business is a Rasa action server returning a stale cached
response after a code deploy — for example, the deposit policy
threshold changes from £300 to £500, the Python action is updated,
but the running rasa-actions process still has the old module in
memory. A booking that should be approved under the new policy gets
rejected, and the customer is told "deposit_too_high" incorrectly.

The sovereign-agent primitive that would surface this is the ticket
state machine. Each structured half invocation writes a ticket with
state=success or state=failed and a raw_output.json capturing the
full Rasa response including the rejection reason. In my Ex6 session
sess_e19fb23a9de7 the ticket recorded the confirmed booking reference
BK-7D401E9E. If instead the response had been "deposit_too_high" with
a plausible deposit amount, a human operator could read the ticket's
raw_output.json and immediately see the Rasa response — but without
the ticket capturing the exact Rasa payload, the failure would be
invisible: the agent would report "structured half rejected" with no
evidence of why.

The ticket state machine is the right primitive here because it
creates an immutable record of what the external service actually
returned, separate from what the agent inferred. That's the audit
trail that distinguishes "Rasa rejected correctly" from "Rasa
returned stale policy."

### Citation

- sess_e19fb23a9de7/session.json (Ex6 real Rasa confirmed booking)
- sess_a648a59eb17d/logs/trace.jsonl — session.state_changed
  structured→loop with rejection_reason field