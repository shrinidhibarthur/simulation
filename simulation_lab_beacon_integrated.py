import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import plotly.express as px

# ================== Beacon Metrics ==================
class BeaconMetrics:
    @staticmethod
    def calculate_win_probability(conversion_rate, target_rate, volatility):
        from scipy.stats import norm
        if volatility <= 0:
            return 50.0
        d1 = (np.log(conversion_rate / target_rate) + 0.5 * volatility ** 2) / volatility
        win_prob = norm.cdf(d1) * 100
        return min(max(win_prob, 0), 100)

    @staticmethod
    def calculate_demand_momentum(conversion_rate, days_to_launch=30):
        annual_factor = np.sqrt(365 / max(days_to_launch, 1))
        momentum = conversion_rate * annual_factor * 100
        return min(max(momentum, 0), 200)

    @staticmethod
    def calculate_traffic_sensitivity(conversion_rate):
        return conversion_rate * 100

    @staticmethod
    def calculate_acceleration(conversion_lift, days=7):
        return (conversion_lift / max(days, 1)) * 10

    @staticmethod
    def calculate_time_decay(days_remaining, total_days=30):
        if total_days <= 0:
            return 0
        return (days_remaining / total_days) * 100

    @staticmethod
    def calculate_visibility_budget(win_prob, rpv_lift, max_budget=100000):
        score = (win_prob / 100) * (1 + rpv_lift)
        budget = score * max_budget
        return min(max(budget, 0), max_budget)

# ================== Integrated Dashboard ==================
def run_integrated_dashboard():
    st.title("🏠 Integrated KPIs Dashboard")

    sim_kpis = {
        "Active Simulations": 15,
        "Avg Conversion Lift": "6.1%",
        "Avg Margin Impact": "-0.4%",
        "ROI Lift": "11.5%"
    }
    beacon_kpis = {
        "Avg Win Probability": "75.7%",
        "Avg Demand Momentum": "127.9",
        "Avg Traffic Sensitivity": "2.56",
        "Total Visibility Budget": "$475,000"
    }

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Simulation Lab KPIs")
        for k, v in sim_kpis.items():
            st.metric(k, v)
    with col2:
        st.subheader("Beacon Momentum KPIs")
        for k, v in beacon_kpis.items():
            st.metric(k, v)

    st.markdown("---")
    st.markdown("### Recent Combined Actions and Decisions")
    data = [
        {"Scenario": "Holiday Promo", "Sim Score": 92, "Win Probability": "82%", "Visibility Budget": "$187,000"},
        {"Scenario": "Free Shipping", "Sim Score": 87, "Win Probability": "75%", "Visibility Budget": "$156,000"},
    ]
    st.table(pd.DataFrame(data))

# ------------ Sidebar Navigation ---------------
st.sidebar.title("VS&Co Unified Platform")
page = st.sidebar.radio("Navigate to:", ["Integrated Dashboard", "Simulation Lab", "Beacon"])

# Route user to appropriate app section
if page == "Integrated Dashboard":
    run_integrated_dashboard()

# ================== Simulation Lab Workflow (Full) ==================

def run_simulation_lab():
    st.header("🔬 Simulation Lab - Full Workflow")

    if 'step' not in st.session_state:
        st.session_state.step = 1

    if st.session_state.step == 1:
        st.subheader("Step 1: New Request")
        if 'request_text' not in st.session_state:
            st.session_state.request_text = ''
        st.session_state.request_text = st.text_area("Describe your test idea", st.session_state.request_text, height=120)

        if st.button("Next: Clarifier"):
            if st.session_state.request_text.strip() == '':
                st.warning("Please enter the test idea request.")
            else:
                st.session_state.scenarios = []  # clear previous scenarios
                st.session_state.step = 2

    elif st.session_state.step == 2:
        st.subheader("Step 2: AI Clarifier (Placeholder)")

        st.info("Placeholder for AI clarifier questions based on your input to refine the use case.")
        if st.button("Next: Scenario Options"):
            # For demo, generate fixed scenarios
            st.session_state.scenarios = [
                {"name": "Scenario A", "conv_lift": 7.5, "margin_impact": -0.3},
                {"name": "Scenario B", "conv_lift": 3.2, "margin_impact": 0.1},
                {"name": "Scenario C", "conv_lift": 9.1, "margin_impact": -0.8},
            ]
            st.session_state.step = 3

    elif st.session_state.step == 3:
        st.subheader("Step 3: Scenario Options")
        df = pd.DataFrame(st.session_state.scenarios)
        edited_df = st.data_editor(df, use_container_width=True)
        st.session_state.scenarios = edited_df.to_dict('records')

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back: Clarifier"):
                st.session_state.step = 2
        with col2:
            if st.button("Next: Configuration"):
                st.session_state.step = 4

    elif st.session_state.step == 4:
        st.subheader("Step 4: Configuration Settings")
        st.info("Configure variables, budgets, constraints here. Placeholder for demonstration.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back: Scenarios"):
                st.session_state.step = 3
        with col2:
            if st.button("Next: Data Lock"):
                st.session_state.step = 5

    elif st.session_state.step == 5:
        st.subheader("Step 5: Data Lock")
        st.info("Data validation and locking step. Placeholder for demonstration.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back: Configuration"):
                st.session_state.step = 4
        with col2:
            if st.button("Next: Run Simulation"):
                st.session_state.step = 6

    elif st.session_state.step == 6:
        st.subheader("Step 6: Run Simulation")

        if st.button("Run Now"):
            st.session_state.results = []
            beacon = BeaconMetrics()
            progress_bar = st.progress(0)
            status_text = st.empty()
            scenarios = st.session_state.scenarios

            for i, scenario in enumerate(scenarios):
                progress_bar.progress((i + 1) / len(scenarios))
                status_text.text(f"Running simulation for {scenario['name']}...")
                time.sleep(0.5)  # simulate processing

                base_cvr = 0.025
                conversion_rate = base_cvr * (1 + scenario['conv_lift'] / 100)
                win_prob = beacon.calculate_win_probability(conversion_rate, 0.03, 0.2)
                momentum = beacon.calculate_demand_momentum(conversion_rate)
                sensitivity = beacon.calculate_traffic_sensitivity(conversion_rate)
                visibility_budget = beacon.calculate_visibility_budget(win_prob, rpv_lift=0.1, max_budget=200000)

                st.session_state.results.append({
                    "Scenario": scenario['name'],
                    "Conversion Lift (%)": scenario['conv_lift'],
                    "Margin Impact (%)": scenario['margin_impact'],
                    "Win Probability (%)": round(win_prob, 2),
                    "Demand Momentum": round(momentum, 2),
                    "Traffic Sensitivity": round(sensitivity, 2),
                    "Visibility Budget ($)": f"${int(visibility_budget):,}"
                })

            progress_bar.empty()
            status_text.text("Simulation complete!")

        if 'results' in st.session_state and st.session_state.results:
            st.subheader("Simulation Results")
            results_df = pd.DataFrame(st.session_state.results)
            st.dataframe(results_df, use_container_width=True)
            fig = px.bar(results_df, x='Scenario', y='Win Probability (%)', color='Win Probability (%)',
                         color_continuous_scale='Blues')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back: Data Lock"):
                st.session_state.step = 5
        with col2:
            if st.button("Next: Results Dashboard"):
                st.session_state.step = 7

    elif st.session_state.step == 7:
        st.subheader("Step 7: Results Dashboard")

        if 'results' not in st.session_state or not st.session_state.results:
            st.warning("Please run the simulation first.")
        else:
            results_df = pd.DataFrame(st.session_state.results)
            st.dataframe(results_df, use_container_width=True)

            top_scenario = results_df.loc[results_df['Win Probability (%)'].idxmax()]
            st.success(f"Recommended Scenario: {top_scenario['Scenario']} "
                       f"with Win Probability {top_scenario['Win Probability (%)']}%")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back: Run Simulation"):
                st.session_state.step = 6
        with col2:
            if st.button("Next: Rollout Plan"):
                st.session_state.step = 8

    elif st.session_state.step == 8:
        st.subheader("Step 8: Rollout Plan")

        if 'results' not in st.session_state or not st.session_state.results:
            st.warning("Please run the simulation first.")
        else:
            results_df = pd.DataFrame(st.session_state.results)
            options = results_df["Scenario"].tolist()
            choice = st.selectbox("Select scenario for rollout", options)
            selected = results_df[results_df["Scenario"] == choice].iloc[0]

            st.markdown(f"""
            **Selected Scenario:** {selected['Scenario']}  
            Win Probability: {selected['Win Probability (%)']}%  
            Visibility Budget: {selected['Visibility Budget ($)']}  
            Margin Impact: {selected['Margin Impact (%)']}%  
            """)

            st.markdown("**Recommended Rollout:**")
            st.write("""
            - Day 1-2: 10% rollout (validate metrics)  
            - Day 3-5: 30% rollout  
            - Day 6+: 50% rollout full deployment  
            """)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back: Results Dashboard"):
                st.session_state.step = 7
        with col2:
            if st.button("Finish and Return to Request"):
                st.session_state.step = 1

    else:
        st.info("Use sidebar or buttons to navigate simulation workflow.")

# ================== Beacon Momentum Intelligence Platform ==================

def run_beacon():
    st.header("🎯 Beacon Momentum Intelligence Platform")

    # Example scenario momentum data (replace with real data integration)
    scenarios = [
        {"Scenario": "Option A", "Win Probability": 82.5, "Demand Momentum": 145.2, "Traffic Sensitivity": 2.94, "Visibility Budget": "$187,000"},
        {"Scenario": "Option B", "Win Probability": 74.0, "Demand Momentum": 128.4, "Traffic Sensitivity": 2.61, "Visibility Budget": "$156,000"},
        {"Scenario": "Option C", "Win Probability": 69.0, "Demand Momentum": 110.3, "Traffic Sensitivity": 2.12, "Visibility Budget": "$132,000"},
    ]
    df = pd.DataFrame(scenarios)

    st.subheader("Momentum Scenario Metrics")
    st.dataframe(df, use_container_width=True)

    # Win Probability chart
    fig = px.bar(df, x="Scenario", y="Win Probability",
                 title="Win Probability by Scenario",
                 labels={'Win Probability': 'Win Probability (%)'},
                 color='Win Probability',
                 color_continuous_scale='Blues')
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

    # Summary KPIs
    st.markdown("### Beacon Summary KPIs")
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Win Probability", f"{df['Win Probability'].mean():.1f}%")
    col2.metric("Avg Demand Momentum", f"{df['Demand Momentum'].mean():.1f}")
    # Remove $ and commas from Visibility Budget to sum correctly
    budget_sum = df['Visibility Budget'].str.replace('[\$,]', '', regex=True).astype(int).sum()
    col3.metric("Total Visibility Budget", f"${budget_sum:,}")

    st.markdown("---")
    st.info("This data is powered by Beacon's options-inspired momentum algorithms.")

# Main app will route here when user selects Beacon section in sidebar

# ================== Main App Routing & Footer ==================

st.sidebar.title("VS&Co Unified Platform")
page = st.sidebar.radio("Navigate to:", ["Integrated Dashboard", "Simulation Lab", "Beacon"])

if page == "Integrated Dashboard":
    run_integrated_dashboard()
elif page == "Simulation Lab":
    run_simulation_lab()
elif page == "Beacon":
    run_beacon()
else:
    st.error("Unknown page selected.")

st.markdown("---")
st.caption("VS&Co Integrated Simulation Lab + Beacon Momentum Intelligence\n© 2025 VS&Co Labs")
