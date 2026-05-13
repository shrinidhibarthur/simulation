
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Simulation Lab - A VS&Co Digital Wind Tunnel",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: #1f1f1f;
        padding: 20px;
    }
    .sub-header {
        font-size: 24px;
        text-align: center;
        color: #666;
        padding-bottom: 30px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .scenario-card {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF1493;
        color: white;
        font-weight: bold;
        padding: 15px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'request_text' not in st.session_state:
    st.session_state.request_text = ""
if 'kpis_selected' not in st.session_state:
    st.session_state.kpis_selected = []
if 'selected_scenario' not in st.session_state:
    st.session_state.selected_scenario = None
if 'simulation_complete' not in st.session_state:
    st.session_state.simulation_complete = False

# Sidebar navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/FF1493/FFFFFF?text=VS%26Co", use_container_width=True)
    st.title("Navigation")

    steps = [
        "🏠 Home",
        "📝 New Request",
        "❓ AI Clarifier",
        "📊 Scenarios",
        "⚙️ Configuration",
        "🔒 Data Lock",
        "🚀 Run Simulation",
        "📈 Results",
        "🎯 Rollout Plan",
        "📚 Ledger"
    ]

    selected_step = st.radio("Demo Steps", steps, index=st.session_state.step)
    st.session_state.step = steps.index(selected_step)

    st.markdown("---")
    st.info("**Simulation Lab v2.0**\n\nThe Digital Wind Tunnel for VS&Co Decisions")

# Main content based on selected step
if st.session_state.step == 0:
    # Step 1: Title & Problem
    st.markdown('<div class="main-header">🔬 Simulation Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">The Digital Wind Tunnel For VS&Co Decisions</div>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### What if Victoria's Secret could test every idea before a single customer sees it?

        **The Challenge:**
        - Real customers see half-baked experiences
        - Weeks spent wiring dashboards and debating numbers
        - SEVs, stockouts, and margin surprises lead to war-rooms
        - Rising costs require faster, smarter decisions

        **The Solution:**
        Simulation Lab bridges imagination and implementation – a governed space where every idea, 
        change, or campaign is safely tested, optimized, and proven before it touches customers, 
        associates, operations, or revenue.
        """)

    st.markdown("---")

    # Key Features Section
    st.markdown("### 🎯 Key Features & Capabilities")

    col1, col2 = st.columns(2)

    with col1:
        with st.container():
            st.markdown("**🚀 Request to Results in Hours**")
            st.caption("No rigid forms or templates. The Lab understands context and asks the right questions.")
            st.markdown("""
            • **Freeform Request Entry** - Describe ideas in plain English  
            • **AI-Powered Clarification** - Smart follow-up questions to refine scope  
            • **Auto-Generated Use-Case Brief** - Goals, KPIs, constraints documented automatically  
            """)

        st.markdown("---")

        with st.container():
            st.markdown("**📊 Intelligent Scenario Generation**")
            st.caption("Scenarios span the entire customer journey with built-in feasibility checks.")
            st.markdown("""
            • **Cross-Functional Bundles** - Storefront + Marketing + Operations scenarios  
            • **Guardrailed Options** - Only simulatable levers, no hallucinations  
            • **Bias-Checked** - Validated across segments, geos, and channels  
            """)

        st.markdown("---")

        with st.container():
            st.markdown("**⚡ Parallel Simulation Engine**")
            st.caption("Simulates 400K+ orders in minutes with full conversion, margin, and SLA impact.")
            st.markdown("""
            • **Multi-Scenario Testing** - Run 8+ scenarios simultaneously  
            • **Multivariate Support (MVT)** - Test variable combinations  
            • **Real-Time Telemetry** - Live KPI tracking during runs  
            """)

        st.markdown("---")

        with st.container():
            st.markdown("**🔒 Data Governance & Quality**")
            st.caption("Every simulation locks data assumptions with audit-grade traceability.")
            st.markdown("""
            • **7+ Data Source Integration** - Adobe/EDDL, Orders, Inventory, OMS/WMS, Carriers  
            • **Quality & Freshness Checks** - Automated validation before every run  
            • **Bias Detection** - Cross-segment parity verification  
            """)

    with col2:
        with st.container():
            st.markdown("**📈 Decision Dashboard & Analytics**")
            st.caption("Visual analytics help you pick winners with confidence intervals and risk assessment.")
            st.markdown("""
            • **Scenario Rankings** - Scored by revenue, margin, confidence, and risk  
            • **Trade-Off Visualization** - Interactive charts for conversion vs margin  
            • **Historical Context** - Compare with 14+ past similar simulations  
            """)

        st.markdown("---")

        with st.container():
            st.markdown("**🎯 Automated Rollout Plans**")
            st.caption("Go from decision to production-ready deployment plan in one click.")
            st.markdown("""
            • **Feature Flag Configuration** - Target regions, channels, holdout groups  
            • **Auto-Rollback Rules** - CVR drops, SLA breaches, margin thresholds  
            • **One-Click Export** - Jira, LaunchDarkly, OMS, Promo Engine  
            """)

        st.markdown("---")

        with st.container():
            st.markdown("**📚 Complete Audit Trail**")
            st.caption("Finance, Legal, and Tech share one source of truth for every decision.")
            st.markdown("""
            • **Simulation Ledger** - Full request-to-rollout timeline  
            • **Configuration Hashes** - Reproducible with exact data snapshots  
            • **Assumption Tracking** - Every input documented and versioned  
            """)

        st.markdown("---")

        with st.container():
            st.markdown("**🔄 Continuous Learning**")
            st.caption("Each rollout makes the next simulation smarter and more accurate.")
            st.markdown("""
            • **Predicted vs Actual Tracking** - Post-launch comparison  
            • **Model Recalibration** - Improves accuracy over time  
            • **Pattern Library** - Learn from past simulations  
            """)

    st.markdown("---")

    # System Integration Architecture
    st.markdown("### 🏗️ System Integration Architecture")

    tab1, tab2, tab3 = st.tabs(["📊 Core Systems", "🤖 AI Architecture", "📋 Integration Summary"])

    with tab1:
        st.markdown("#### End-to-End Technical Architecture")

        st.code("""
┌─────────────────────────────────────────────────────────┐
│             SIMULATION LAB      
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│         API Gateway / Orchestration Layer               │
│  (FastAPI, Flask, or Microservices)                     │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────┼─────────┬─────────────┬──────────────┐
        │         │         │             │              │
   ┌────▼───┐ ┌──▼──┐ ┌────▼────┐ ┌──────▼─────┐ ┌─────▼─────┐
   │ Adobe  │ │ OMS │ │Inventory│ │  Carrier   │ │   CRM     │
   │Analytics│ │     │ │   WMS   │ │    APIs    │ │           │
   └────────┘ └─────┘ └─────────┘ └────────────┘ └───────────┘
        │         │         │             │              │
   ┌────▼─────────▼─────────▼─────────────▼──────────────▼────┐
   │         Data Warehouse (Snowflake/BigQuery)               │
   │  • Historical transactions                                │
   │  • Campaign results                                       │
   │  • Inventory turnover                                     │
   │  • Customer segments                                      │
   └───────────────────────────────────────────────────────────┘
                          │
                   ┌──────▼──────┐
                   │  Simulation  │
                   │    Engine    │
                   │  (Python/R)  │
                   └──────┬──────┘
                          │
                   ┌──────▼──────┐
                   │  ML Models   │
                   │  (Elasticity,│
                   │   Propensity)│
                   └─────────────┘
        """, language="text")

        st.markdown("---")

        # Integration categories in expandable sections
        col1, col2 = st.columns(2)

        with col1:
            with st.expander("🌐 Digital Experience & Analytics", expanded=False):
                st.markdown("""
                **Adobe Analytics / EDDL**
                - Real-time customer behavior tracking
                - Conversion funnels by device/geo
                - API: Adobe Analytics API 2.0, Adobe Launch webhooks

                **Google Cloud AI + Gemini LLM**
                - Conversational request entry & idea refinement
                - Product recommendations engine
                - Search optimization & personalization
                - ML-based recommendation lift predictions
                """)

            with st.expander("💰 Transactional & Order Data", expanded=False):
                st.markdown("""
                **Order Management System (OMS)**
                - Order history, AOV, discount redemption
                - REST APIs for order retrieval
                - Order volume by promo, payment success rates

                **Pricing & Promotion Engine**
                - Dynamic pricing, promo code management
                - Price elasticity by category
                - Margin impact per promo type
                """)

            with st.expander("📦 Inventory & Supply Chain", expanded=False):
                st.markdown("""
                **Inventory Management**
                - Real-time stock levels by SKU/DC
                - Stockout scenarios, markdown triggers
                - Replenishment cycles & lost sales correlation

                **Warehouse Management System (WMS)**
                - DC capacity constraints
                - Pick/pack/ship times, cost-to-serve
                - Fulfillment SLAs by carrier

                **Carrier & Shipping APIs**
                - UPS, FedEx, USPS integration
                - Real-time shipping costs & delivery estimates
                - SLA performance tracking
                """)

            with st.expander("👥 Customer & CRM Data", expanded=False):
                st.markdown("""
                **CRM System**
                - Customer segments (VIP, new, dormant)
                - Customer lifetime value by segment
                - Repeat purchase rates

                **App Analytics (iOS & Android)**
                - Firebase Analytics, Mixpanel
                - App vs web conversion differences
                - Push notification effectiveness
                """)

        with col2:
            with st.expander("🚩 Feature Flags & Experimentation", expanded=False):
                st.markdown("""
                **LaunchDarkly**
                - Feature flag management
                - Export rollout plans directly
                - Target segments, holdout groups, ramp schedules

                **A/B Testing Platform**
                - Optimizely, Adobe Target
                - Compare predictions vs actuals
                - Feed learnings back to simulator
                """)

            with st.expander("📋 Project & Workflow Management", expanded=False):
                st.markdown("""
                **Jira / Project Management**
                - Auto-create tickets from rollout plans
                - Feature specs, deployment steps
                - JSON/API for epics, stories, sub-tasks

                **Confluence / Documentation**
                - Store simulation briefs
                - Auto-publish ledger entries
                - Post-mortem analysis
                """)

            with st.expander("🗄️ Data Warehouse & ML Infrastructure", expanded=False):
                st.markdown("""
                **Data Lake/Warehouse**
                - Snowflake, BigQuery, or Redshift
                - Multi-year transaction history
                - Campaign performance archives
                - Inventory turnover patterns

                **ML Model Registry**
                - MLflow, SageMaker
                - Model versioning & A/B testing
                - Continuous retraining pipeline
                """)

            with st.expander("💵 Financial & Compliance", expanded=False):
                st.markdown("""
                **Finance Systems (ERP)**
                - Margin calculations, budget tracking
                - COGS, margin targets by category
                - P&L impact modeling

                **Audit & Compliance Logs**
                - Blockchain or append-only ledger
                - All simulation runs, decisions, actuals
                - Configuration snapshots with hashes
                """)

    with tab2:
        st.markdown("#### AI-Powered Architecture with Gemini LLM")

        st.code("""
┌─────────────────────────────────────────────────────────┐
│             SIMULATION LAB
│  • Chat Interface (st.chat_message)                     │
│  • Multi-turn conversation history                      │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│      Google Cloud Vertex AI - Gemini 2.5 Pro           │
│  • Conversational AI for idea refinement                │
│  • Context-aware scenario generation                    │
│  • Natural language query understanding                 │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────┼─────────────────────────────────┐
        │         │                                 │
   ┌────▼────┐ ┌─▼─────┐                    ┌──────▼────┐
   │ Vertex  │ │Vector │                    │  Prompt   │
   │AI Search│ │Search │                    │ Templates │
   │(Product)│ │(Past  │                    │(Use-case  │
   │         │ │Sims)  │                    │ patterns) │
   └─────────┘ └───────┘                    └───────────┘
        """, language="text")

        st.markdown("---")

        st.markdown("#### 🤖 LLM Use Cases in Simulation Lab")

        use_cases = pd.DataFrame({
            'Stage': [
                '💬 Request Entry',
                '❓ Clarification',
                '📊 Scenario Generation',
                '🔍 Data Quality',
                '📈 Results Interpretation',
                '🎯 Rollout Planning'
            ],
            'LLM Function': [
                'Natural language idea input with real-time clarification',
                'Smart follow-up questions based on business context',
                'Auto-suggest 3 scenario bundles from freeform text',
                'Explain bias checks, data freshness issues in plain English',
                'Interpret trade-offs, confidence levels, recommendations',
                'Generate deployment steps, rollback rules, Jira tickets'
            ],
            'Model': [
                'Gemini 2.0 Flash',
                'Gemini 2.0 Flash',
                'Gemini 2.5 Pro',
                'Gemini 2.0 Flash',
                'Gemini 2.5 Pro',
                'Gemini 2.5 Pro'
            ],
            'Latency': [
                '< 1s',
                '< 1s',
                '2-3s',
                '< 1s',
                '2-3s',
                '2-3s'
            ]
        })

        st.dataframe(use_cases, use_container_width=True, hide_index=True)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**💰 Cost Optimization**")
            cost_df = pd.DataFrame({
                'Model': ['Gemini 2.5 Pro', 'Gemini 2.0 Flash', 'Gemini 1.5 Pro'],
                'Use Case': ['Complex generation', 'Quick clarifications', 'Batch processing'],
                'Cost/1M Tokens': ['$3.50 / $10.50', '$0.15 / $0.60', '$1.25 / $5.00']
            })
            st.dataframe(cost_df, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("**🎯 Recommended Setup**")
            st.info("""
            - **Chat Interface**: Gemini 2.0 Flash (99% of interactions)
            - **Scenario Generation**: Gemini 2.5 Pro (complex reasoning)
            - **Batch Analysis**: Gemini 1.5 Pro (historical patterns)

            **Est. Monthly Cost**: $500-1500 for 1000 simulations
            """)

    with tab3:
        st.markdown("#### 📊 Integration Summary")

        summary_df = pd.DataFrame({
            'System Category': [
                '🌐 Digital Experience',
                '💰 Transactional',
                '📦 Supply Chain',
                '👥 Customer Data',
                '🚩 Experimentation',
                '📋 Workflow',
                '🗄️ Data & ML',
                '💵 Finance & Audit'
            ],
            'Primary Systems': [
                'Adobe Analytics, EDDL, Google Cloud AI + Gemini',
                'OMS, Pricing Engine, Payment Gateway',
                'Inventory, WMS, Carrier APIs (UPS/FedEx/USPS)',
                'CRM, App Analytics (Firebase/Mixpanel)',
                'LaunchDarkly, A/B Testing (Optimizely/Adobe Target)',
                'Jira, Confluence',
                'Snowflake/BigQuery, MLflow/SageMaker',
                'ERP, Compliance Ledger'
            ],
            'Integration Type': [
                'REST API, Webhooks',
                'REST API',
                'REST API, Batch',
                'REST API',
                'REST API, SDK',
                'REST API',
                'SQL, REST API',
                'REST API, Blockchain'
            ],
            'Data Refresh': [
                'Real-time',
                'Near real-time (5 min)',
                '15-30 min',
                'Daily',
                'Real-time',
                'On-demand',
                'Hourly/Daily',
                'Daily/Weekly'
            ],
            'Priority': [
                '🔴 Critical',
                '🔴 Critical',
                '🟡 High',
                '🟡 High',
                '🟢 Medium',
                '🟢 Medium',
                '🔴 Critical',
                '🟡 High'
            ]
        })

        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Systems",
                "20+",
                help="Number of external systems integrated"
            )

        with col2:
            st.metric(
                "Data Sources",
                "7 Core",
                delta="Real-time + Batch",
                help="Adobe, OMS, Inventory, WMS, Carriers, CRM, App Analytics"
            )

        with col3:
            st.metric(
                "Integration Methods",
                "REST API",
                delta="+ Webhooks, SQL",
                help="Primary integration patterns"
            )

        st.markdown("---")

        st.markdown("#### 🚀 Phased Implementation Roadmap")

        phases = pd.DataFrame({
            'Phase': ['Phase 1: MVP', 'Phase 2: Production', 'Phase 3: Advanced'],
            'Timeline': ['3-4 months', '6-8 months', '12 months'],
            'Key Deliverables': [
                'Streamlit UI, Adobe Analytics, OMS data, Basic simulation, CSV export',
                'Real-time pipelines (7+ sources), ML models, LaunchDarkly, Jira API, Audit ledger',
                'MVT support, Reinforcement learning, Pred vs Actual feedback, Cross-channel attribution'
            ],
            'Team Size': ['3-4', '6-8', '10-12'],
            'Investment': ['$150-200K', '$500-750K', '$1-1.5M']
        })

        st.dataframe(phases, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Business Impact Metrics
    st.markdown("### 💎 Business Impact")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Decision Speed",
            value="Hours",
            delta="-95% vs traditional",
            help="From weeks of analysis to hours with AI-guided simulation"
        )

    with col2:
        st.metric(
            label="Test Cost Reduction",
            value="30-50%",
            delta="Fewer live tests",
            help="Kill bad ideas in simulation, not production"
        )

    with col3:
        st.metric(
            label="Stockout + Markdown",
            value="20-30%",
            delta="Cost reduction",
            help="Better inventory and fulfillment scenarios while protecting SLAs"
        )

    with col4:
        st.metric(
            label="Conversion Lift",
            value="2-5%",
            delta="Typical gain",
            help="Even small lifts are meaningful at VS&Co scale"
        )

    st.markdown("---")

    # Call to Action
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.success("👉 **Ready to start?** Click **'1) New Request'** in the sidebar to begin your first simulation!")

        with st.expander("📖 How to Use This Demo"):
            st.markdown("""
            **Step-by-Step Guide:**

            1. **New Request** - Enter your test idea in plain text
            2. **Clarifier** - Answer AI questions to refine your use case
            3. **Scenario Options** - Review and edit 3 auto-generated scenarios
            4. **Configuration** - Set variables, budgets, and constraints
            5. **Data Lock** - Validate data sources and assumptions
            6. **Run Simulation** - Execute parallel scenario testing
            7. **Results Dashboard** - Analyze outcomes and pick a winner
            8. **Rollout Plan** - Generate deployment configuration
            9. **Ledger** - Review complete audit trail

            **Tips:**
            - Use the example request or customize it
            - Toggle MVT and adjust budget in Configuration
            - Watch the real-time simulation progress
            - Export rollout plans to your tools
            """)

elif st.session_state.step == 1:
    # Step 2: Home Screen & New Request
    st.title("Simulation Lab Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Simulations", "12", "+3")
    with col2:
        st.metric("Completed This Month", "47", "+8")
    with col3:
        st.metric("Avg Decision Time", "4.2 hrs", "-2.1 hrs")
    with col4:
        st.metric("ROI Lift (Avg)", "12.3%", "+2.1%")

    st.markdown("---")

    st.subheader("📝 New Simulation Request")

    st.markdown("""
    Describe your use case in plain English. The AI will help clarify and structure your request.
    """)

    example_text = """Test new PLP layout + holiday promo for US traffic. 
Goal: lift conversion and protect margin while maintaining delivery SLAs."""

    request_text = st.text_area(
        "What would you like to simulate?",
        value=st.session_state.request_text,
        placeholder=example_text,
        height=150,
        help="Any team can start with simple free-text, describing their use case in their own words."
    )

    st.session_state.request_text = request_text

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🚀 Submit Request", type="primary"):
            if request_text:
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Please enter a request description")

    st.markdown("---")

    st.subheader("Recent Simulations")
    recent_sims = pd.DataFrame({
        'Request': ['Black Friday PLP + Promo', 'Free Shipping Test', 'New Recommendation Engine', 'Memorial Day Campaign'],
        'Team': ['Digital Commerce', 'Marketing', 'Digital Commerce', 'Marketing'],
        'Status': ['Completed', 'Running', 'Completed', 'In Rollout'],
        'Expected Lift': ['+8.2%', '+3.1%', '+11.4%', '+6.7%'],
        'Date': ['2 days ago', '1 hour ago', '5 days ago', '3 days ago']
    })
    st.dataframe(recent_sims, use_container_width=True, hide_index=True)

elif st.session_state.step == 2:
    # Step 3: AI Clarifier & Use-Case Brief
    st.title("🤖 AI Clarifier - Smart Questions")

    st.markdown(f"""
    **Your Request:**
    > {st.session_state.request_text}
    """)

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Clarifying Questions")

        st.markdown("#### 1. Which KPIs matter most?")
        kpi_options = ['Conversion Rate', 'AOV (Average Order Value)', 'RPV (Revenue Per Visit)', 
                       'Margin %', 'Stockouts', 'Cost-to-Serve', 'SLA Performance']
        selected_kpis = st.multiselect(
            "Select primary KPIs",
            kpi_options,
            default=['Conversion Rate', 'AOV (Average Order Value)', 'Margin %']
        )
        st.session_state.kpis_selected = selected_kpis

        st.markdown("#### 2. Which regions/channels?")
        region = st.selectbox("Primary Region", ['US', 'Canada', 'UK', 'All Markets'])
        channel = st.multiselect("Channels", ['Web', 'App', 'In-Store'], default=['Web', 'App'])

        st.markdown("#### 3. Any constraints or limits?")
        constraint_delivery = st.checkbox("No increase in delivery time", value=True)
        constraint_budget = st.slider("Max Marketing Budget ($K)", 0, 500, 200)
        constraint_inventory = st.checkbox("Work within current inventory levels", value=True)

    with col2:
        st.subheader("Generated Use-Case Brief")

        st.markdown("""
        <div class="scenario-card">
        <h4>📋 Use Case Summary</h4>
        <p><strong>Objective:</strong> Test new PLP layout with holiday promo to increase conversion while protecting margin</p>

        <p><strong>Primary KPIs:</strong></p>
        <ul>
        """, unsafe_allow_html=True)

        for kpi in st.session_state.kpis_selected:
            st.markdown(f"<li>{kpi}</li>", unsafe_allow_html=True)

        st.markdown(f"""
        </ul>

        <p><strong>Target Audience:</strong></p>
        <ul>
        <li>Region: {region}</li>
        <li>Channels: {', '.join(channel)}</li>
        </ul>

        <p><strong>Constraints:</strong></p>
        <ul>
        <li>✓ Maintain delivery SLA</li>
        <li>✓ Max marketing budget: ${constraint_budget}K</li>
        <li>✓ Current inventory levels</li>
        </ul>

        <p><strong>Required Data Sources:</strong></p>
        <ul>
        <li>Adobe/EDDL (behavioral data)</li>
        <li>Orders & transactions</li>
        <li>Inventory levels (by DC)</li>
        <li>Pricing & promotions</li>
        <li>CRM customer segments</li>
        <li>OMS/WMS fulfillment data</li>
        <li>Carrier SLAs & costs</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("⬅️ Back to Request"):
            st.session_state.step = 1
            st.rerun()
    with col3:
        if st.button("Generate Scenarios ➡️", type="primary"):
            st.session_state.step = 3
            st.rerun()

elif st.session_state.step == 3:
    # Step 4: Recommended Scenario Options
    st.title("📊 Recommended Scenario Options")

    st.info("Based on your use-case brief, the Lab recommends these scenario bundles spanning storefront, marketing, and fulfillment levers.")

    scenarios = [
        {
            'name': 'Option A: New PLP + 20% Off Promo',
            'description': 'Enhanced product listing layout with prominent 20% discount messaging',
            'levers': ['Storefront', 'Marketing'],
            'expected_lift': '+8-12%',
            'risk': 'Medium'
        },
        {
            'name': 'Option B: Current Layout + Personalized Banner',
            'description': 'Keep existing PLP, add AI-driven personalized offer banners',
            'levers': ['Storefront', 'Marketing', 'CRM'],
            'expected_lift': '+5-8%',
            'risk': 'Low'
        },
        {
            'name': 'Option C: New Layout + Free Shipping Threshold',
            'description': 'Enhanced PLP with free shipping over $75, optimized DC allocation',
            'levers': ['Storefront', 'Marketing', 'Supply & Fulfillment'],
            'expected_lift': '+9-14%',
            'risk': 'Medium-High'
        }
    ]

    for i, scenario in enumerate(scenarios):
        with st.expander(f"**{scenario['name']}**", expanded=True):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Description:** {scenario['description']}")
                st.markdown(f"**Levers:** {' • '.join([f'`{l}`' for l in scenario['levers']])}")

            with col2:
                st.metric("Expected Lift", scenario['expected_lift'])
                st.metric("Risk Level", scenario['risk'])
                st.metric("Investment", scenario['investment'])

            if st.button(f"Select Option {chr(65+i)}", key=f"select_{i}"):
                st.session_state.selected_scenario = scenario
                st.success(f"✓ {scenario['name']} selected!")

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("⬅️ Back to Clarifier"):
            st.session_state.step = 2
            st.rerun()
    with col3:
        if st.button("Configure Simulation ➡️", type="primary"):
            if st.session_state.selected_scenario:
                st.session_state.step = 4
                st.rerun()
            else:
                st.error("Please select a scenario first")

elif st.session_state.step == 4:
    # Step 5: Create Simulations & Configuration
    st.title("⚙️ Simulation Configuration")

    if st.session_state.selected_scenario:
        st.success(f"**Selected Scenario:** {st.session_state.selected_scenario['name']}")

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Variables & Ranges")

        st.markdown("**Storefront Variables:**")
        layout_type = st.selectbox("PLP Layout", ['Current', 'Enhanced Grid', 'Enhanced List', 'Hybrid'])
        badge_display = st.selectbox("Badge Display", ['None', 'Discount %', 'Free Shipping', 'Both'])

        st.markdown("**Marketing Variables:**")
        promo_type = st.selectbox("Promotion Type", ['Percentage Off', 'Dollar Off', 'Free Shipping', 'BOGO', 'Tiered'])
        if promo_type == 'Percentage Off':
            discount_range = st.slider("Discount %", 0, 50, (15, 25), 5)
        elif promo_type == 'Free Shipping':
            threshold_range = st.slider("Order Threshold ($)", 0, 150, (50, 100), 10)

        promo_duration = st.slider("Campaign Duration (days)", 1, 30, 7)

        st.markdown("**Fulfillment Variables:**")
        dc_strategy = st.selectbox("DC Allocation", ['Nearest DC', 'Cost Optimized', 'SLA Optimized', 'Hybrid'])
        carrier_mix = st.multiselect("Carrier Options", ['Standard', 'Express', '2-Day', 'Next-Day'], default=['Standard', '2-Day'])

    with col2:
        st.subheader("Constraints & Limits")

        st.markdown("**Budget Constraints:**")
        max_marketing = st.number_input("Max Marketing Spend ($)", 0, 500000, 200000, 10000)
        max_fulfillment = st.number_input("Max Incremental Fulfillment Cost ($)", 0, 100000, 30000, 5000)

        st.markdown("**Capacity Constraints:**")
        max_order_volume = st.slider("Max Daily Order Increase (%)", 0, 100, 30)
        warehouse_capacity = st.slider("Warehouse Capacity Utilization (%)", 50, 100, 85)

        st.markdown("**SLA Thresholds:**")
        min_delivery_sla = st.slider("Min Delivery SLA Achievement (%)", 80, 100, 95)
        max_customer_care = st.slider("Max Customer Care Contact Rate (%)", 0, 20, 8)

        st.markdown("**Test Design:**")
        multivariate = st.checkbox("Enable Multivariate Testing (MVT)", value=True)
        if multivariate:
            st.info("MVT will test all variable combinations to find optimal mix")

        traffic_split = st.slider("Traffic Allocation to Test (%)", 10, 90, 50)
        holdout = st.slider("Holdout/Control Group (%)", 5, 30, 10)

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("⬅️ Back to Scenarios"):
            st.session_state.step = 3
            st.rerun()
    with col3:
        if st.button("Lock Data & Proceed ➡️", type="primary"):
            st.session_state.step = 5
            st.rerun()

elif st.session_state.step == 5:
    # Step 6: Data & Assumptions Lock
    st.title("🔒 Data & Assumptions Lock")

    st.markdown("The Lab validates and locks all data sources and assumptions for this simulation run.")

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Connected Data Sources")

        data_sources = [
            {'name': 'Adobe Analytics / EDDL', 'status': 'Connected', 'freshness': 'Real-time', 'quality': 98},
            {'name': 'Order Management System', 'status': 'Connected', 'freshness': '5 min delay', 'quality': 99},
            {'name': 'Inventory System (by DC)', 'status': 'Connected', 'freshness': '15 min delay', 'quality': 97},
            {'name': 'Pricing & Promotions', 'status': 'Connected', 'freshness': 'Real-time', 'quality': 100},
            {'name': 'CRM Customer Data', 'status': 'Connected', 'freshness': 'Daily refresh', 'quality': 95},
            {'name': 'WMS/Fulfillment', 'status': 'Connected', 'freshness': '10 min delay', 'quality': 96},
            {'name': 'Carrier SLA & Costs', 'status': 'Connected', 'freshness': 'Weekly refresh', 'quality': 94}
        ]

        for source in data_sources:
            with st.container():
                st.markdown(f"""
                <div class="metric-card">
                <strong>✓ {source['name']}</strong><br>
                Status: <span style="color: green">{source['status']}</span> | 
                Freshness: {source['freshness']} | 
                Quality: {source['quality']}%
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.subheader("Validation Checks")

        st.markdown("""
        <div class="success-box">
        <strong>✓ Data Quality Check: PASSED</strong><br>
        All sources meet minimum 90% quality threshold
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="success-box">
        <strong>✓ Bias Check: PASSED</strong><br>
        No significant bias detected across:<br>
        • Geographic segments<br>
        • Customer demographics<br>
        • Device types<br>
        • Time periods
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="success-box">
        <strong>✓ Freshness Check: PASSED</strong><br>
        All critical data updated within last 24 hours
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="success-box">
        <strong>✓ Completeness Check: PASSED</strong><br>
        Required fields: 99.2% complete<br>
        Missing data handled via imputation rules
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Key Assumptions")

        assumptions = pd.DataFrame({
            'Assumption': [
                'Baseline conversion rate',
                'Average order value',
                'Price elasticity',
                'Shipping cost per order',
                'Peak capacity utilization',
                'Customer acquisition cost'
            ],
            'Value': ['2.8%', '$87.50', '-1.2', '$8.45', '78%', '$35.20'],
            'Source': ['Last 30 days', 'Last 30 days', 'Historical model', 'Last quarter', 'Current', 'Q4 2024']
        })
        st.dataframe(assumptions, use_container_width=True, hide_index=True)

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("⬅️ Back to Config"):
            st.session_state.step = 4
            st.rerun()
    with col3:
        if st.button("Run Simulation ➡️", type="primary"):
            st.session_state.step = 6
            st.rerun()

elif st.session_state.step == 6:
    # Step 7: Simulation Run & Telemetry
    st.title("🚀 Running Simulation")

    st.markdown("The Lab is running scenarios in parallel, modeling storefront behavior, promo response, and supply-chain impact together.")

    # Simulation progress
    if not st.session_state.simulation_complete:
        progress_bar = st.progress(0)
        status_text = st.empty()

        scenarios_running = [
            "Scenario A.1: Enhanced Grid + 15% Off",
            "Scenario A.2: Enhanced Grid + 20% Off", 
            "Scenario A.3: Enhanced Grid + 25% Off",
            "Scenario B.1: Enhanced List + 15% Off",
            "Scenario B.2: Enhanced List + 20% Off",
            "Scenario B.3: Enhanced List + 25% Off",
            "Scenario C.1: Hybrid + Free Ship $50",
            "Scenario C.2: Hybrid + Free Ship $75"
        ]

        for i, scenario in enumerate(scenarios_running):
            progress = (i + 1) / len(scenarios_running)
            progress_bar.progress(progress)
            status_text.text(f"Running: {scenario}")
            time.sleep(0.3)

        status_text.text("✓ All scenarios complete!")
        st.session_state.simulation_complete = True
        time.sleep(1)

    st.success("✓ Simulation Complete!")

    st.markdown("---")

    # Telemetry metrics
    st.subheader("📊 Real-Time Simulation Telemetry")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Scenarios Run", "8", delta="+8")
    with col2:
        st.metric("Variables Tested", "24", delta="+24")
    with col3:
        st.metric("Simulated Orders", "487K", delta="+487K")
    with col4:
        st.metric("Run Time", "4.2 min", delta="-1.8 min")

    st.markdown("---")

    # KPI tracking across scenarios
    st.subheader("KPI Ranges Across Scenarios")

    col1, col2 = st.columns(2)

    with col1:
        kpi_data = pd.DataFrame({
            'KPI': ['Conversion Rate', 'AOV', 'RPV', 'Margin %'],
            'Baseline': ['2.8%', '$87.50', '$2.45', '42.1%'],
            'Min': ['2.9%', '$89.20', '$2.58', '38.2%'],
            'Max': ['3.4%', '$96.30', '$3.27', '43.8%'],
            'Best Scenario': ['A.3', 'B.2', 'A.3', 'B.1']
        })
        st.dataframe(kpi_data, use_container_width=True, hide_index=True)

    with col2:
        ops_data = pd.DataFrame({
            'Metric': ['Stockouts', 'Markdown %', 'Cost-to-Serve', 'SLA Risk'],
            'Baseline': ['4.2%', '12.3%', '$14.20', 'Low'],
            'Min': ['3.8%', '11.1%', '$13.85', 'Low'],
            'Max': ['6.7%', '18.9%', '$16.40', 'Medium'],
            'Best Scenario': ['C.1', 'A.1', 'C.2', 'B.1']
        })
        st.dataframe(ops_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("⬅️ Back to Data Lock"):
            st.session_state.step = 5
            st.rerun()
    with col3:
        if st.button("View Results ➡️", type="primary"):
            st.session_state.step = 7
            st.rerun()

elif st.session_state.step == 7:
    # Step 8: Results Dashboard & Recommendations
    st.title("📈 Decision Dashboard")

    st.markdown("Scenarios ranked by expected revenue and margin, with trade-off analysis and historical context.")

    # Top-line summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Best Scenario", "A.3", delta="Enhanced Grid + 25% Off")
    with col2:
        st.metric("Expected Revenue Lift", "+14.2%", delta="$2.1M incremental")
    with col3:
        st.metric("Margin Impact", "-1.3%", delta="Within acceptable range")
    with col4:
        st.metric("Confidence Level", "87%", delta="High")

    st.markdown("---")

    # Scenario ranking table
    st.subheader("Scenario Rankings")

    results_df = pd.DataFrame({
        'Rank': [1, 2, 3, 4, 5, 6, 7, 8],
        'Scenario': ['A.3: Enhanced Grid + 25% Off', 'A.2: Enhanced Grid + 20% Off', 
                     'C.2: Hybrid + Free Ship $75', 'B.2: Enhanced List + 20% Off',
                     'C.1: Hybrid + Free Ship $50', 'B.3: Enhanced List + 25% Off',
                     'A.1: Enhanced Grid + 15% Off', 'B.1: Enhanced List + 15% Off'],
        'Conv. Lift': ['+21.4%', '+18.2%', '+16.8%', '+14.3%', '+12.9%', '+11.7%', '+10.2%', '+8.4%'],
        'Revenue Lift': ['+14.2%', '+12.8%', '+13.1%', '+10.9%', '+9.7%', '+8.2%', '+7.1%', '+5.8%'],
        'Margin Impact': ['-1.3%', '-0.8%', '-0.5%', '-0.6%', '-0.3%', '-1.8%', '-0.4%', '-0.2%'],
        'Risk': ['Medium', 'Medium', 'Medium-High', 'Low', 'Medium', 'Medium', 'Low', 'Low'],
        'Score': [92, 88, 86, 82, 78, 74, 70, 66]
    })

    st.dataframe(results_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Trade-off charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Conversion vs Margin Trade-off")

        fig1 = go.Figure()

        conv_data = [21.4, 18.2, 16.8, 14.3, 12.9, 11.7, 10.2, 8.4]
        margin_data = [-1.3, -0.8, -0.5, -0.6, -0.3, -1.8, -0.4, -0.2]
        scenarios = ['A.3', 'A.2', 'C.2', 'B.2', 'C.1', 'B.3', 'A.1', 'B.1']

        fig1.add_trace(go.Scatter(
            x=margin_data,
            y=conv_data,
            mode='markers+text',
            marker=dict(size=15, color=conv_data, colorscale='Viridis', showscale=True),
            text=scenarios,
            textposition='top center',
            name='Scenarios'
        ))

        fig1.update_layout(
            xaxis_title='Margin Impact (%)',
            yaxis_title='Conversion Lift (%)',
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Risk vs Return Matrix")

        risk_map = {'Low': 1, 'Medium': 2, 'Medium-High': 3, 'High': 4}
        risk_numeric = [risk_map[r] for r in results_df['Risk']]

        fig2 = go.Figure()

        fig2.add_trace(go.Scatter(
            x=risk_numeric,
            y=results_df['Score'],
            mode='markers+text',
            marker=dict(size=15, color=results_df['Score'], colorscale='RdYlGn', showscale=True),
            text=results_df['Scenario'].str[:3],
            textposition='top center',
            name='Scenarios'
        ))

        fig2.update_layout(
            xaxis=dict(
                title='Risk Level',
                tickmode='array',
                tickvals=[1, 2, 3, 4],
                ticktext=['Low', 'Medium', 'Med-High', 'High']
            ),
            yaxis_title='Overall Score',
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Historical context
    st.subheader("📚 Historical Context")

    st.info("""
    **Compared with 14 past simulations for similar holiday PLP tests:**
    - This scenario's predicted lift (+14.2%) is in the **top quartile** of historical performance
    - Margin impact (-1.3%) is **within normal range** for discount-based promos
    - Similar scenarios in past delivered **92% accuracy** vs actual results
    - Recommended confidence adjustment: **+5%** based on historical pattern matching
    """)

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("⬅️ Back to Simulation"):
            st.session_state.step = 6
            st.rerun()
    with col3:
        if st.button("Create Rollout Plan ➡️", type="primary"):
            st.session_state.step = 8
            st.rerun()

elif st.session_state.step == 8:
    # Step 9: Rollout Plan & Export
    st.title("🎯 Rollout Plan")

    st.success("**Selected Scenario:** A.3 - Enhanced Grid Layout + 25% Off Promo")

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🚩 Feature Flags & Targeting")

        st.markdown("""
        <div class="scenario-card">
        <strong>Target Audience:</strong>
        <ul>
        <li>Platform: Web + App (iOS & Android)</li>
        <li>Region: US only</li>
        <li>Traffic: 50% of eligible users</li>
        <li>Holdout: 10% control group</li>
        </ul>

        <strong>Feature Flags:</strong>
        <ul>
        <li><code>plp_layout_enhanced_grid</code> = true</li>
        <li><code>holiday_promo_25_percent</code> = true</li>
        <li><code>promo_badge_display</code> = true</li>
        </ul>

        <strong>Ramp Schedule:</strong>
        <ul>
        <li>Day 1-2: 10% traffic (validation)</li>
        <li>Day 3-4: 30% traffic</li>
        <li>Day 5+: 50% traffic (full rollout)</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        st.subheader("💰 Promo Plan")

        st.markdown("""
        <div class="scenario-card">
        <strong>Offer Details:</strong>
        <ul>
        <li>Type: 25% off sitewide</li>
        <li>Code: HOLIDAY25</li>
        <li>Duration: 7 days (Nov 27 - Dec 3)</li>
        <li>Min purchase: None</li>
        <li>Max discount: $200 per order</li>
        </ul>

        <strong>Budget Allocation:</strong>
        <ul>
        <li>Total budget: $195,000</li>
        <li>Expected redemptions: ~12,500 orders</li>
        <li>Avg discount per order: $15.60</li>
        <li>Buffer: 15% ($29,250)</li>
        </ul>

        <strong>Marketing Channels:</strong>
        <ul>
        <li>Email: Targeted to active customers</li>
        <li>SMS: VIP segment only</li>
        <li>On-site: Homepage banner + PLP badge</li>
        <li>Paid: Excluded (organic only)</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.subheader("📦 Inventory & Fulfillment")

        st.markdown("""
        <div class="scenario-card">
        <strong>DC Allocation Strategy:</strong>
        <ul>
        <li>Primary: SLA-Optimized</li>
        <li>East Coast: Columbus DC (60%)</li>
        <li>West Coast: LA DC (30%)</li>
        <li>Midwest: Chicago DC (10%)</li>
        </ul>

        <strong>Carrier Mix:</strong>
        <ul>
        <li>Standard (5-7 day): 45%</li>
        <li>2-Day: 40%</li>
        <li>Next-Day: 15% (high-value only)</li>
        </ul>

        <strong>Inventory Guardrails:</strong>
        <ul>
        <li>Safety stock: Maintain 20% buffer</li>
        <li>Auto-disable promo if stockout >8%</li>
        <li>Priority allocation to test cohort</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        st.subheader("🛡️ Auto-Rollback Rules")

        st.markdown("""
        <div class="warning-box">
        <strong>⚠️ Automatic Rollback Triggers:</strong>
        <ul>
        <li>Conversion drops >2% vs control</li>
        <li>SLA achievement falls below 92%</li>
        <li>Stockout rate exceeds 8%</li>
        <li>Customer care contacts spike >12%</li>
        <li>Page load time increases >15%</li>
        <li>Error rate >0.5%</li>
        </ul>

        <strong>Rollback Actions:</strong>
        <ul>
        <li>Disable feature flags immediately</li>
        <li>Notify: Product, Eng, Marketing, Ops</li>
        <li>Preserve data for post-mortem</li>
        <li>Auto-create incident ticket</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("📤 Export Rollout Plan")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📋 Export to Jira", use_container_width=True):
            st.success("✓ Exported to Jira Project: VSCO-HOLIDAY")

    with col2:
        if st.button("🚩 Export to LaunchDarkly", use_container_width=True):
            st.success("✓ Feature flags created in LaunchDarkly")

    with col3:
        if st.button("📦 Export to OMS", use_container_width=True):
            st.success("✓ Fulfillment rules updated in OMS")

    with col4:
        if st.button("💰 Export to Promo Engine", use_container_width=True):
            st.success("✓ Promo configured and scheduled")

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("⬅️ Back to Results"):
            st.session_state.step = 7
            st.rerun()
    with col3:
        if st.button("View Ledger ➡️", type="primary"):
            st.session_state.step = 9
            st.rerun()

else:  # Step 9: Ledger
    st.title("📚 Simulation Ledger")

    st.markdown("Every decision is fully traceable, auditable, and reusable for continuous learning.")

    st.markdown("---")

    # Activity Timeline
    st.subheader("📅 Activity Timeline")

    timeline_data = pd.DataFrame({
        'Timestamp': [
            '2025-11-20 09:15:00',
            '2025-11-20 09:18:00',
            '2025-11-20 09:25:00',
            '2025-11-20 09:32:00',
            '2025-11-20 09:38:00',
            '2025-11-20 09:42:00',
            '2025-11-20 09:47:00',
            '2025-11-20 09:55:00',
            '2025-11-20 10:02:00',
            '2025-11-20 10:15:00'
        ],
        'Stage': [
            'Request Submitted',
            'AI Clarification Complete',
            'Use-Case Brief Generated',
            'Scenarios Recommended',
            'Configuration Locked',
            'Data Validation Complete',
            'Simulation Started',
            'Simulation Complete',
            'Decision Made',
            'Rollout Plan Exported'
        ],
        'User/System': [
            'Sarah Chen (Digital Commerce)',
            'AI Clarifier',
            'AI Clarifier',
            'Simulation Lab',
            'Sarah Chen',
            'Data Validator',
            'Simulation Engine',
            'Simulation Engine',
            'Sarah Chen + Mike Rodriguez (Marketing)',
            'Sarah Chen'
        ],
        'Details': [
            'New PLP layout + holiday promo request',
            '5 questions answered, 3 KPIs selected',
            'Brief created with all stakeholder inputs',
            '3 scenario bundles generated',
            '8 scenarios configured with MVT enabled',
            'All 7 data sources validated',
            '8 scenarios, 487K simulated orders',
            'Results: A.3 recommended (92 score)',
            'Scenario A.3 selected for rollout',
            'Exported to Jira, LaunchDarkly, OMS, Promo'
        ]
    })

    st.dataframe(timeline_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Summary cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
        <h4>⚡ Faster Decisions</h4>
        <p><strong>Total Time:</strong> 60 minutes</p>
        <p><strong>vs Traditional:</strong> 2-3 weeks</p>
        <p><strong>Efficiency Gain:</strong> 95%</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
        <h4>💎 Higher ROI</h4>
        <p><strong>Expected Lift:</strong> +14.2%</p>
        <p><strong>Revenue Impact:</strong> +$2.1M</p>
        <p><strong>Confidence:</strong> 87%</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
        <h4>🛡️ Reduced Risk</h4>
        <p><strong>Scenarios Tested:</strong> 8</p>
        <p><strong>Bad Ideas Killed:</strong> 5</p>
        <p><strong>Auto-Rollback:</strong> Enabled</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Audit trail
    st.subheader("🔍 Complete Audit Trail")

    with st.expander("📝 Request & Brief", expanded=False):
        st.markdown(f"""
        **Original Request:**
        > {st.session_state.request_text}

        **Clarifications:**
        - KPIs: {', '.join(st.session_state.kpis_selected)}
        - Region: US
        - Channels: Web, App
        - Constraints: No delivery SLA degradation, max budget $200K

        **Brief Hash:** `a3f7b9c2e4d1...`
        """)

    with st.expander("🔒 Data Sources & Assumptions", expanded=False):
        st.markdown("""
        **Data Sources (7):**
        - Adobe/EDDL: Real-time, Quality 98%
        - Orders: 5min delay, Quality 99%
        - Inventory: 15min delay, Quality 97%
        - Pricing: Real-time, Quality 100%
        - CRM: Daily, Quality 95%
        - WMS: 10min delay, Quality 96%
        - Carriers: Weekly, Quality 94%

        **Key Assumptions:**
        - Baseline conversion: 2.8%
        - Baseline AOV: $87.50
        - Price elasticity: -1.2
        - Shipping cost: $8.45/order

        **Validation Hash:** `b8e4c1f9a2d5...`
        """)

    with st.expander("⚙️ Configuration & Variables", expanded=False):
        st.markdown("""
        **Scenarios Configured:** 8
        **Variables:** 24
        **MVT Enabled:** Yes
        **Traffic Split:** 50% test / 10% holdout

        **Configuration Hash:** `c9d2a4f8b1e6...`
        """)

    with st.expander("🚀 Simulation Execution", expanded=False):
        st.markdown("""
        **Run ID:** SIM-20251120-001
        **Engine Version:** 2.3.1
        **Start Time:** 2025-11-20 09:47:00
        **End Time:** 2025-11-20 09:55:00
        **Duration:** 4.2 minutes
        **Simulated Orders:** 487,000
        **Compute Resources:** 16 cores, 64GB RAM

        **Execution Hash:** `d1e6f3a9c2b7...`
        """)

    with st.expander("📊 Results & Decision", expanded=False):
        st.markdown("""
        **Recommended Scenario:** A.3 - Enhanced Grid + 25% Off
        **Score:** 92/100
        **Expected Lift:** +14.2% revenue
        **Confidence:** 87%
        **Decision Maker:** Sarah Chen, Mike Rodriguez
        **Decision Time:** 2025-11-20 10:02:00
        **Approval:** Auto-approved (within guardrails)

        **Results Hash:** `e2f7a1c9d4b8...`
        """)

    with st.expander("🎯 Rollout Plan", expanded=False):
        st.markdown("""
        **Rollout Start:** 2025-11-27 00:00:00
        **Duration:** 7 days
        **Ramp:** 10% → 30% → 50%
        **Feature Flags:** 3 created in LaunchDarkly
        **Jira Tickets:** VSCO-4521, VSCO-4522
        **OMS Rules:** Updated
        **Auto-Rollback:** Enabled (6 triggers)

        **Rollout Hash:** `f3a8b2e1c9d7...`
        """)

    st.markdown("---")

    st.subheader("🔄 Continuous Learning")

    st.info("""
    **Post-Launch Tracking:**
    - Real-time comparison of predicted vs actual KPIs
    - Automatic model recalibration based on results
    - Learnings fed back into next simulation for improved accuracy
    - Historical pattern library updated for future use

    **Next Steps:**
    - Monitor rollout for 7 days
    - Compare actuals to predictions
    - Generate post-mortem report
    - Update simulation models with learnings
    """)

    st.markdown("---")

    # Export options
    st.subheader("📤 Export Ledger")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📄 PDF Report", use_container_width=True):
            st.success("✓ Ledger exported as PDF")

    with col2:
        if st.button("📊 Excel Summary", use_container_width=True):
            st.success("✓ Summary exported to Excel")

    with col3:
        if st.button("🔗 Share Link", use_container_width=True):
            st.success("✓ Shareable link copied")

    with col4:
        if st.button("💾 Archive", use_container_width=True):
            st.success("✓ Simulation archived")

    st.markdown("---")

    # Final summary
    st.markdown("""
    <div class="main-header" style="font-size: 32px">
    ✅ Simulation Complete
    </div>

    <div class="sub-header" style="font-size: 18px; padding-bottom: 10px">
    From idea to validated rollout plan in 60 minutes
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="success-box">
        <h4>⚡ Faster Decisions</h4>
        <p>From weeks to hours with AI-guided simulation</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="success-box">
        <h4>🛡️ Less Risk, Higher ROI</h4>
        <p>Test and optimize before touching customers</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="success-box">
        <h4>📚 Consistent & Auditable</h4>
        <p>One decision framework across all teams</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("⬅️ Back to Rollout"):
            st.session_state.step = 8
            st.rerun()
    with col3:
        if st.button("🏠 Start New Simulation", type="primary"):
            # Reset session state
            st.session_state.step = 0
            st.session_state.request_text = ""
            st.session_state.kpis_selected = []
            st.session_state.selected_scenario = None
            st.session_state.simulation_complete = False
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
<strong>Simulation Lab v2.0</strong> | The Digital Wind Tunnel for VS&Co Decisions<br>
Built for faster, smarter, safer decisions across Digital Commerce, Marketing, and Operations
</div>
""", unsafe_allow_html=True)
