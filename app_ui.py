"""
app_ui.py
EnergyWise AI Agent — Streamlit Web UI
Run with: streamlit run app_ui.py (from inside energy_agent/)
"""
import sys
import os
import json
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.energy_models import HouseholdProfile, ApplianceUsage
from modules.analysis import analyze_household, calculate_single_appliance
from modules.education import (
    get_random_fact, explain_kwh_in_simple_terms, explain_carbon_impact,
    explain_bill_breakdown, get_peak_hour_explanation, get_seasonal_tips,
    get_myth_fact, get_all_myths, get_all_facts,
)
from modules.suggestions import get_personalised_tips, format_tips_as_text
from utils.watsonx_client import get_watsonx_client
from utils.prompt_templates import (
    build_analysis_prompt, build_conversation_prompt,
)

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EnergyWise AI Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State ──────────────────────────────────────────────────────────────
if "profile" not in st.session_state:
    st.session_state.profile = None
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "messages" not in st.session_state:
    st.session_state.messages = []


# ── Helpers ────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_llm():
    return get_watsonx_client()


def run_analysis(profile: HouseholdProfile) -> dict:
    if st.session_state.analysis is None:
        st.session_state.analysis = analyze_household(profile)
    return st.session_state.analysis


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=80)
    st.title("⚡ EnergyWise")
    st.caption("AI Agent for Electricity Consumption Awareness")
    st.divider()

    llm = get_llm()
    if llm.is_ready:
        st.success("✅ IBM watsonx.ai Connected")
    else:
        st.warning("⚠️ watsonx.ai not connected\nConfigure .env file")

    st.divider()
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📋 Setup Profile", "📊 Analysis", "💡 Tips & Advice",
         "📚 Learn", "🔌 Appliance Calculator", "💬 Chat with EnergyWise"],
    )

# ── Page: Home ─────────────────────────────────────────────────────────────────
if page == "🏠 Home":
    st.title("⚡ EnergyWise — AI Agent for Electricity Awareness")
    st.markdown("""
    **EnergyWise** is an AI-powered assistant that helps you understand, monitor,
    and reduce your household electricity consumption.

    ### What can EnergyWise do for you?
    | Feature | Description |
    |---------|-------------|
    | 📊 **Consumption Analysis** | Identify your top energy consumers and high-usage patterns |
    | 💡 **Personalised Tips** | Get actionable, prioritised energy-saving recommendations |
    | 📚 **Energy Education** | Learn about bills, carbon footprint, peak hours & more |
    | 🔌 **Appliance Calculator** | Estimate cost of any appliance instantly |
    | 💬 **AI Chat** | Ask any question — powered by IBM Granite (watsonx.ai) |

    ### Get Started
    👈 Use the sidebar to navigate. Start with **📋 Setup Profile** to enter your appliances.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg. Monthly Bill", "₹6,577", help="India average household ~877 kWh × ₹7.5")
    with col2:
        st.metric("CO₂ per kWh", "0.82 kg", help="India grid emission factor")
    with col3:
        st.metric("Potential Savings", "Up to 35%", help="With best practices & upgrades")

    st.info(f"💡 **Did You Know?** {get_random_fact()}")

# ── Page: Setup Profile ────────────────────────────────────────────────────────
elif page == "📋 Setup Profile":
    st.title("📋 Household Profile Setup")
    st.markdown("Enter your appliances to get a personalised energy analysis.")

    with st.form("profile_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Household Name", value="My Home")
        with col2:
            city = st.text_input("City", value="Bangalore")
        with col3:
            occupants = st.number_input("Occupants", min_value=1, max_value=20, value=4)

        rate = st.slider("Electricity Rate (₹/kWh)", min_value=3.0, max_value=15.0, value=7.5, step=0.5)

        st.subheader("Appliances")
        st.markdown("Add each appliance in your home:")

        appliance_data = []
        common_appliances = [
            ("Air Conditioner", 1500, 8, 1, "Cooling"),
            ("Refrigerator", 150, 24, 1, "Kitchen"),
            ("Water Heater", 4000, 2, 1, "Heating"),
            ("Washing Machine", 500, 1, 1, "Laundry"),
            ("LED TV", 100, 5, 1, "Electronics"),
            ("Ceiling Fan", 75, 10, 3, "Cooling"),
            ("LED Bulbs", 10, 6, 8, "Lighting"),
            ("Laptop", 50, 6, 1, "Electronics"),
        ]

        for appl_name, def_w, def_h, def_q, def_cat in common_appliances:
            with st.expander(f"🔌 {appl_name}", expanded=False):
                c1, c2, c3 = st.columns(3)
                w = c1.number_input(f"Wattage (W)", value=def_w, key=f"w_{appl_name}")
                h = c2.number_input(f"Daily Hours", value=float(def_h), min_value=0.0, max_value=24.0, step=0.5, key=f"h_{appl_name}")
                q = c3.number_input(f"Quantity", value=def_q, min_value=0, max_value=20, key=f"q_{appl_name}")
                if q > 0 and h > 0:
                    appliance_data.append((appl_name, w, h, q, def_cat))

        submitted = st.form_submit_button("💾 Save Profile & Analyse", type="primary")

    if submitted:
        profile = HouseholdProfile(name=name, city=city, occupants=occupants, rate_per_kwh=rate)
        for appl_name, w, h, q, cat in appliance_data:
            profile.add_appliance(ApplianceUsage(name=appl_name, wattage=w, daily_hours=h, quantity=q, category=cat))
        st.session_state.profile = profile
        st.session_state.analysis = None  # invalidate cache
        st.success(f"✅ Profile saved! {len(profile.appliances)} appliances tracked.")
        st.metric("Monthly Consumption", f"{profile.total_monthly_kwh} kWh")
        st.metric("Estimated Monthly Bill", f"₹{profile.monthly_bill}")

# ── Page: Analysis ─────────────────────────────────────────────────────────────
elif page == "📊 Analysis":
    st.title("📊 Energy Consumption Analysis")
    if st.session_state.profile is None:
        st.warning("Please set up your household profile first (📋 Setup Profile).")
    else:
        profile: HouseholdProfile = st.session_state.profile
        report = run_analysis(profile)

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Monthly Consumption", f"{report['summary']['total_monthly_kwh']} kWh")
        col2.metric("Monthly Bill", f"₹{report['summary']['monthly_bill_inr']}")
        col3.metric("CO₂ Footprint", f"{report['summary']['carbon_footprint_kg']} kg")
        col4.metric("kWh per Person", f"{report['summary']['kwh_per_person']} kWh")

        # Benchmark
        bm = report["benchmark"]
        st.subheader("📈 Benchmark vs. National Average")
        if "Excellent" in bm["rating"] or "Good" in bm["rating"]:
            st.success(f"**{bm['rating']}**")
        elif "Average" in bm["rating"]:
            st.warning(f"**{bm['rating']}**")
        else:
            st.error(f"**{bm['rating']}**")

        st.write(f"Your usage: **{bm['your_monthly_kwh']} kWh** | National avg: **{bm['average_monthly_kwh']} kWh** | Difference: **{bm['difference_pct']}%**")

        # Top consumers chart
        st.subheader("🔝 Top Energy Consumers")
        top = report["top_consumers"]
        if top:
            chart_data = {t["name"]: t["monthly_kwh"] for t in top}
            st.bar_chart(chart_data)

        # Category breakdown
        st.subheader("📂 Category Breakdown")
        cat_breakdown = report["category_breakdown"]
        if cat_breakdown:
            st.bar_chart(cat_breakdown)

        # Alerts
        flags = report["high_usage_flags"]
        if flags:
            st.subheader("⚠️ High Usage Alerts")
            for f in flags:
                color = "🔴" if f["severity"] == "CRITICAL" else "🟡"
                st.warning(
                    f"{color} **{f['appliance']}** [{f['severity']}]: "
                    f"Using {f['excess_kwh']} kWh/month extra → ₹{f['excess_cost_inr']}/month wasted\n\n"
                    f"💡 {f['tip']}"
                )
        else:
            st.success("✅ No high-usage alerts. Your appliance usage looks healthy!")

        # Savings potential
        sp = report["savings_potential"]
        st.subheader("💰 Savings Potential")
        c1, c2, c3 = st.columns(3)
        c1.metric("Conservative (10%)", f"₹{sp['conservative']['saving_inr']}/mo", f"{sp['conservative']['saving_kwh']} kWh saved")
        c2.metric("Moderate (20%)", f"₹{sp['moderate']['saving_inr']}/mo", f"{sp['moderate']['saving_kwh']} kWh saved")
        c3.metric("Aggressive (35%)", f"₹{sp['aggressive']['saving_inr']}/mo", f"{sp['aggressive']['saving_kwh']} kWh saved")

        # AI Narrative
        if st.button("🤖 Get AI-Powered Analysis Narrative (IBM Granite)"):
            with st.spinner("Generating analysis with IBM watsonx.ai..."):
                llm = get_llm()
                from utils.prompt_templates import build_analysis_prompt
                prompt = build_analysis_prompt(profile.to_dict(), report)
                narrative = llm.generate(prompt)
                st.markdown("### 🤖 AI Analysis Narrative")
                st.markdown(narrative)

# ── Page: Tips & Advice ────────────────────────────────────────────────────────
elif page == "💡 Tips & Advice":
    st.title("💡 Personalised Energy Saving Tips")
    if st.session_state.profile is None:
        st.info("For personalised tips, set up your profile. Showing general tips:")
        from modules.suggestions import get_quick_wins
        tips = get_quick_wins()
    else:
        report = run_analysis(st.session_state.profile)
        tips = get_personalised_tips(report)

    rate = st.session_state.profile.rate_per_kwh if st.session_state.profile else 7.5

    for i, tip in enumerate(tips, 1):
        saving_inr = round(tip.get("saving_kwh_monthly", 0) * rate, 2)
        priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(tip["priority"], "⚪")
        with st.expander(f"{priority_color} Tip {i}: {tip['tip'][:60]}..."):
            st.markdown(f"**{tip['tip']}**")
            c1, c2, c3 = st.columns(3)
            c1.metric("Category", tip["category"])
            c2.metric("Monthly Saving", f"~₹{saving_inr}", f"{tip.get('saving_kwh_monthly','?')} kWh")
            c3.metric("Effort", tip.get("effort", "N/A"))

    st.info(f"💡 **Energy Fact:** {get_random_fact()}")

# ── Page: Learn ────────────────────────────────────────────────────────────────
elif page == "📚 Learn":
    st.title("📚 Energy Education Hub")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["💡 Did You Know?", "🔍 Myths vs Facts", "⏰ Peak Hours", "🌡️ Seasonal Tips", "🌱 Carbon Impact"]
    )

    with tab1:
        st.subheader("Energy Facts")
        for fact in get_all_facts():
            st.info(f"💡 {fact}")

    with tab2:
        st.subheader("Common Energy Myths — Busted!")
        for myth in get_all_myths():
            with st.expander(f"❓ MYTH: {myth['myth']}"):
                st.success(f"✅ FACT: {myth['fact']}")

    with tab3:
        st.markdown(get_peak_hour_explanation())

    with tab4:
        season = st.selectbox("Select Season", ["summer", "winter", "monsoon"])
        tips = get_seasonal_tips(season)
        for i, tip in enumerate(tips, 1):
            st.write(f"**{i}.** {tip}")

    with tab5:
        kwh_input = st.number_input("Enter kWh to calculate CO₂ impact:", min_value=1.0, value=877.0)
        st.markdown(explain_carbon_impact(kwh_input))
        st.markdown(explain_kwh_in_simple_terms(kwh_input))

# ── Page: Appliance Calculator ─────────────────────────────────────────────────
elif page == "🔌 Appliance Calculator":
    st.title("🔌 Appliance Energy Calculator")
    st.markdown("Estimate the electricity consumption and cost of any appliance.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        appl_name = st.text_input("Appliance Name", value="Air Conditioner")
    with col2:
        wattage = st.number_input("Wattage (W)", min_value=1.0, value=1500.0)
    with col3:
        daily_hrs = st.number_input("Daily Usage (hours)", min_value=0.1, max_value=24.0, value=8.0, step=0.5)
    with col4:
        qty = st.number_input("Quantity", min_value=1, max_value=20, value=1)

    rate = st.slider("Electricity Rate (₹/kWh)", min_value=3.0, max_value=15.0, value=7.5, step=0.5)

    if st.button("⚡ Calculate", type="primary"):
        result = calculate_single_appliance(appl_name, wattage, daily_hrs, qty, rate)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Daily kWh",    f"{result['daily_kwh']} kWh")
        c2.metric("Monthly kWh",  f"{result['monthly_kwh']} kWh")
        c3.metric("Monthly Cost", f"₹{result['monthly_cost']}")
        c4.metric("Annual Cost",  f"₹{result['annual_cost']}")
        st.markdown("---")
        st.markdown(explain_kwh_in_simple_terms(result["monthly_kwh"]))
        st.markdown(explain_carbon_impact(result["monthly_kwh"]))

# ── Page: Chat ─────────────────────────────────────────────────────────────────
elif page == "💬 Chat with EnergyWise":
    st.title("💬 Chat with EnergyWise")
    st.caption("Powered by IBM watsonx.ai (Granite model)")

    # Display history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Suggested questions
    if not st.session_state.messages:
        st.markdown("**Try asking:**")
        cols = st.columns(2)
        suggestions = [
            "How can I reduce my electricity bill?",
            "What appliances use the most energy?",
            "Explain peak and off-peak electricity hours",
            "What is my carbon footprint?",
            "Give me energy saving tips for summer",
            "Is it a myth that ceiling fans cool rooms?",
        ]
        for i, s in enumerate(suggestions):
            if cols[i % 2].button(s, key=f"sug_{i}"):
                st.session_state.messages.append({"role": "user", "content": s})
                st.rerun()

    if user_input := st.chat_input("Ask anything about electricity and energy..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("EnergyWise is thinking..."):
                llm = get_llm()
                profile = st.session_state.profile
                household_summary = ""
                if profile:
                    household_summary = (
                        f"{profile.name} | {profile.city} | {profile.occupants} occupants | "
                        f"{profile.total_monthly_kwh} kWh/month | ₹{profile.monthly_bill}/month"
                    )
                history = "\n".join(
                    f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}"
                    for m in st.session_state.messages[-8:]
                )
                prompt = build_conversation_prompt(
                    user_question=user_input,
                    context=history,
                    household_summary=household_summary,
                )
                response = llm.generate(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption("⚡ EnergyWise AI Agent | Problem Statement 20 | Powered by IBM watsonx.ai (Granite) + IBM Langflow")
