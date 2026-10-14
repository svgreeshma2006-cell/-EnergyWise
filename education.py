"""
education.py
User Awareness & Education Module.
Provides energy facts, myth-busting, carbon awareness, and
plain-language explanations of consumption patterns.
"""
import json
import os
import random
from typing import Dict, List, Optional

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

with open(os.path.join(_DATA_DIR, "energy_facts.json"), encoding="utf-8") as f:
    _FACTS = json.load(f)

CARBON_FACTOR = _FACTS["carbon_factor_kg_per_kwh"]           # 0.82 kg CO₂/kWh
TREE_ABSORPTION = _FACTS["tree_absorption_kg_co2_per_year"]  # 21 kg/tree/year


# ── Public API ─────────────────────────────────────────────────────────────────

def get_random_fact() -> str:
    """Return a random 'Did You Know?' energy fact."""
    return random.choice(_FACTS["did_you_know"])


def get_all_facts() -> List[str]:
    """Return all energy facts."""
    return _FACTS["did_you_know"]


def get_myth_fact(index: Optional[int] = None) -> Dict:
    """Return a myth vs fact entry. Random if index is None."""
    myths = _FACTS["myths_vs_facts"]
    if index is not None and 0 <= index < len(myths):
        return myths[index]
    return random.choice(myths)


def get_all_myths() -> List[Dict]:
    """Return all myth vs fact pairs."""
    return _FACTS["myths_vs_facts"]


def explain_kwh_in_simple_terms(kwh: float) -> str:
    """
    Convert a kWh value into relatable everyday comparisons.
    Helps non-technical users understand energy in human terms.
    """
    smartphone_charges = round(kwh / 0.012)          # ~12 Wh per charge
    led_hours = round(kwh / 0.010)                   # 10W LED
    tv_hours = round(kwh / 0.100)                    # 100W TV
    laptop_hours = round(kwh / 0.050)                # 50W laptop
    fan_hours = round(kwh / 0.075)                   # 75W ceiling fan

    return (
        f"**{kwh} kWh** is equivalent to:\n"
        f"  • Charging a smartphone **{smartphone_charges} times**\n"
        f"  • Running a 10W LED bulb for **{led_hours} hours**\n"
        f"  • Watching TV (55\" LED) for **{tv_hours} hours**\n"
        f"  • Using a laptop for **{laptop_hours} hours**\n"
        f"  • Running a ceiling fan for **{fan_hours} hours**"
    )


def explain_carbon_impact(kwh: float) -> str:
    """
    Translate kWh to CO₂ impact with relatable analogies.
    """
    co2_kg = round(kwh * CARBON_FACTOR, 2)
    trees_monthly = round(co2_kg / (TREE_ABSORPTION / 12), 1)
    car_km = round(co2_kg / 0.21)   # average car emits ~210 g CO₂/km

    return (
        f"**{kwh} kWh** of electricity generates approximately **{co2_kg} kg of CO₂**.\n\n"
        f"To put that in perspective:\n"
        f"  🌳 You would need **{trees_monthly} trees** to absorb this CO₂ in a month.\n"
        f"  🚗 It's equivalent to driving a car for **{car_km} km**.\n\n"
        f"  *Every kWh saved = {CARBON_FACTOR} kg less CO₂ released into the atmosphere.*"
    )


def explain_bill_breakdown(monthly_kwh: float, rate_per_kwh: float = 7.5) -> str:
    """
    Explain a monthly electricity bill in simple terms with daily breakdowns.
    """
    monthly_bill = round(monthly_kwh * rate_per_kwh, 2)
    daily_kwh = round(monthly_kwh / 30, 2)
    daily_bill = round(daily_kwh * rate_per_kwh, 2)
    hourly_cost = round(daily_bill / 24, 2)

    return (
        f"### 💡 Your Monthly Bill Explained\n\n"
        f"| Period   | Units (kWh) | Cost (₹)   |\n"
        f"|----------|-------------|------------|\n"
        f"| Per Hour | {round(daily_kwh/24,3)}        | ₹{hourly_cost}   |\n"
        f"| Per Day  | {daily_kwh}        | ₹{daily_bill}  |\n"
        f"| Per Month| {monthly_kwh}       | ₹{monthly_bill} |\n\n"
        f"At ₹{rate_per_kwh}/kWh, every **1 kWh saved = ₹{rate_per_kwh} saved**."
    )


def get_peak_hour_explanation() -> str:
    """Explain what peak and off-peak electricity hours mean."""
    return (
        "### ⏰ Understanding Peak & Off-Peak Hours\n\n"
        "**Peak Hours** (6–9 AM & 5–9 PM) are when electricity demand is highest.\n"
        "  • The grid is under stress → higher cost on time-of-use tariffs.\n"
        "  • Avoid running heavy appliances (washing machine, dishwasher, EV charger) during this time.\n\n"
        "**Off-Peak Hours** (10 PM – 6 AM) are the best times to run energy-hungry appliances:\n"
        "  • Lower electricity rates on ToU tariffs.\n"
        "  • Less carbon-intensive as renewables have higher share at night in many grids.\n\n"
        "💡 **Tip:** Use smart plugs or appliance timers to automatically shift loads to off-peak hours."
    )


def get_seasonal_tips(season: str = "summer") -> List[str]:
    """Return seasonal energy-saving tips."""
    tips = {
        "summer": [
            "Set AC to 24–26°C — each degree lower increases consumption by 6%.",
            "Use blackout curtains to block heat; reduces AC workload by 15%.",
            "Run refrigerators in cooler parts of the kitchen, away from direct sunlight.",
            "Pre-cool your home in the morning before peak heat of the day.",
            "Switch to cold-water washing — clothes come just as clean.",
        ],
        "winter": [
            "Set space heaters to 20°C — each degree higher adds 7% to heating bills.",
            "Seal window and door drafts to prevent heat loss.",
            "Use thick curtains at night to retain warmth.",
            "Use energy-efficient heat pumps instead of resistive electric heaters.",
            "Wear an extra layer before turning up the heater.",
        ],
        "monsoon": [
            "Dehumidifiers increase consumption — use cross-ventilation instead.",
            "Use natural drying racks instead of clothes dryers when possible.",
            "Check for water ingress that can damage appliance efficiency.",
            "Run ceiling fans instead of AC when temperature is mild.",
        ],
    }
    return tips.get(season.lower(), tips["summer"])


def get_saving_goals_info() -> Dict:
    """Return the three energy-saving goal tiers."""
    return _FACTS["energy_saving_goals"]
