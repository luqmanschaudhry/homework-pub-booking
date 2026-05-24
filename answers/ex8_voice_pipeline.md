# Ex8 — Voice pipeline

## Your answer

Session sess_452094cd7463 ran in text mode. The trace shows 2 turns:

Turn 0: user said "Hi, I'd like to book a table for 6 people on the
25th of April". Alasdair (ManagerPersona backed by Llama-3.3-70B)
replied "Aye, we can do that. I'll pencil you in for 25th April.
What's the contact number?" — 12 seconds LLM latency.

Turn 1: user said "012345678". Alasdair replied "Got it, 012345678.
See you on the 25th." — 12 seconds LLM latency.

Both turns emitted voice.utterance_in and voice.utterance_out trace
events with payload {text, turn, mode:"text"}. The mode field
distinguishes text from voice transport in the trace without changing
the event schema.

The graceful degradation design means voice mode falls back to text
mode when SPEECHMATICS_KEY is absent. This is why the CI check
"voice loop implemented" passes without a microphone — the same code
path runs, just with stdin as the transport instead of an audio
stream.

## Citations

- sess_452094cd7463/logs/trace.jsonl (2 turns, utterance_in/out events)