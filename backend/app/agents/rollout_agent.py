"""
Step 8 — Rollout Plan Agent.
Takes the winning SimResult + Scenario and generates a deployment plan via Gemini.
Auto-rollback thresholds ported from simulation_lab_demo5.py lines 1362-1382.
"""
import json

from app.models.result import Result
from app.models.scenario import Scenario
from app.models.simulation import Simulation

ROLLOUT_PROMPT = """
You are an Albertsons deployment architect.

Given these simulation results, generate a phased rollout plan for a production A/B test.

Winning scenario: {scenario_name}
Scenario config: {scenario_json}
Simulation KPIs:
  - Conversion lift: {conversion_lift:.2%}
  - RPV lift: {rpv_lift:.2%}
  - Margin impact: {margin_impact:.2%}
  - Confidence: {confidence:.0%}
  - Win probability: {win_probability:.1f}%

Return ONLY this JSON:
{{
  "feature_flags": [
    {{"flag_name": "...", "week1_pct": 10, "week2_pct": 30, "week3_pct": 50, "week4_pct": 100}}
  ],
  "promo_plan": {{
    "channels": ["email", "on-site"],
    "timing": "...",
    "budget_allocation": {{"email": "...", "sms": "...", "on_site": "..."}}
  }},
  "inventory_guardrails": {{
    "min_stock_level_pct": 20,
    "reorder_trigger_pct": 30,
    "safety_buffer_pct": 15,
    "auto_disable_if_stockout_exceeds_pct": 8
  }},
  "auto_rollback_rules": [
    {{"trigger_metric": "conversion_rate", "threshold": "-2%", "action": "disable_feature_flags", "notify": ["Product","Engineering","Marketing"]}},
    {{"trigger_metric": "sla_achievement", "threshold": "below 92%", "action": "disable_feature_flags", "notify": ["Ops","Engineering"]}},
    {{"trigger_metric": "stockout_rate", "threshold": "above 8%", "action": "disable_feature_flags", "notify": ["Ops","Merchandising"]}},
    {{"trigger_metric": "care_contacts", "threshold": "spike >12%", "action": "alert_and_review", "notify": ["CX","Product"]}},
    {{"trigger_metric": "error_rate", "threshold": "above 0.5%", "action": "disable_feature_flags", "notify": ["Engineering"]}}
  ],
  "monitoring_dashboard": {{
    "metrics": ["CVR", "AOV", "RPV", "Stockout Rate", "SLA %", "Error Rate", "Care Contacts"],
    "alert_thresholds": {{}}
  }},
  "timeline": [
    {{"phase": "Validation", "week": 1, "traffic_pct": 10, "action": "Monitor KPIs, validate feature flags", "owner": "Engineering"}},
    {{"phase": "Ramp", "week": 2, "traffic_pct": 30, "action": "Expand traffic, notify marketing", "owner": "Product"}},
    {{"phase": "Scale", "week": 3, "traffic_pct": 50, "action": "Full segment rollout", "owner": "Product"}},
    {{"phase": "Full", "week": 4, "traffic_pct": 100, "action": "Complete rollout or hold for review", "owner": "Product"}}
  ]
}}
No markdown. No explanation.
"""


async def generate_rollout(sim: Simulation, winner: Result, winner_scenario: Scenario | None) -> dict:
    from app.agents.gemini_client import generate_json

    scenario_name = winner_scenario.name if winner_scenario else "Unknown"
    scenario_json = json.dumps({
        "storefront": winner_scenario.storefront if winner_scenario else {},
        "marketing": winner_scenario.marketing if winner_scenario else {},
        "ops": winner_scenario.ops if winner_scenario else {},
    }, indent=2)

    prompt = ROLLOUT_PROMPT.format(
        scenario_name=scenario_name,
        scenario_json=scenario_json,
        conversion_lift=float(winner.conversion_lift),
        rpv_lift=float(winner.rpv_lift),
        margin_impact=float(winner.margin_impact),
        confidence=float(winner.confidence),
        win_probability=float(winner.win_probability or 0),
    )

    return await generate_json(prompt)
