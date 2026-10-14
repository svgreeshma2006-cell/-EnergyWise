"""
agent.py
EnergyWise AI Agent — Core Conversational Engine.
Orchestrates: analysis → education → suggestions → IBM watsonx LLM response.
"""
import uuid
import sys
import os

# Load .env credentials automatically
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass  # python-dotenv not installed; environment variables must be set manually

# Make imports work from any working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.energy_models import (
    HouseholdProfile, ApplianceUsage, ConversationSession
)
from modules.analysis import analyze_household, calculate_single_appliance
from modules.education import (
    get_random_fact, explain_kwh_in_simple_terms, explain_carbon_impact,
    explain_bill_breakdown, get_peak_hour_explanation, get_seasonal_tips,
    get_myth_fact, get_all_myths
)
from modules.suggestions import (
    get_personalised_tips, get_quick_wins, format_tips_as_text
)
from utils.watsonx_client import get_watsonx_client
from utils.prompt_templates import (
    build_analysis_prompt, build_conversation_prompt,
    build_tip_explanation_prompt, build_quiz_prompt
)


class EnergyWiseAgent:
    """
    Main AI Agent for Electricity Consumption Awareness.
    Supports both programmatic API use and interactive CLI chat.
    """

    def __init__(self):
        self.session = ConversationSession(session_id=str(uuid.uuid4()))
        self.llm = get_watsonx_client()
        self._analysis_cache: dict = {}

        print("\n" + "=" * 60)
        print("  ⚡ EnergyWise AI Agent — Electricity Consumption Advisor")
        print("=" * 60)
        if self.llm.is_ready:
            print("  ✅ IBM watsonx.ai connected (IBM Granite model active)")
        else:
            print("  ⚠️  IBM watsonx.ai not connected — rule-based mode active")
            print("     (Configure .env to enable AI-powered responses)")
        print("=" * 60 + "\n")

    # ── Profile Setup ──────────────────────────────────────────────────────────

    def set_household_profile(self, profile: HouseholdProfile):
        """Attach a household profile to the session."""
        self.session.household_profile = profile
        self._analysis_cache = {}  # Invalidate cache

    def create_profile_interactively(self) -> HouseholdProfile:
        """CLI wizard to build a household profile step by step."""
        print("📋 Let's set up your household profile.\n")
        name      = input("  Your name / household name: ").strip() or "My Home"
        city      = input("  City: ").strip() or "India"
        occupants = int(input("  Number of occupants: ").strip() or "3")
        rate      = float(input("  Electricity rate ₹/kWh [default 7.5]: ").strip() or "7.5")

        profile = HouseholdProfile(
            name=name, city=city, occupants=occupants, rate_per_kwh=rate
        )

        print("\n📱 Now let's add your appliances. Press Enter to skip any appliance.\n")
        print("  (Tip: Common ones — Air Conditioner, Refrigerator, Water Heater,")
        print("   Washing Machine, TV, Computer, Lights, Ceiling Fan)\n")

        while True:
            appl_name = input("  Appliance name (or 'done' to finish): ").strip()
            if appl_name.lower() in ("done", ""):
                break
            try:
                wattage    = float(input(f"  Wattage of {appl_name} (W): ").strip())
                daily_hrs  = float(input(f"  Daily hours of use: ").strip())
                qty        = int(input(f"  Quantity [1]: ").strip() or "1")
                category   = input(f"  Category (Cooling/Heating/Kitchen/etc.) [General]: ").strip() or "General"
                profile.add_appliance(
                    ApplianceUsage(name=appl_name, wattage=wattage,
                                   daily_hours=daily_hrs, quantity=qty,
                                   category=category)
                )
                print(f"  ✅ Added: {appl_name} ({daily_hrs}h/day × {wattage}W × {qty})\n")
            except ValueError:
                print("  ⚠️  Invalid input, skipping this appliance.\n")

        self.set_household_profile(profile)
        return profile

    # ── Analysis ───────────────────────────────────────────────────────────────

    def run_analysis(self) -> dict:
        """Analyse the current household profile and return full report."""
        if not self.session.household_profile:
            return {"error": "No household profile set. Use set_household_profile() first."}
        if not self._analysis_cache:
            self._analysis_cache = analyze_household(self.session.household_profile)
        return self._analysis_cache

    def get_analysis_summary_text(self) -> str:
        """Return a human-readable analysis using IBM watsonx.ai LLM."""
        profile = self.session.household_profile
        if not profile:
            return "Please set up a household profile first."
        report = self.run_analysis()
        prompt = build_analysis_prompt(profile.to_dict(), report)
        return self.llm.generate(prompt)

    # ── Suggestions ────────────────────────────────────────────────────────────

    def get_tips(self, max_tips: int = 8) -> str:
        """Return personalised energy saving tips as formatted text."""
        report = self.run_analysis()
        if "error" in report:
            tips = get_quick_wins()
        else:
            tips = get_personalised_tips(report, max_tips)
        rate = (self.session.household_profile.rate_per_kwh
                if self.session.household_profile else 7.5)
        return format_tips_as_text(tips, rate)

    # ── Education ──────────────────────────────────────────────────────────────

    def explain_my_bill(self) -> str:
        profile = self.session.household_profile
        if not profile:
            return "Please set up your household profile first."
        return explain_bill_breakdown(profile.total_monthly_kwh, profile.rate_per_kwh)

    def explain_carbon_impact_for_profile(self) -> str:
        profile = self.session.household_profile
        if not profile:
            return "Please set up your household profile first."
        return explain_carbon_impact(profile.total_monthly_kwh)

    def get_fact(self) -> str:
        return f"💡 **Did You Know?**\n{get_random_fact()}"

    def get_myth_busting(self) -> str:
        myth = get_myth_fact()
        return (f"### 🔍 Myth vs Fact\n\n"
                f"**MYTH:** {myth['myth']}\n\n"
                f"**FACT:** {myth['fact']}")

    def explain_peak_hours(self) -> str:
        return get_peak_hour_explanation()

    def get_seasonal_advice(self, season: str = "summer") -> str:
        tips = get_seasonal_tips(season)
        header = f"### 🌡️ Energy Tips for {season.capitalize()}\n"
        return header + "\n".join(f"  {i+1}. {t}" for i, t in enumerate(tips))

    def calculate_appliance(self, name: str, wattage: float,
                             daily_hours: float, qty: int = 1) -> str:
        result = calculate_single_appliance(name, wattage, daily_hours, qty,
                                            rate=self.session.household_profile.rate_per_kwh
                                            if self.session.household_profile else 7.5)
        return (
            f"### 🔌 {name} — Consumption Estimate\n\n"
            f"| Metric          | Value              |\n"
            f"|-----------------|--------------------|\n"
            f"| Wattage         | {result['wattage']} W         |\n"
            f"| Daily Use       | {result['daily_hours']} hours      |\n"
            f"| Daily kWh       | {result['daily_kwh']} kWh      |\n"
            f"| Monthly kWh     | {result['monthly_kwh']} kWh      |\n"
            f"| Monthly Cost    | ₹{result['monthly_cost']}         |\n"
            f"| Annual Cost     | ₹{result['annual_cost']}        |\n"
            f"| CO₂ (monthly)   | {result['carbon_monthly_kg']} kg       |\n\n"
            + explain_kwh_in_simple_terms(result['monthly_kwh'])
        )

    # ── Conversational Chat ────────────────────────────────────────────────────

    def chat(self, user_input: str) -> str:
        """
        Main conversational interface. Routes the user's question to the
        most appropriate handler and enriches the response with LLM when available.
        """
        user_input_lower = user_input.lower()
        self.session.add_message("user", user_input)

        # ── Intent routing ──────────────────────────────────────────────────
        response = None

        if any(k in user_input_lower for k in ["analyse", "analyze", "report", "summary", "consumption"]):
            response = self.get_analysis_summary_text()

        elif any(k in user_input_lower for k in ["tip", "suggest", "recommend", "save", "reduce"]):
            response = self.get_tips()

        elif any(k in user_input_lower for k in ["bill", "cost", "rupee", "price", "money"]):
            response = self.explain_my_bill()

        elif any(k in user_input_lower for k in ["carbon", "co2", "emission", "footprint", "environment"]):
            response = self.explain_carbon_impact_for_profile()

        elif any(k in user_input_lower for k in ["peak", "off-peak", "time", "when to use"]):
            response = self.explain_peak_hours()

        elif any(k in user_input_lower for k in ["myth", "fact", "true", "false", "misconception"]):
            response = self.get_myth_busting()

        elif any(k in user_input_lower for k in ["summer", "winter", "monsoon", "season"]):
            if "winter" in user_input_lower:
                response = self.get_seasonal_advice("winter")
            elif "monsoon" in user_input_lower:
                response = self.get_seasonal_advice("monsoon")
            else:
                response = self.get_seasonal_advice("summer")

        elif any(k in user_input_lower for k in ["fact", "know", "learn", "educate"]):
            response = self.get_fact()

        elif any(k in user_input_lower for k in ["quiz", "question", "test me"]):
            prompt = build_quiz_prompt()
            response = self.llm.generate(prompt)

        else:
            # General Q&A via LLM
            household_summary = ""
            if self.session.household_profile:
                p = self.session.household_profile
                household_summary = (
                    f"{p.name} | {p.city} | {p.occupants} occupants | "
                    f"{p.total_monthly_kwh} kWh/month | ₹{p.monthly_bill}/month bill"
                )
            prompt = build_conversation_prompt(
                user_question=user_input,
                context=self.session.get_history_text(max_turns=4),
                household_summary=household_summary,
            )
            response = self.llm.generate(prompt)

        self.session.add_message("assistant", response)
        return response

    # ── Interactive CLI ────────────────────────────────────────────────────────

    def run_interactive(self):
        """
        Launch an interactive CLI chat session.
        """
        print("Welcome to EnergyWise! ⚡ I'm here to help you understand")
        print("and reduce your household electricity consumption.\n")
        print("Commands you can try:")
        print("  • 'setup'    — Set up your household profile")
        print("  • 'analyse'  — Get a full consumption analysis")
        print("  • 'tips'     — Get personalised saving recommendations")
        print("  • 'bill'     — Understand your electricity bill")
        print("  • 'carbon'   — Learn about your CO₂ footprint")
        print("  • 'myth'     — Bust an energy myth")
        print("  • 'peak'     — Learn about peak/off-peak hours")
        print("  • 'fact'     — Get a random energy fact")
        print("  • 'quiz'     — Test your energy knowledge")
        print("  • 'quit'     — Exit\n")
        print("-" * 60)

        while True:
            try:
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("quit", "exit", "bye"):
                    print("\nAssistant: Goodbye! Remember — every kWh saved counts. 🌱")
                    break
                if user_input.lower() == "setup":
                    self.create_profile_interactively()
                    print("\nAssistant: Profile created! Ask me anything about your energy usage.")
                    continue

                response = self.chat(user_input)
                print(f"\nAssistant: {response}")
            except KeyboardInterrupt:
                print("\n\nAssistant: Session ended. Stay energy-smart! ⚡")
                break


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = EnergyWiseAgent()
    agent.run_interactive()
