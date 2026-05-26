# Ex7 — Handoff bridge

## Your answer

In offline mode (sess_a648a59eb17d) the bridge completed in 2 rounds.
Round 1: loop called venue_search(near="Haymarket", party_size=12),
found 0 results, then called handoff_to_structured with venue_id=
"Haymarket Tap". The mock Rasa rejected with "party_too_large"
(party=12 > cap=8). The bridge wrote a reverse handoff and started
round 2. Round 2: loop searched Old Town for party=6, found royal_oak
(16 seats), handed off again. Structured confirmed. The trace shows
4 session.state_changed events: loop→structured (round 1),
structured→loop (round 1, rejection), loop→structured (round 2),
structured→complete (round 2).

In real mode (sess_a7b13b18df6d, Llama-3.3-70B), the bridge completed
in 1 round. The executor called venue_search, then handoff_to_structured
with the booking data. The mock Rasa confirmed immediately since
party_size=6 is within policy limits (≤8) and deposit was £0 (≤£300).
The bridge marked the session complete after round 1.

The key design insight: the validator (normalise_booking_payload) is
the seam between non-deterministic loop output and deterministic
structured policy. In real mode the LLM passed incomplete data
(missing date, time) — the validator fills in defaults rather than
rejecting, making the bridge robust to LLM variability without
compromising the policy enforcement in ActionValidateBooking.

## Citations

- sess_a648a59eb17d/logs/trace.jsonl (offline, 2 rounds, 4 state changes)
- sess_a7b13b18df6d (real mode, completed round 1)