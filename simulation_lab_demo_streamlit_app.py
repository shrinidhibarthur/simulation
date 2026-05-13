# Streamlit Demo: Project Catalyst – VS Simulation Lab (Single-File MVP)
# ---------------------------------------------------------------
# How to run locally:
# 1) pip install streamlit pandas numpy plotly pydantic
# 2) python -m streamlit run simulation_lab_demo_streamlit_app.py
#
# Note: This is a self-contained demo that simulates the Lab flow end-to-end
# without external systems. Replace the stubbed functions with real integrations
# (Adobe/EDDL, orders, pricing, CRM, OMS/WMS, carriers) for production.

import json
import random
import hashlib
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from pydantic import BaseModel, Field

# (Optional) Use the uploaded infographic if available for a hero image.
HERO_IMAGE_PATH = "/mnt/data/67F970B6-26E9-4251-986A-14E24D8D3DBA.png"

# -------------------- Helpers & Models --------------------
class UseCaseBrief(BaseModel):
    title: str
    domain: str
    goals: list[str]
    kpis: list[str]
    constraints: list[str]
    audience: list[str]
    timeline: str
    risk_limits: list[str]
    datasets: list[str]

class Scenario(BaseModel):
    name: str
    storefront: dict = Field(default_factory=dict)
    marketing: dict = Field(default_factory=dict)
    ops: dict = Field(default_factory=dict)
    notes: str = ""

class SimResult(BaseModel):
    scenario: str
    conversion_lift: float  # percentage points
    aov_delta: float        # currency delta
    rpv_lift: float         # %
    margin_impact: float    # %
    stockout_change: float  # %
    markdown_change: float  # %
    cost_to_serve_delta: float  # currency delta
    sla_risk: str          # Low/Med/High
    confidence: float      # 0..1

# seeded randomness for reproducibility by request text
def seeded_rng(seed_text: str):
    seed = int(hashlib.md5(seed_text.encode()).hexdigest(), 16) % (2**32 - 1)
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    return rng, np_rng

# simple domain detector
def detect_domain(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["plp", "pdp", "layout", "recommend", "checkout", "badge"]):
        return "Storefront & App UX"
    if any(k in t for k in ["promo", "campaign", "offer", "discount"]):
        return "Marketing & Promotions"
    if any(k in t for k in ["inventory", "fulfillment", "carrier", "sla", "stockout", "dc"]):
        return "Supply Chain & Fulfillment"
    return "Cross-Functional"

# scenario generator (stub)
def generate_scenarios(text: str) -> list[Scenario]:
    dom = detect_domain(text)
    base = [
        Scenario(
            name="Option A",
            storefront={"layout": "New grid", "recs": "Personalized", "badges": True},
            marketing={"offer": "20% off", "banner": True, "cadence": "Burst"},
            ops={"dc_mix": "Baseline", "carrier": "Preferred", "free_ship_threshold": 60},
            notes=f"Balanced bundle for {dom}"
        ),
        Scenario(
            name="Option B",
            storefront={"layout": "Current", "recs": "Hybrid", "badges": False},
            marketing={"offer": "Free shipping", "banner": False, "cadence": "Always-on"},
            ops={"dc_mix": "Speed-leaning", "carrier": "Fastest", "free_ship_threshold": 75},
            notes="Optimized for margin + SLA"
        ),
        Scenario(
            name="Option C",
            storefront={"layout": "New editorial", "recs": "Trending", "badges": True},
            marketing={"offer": "Buy 2 Save 10%", "banner": True, "cadence": "Weekend"},
            ops={"dc_mix": "Cost-leaning", "carrier": "Economy", "free_ship_threshold": 50},
            notes="Optimized for traffic and AOV"
        ),
    ]
    return base

# fake simulator
def simulate(request_text: str, scenarios: list[Scenario], mvt: bool, budget: int, sla_limit_days: float, preview: dict | None = None):
    rng, np_rng = seeded_rng(request_text + str(mvt) + str(budget) + str(sla_limit_days))
    results: list[SimResult] = []
    for sc in scenarios:
        # apply preview overrides without mutating originals
        eff_storefront = dict(sc.storefront)
        eff_marketing = dict(sc.marketing)
        eff_ops = dict(sc.ops)
        if preview:
            if preview.get("layout"):
                eff_storefront["layout"] = preview["layout"]
            if preview.get("badges") is not None:
                eff_storefront["badges"] = bool(preview["badges"])
            if preview.get("banner") is not None:
                eff_marketing["banner"] = bool(preview["banner"])
        # create some pseudo relationships
        layout_factor = {"New grid": 1.04, "Current": 1.0, "New editorial": 1.06}.get(eff_storefront.get("layout"), 1.0)
        recs_factor = {"Personalized": 1.03, "Hybrid": 1.02, "Trending": 1.01}.get(eff_storefront.get("recs"), 1.0)
        offer_factor = {"20% off": 1.05, "Free shipping": 1.03, "Buy 2 Save 10%": 1.02}.get(eff_marketing.get("offer"), 1.0)
        carrier_factor = {"Preferred": 1.0, "Fastest": 1.01, "Economy": 0.98}.get(eff_ops.get("carrier"), 1.0)

        base_cvr = 0.025  # 2.5%
        cvr = base_cvr * layout_factor * recs_factor * offer_factor * carrier_factor
        cvr_lift_pp = (cvr - base_cvr) * 100  # percentage points

        base_aov = 80
        aov = base_aov * (1 + (recs_factor - 1) + (0.01 if eff_marketing.get("banner") else 0))
        aov_delta = aov - base_aov

        rpv_lift = (cvr * aov) / (base_cvr * base_aov) - 1
        margin_impact = -0.6 if sc.marketing.get("offer") == "20% off" else (0.2 if sc.marketing.get("offer") == "Free shipping" else 0.0)

        stockout_change = -0.05 if eff_ops.get("dc_mix") == "Speed-leaning" else (0.03 if eff_ops.get("dc_mix") == "Cost-leaning" else -0.01)
        markdown_change = -0.02 if eff_storefront.get("badges") else 0.0
        cost_to_serve_delta = -0.2 if eff_ops.get("carrier") == "Economy" else (0.5 if eff_ops.get("carrier") == "Fastest" else 0.0)

        # SLA risk rises if carrier is Economy or free_ship_threshold is low relative to sla_limit
        sla_risk_score = 0
        sla_risk_score += 1 if eff_ops.get("carrier") == "Economy" else 0
        sla_risk_score += 1 if eff_ops.get("free_ship_threshold", 60) < 55 else 0
        sla_risk = "High" if sla_risk_score >= 2 else ("Medium" if sla_risk_score == 1 else "Low")

        # multivariate adds variance but can increase confidence if budget high
        noise = np_rng.normal(0, 0.01 if mvt else 0.008)
        rpv_lift = rpv_lift + noise
        confidence = min(0.95, 0.7 + (budget / 100_000) + (0.05 if mvt else 0.0) - (0.05 if sla_risk == "High" else 0.0))
        # component tag risk: penalize beta tags from preview
        if preview:
            tag_penalty = 0.0
            for tag in [preview.get("web_tag"), preview.get("ios_tag"), preview.get("android_tag")]:
                if tag and "beta" in tag.lower():
                    tag_penalty += 0.03
            confidence = max(0.5, confidence - tag_penalty)
        confidence = max(0.5, confidence)

        results.append(SimResult(
            scenario=sc.name,
            conversion_lift=cvr_lift_pp,
            aov_delta=aov_delta,
            rpv_lift=rpv_lift,
            margin_impact=margin_impact,
            stockout_change=stockout_change,
            markdown_change=markdown_change,
            cost_to_serve_delta=cost_to_serve_delta,
            sla_risk=sla_risk,
            confidence=confidence
        ))
    return results

# --------------- Streamlit UI ---------------
st.set_page_config(page_title="VS Simulation Lab – Demo", layout="wide")

with st.sidebar:
    st.title("VS Simulation Lab – Demo")
    st.caption("Project Catalyst · Single-file MVP")
    nav = st.radio("Navigate", [
        "0) New Request",
        "1) Clarifier",
        "2) Scenario Options",
        "2b) Visual Preview",
        "3) Create Simulations",
        "4) Data & Assumptions",
        "5) Execute",
        "6) Decision Dashboard",
        "7) Rollout Plan",
        "8) Simulation Ledger",
        "9) Post-Decision Learning",
    ])
    st.markdown("---")
    st.markdown("**Demo Tips**\n- Use the example request.\n- Toggle MVT & budget.\n- Run, pick a winner, export plan.")

# session state
if "request_text" not in st.session_state:
    st.session_state.request_text = "Test new PLP layout + 20% off promo for US traffic. Goal: lift conversion and protect margin & SLA."
if "brief" not in st.session_state:
    st.session_state.brief = None
if "scenarios" not in st.session_state:
    st.session_state.scenarios = []
if "results_df" not in st.session_state:
    st.session_state.results_df = None
if "rollout" not in st.session_state:
    st.session_state.rollout = None
if "ledger" not in st.session_state:
    st.session_state.ledger = []

# hero
try:
    st.image(HERO_IMAGE_PATH, use_column_width=True)
except Exception:
    pass

st.markdown("### Simulation Lab: The Digital Wind Tunnel for VS&Co Decisions")

# 0) New Request
if nav == "0) New Request":
    st.subheader("0) Entry & Context")
    st.write("Describe your idea in freeform text. The Lab will ask smart follow-ups.")
    txt = st.text_area("New Simulation Request", st.session_state.request_text, height=120)
    st.session_state.request_text = txt
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Detect Domain & Draft Brief"):
            domain = detect_domain(txt)
            brief = UseCaseBrief(
                title="Draft – " + txt[:40] + ("…" if len(txt) > 40 else ""),
                domain=domain,
                goals=["Lift conversion", "Protect margin", "Meet SLAs"],
                kpis=["CVR", "AOV", "RPV", "Margin", "SLA risk"],
                constraints=["Budget cap", "Delivery time not to increase"],
                audience=["US", "Web", "App"],
                timeline="Next 2–4 weeks",
                risk_limits=["Auto-rollback if CVR -2%", "Flag if SLA=High"],
                datasets=["Adobe/EDDL", "Orders", "Pricing/Promo", "CRM", "Inventory", "OMS/WMS", "Carriers"]
            )
            st.session_state.brief = brief
            st.success(f"Draft brief created for domain: {domain}")
    with col2:
        st.info("Tip: Include hints like PLP/PDP/promo/inventory to guide domain detection.")
    if st.session_state.brief:
        st.json(st.session_state.brief.model_dump())

# 1) Clarifier
elif nav == "1) Clarifier":
    st.subheader("1) Understanding the Use Case (AI Clarifier)")
    if not st.session_state.brief:
        st.warning("Create a draft brief first in step 0.")
    else:
        b: UseCaseBrief = st.session_state.brief
        b.goals = st.multiselect("Goals", ["Lift conversion", "Grow AOV", "Improve RPV", "Protect margin", "Reduce stockouts", "Meet SLAs"], default=b.goals)
        b.kpis = st.multiselect("KPIs", ["CVR", "AOV", "RPV", "Margin", "Stockouts", "Markdown %", "Cost-to-serve", "SLA risk"], default=b.kpis)
        b.constraints = st.multiselect("Constraints", ["Budget cap", "No SLA increase", "No additional engineering", "Promo guardrails"], default=b.constraints)
        b.audience = st.multiselect("Audience/Regions", ["US", "CA", "UK", "Web", "App (iOS)", "App (Android)"], default=b.audience)
        b.timeline = st.text_input("Timeline", value=b.timeline)
        b.risk_limits = st.multiselect("Risk Limits", ["Auto-rollback if CVR -2%", "Alert if SLA=High", "Pause if margin -1%"], default=b.risk_limits)
        st.session_state.brief = b
        st.success("Use-Case Brief updated.")
        st.json(b.model_dump())

# 2) Scenario Options
elif nav == "2) Scenario Options":
    st.subheader("2) Recommendation Draft (Before Build)")
    if not st.session_state.brief:
        st.warning("Complete steps 0–1 first.")
    else:
        if not st.session_state.scenarios:
            st.session_state.scenarios = generate_scenarios(st.session_state.request_text)
        # editable grid
        edited = []
        for sc in st.session_state.scenarios:
            with st.expander(f"Edit {sc.name}"):
                sc.storefront["layout"] = st.selectbox(f"{sc.name} – Layout", ["Current", "New grid", "New editorial"], index=["Current", "New grid", "New editorial"].index(sc.storefront.get("layout", "Current")))
                sc.storefront["recs"] = st.selectbox(f"{sc.name} – Recs", ["Hybrid", "Personalized", "Trending"], index=["Hybrid", "Personalized", "Trending"].index(sc.storefront.get("recs", "Hybrid")))
                sc.storefront["badges"] = st.checkbox(f"{sc.name} – PLP Badges", value=sc.storefront.get("badges", False))
                sc.marketing["offer"] = st.selectbox(f"{sc.name} – Offer", ["20% off", "Free shipping", "Buy 2 Save 10%"], index=["20% off", "Free shipping", "Buy 2 Save 10%"].index(sc.marketing.get("offer", "20% off")))
                sc.marketing["banner"] = st.checkbox(f"{sc.name} – Banner", value=sc.marketing.get("banner", False))
                sc.marketing["cadence"] = st.selectbox(f"{sc.name} – Cadence", ["Burst", "Always-on", "Weekend"], index=["Burst", "Always-on", "Weekend"].index(sc.marketing.get("cadence", "Burst")))
                sc.ops["dc_mix"] = st.selectbox(f"{sc.name} – DC Mix", ["Baseline", "Speed-leaning", "Cost-leaning"], index=["Baseline", "Speed-leaning", "Cost-leaning"].index(sc.ops.get("dc_mix", "Baseline")))
                sc.ops["carrier"] = st.selectbox(f"{sc.name} – Carrier", ["Preferred", "Fastest", "Economy"], index=["Preferred", "Fastest", "Economy"].index(sc.ops.get("carrier", "Preferred")))
                sc.ops["free_ship_threshold"] = st.slider(f"{sc.name} – Free Ship Threshold", 30, 100, value=int(sc.ops.get("free_ship_threshold", 60)), step=5)
                sc.notes = st.text_input(f"{sc.name} – Notes", value=sc.notes)
            edited.append(sc)
        st.session_state.scenarios = edited
        st.success("Scenario bundles ready.")

# 2b) Visual Preview
elif nav == "2b) Visual Preview":
    st.subheader("2b) Visual Preview – No‑code Overlay & Versioned Components")
    st.caption("Quickly preview customer-facing changes (e.g., badges, banners, layouts) without touching app code, or switch to version‑accurate component previews.")

    colA, colB = st.columns(2)
    with colA:
        st.markdown("**No‑code Overlay (Web/App)**")
        show_badge = st.toggle("Show Promotional Badge Overlay", True)
        show_banner = st.toggle("Show Top Banner", False)
        layout_choice = st.selectbox("Layout", ["Current", "New grid", "New editorial"], index=1)
        st.write(":sparkles: This overlay is for ideation only; no production code changes.")
    with colB:
        st.markdown("**Versioned Component Preview**")
        web_ver = st.selectbox("Web PLPCard component tag", ["web/plp-card@1.12.0", "web/plp-card@1.13.2", "web/plp-card@2.0.0-beta"], index=1)
        ios_ver = st.selectbox("iOS ProductCell tag", ["ios/ProductCell@2.1.0", "ios/ProductCell@2.2.3"], index=0)
        and_ver = st.selectbox("Android ProductTile tag", ["android/ProductTile@3.0.0", "android/ProductTile@3.1.1"], index=1)
        st.write("These tags mimic pulling built artifacts for pixel‑true previews.")

    st.markdown("---")

    # Render a lightweight PLP grid preview
    st.markdown("**PLP Grid Preview (demo)**")
    products = [
        {"name": "Lightly Lined Bra", "price": 49.5},
        {"name": "Push‑Up Bra", "price": 59.5},
        {"name": "Seamless Panty", "price": 12.5},
        {"name": "Lace Bralette", "price": 39.5},
        {"name": "Sports Bra", "price": 54.5},
        {"name": "Satin Slip", "price": 69.5},
        {"name": "Cotton Hipster", "price": 10.5},
        {"name": "Wireless Bra", "price": 44.5},
    ]

    def card(p):
        badge_html = """
            <div style='position:absolute; top:6px; left:6px; background:#111; color:#fff; font-size:11px; padding:2px 6px; border-radius:6px;'>
                PROMO
            </div>
        """ if show_badge else ""
        banner_html = """
            <div style='width:100%; background:#ffd5e5; padding:6px 8px; border-radius:8px; text-align:center; font-weight:600; margin-bottom:6px;'>
                Holiday Savings – This Weekend Only
            </div>
        """ if show_banner else ""
        card_html = f"""
            <div style='position:relative; border:1px solid #eee; border-radius:12px; padding:10px; height:170px;'>
                {badge_html}
                <div style='height:90px; background:#f7f7f7; border-radius:8px; display:flex; align-items:center; justify-content:center;'>
                    <span style='color:#bbb'>IMG</span>
                </div>
                <div style='margin-top:8px; font-weight:600'>{p['name']}</div>
                <div style='font-size:13px'>$ {p['price']:.2f}</div>
            </div>
        """
        return banner_html + card_html

    # layout columns based on layout_choice
    cols_per_row = 3 if layout_choice == "Current" else (4 if layout_choice == "New grid" else 2)
    rows = [products[i:i+cols_per_row] for i in range(0, len(products), cols_per_row)]
    for row in rows:
        cols = st.columns(len(row))
        for col, prod in zip(cols, row):
            with col:
                st.markdown(card(prod), unsafe_allow_html=True)
    # Persist preview overrides for simulation scoring
    st.session_state.preview = {
        "layout": layout_choice,
        "badges": show_badge,
        "banner": show_banner,
        "web_tag": web_ver,
        "ios_tag": ios_ver,
        "android_tag": and_ver,
    }
    st.success("Visual Preview overrides saved for simulation scoring.")
    st.info(
        f"Previewing with component tags → Web: {web_ver} · iOS: {ios_ver} · Android: {and_ver}"
    )

# 3) Create Simulations
elif nav == "3) Create Simulations":
    st.subheader("3) Simulate Scenarios (Run Engine)")
    if not st.session_state.scenarios:
        st.warning("Complete steps 0–2 first.")
    else:
        st.markdown("**Configure Simulation:**")
        mvt = st.toggle("Enable Multivariate Testing (MVT)", True)
        budget = st.slider("Test Budget ($)", 10000, 300000, 120000, step=5000)
        sla_limit = st.slider("Max SLA (Days)", 2.0, 10.0, 5.0, step=0.5)

        # Quick Patch B: Add weights for preview controls
        st.markdown("**Weights: How strong are preview choices?**")
        w1, w2, w3 = st.columns(3)
        with w1:
            w_badge = st.slider("Badge → CVR (pp)", 0.0, 2.0, 0.3, 0.1)
        with w2:
            w_banner = st.slider("Banner → AOV (%)", 0.0, 5.0, 0.5, 0.1)
        with w3:
            w_layout = st.slider("Layout → RPV (%)", 0.0, 5.0, 1.0, 0.1)
        # Show active Visual Preview overrides
        pv = st.session_state.get("preview", {})
        if pv:
            st.caption(
                f"Using Visual Preview overrides → Layout: {pv.get('layout')} · "
                f"Badges: {pv.get('badges')} · Banner: {pv.get('banner')} · "
                f"Tags: {pv.get('web_tag')}, {pv.get('ios_tag')}, {pv.get('android_tag')}"
            )

        run_btn = st.button("RUN Simulation")
        if run_btn:
            res = simulate(st.session_state.request_text, st.session_state.scenarios, mvt, budget, sla_limit, preview=pv)
            df = pd.DataFrame([r.model_dump() for r in res])

            # Quick Patch C: Apply Visual Preview weights to metrics and add audit columns
            if pv:
                # badges add CVR (pp)
                if pv.get("badges"):
                    df["conversion_lift"] = df["conversion_lift"] + w_badge
                # banner increases AOV (%) → approximate via base AOV ~80 in simulator
                if pv.get("banner"):
                    df["aov_delta"] = df["aov_delta"] + (w_banner / 100.0) * 80.0
                # layout influences RPV (%). Stronger for new layouts.
                layout_boost = 0.0
                if pv.get("layout") == "New grid":
                    layout_boost = w_layout / 100.0
                elif pv.get("layout") == "New editorial":
                    layout_boost = (w_layout + 0.5) / 100.0
                if layout_boost > 0:
                    df["rpv_lift"] = df["rpv_lift"] * (1 + layout_boost)
                # beta tags reduce confidence slightly
                tags = [pv.get("web_tag", ""), pv.get("ios_tag", ""), pv.get("android_tag", "")]
                if any("beta" in str(t).lower() for t in tags):
                    df["confidence"] = (df["confidence"] - 0.05).clip(lower=0.5)
                # carry audit columns
                df["preview_layout"]  = pv.get("layout")
                df["preview_badges"]  = bool(pv.get("badges"))
                df["preview_banner"]  = bool(pv.get("banner"))
                df["preview_tags"]    = ", ".join([str(t) for t in tags])
                df["w_badge_pp"]      = w_badge
                df["w_banner_pct"]    = w_banner
                df["w_layout_pct"]    = w_layout

            # Add a composite score
            df["score"] = (
                df["confidence"] * 0.25 +
                df["rpv_lift"] * 0.3 +
                df["conversion_lift"] * 0.2 +
                df["margin_impact"] * 0.15 +
                df.apply(lambda r: 0.05 if r["sla_risk"] == "Low" else (-0.05 if r["sla_risk"] == "High" else 0), axis=1)
            )
            df = df.sort_values("score", ascending=False)
            st.session_state.results_df = df
            # Ledger entry
            st.session_state.ledger.append({
                "timestamp": datetime.utcnow().isoformat(),
                "params": dict(request=st.session_state.request_text, mvt=mvt, budget=budget, sla_limit=sla_limit, preview=pv),
                "results": df.to_dict(orient="records"),
            })
            st.success("Simulation run complete. Results ready.")
            st.dataframe(df, use_container_width=True)

# 4) Data & Assumptions
elif nav == "4) Data & Assumptions":
    st.subheader("4) Data & Assumptions Lock")
    sources = st.multiselect("Connected Data Sources", ["Adobe/EDDL", "Orders", "Pricing/Promo", "CRM", "Inventory", "OMS/WMS", "Carrier SLAs", "App Analytics"], default=["Adobe/EDDL", "Orders", "Pricing/Promo", "Inventory", "OMS/WMS"])
    st.checkbox("Data Quality Check: Passed", value=True)
    st.checkbox("Bias/Parity Check: Passed", value=True)
    st.checkbox("Freshness < 24h", value=True)
    st.text_input("Assumption Notes", value="Demand elasticity range 0.6–1.1; no SLA degradation allowed")
    st.success("Snapshot locked (demo).")

# 5) Execute
elif nav == "5) Execute":
    st.subheader("5) Execute Simulations (MVT Included)")
    st.write("Run from step 3 to populate results.")
    if st.session_state.results_df is not None:
        st.dataframe(st.session_state.results_df, use_container_width=True)
        fig = px.bar(st.session_state.results_df, x="scenario", y="score", title="Composite Score by Scenario")
        st.plotly_chart(fig, use_container_width=True)

# 6) Decision Dashboard
elif nav == "6) Decision Dashboard":
    st.subheader("6) Results & Recommendations")
    if st.session_state.results_df is None:
        st.warning("No results yet. Go to step 3 and RUN.")
    else:
        df = st.session_state.results_df
        top = df.iloc[0]
        st.success(f"Recommended: {top['scenario']} (confidence {top['confidence']:.2f})")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Top Scenarios by Score")
            # Patch D: Show preview and weight columns if present
            cols = ["scenario","score","confidence","sla_risk","rpv_lift","conversion_lift","margin_impact"]
            extra_cols = [c for c in ["preview_layout","preview_badges","preview_banner","preview_tags","w_badge_pp","w_banner_pct","w_layout_pct"] if c in df.columns]
            st.dataframe(df[cols + extra_cols], use_container_width=True)
        with c2:
            fig = px.scatter(df, x="rpv_lift", y="margin_impact", color="sla_risk", size="confidence", hover_name="scenario", title="Trade-offs: RPV vs Margin")
            st.plotly_chart(fig, use_container_width=True)

# 7) Rollout Plan
elif nav == "7) Rollout Plan":
    st.subheader("7) What to Ship (Guardrailed Plan)")
    if st.session_state.results_df is None:
        st.warning("Run a simulation first.")
    else:
        choice = st.selectbox("Choose Scenario to Roll Out", st.session_state.results_df["scenario"].tolist())
        holdout = st.slider("Holdout %", 0, 20, 10)
        regions = st.multiselect("Targets", ["US Web", "US iOS", "US Android", "CA Web"], default=["US Web", "US iOS", "US Android"])
        thresholds = {
            "rollback_if_cvr_drop_pp": st.number_input("Rollback if CVR drop (pp)", value=2.0, step=0.5),
            "alert_if_sla": st.selectbox("Alert if SLA risk becomes", ["Medium", "High"], index=1)
        }
        plan = {
            "scenario": choice,
            "feature_flags": {"targets": regions, "holdout_pct": holdout},
            "promo_budget": "As configured in scenario",
            "inventory_guidance": "Per DC mix selection",
            "monitoring": thresholds,
            "export": ["Jira", "LaunchDarkly", "Adobe", "OMS"],
        }
        st.session_state.rollout = plan
        st.json(plan)
        st.download_button("Download Rollout Plan (JSON)", data=json.dumps(plan, indent=2), file_name="rollout_plan.json")

# 8) Simulation Ledger
elif nav == "8) Simulation Ledger":
    st.subheader("8) Traceability & Audit")
    if not st.session_state.ledger:
        st.info("No entries yet. Run a simulation in step 3.")
    else:
        df = pd.DataFrame(st.session_state.ledger)
        st.dataframe(df, use_container_width=True)
        st.download_button("Export Ledger (JSON)", data=json.dumps(st.session_state.ledger, indent=2), file_name="simulation_ledger.json")

# 9) Post-Decision Learning
elif nav == "9) Post-Decision Learning":
    st.subheader("9) Post-Decision Learning")
    st.write("Enter actuals to calibrate your simulator.")
    col1, col2, col3 = st.columns(3)
    with col1:
        actual_cvr_delta = st.number_input("Actual CVR delta (pp)", value=1.0, step=0.1)
    with col2:
        actual_aov_delta = st.number_input("Actual AOV delta ($)", value=0.0, step=1.0)
    with col3:
        actual_rpv_lift = st.number_input("Actual RPV lift (%)", value=1.0, step=0.1)
    if st.button("Compare vs Last Recommendation"):
        if st.session_state.results_df is None:
            st.warning("Run a simulation first.")
        else:
            top = st.session_state.results_df.iloc[0]
            report = {
                "recommended": top["scenario"],
                "pred_vs_actual": {
                    "CVR_pp": {"pred": round(float(top["conversion_lift"]), 3), "actual": actual_cvr_delta, "error": round(actual_cvr_delta - float(top["conversion_lift"]), 3)},
                    "AOV_delta": {"pred": round(float(top["aov_delta"]), 2), "actual": actual_aov_delta, "error": round(actual_aov_delta - float(top["aov_delta"]), 2)},
                    "RPV_%": {"pred": round(float(top["rpv_lift"] * 100), 2), "actual": actual_rpv_lift, "error": round(actual_rpv_lift - float(top["rpv_lift"] * 100), 2)},
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            st.json(report)
            st.success("Calibration complete (demo).")
