"""
Step 2 — AI Clarifier Agent.
First call: returns 3-5 clarifying questions.
Subsequent calls (with answers): returns UseCaseBrief + complete=True.
"""
from app.models.simulation import Simulation

SYSTEM_CONTEXT = """
You are an e-commerce strategy analyst at Albertsons.
Your job is to help product teams structure A/B test hypotheses.

Albertsons baseline KPIs:
- Conversion rate (CVR): 2.8%
- Average Order Value (AOV): $87.50
- Revenue Per Visit (RPV): $2.45
- Gross Margin: 42.1%

Domains: pricing, inventory, promotions, checkout UX, search, recommendations, fulfillment.
"""

QUESTIONS_PROMPT = """
{context}

A product manager submitted this test request:
"{request_text}"

Generate 3 to 5 concise clarifying questions to better understand:
- The specific hypothesis and expected outcome
- Which customer segment is targeted
- What data or baseline metrics are available
- Any constraints (budget, timeline, technical)
- KPIs to measure success

Return ONLY a JSON object with this schema:
{{"questions": ["question 1", "question 2", ...]}}
No markdown. No explanation.
"""

BRIEF_PROMPT = """
{context}

A product manager submitted this test request:
"{request_text}"

They answered the following clarifying questions:
{qa_text}

Generate a structured UseCaseBrief for this simulation. Return ONLY this JSON:
{{
  "title": "short title of the test",
  "domain": "one of: Storefront & App UX | Marketing & Promotions | Supply Chain & Fulfillment | Pricing | Cross-Functional",
  "goals": ["goal 1", "goal 2"],
  "kpis": ["CVR", "AOV", "RPV", "margin_impact"],
  "constraints": ["constraint 1"],
  "audience": "customer segment description",
  "timeline": "e.g. 2 weeks",
  "risk_limits": {{"max_margin_decline": "-2%", "max_stockout_increase": "5%"}},
  "datasets": ["Adobe Analytics", "OMS", "CRM"]
}}
No markdown. No explanation.
"""


async def run_clarifier(sim: Simulation, answers: dict[str, str] | None) -> dict:
    from app.agents.gemini_client import generate_json

    if not answers:
        # First call — generate questions
        prompt = QUESTIONS_PROMPT.format(context=SYSTEM_CONTEXT, request_text=sim.request_text)
        result = await generate_json(prompt)
        questions = result.get("questions", [])
        return {"questions": questions, "use_case_brief": None, "complete": False}

    # Subsequent call — synthesize brief
    qa_text = "\n".join(f"Q: {q}\nA: {a}" for q, a in answers.items())
    prompt = BRIEF_PROMPT.format(
        context=SYSTEM_CONTEXT,
        request_text=sim.request_text,
        qa_text=qa_text,
    )
    brief = await generate_json(prompt)
    return {"questions": [], "use_case_brief": brief, "complete": True}
