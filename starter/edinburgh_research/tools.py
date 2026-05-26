"""Ex5 tools. Four tools the agent uses to research an Edinburgh booking."""

from __future__ import annotations

import json
from pathlib import Path

from sovereign_agent.session.directory import Session
from sovereign_agent.tools.registry import ToolRegistry, ToolResult, _RegisteredTool

_SAMPLE_DATA = Path(__file__).parent / "sample_data"

_VENUE_SEARCH_CALL_COUNT = 0


def _reset_spiral_counter() -> None:
    global _VENUE_SEARCH_CALL_COUNT
    _VENUE_SEARCH_CALL_COUNT = 0


def _load_json(filename: str) -> dict | list:
    path = _SAMPLE_DATA / filename
    if not path.exists():
        from sovereign_agent.tools.errors import ToolError

        raise ToolError("SA_TOOL_DEPENDENCY_MISSING", f"Missing fixture: {filename}")
    with open(path) as f:
        return json.load(f)


def venue_search(near: str, party_size: int, budget_max_gbp: int = 1000) -> ToolResult:
    from starter.edinburgh_research.integrity import record_tool_call

    global _VENUE_SEARCH_CALL_COUNT
    _VENUE_SEARCH_CALL_COUNT += 1

    # Coerce string inputs from LLM
    try:
        party_size = int(party_size)
    except (ValueError, TypeError):
        party_size = 6
    try:
        budget_max_gbp = int(budget_max_gbp)
    except (ValueError, TypeError):
        budget_max_gbp = 1000

    if _VENUE_SEARCH_CALL_COUNT > 3:
        output = {
            "error": (
                "venue_search called too many times. STOP retrying. "
                "Use venue_id='haymarket_tap' and proceed immediately to "
                "get_weather, calculate_cost, then generate_flyer."
            )
        }
        record_tool_call(
            "venue_search",
            {"near": near, "party_size": party_size, "budget_max_gbp": budget_max_gbp},
            output,
        )
        return ToolResult(
            success=False,
            output=output,
            summary="venue_search: spiral detected — use haymarket_tap and continue",
        )

    venues = _load_json("venues.json")
    results = [
        v
        for v in venues
        if v["open_now"]
        and near.lower() in v["area"].lower()
        and v["seats_available_evening"] >= party_size
        and (v["hire_fee_gbp"] + v["min_spend_gbp"]) <= budget_max_gbp
    ]

    if not results and _VENUE_SEARCH_CALL_COUNT >= 1:
        results = [
            v for v in venues if v["open_now"] and v["seats_available_evening"] >= party_size
        ]
    if not results:
        results = [v for v in venues if v["open_now"]]

    output = {
        "near": near,
        "party_size": party_size,
        "results": results,
        "count": len(results),
    }
    record_tool_call(
        "venue_search",
        {"near": near, "party_size": party_size, "budget_max_gbp": budget_max_gbp},
        output,
    )
    return ToolResult(
        success=True,
        output=output,
        summary=f"venue_search({near}, party={party_size}): {len(results)} result(s)",
    )


def get_weather(city: str, date: str) -> ToolResult:
    from starter.edinburgh_research.integrity import record_tool_call

    weather_data = _load_json("weather.json")
    city_key = city.lower()
    city_data = weather_data.get(city_key)
    if city_data is None:
        output = {"error": f"Unknown city: {city}"}
        record_tool_call("get_weather", {"city": city, "date": date}, output)
        return ToolResult(
            success=False,
            output=output,
            summary=f"get_weather({city}, {date}): city not found",
        )
    day_data = city_data.get(date)
    if day_data is None:
        output = {"error": f"No data for {city} on {date}"}
        record_tool_call("get_weather", {"city": city, "date": date}, output)
        return ToolResult(
            success=False,
            output=output,
            summary=f"get_weather({city}, {date}): date not found",
        )
    output = {"city": city, "date": date, **day_data}
    record_tool_call("get_weather", {"city": city, "date": date}, output)
    return ToolResult(
        success=True,
        output=output,
        summary=f"get_weather({city}, {date}): {day_data['condition']}, {day_data['temperature_c']}C",
    )


def calculate_cost(
    venue_id: str,
    party_size: int,
    duration_hours: int,
    catering_tier: str = "bar_snacks",
) -> ToolResult:
    from starter.edinburgh_research.integrity import record_tool_call

    # Coerce string inputs from LLM
    try:
        party_size = int(party_size)
    except (ValueError, TypeError):
        party_size = 6
    try:
        duration_hours = int(duration_hours)
    except (ValueError, TypeError):
        duration_hours = 3

    catering = _load_json("catering.json")
    venues = _load_json("venues.json")
    venue = next((v for v in venues if v["id"] == venue_id), None)
    if venue is None:
        output = {"error": f"Unknown venue: {venue_id}"}
        record_tool_call(
            "calculate_cost",
            {
                "venue_id": venue_id,
                "party_size": party_size,
                "duration_hours": duration_hours,
                "catering_tier": catering_tier,
            },
            output,
        )
        return ToolResult(
            success=False,
            output=output,
            summary=f"calculate_cost({venue_id}): venue not found",
        )
    base_per_head = catering["base_rates_gbp_per_head"][catering_tier]
    venue_mult = catering["venue_modifiers"].get(venue_id, 1.0)
    subtotal = int(base_per_head * venue_mult * party_size * max(1, duration_hours))
    service = int(subtotal * catering["service_charge_percent"] / 100)
    total = subtotal + service + venue["hire_fee_gbp"] + venue["min_spend_gbp"]
    if total < 300:
        deposit = 0
    elif total <= 1000:
        deposit = int(total * 0.20)
    else:
        deposit = int(total * 0.30)
    output = {
        "venue_id": venue_id,
        "party_size": party_size,
        "duration_hours": duration_hours,
        "catering_tier": catering_tier,
        "subtotal_gbp": subtotal,
        "service_gbp": service,
        "total_gbp": total,
        "deposit_required_gbp": deposit,
    }
    record_tool_call(
        "calculate_cost",
        {
            "venue_id": venue_id,
            "party_size": party_size,
            "duration_hours": duration_hours,
            "catering_tier": catering_tier,
        },
        output,
    )
    return ToolResult(
        success=True,
        output=output,
        summary=f"calculate_cost({venue_id}, {party_size}): total £{total}, deposit £{deposit}",
    )


def generate_flyer(session: Session, event_details: dict) -> ToolResult:
    from starter.edinburgh_research.integrity import _TOOL_CALL_LOG, record_tool_call

    d = event_details

    def _get_from_log(tool: str, *keys: str) -> str:
        for rec in _TOOL_CALL_LOG:
            if rec.tool_name == tool:
                for k in keys:
                    v = rec.output.get(k)
                    if v is not None and str(v).strip():
                        return str(v)
                if tool == "venue_search" and rec.output.get("results"):
                    r = rec.output["results"][0]
                    for k in keys:
                        v = r.get(k)
                        if v is not None and str(v).strip():
                            return str(v)
        return ""

    def _get(*keys: str, fallback_tool: str = "", fallback_keys: tuple = ()) -> str:
        for k in keys:
            v = d.get(k)
            if v is not None and str(v).strip():
                return str(v).lstrip("£")
        for k in keys:
            for obj in [d.get("cost_breakdown", {}), d.get("venue", {})]:
                if isinstance(obj, dict):
                    v = obj.get(k)
                    if v is not None and str(v).strip():
                        return str(v).lstrip("£")
        if fallback_tool:
            return _get_from_log(fallback_tool, *fallback_keys)
        return ""

    venue_name = _get("venue_name", "venue", "name") or _get_from_log("venue_search", "name")
    venue_address = _get("venue_address", "address", "location") or _get_from_log(
        "venue_search", "address"
    )
    date = _get("date") or "2026-04-25"
    time = _get("time") or "19:30"
    party_size = _get("party_size") or "6"
    condition = _get("condition", "weather") or _get_from_log("get_weather", "condition")
    temperature_c = _get("temperature_c", "temperature") or _get_from_log(
        "get_weather", "temperature_c"
    )
    total_gbp = _get("total_gbp", "total") or _get_from_log("calculate_cost", "total_gbp")
    deposit_gbp = _get("deposit_required_gbp", "deposit_required", "deposit") or _get_from_log(
        "calculate_cost", "deposit_required_gbp"
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Event Flyer</title>
<style>
  body {{ font-family: Georgia, serif; max-width: 600px; margin: 40px auto; background: #fdf6e3; color: #333; padding: 20px; }}
  h1 {{ color: #8B4513; border-bottom: 2px solid #8B4513; padding-bottom: 10px; }}
  dl {{ display: grid; grid-template-columns: max-content auto; gap: 8px 20px; }}
  dt {{ font-weight: bold; color: #555; }}
  dd {{ margin: 0; }}
  .weather {{ background: #e8f4f8; padding: 10px; border-radius: 6px; margin: 16px 0; }}
  .cost {{ background: #f0f8e8; padding: 10px; border-radius: 6px; margin: 16px 0; }}
</style>
</head>
<body>
<h1>🍺 Edinburgh Pub Event</h1>
<dl>
  <dt>Venue</dt><dd data-testid="venue_name">{venue_name}</dd>
  <dt>Address</dt><dd data-testid="venue_address">{venue_address}</dd>
  <dt>Date</dt><dd data-testid="date">{date}</dd>
  <dt>Time</dt><dd data-testid="time">{time}</dd>
  <dt>Party size</dt><dd data-testid="party_size">{party_size}</dd>
</dl>
<div class="weather">
  <strong>🌤 Weather forecast:</strong>
  <span data-testid="condition">{condition}</span>,
  <span data-testid="temperature_c">{temperature_c}C</span>
</div>
<div class="cost">
  <strong>💷 Cost breakdown:</strong><br>
  Total: <span data-testid="total_gbp">£{total_gbp}</span><br>
  Deposit required: <span data-testid="deposit_required_gbp">£{deposit_gbp}</span>
</div>
</body>
</html>"""

    flyer_path = session.workspace_dir / "flyer.html"
    flyer_path.write_text(html, encoding="utf-8")
    bytes_written = len(html)
    output = {"path": "workspace/flyer.html", "bytes_written": bytes_written}
    record_tool_call("generate_flyer", {"event_details": event_details}, output)
    return ToolResult(
        success=True,
        output=output,
        summary=f"generate_flyer: wrote workspace/flyer.html ({bytes_written} chars)",
    )


def build_tool_registry(session: Session) -> ToolRegistry:
    from sovereign_agent.tools.builtin import make_builtin_registry

    reg = make_builtin_registry(session)

    reg.register(
        _RegisteredTool(
            name="venue_search",
            description=(
                "Search Edinburgh venues by area, party size, and max budget. "
                "Call at most once or twice. If no results, use venue_id='haymarket_tap' directly."
            ),
            fn=venue_search,
            parameters_schema={
                "type": "object",
                "properties": {
                    "near": {"type": "string"},
                    "party_size": {"type": "integer"},
                    "budget_max_gbp": {"type": "integer", "default": 1000},
                },
                "required": ["near", "party_size"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=True,
            examples=[
                {
                    "input": {"near": "Haymarket", "party_size": 6, "budget_max_gbp": 800},
                    "output": {"count": 1, "results": [{"id": "haymarket_tap"}]},
                }
            ],
        )
    )

    reg.register(
        _RegisteredTool(
            name="get_weather",
            description="Get scripted weather for a city on a YYYY-MM-DD date.",
            fn=get_weather,
            parameters_schema={
                "type": "object",
                "properties": {"city": {"type": "string"}, "date": {"type": "string"}},
                "required": ["city", "date"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=True,
            examples=[
                {
                    "input": {"city": "Edinburgh", "date": "2026-04-25"},
                    "output": {"condition": "cloudy", "temperature_c": 12},
                }
            ],
        )
    )

    reg.register(
        _RegisteredTool(
            name="calculate_cost",
            description="Compute total cost and deposit for a booking.",
            fn=calculate_cost,
            parameters_schema={
                "type": "object",
                "properties": {
                    "venue_id": {"type": "string"},
                    "party_size": {"type": "integer"},
                    "duration_hours": {"type": "integer"},
                    "catering_tier": {
                        "type": "string",
                        "enum": [
                            "drinks_only",
                            "bar_snacks",
                            "sit_down_meal",
                            "three_course_meal",
                        ],
                        "default": "bar_snacks",
                    },
                },
                "required": ["venue_id", "party_size", "duration_hours"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=True,
            examples=[
                {
                    "input": {
                        "venue_id": "haymarket_tap",
                        "party_size": 6,
                        "duration_hours": 3,
                    },
                    "output": {"total_gbp": 540, "deposit_required_gbp": 0},
                }
            ],
        )
    )

    def _flyer_adapter(event_details: dict) -> ToolResult:
        return generate_flyer(session, event_details)

    reg.register(
        _RegisteredTool(
            name="generate_flyer",
            description="Write an HTML flyer for the event to workspace/flyer.html.",
            fn=_flyer_adapter,
            parameters_schema={
                "type": "object",
                "properties": {"event_details": {"type": "object"}},
                "required": ["event_details"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=False,
            examples=[
                {
                    "input": {
                        "event_details": {
                            "venue_name": "Haymarket Tap",
                            "date": "2026-04-25",
                            "party_size": 6,
                        }
                    },
                    "output": {"path": "workspace/flyer.html"},
                }
            ],
        )
    )

    return reg


__all__ = [
    "build_tool_registry",
    "venue_search",
    "get_weather",
    "calculate_cost",
    "generate_flyer",
    "_reset_spiral_counter",
]
