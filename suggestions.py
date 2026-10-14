"""
suggestions.py
Energy Saving Suggestions Module.
Generates personalised, prioritised, actionable recommendations
for a household profile.
"""
import json
import os
from typing import Dict, List

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

with open(os.path.join(_DATA_DIR, "appliances.json"), encoding="utf-8") as f:
    _APPLIANCE_DB = json.load(f)


# ── General tips pool ──────────────────────────────────────────────────────────
_GENERAL_TIPS: List[Dict] = [
    {
        "id": "T001",
        "category": "Behaviour",
        "priority": "High",
        "tip": "Turn off lights, fans, and TVs when leaving any room.",
        "saving_kwh_monthly": 15,
        "effort": "Zero cost",
    },
    {
        "id": "T002",
        "category": "Behaviour",
        "priority": "High",
        "tip": "Unplug chargers, microwaves, and entertainment systems when not in use to eliminate phantom/standby load.",
        "saving_kwh_monthly": 20,
        "effort": "Zero cost",
    },
    {
        "id": "T003",
        "category": "Scheduling",
        "priority": "High",
        "tip": "Shift washing machine, dishwasher, and EV charging to off-peak hours (10 PM – 6 AM).",
        "saving_kwh_monthly": 12,
        "effort": "Zero cost – use timers",
    },
    {
        "id": "T004",
        "category": "Cooling",
        "priority": "High",
        "tip": "Raise AC thermostat from 18°C to 24°C. Each degree increase saves ~6% on cooling energy.",
        "saving_kwh_monthly": 54,
        "effort": "Zero cost",
    },
    {
        "id": "T005",
        "category": "Lighting",
        "priority": "High",
        "tip": "Replace all incandescent / CFL bulbs with LED equivalents.",
        "saving_kwh_monthly": 30,
        "effort": "Low cost – LED bulbs pay back in < 2 months",
    },
    {
        "id": "T006",
        "category": "Heating",
        "priority": "Medium",
        "tip": "Set water heater temperature to 49°C instead of 60°C+.",
        "saving_kwh_monthly": 25,
        "effort": "Zero cost",
    },
    {
        "id": "T007",
        "category": "Kitchen",
        "priority": "Medium",
        "tip": "Use pressure cookers and microwave ovens instead of electric stoves for 70% energy savings.",
        "saving_kwh_monthly": 18,
        "effort": "Zero cost if you already own them",
    },
    {
        "id": "T008",
        "category": "Laundry",
        "priority": "Medium",
        "tip": "Always wash full loads and use cold water settings.",
        "saving_kwh_monthly": 10,
        "effort": "Zero cost",
    },
    {
        "id": "T009",
        "category": "Electronics",
        "priority": "Medium",
        "tip": "Enable sleep/power-saving mode on computers, TVs, and gaming consoles.",
        "saving_kwh_monthly": 8,
        "effort": "Zero cost",
    },
    {
        "id": "T010",
        "category": "Upgrade",
        "priority": "Medium",
        "tip": "Upgrade to BEE 5-star rated appliances when replacing old ones (refrigerator, AC, washing machine).",
        "saving_kwh_monthly": 60,
        "effort": "Medium cost – long-term ROI is excellent",
    },
    {
        "id": "T011",
        "category": "Solar",
        "priority": "Low",
        "tip": "Install rooftop solar panels. A 3 kW system can generate 360–450 kWh/month in India.",
        "saving_kwh_monthly": 360,
        "effort": "High upfront – ROI in 5–7 years",
    },
    {
        "id": "T012",
        "category": "Monitoring",
        "priority": "Low",
        "tip": "Install a smart energy monitor to track real-time consumption per circuit.",
        "saving_kwh_monthly": 20,
        "effort": "Low cost – awareness drives 10–15% reduction",
    },
    {
        "id": "T013",
        "category": "Insulation",
        "priority": "Low",
        "tip": "Improve home insulation and seal air leaks around doors and windows.",
        "saving_kwh_monthly": 30,
        "effort": "Medium cost – reduces heating & cooling load by 15–20%",
    },
    {
        "id": "T014",
        "category": "Cooling",
        "priority": "Medium",
        "tip": "Use ceiling fans with AC — it spreads cool air so you can raise AC temperature by 2°C.",
        "saving_kwh_monthly": 24,
        "effort": "Zero cost",
    },
    {
        "id": "T015",
        "category": "Refrigeration",
        "priority": "Medium",
        "tip": "Do not place hot food directly in the refrigerator. Let it cool first.",
        "saving_kwh_monthly": 5,
        "effort": "Zero cost",
    },
]


def get_personalised_tips(analysis_report: Dict, max_tips: int = 8) -> List[Dict]:
    """
    Generate personalised, prioritised saving tips based on the household analysis.
    High-impact appliances get appliance-specific tips first; general tips fill the rest.
    """
    tips: List[Dict] = []

    # 1. Appliance-specific tips from high-usage flags
    for flag in analysis_report.get("high_usage_flags", []):
        if flag.get("tip"):
            tips.append({
                "id":         f"SPECIFIC-{flag['appliance'][:4].upper()}",
                "category":   "Appliance-Specific",
                "priority":   "High" if flag["severity"] == "CRITICAL" else "Medium",
                "tip":        f"[{flag['appliance']}] {flag['tip']}",
                "saving_kwh_monthly": round(flag["excess_kwh"] * 0.5, 1),
                "effort":     "Zero cost – usage adjustment",
                "source":     "Your Usage Pattern",
            })

    # 2. Category-based tips (top consuming categories)
    top_category = None
    breakdown = analysis_report.get("category_breakdown", {})
    if breakdown:
        top_category = next(iter(breakdown))

    category_map = {
        "Cooling":      ["T004", "T014"],
        "Heating":      ["T006"],
        "Kitchen":      ["T007", "T015"],
        "Laundry":      ["T008"],
        "Electronics":  ["T009"],
        "Lighting":     ["T005"],
    }

    tip_ids_added = set()
    if top_category and top_category in category_map:
        for tid in category_map[top_category]:
            t = _tip_by_id(tid)
            if t and t["id"] not in tip_ids_added:
                tips.append({**t, "source": f"Your top category: {top_category}"})
                tip_ids_added.add(t["id"])

    # 3. Fill with high-priority general tips
    for t in sorted(_GENERAL_TIPS, key=lambda x: ("High", "Medium", "Low").index(x["priority"])):
        if len(tips) >= max_tips:
            break
        if t["id"] not in tip_ids_added:
            tips.append({**t, "source": "General Best Practice"})
            tip_ids_added.add(t["id"])

    return tips[:max_tips]


def get_quick_wins() -> List[Dict]:
    """Return zero-cost, immediately actionable tips (quick wins)."""
    return [t for t in _GENERAL_TIPS if "Zero cost" in t.get("effort", "")]


def get_tips_by_category(category: str) -> List[Dict]:
    """Filter tips by category name (case-insensitive)."""
    return [t for t in _GENERAL_TIPS
            if category.lower() in t["category"].lower()]


def format_tips_as_text(tips: List[Dict], rate_per_kwh: float = 7.5) -> str:
    """Format a list of tips as a human-readable string."""
    lines = ["### 💡 Energy Saving Recommendations\n"]
    for i, tip in enumerate(tips, 1):
        saving_inr = round(tip.get("saving_kwh_monthly", 0) * rate_per_kwh, 2)
        lines.append(
            f"**{i}. {tip['tip']}**\n"
            f"   • Category: {tip['category']} | Priority: {tip['priority']}\n"
            f"   • Potential saving: ~{tip.get('saving_kwh_monthly', '?')} kWh/month "
            f"(~₹{saving_inr}/month)\n"
            f"   • Effort: {tip.get('effort', 'N/A')}\n"
        )
    return "\n".join(lines)


def _tip_by_id(tip_id: str) -> Dict:
    for t in _GENERAL_TIPS:
        if t["id"] == tip_id:
            return t
    return {}
