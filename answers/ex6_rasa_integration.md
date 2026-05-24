# Ex6 — Rasa structured half

## Your answer

In offline mode the RasaStructuredHalf POSTs to a stdlib mock server
spawned on port 5905. The mock applies the same party/deposit rules
as the real Rasa action server. Session sess_4a01b4949f53 confirmed
booking reference BK-7D401E9E with outcome "complete".

In real mode (sess_e19fb23a9de7) we ran three terminals: action server
on port 5055, Rasa server on port 5005 (trained model
20260524-042948-energetic-bend.tar.gz), and the scenario in terminal 3.
The structured half POSTed sender "homework-185d7d73" with the booking
payload. Rasa returned two messages: "Booking confirmed. Reference:
BK-7D401E9E." and "Is there anything else I can help you with?".
The half parsed the first message, detected "booking confirmed" in the
text, and returned next_action="complete".

The normalise_booking_payload step is critical — it converts raw loop
output into the canonical Rasa webhook shape with typed fields. Without
it, Rasa's action server would receive untyped strings and the
ActionValidateBooking custom action would fail silently.

## Citations

- sess_e19fb23a9de7 (Ex6 real mode, Rasa confirmed BK-7D401E9E)
- sess_4a01b4949f53 (Ex6 offline mock, same reference)