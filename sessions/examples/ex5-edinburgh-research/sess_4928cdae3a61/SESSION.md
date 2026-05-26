# Session sess_4928cdae3a61

**Scenario:** edinburgh-research
**Created:** 2026-05-26T02:59:31.452463+00:00

## Your task

(The loop half reads this file on every turn. The initial task description
has been written below by the orchestrator when the session was created.
Additional per-session instructions — constraints, identity, voice — can
be added by the scenario author.)

## Task description

Research an Edinburgh pub booking and write a flyer. Follow ALL steps below. Use ONLY party_size=6.

STEP 1 — call venue_search:
  venue_search(near='Haymarket', party_size=6, budget_max_gbp=800)
  → note the venue id, name, address from the result

STEP 2 — call get_weather:
  get_weather(city='edinburgh', date='2026-04-25')
  → note condition and temperature_c from the result

STEP 3 — call calculate_cost:
  calculate_cost(venue_id=<id from step 1>, party_size=6,
                 duration_hours=3, catering_tier='bar_snacks')
  → note total_gbp and deposit_required_gbp from the result

STEP 4 — call generate_flyer with the ACTUAL values from steps 1-3:
  generate_flyer(event_details={
    'venue_name': <actual name from step 1>,
    'venue_address': <actual address from step 1>,
    'date': '2026-04-25',
    'time': '19:30',
    'party_size': 6,
    'condition': <actual condition from step 2>,
    'temperature_c': <actual number from step 2>,
    'total_gbp': <actual number from step 3>,
    'deposit_required_gbp': <actual number from step 3>
  })
  ALL fields must be filled with real values from the tool outputs.
  Empty strings are NOT acceptable.

STEP 5 — call complete_task.

CRITICAL RULES:
- party_size is ALWAYS 6. Never use any other value.
- Do NOT call handoff_to_structured.
- Do NOT call complete_task before generate_flyer.
- Every field in event_details MUST contain the actual value returned by the tool, not an empty string.


## Constraints

- Be honest when you do not know something.
- Prefer reading memory over guessing.
- When the task is ambiguous, ask for clarification rather than inventing an answer.
