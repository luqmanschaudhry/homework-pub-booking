# Ex7 — Handoff bridge

## Your answer

Session sess_94fd867e614b completed in 2 rounds with "structured
confirmed in round 2". Round 1: the loop half ran and produced a
booking candidate via its tools. The bridge detected next_action=
handoff_to_structured and wrote a forward handoff file, then invoked
the structured half. Round 2: the structured half confirmed, returning
next_action="complete". The bridge marked the session done.

The round-trip state machine is what makes this exercise interesting.
The bridge is not just a router — it rewrites the task between rounds.
If the structured half had rejected, the bridge would have built a
reverse task containing the rejection_reason and retry=True, giving
the loop half context to try a different venue. In the scripted offline
demo the confirmation happens in round 2 so the retry path is not
exercised, but the bridge.py code handles it.

The key design insight is that the loop half and structured half never
talk directly — the bridge is the only entity that sees both results.
This isolation means each half can be tested independently, and the
bridge's state machine is the only place where the round-trip logic
lives.

## Citations

- sess_94fd867e614b (Ex7 offline, 2 rounds, structured confirmed)