"""
prompt_templates.py
System and user prompt templates for the IBM Granite LLM agent.
All prompts follow IBM Granite's instruction-following format.
"""

# ── System Prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are EnergyWise, an expert AI Agent for Electricity Consumption Awareness.
You help household users understand their electricity usage, identify wasteful habits,
and adopt energy-efficient practices.

Your capabilities:
1. Analyse household electricity consumption data and identify high-usage areas.
2. Explain energy concepts in simple, jargon-free language.
3. Provide practical, prioritised energy-saving recommendations.
4. Answer questions about appliances, bills, carbon footprint, and electricity tariffs.
5. Motivate users with relatable comparisons and progress tracking.

Guidelines:
- Always be friendly, encouraging, and non-judgmental.
- Use specific numbers and comparisons to make advice tangible.
- Prioritise zero-cost behavioural tips first, then low-cost upgrades, then investments.
- Reference the user's actual appliance data when available.
- Keep responses concise but complete (100–250 words unless detail is requested).
- End every response with one actionable next step the user can take today.
"""


def build_analysis_prompt(household_dict: dict, analysis_report: dict) -> str:
    """
    Build a prompt asking the LLM to narrate the household analysis results
    in a friendly, educational tone.
    """
    top_consumers = analysis_report.get("top_consumers", [])
    flags = analysis_report.get("high_usage_flags", [])
    benchmark = analysis_report.get("benchmark", {})
    savings = analysis_report.get("savings_potential", {})

    top_str = "\n".join(
        f"  - {c['name']}: {c['monthly_kwh']} kWh/month ({c['pct_of_total']}% of total)"
        for c in top_consumers
    )
    flag_str = "\n".join(
        f"  - {f['appliance']} [{f['severity']}]: using {f['excess_kwh']} kWh/month extra"
        for f in flags[:3]
    ) or "  - No critical high-usage appliances detected."

    return f"""{SYSTEM_PROMPT}

### Household Data
- Name: {household_dict.get('name')}
- City: {household_dict.get('city')}
- Occupants: {household_dict.get('occupants')}
- Total Monthly Consumption: {household_dict.get('total_monthly_kwh')} kWh
- Monthly Bill: ₹{household_dict.get('monthly_bill_inr')}
- Carbon Footprint: {household_dict.get('carbon_footprint_monthly_kg')} kg CO₂/month
- Benchmark Rating: {benchmark.get('rating', 'N/A')}

### Top Energy Consumers
{top_str}

### High Usage Alerts
{flag_str}

### Savings Potential
- Conservative (10%): {savings.get('conservative', {}).get('saving_kwh', 0)} kWh → ₹{savings.get('conservative', {}).get('saving_inr', 0)}/month saved
- Moderate (20%): {savings.get('moderate', {}).get('saving_kwh', 0)} kWh → ₹{savings.get('moderate', {}).get('saving_inr', 0)}/month saved

### Task
Write a friendly, motivating 3-paragraph energy consumption summary for this household.
Paragraph 1: Overall picture (bill, benchmark, carbon impact with relatable analogy).
Paragraph 2: Key problem areas and why they matter.
Paragraph 3: Top 3 actions they can take starting TODAY.
"""


def build_conversation_prompt(user_question: str, context: str,
                               household_summary: str = "") -> str:
    """
    Build a conversational Q&A prompt with optional household context
    and recent conversation history.
    """
    household_section = ""
    if household_summary:
        household_section = f"\n### User's Household Profile\n{household_summary}\n"

    history_section = ""
    if context:
        history_section = f"\n### Recent Conversation\n{context}\n"

    return f"""{SYSTEM_PROMPT}
{household_section}{history_section}
### User Question
{user_question}

### Your Response
"""


def build_tip_explanation_prompt(tip: str, appliance: str = "") -> str:
    """Build a prompt to explain WHY a specific tip saves energy."""
    context = f" for the appliance: {appliance}" if appliance else ""
    return f"""{SYSTEM_PROMPT}

A user wants to understand the following energy-saving tip{context}:

"{tip}"

Explain in 3–5 sentences:
1. WHY this tip saves energy (the physics/mechanism).
2. HOW MUCH energy it saves (give an estimate in kWh or % if possible).
3. ANY common mistakes people make that cancel out this tip.
"""


def build_quiz_prompt(topic: str = "electricity saving") -> str:
    """Generate an educational quiz question on the given topic."""
    return f"""{SYSTEM_PROMPT}

Create ONE multiple-choice quiz question about '{topic}' to test the user's knowledge.
Format:
Question: <question text>
A) <option>
B) <option>
C) <option>
D) <option>
Correct Answer: <letter>
Explanation: <1–2 sentence explanation of the correct answer>
"""
