"""
Step 3 — Scenario Generation Agent.
Generates exactly 3 scenarios: Base, Optimistic, Pessimistic.
"""
from app.models.simulation import Simulation

SCENARIO_PROMPT = """
You are an e-commerce simulation architect at Albertsons.

Given the UseCaseBrief below, generate exactly 3 Monte Carlo simulation scenarios.

UseCaseBrief:
{brief_json}

Scenario definitions:
- Base: most likely outcome based on historical Albertsons patterns (status-quo with incremental improvement)
- Optimistic: 90th percentile upside scenario with favorable tailwinds
- Pessimistic: 10th percentile downside scenario as a stress test

For each scenario output:
- name: exactly "Base", "Optimistic", or "Pessimistic"
- storefront: {{"layout": "...", "merchandising": "...", "search_algo": "...", "personalization": "..."}}
- marketing: {{"email_cadence": "...", "push_enabled": true/false, "promo_type": "...", "discount_pct": 0-30}}
- ops: {{"fulfillment_mode": "...", "inventory_buffer_pct": 10-30, "carrier_mix": "..."}}
- notes: 2-3 sentence narrative explanation

Return ONLY a JSON array of exactly 3 scenario objects. No markdown. No explanation.
"""


async def generate_scenarios(sim: Simulation) -> list[dict]:
    import json
    from app.agents.gemini_client import generate_json

    brief_json = json.dumps(sim.use_case_brief, indent=2)
    prompt = SCENARIO_PROMPT.format(brief_json=brief_json)
    result = await generate_json(prompt)

    # Normalize: result may be a list directly or wrapped in {"scenarios": [...]}
    if isinstance(result, list):
        scenarios = result
    else:
        scenarios = result.get("scenarios", [])

    # Ensure exactly 3 with correct names
    names_seen = {sc.get("name") for sc in scenarios}
    required = ["Base", "Optimistic", "Pessimistic"]
    for name in required:
        if name not in names_seen:
            scenarios.append({
                "name": name,
                "storefront": {"layout": "standard", "merchandising": "default", "search_algo": "default", "personalization": "off"},
                "marketing": {"email_cadence": "weekly", "push_enabled": False, "promo_type": "none", "discount_pct": 0},
                "ops": {"fulfillment_mode": "standard", "inventory_buffer_pct": 15, "carrier_mix": "balanced"},
                "notes": f"{name} scenario with default parameters.",
            })

    return [sc for sc in scenarios if sc.get("name") in required][:3]
