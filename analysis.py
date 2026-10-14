"""
analysis.py
Energy Consumption Analysis Module.
Analyzes household electricity usage, detects high-consumption patterns,
and computes comparative benchmarks.
"""
import json
import os
from typing import Dict, List, Tuple

from modules.energy_models import HouseholdProfile, ApplianceUsage

# ── Load appliance reference data ─────────────────────────────────────────────
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

with open(os.path.join(_DATA_DIR, "appliances.json"), encoding="utf-8") as f:
    _APPLIANCE_DB = json.load(f)

AVERAGE_HOUSEHOLD_MONTHLY_KWH: float = _APPLIANCE_DB["average_household_monthly_kwh"]  # 877
COST_PER_KWH_INR: float = _APPLIANCE_DB["average_cost_per_kwh_inr"]


# ── Thresholds ─────────────────────────────────────────────────────────────────
HIGH_USAGE_MULTIPLIER = 1.3   # 30% above appliance baseline = high usage flag
CRITICAL_USAGE_MULTIPLIER = 2.0


def analyze_household(profile: HouseholdProfile) -> Dict:
    """
    Full consumption analysis for a household profile.
    Returns a structured report dict.
    """
    top5 = profile.top_consumers(5)
    category_breakdown = profile.category_breakdown()
    high_usage_appliances = _detect_high_usage(profile.appliances)
    benchmark = _benchmark_vs_average(profile)
    savings_potential = _estimate_savings_potential(profile.appliances)

    return {
        "summary": {
            "total_monthly_kwh":        profile.total_monthly_kwh,
            "monthly_bill_inr":         profile.monthly_bill,
            "carbon_footprint_kg":      profile.carbon_footprint_monthly_kg,
            "trees_needed_to_offset":   _trees_to_offset(profile.carbon_footprint_monthly_kg),
            "occupants":                profile.occupants,
            "kwh_per_person":           round(profile.total_monthly_kwh / max(profile.occupants, 1), 2),
        },
        "benchmark": benchmark,
        "top_consumers": [
            {
                "name":         a.name,
                "category":     a.category,
                "monthly_kwh":  a.monthly_kwh,
                "monthly_cost": a.cost(profile.rate_per_kwh)["monthly_cost"],
                "pct_of_total": round((a.monthly_kwh / max(profile.total_monthly_kwh, 1)) * 100, 1),
            }
            for a in top5
        ],
        "category_breakdown": category_breakdown,
        "high_usage_flags":   high_usage_appliances,
        "savings_potential":  savings_potential,
    }


def _detect_high_usage(appliances: List[ApplianceUsage]) -> List[Dict]:
    """
    Compare each appliance's usage against the reference database baseline.
    Flag appliances using significantly more than expected.
    """
    ref_map = {a["name"].lower(): a for a in _APPLIANCE_DB["appliances"]}
    flags = []
    for a in appliances:
        ref = ref_map.get(a.name.lower())
        if ref:
            baseline_monthly = ref["monthly_kwh"]
            if a.monthly_kwh >= baseline_monthly * CRITICAL_USAGE_MULTIPLIER:
                severity = "CRITICAL"
            elif a.monthly_kwh >= baseline_monthly * HIGH_USAGE_MULTIPLIER:
                severity = "HIGH"
            else:
                severity = None

            if severity:
                excess_kwh = round(a.monthly_kwh - baseline_monthly, 2)
                flags.append({
                    "appliance":     a.name,
                    "severity":      severity,
                    "your_monthly_kwh":   a.monthly_kwh,
                    "baseline_monthly_kwh": baseline_monthly,
                    "excess_kwh":    excess_kwh,
                    "excess_cost_inr": round(excess_kwh * COST_PER_KWH_INR, 2),
                    "tip":           ref.get("efficiency_tip", ""),
                })
    return sorted(flags, key=lambda x: x["excess_kwh"], reverse=True)


def _benchmark_vs_average(profile: HouseholdProfile) -> Dict:
    """
    Compare household total consumption against national average (877 kWh/month).
    """
    diff = profile.total_monthly_kwh - AVERAGE_HOUSEHOLD_MONTHLY_KWH
    diff_pct = round((diff / AVERAGE_HOUSEHOLD_MONTHLY_KWH) * 100, 1)

    if diff_pct <= -20:
        rating = "Excellent – You are a true energy champion! 🌟"
    elif diff_pct <= 0:
        rating = "Good – You are below the national average. Keep it up! ✅"
    elif diff_pct <= 25:
        rating = "Average – Some room for improvement. 🔶"
    elif diff_pct <= 60:
        rating = "High – Your consumption is significantly above average. ⚠️"
    else:
        rating = "Very High – Immediate action recommended. 🚨"

    return {
        "your_monthly_kwh":     profile.total_monthly_kwh,
        "average_monthly_kwh":  AVERAGE_HOUSEHOLD_MONTHLY_KWH,
        "difference_kwh":       round(diff, 2),
        "difference_pct":       diff_pct,
        "rating":               rating,
    }


def _estimate_savings_potential(appliances: List[ApplianceUsage]) -> Dict:
    """
    Estimate how much kWh and cost can be saved with best practices.
    Assumes a 15% improvement is achievable for most appliances.
    """
    total_monthly = sum(a.monthly_kwh for a in appliances)
    conservative_saving_kwh = round(total_monthly * 0.10, 2)
    moderate_saving_kwh     = round(total_monthly * 0.20, 2)
    aggressive_saving_kwh   = round(total_monthly * 0.35, 2)

    return {
        "conservative": {
            "saving_kwh":  conservative_saving_kwh,
            "saving_inr":  round(conservative_saving_kwh * COST_PER_KWH_INR, 2),
            "effort":      "Low – simple behavioural changes",
        },
        "moderate": {
            "saving_kwh":  moderate_saving_kwh,
            "saving_inr":  round(moderate_saving_kwh * COST_PER_KWH_INR, 2),
            "effort":      "Medium – scheduling + habit changes",
        },
        "aggressive": {
            "saving_kwh":  aggressive_saving_kwh,
            "saving_inr":  round(aggressive_saving_kwh * COST_PER_KWH_INR, 2),
            "effort":      "High – appliance upgrades + solar",
        },
    }


def _trees_to_offset(carbon_kg: float) -> int:
    """Number of trees needed to absorb monthly CO₂ (21 kg/tree/year → 1.75/tree/month)."""
    return max(1, round(carbon_kg / 1.75))


def get_appliance_info(appliance_name: str) -> Dict:
    """Look up reference data for a named appliance (case-insensitive)."""
    for a in _APPLIANCE_DB["appliances"]:
        if appliance_name.lower() in a["name"].lower():
            return a
    return {}


def calculate_single_appliance(name: str, wattage: float, daily_hours: float,
                                quantity: int = 1,
                                rate: float = COST_PER_KWH_INR) -> Dict:
    """Quick calculation for a single appliance without a full profile."""
    a = ApplianceUsage(name=name, wattage=wattage, daily_hours=daily_hours, quantity=quantity)
    costs = a.cost(rate)
    return {
        "name":            name,
        "wattage":         wattage,
        "daily_hours":     daily_hours,
        "quantity":        quantity,
        "daily_kwh":       a.daily_kwh,
        "monthly_kwh":     a.monthly_kwh,
        "annual_kwh":      a.annual_kwh,
        **costs,
        "carbon_monthly_kg": round(a.monthly_kwh * 0.82, 2),
    }
