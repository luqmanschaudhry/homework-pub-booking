# Session sess_bdadf3ab5fc7

**Scenario:** edinburgh-research
**Created:** 2026-05-26T02:28:04.968452+00:00

## Your task

(The loop half reads this file on every turn. The initial task description
has been written below by the orchestrator when the session was created.
Additional per-session instructions — constraints, identity, voice — can
be added by the scenario author.)

## Task description

You are researching an Edinburgh pub booking. Follow these steps EXACTLY in order. Do NOT deviate.

STEP 1: Call venue_search ONCE:
  venue_search(near='Haymarket', party_size=6, budget_max_gbp=800)

STEP 2: Call get_weather ONCE:
  get_weather(city='edinburgh', date='2026-04-25')

STEP 3: Call calculate_cost ONCE using the venue_id from step 1:
  calculate_cost(venue_id=<id from step 1>, party_size=6, duration_hours=3, catering_tier='bar_snacks')

STEP 4: Call generate_flyer ONCE with ALL of these fields:
  generate_flyer(event_details={
    'venue_name': <name from step 1>,
    'venue_address': <address from step 1>,
    'date': '2026-04-25',
    'time': '19:30',
    'party_size': 6,
    'condition': <condition from step 2>,
    'temperature_c': <temperature from step 2>,
    'total_gbp': <total from step 3>,
    'deposit_required_gbp': <deposit from step 3>
  })

STEP 5: Call complete_task.

RULES:
- party_size is ALWAYS 6. Never change it.
- Do NOT call handoff_to_structured.
- Do NOT call complete_task before generate_flyer.
- Do NOT repeat any tool call.
- The task is complete ONLY when workspace/flyer.html exists.


## Constraints

- Be honest when you do not know something.
- Prefer reading memory over guessing.
- When the task is ambiguous, ask for clarification rather than inventing an answer.
