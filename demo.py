"""
demo.py
EnergyWise AI Agent — Demonstration Script (no watsonx.ai credentials required).
Showcases all modules: profile creation, analysis, education, suggestions.
Run: python demo.py (from inside energy_agent/)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.energy_models import HouseholdProfile, ApplianceUsage
from modules.analysis import analyze_household, calculate_single_appliance
from modules.education import (
    get_random_fact, explain_kwh_in_simple_terms, explain_carbon_impact,
    explain_bill_breakdown, get_peak_hour_explanation, get_myth_fact,
)
from modules.suggestions import get_personalised_tips, format_tips_as_text


def separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def main():
    print("\n⚡  EnergyWise AI Agent — Demo Run")
    print("    (Rule-based modules — no watsonx.ai credentials needed)")

    # ── 1. Build a sample household profile ──────────────────────────────────
    separator("1. Household Profile")
    profile = HouseholdProfile(
        name="Sharma Family", city="Bangalore", occupants=4, rate_per_kwh=7.5
    )
    profile.add_appliance(ApplianceUsage("Air Conditioner",        1500, 10, 1, "Cooling"))
    profile.add_appliance(ApplianceUsage("Refrigerator",           150,  24, 1, "Kitchen"))
    profile.add_appliance(ApplianceUsage("Water Heater (Electric)",4000,  3, 1, "Heating"))
    profile.add_appliance(ApplianceUsage("Washing Machine",        500,   1, 1, "Laundry"))
    profile.add_appliance(ApplianceUsage("LED TV",                 100,   6, 2, "Electronics"))
    profile.add_appliance(ApplianceUsage("Ceiling Fan",            75,   12, 4, "Cooling"))
    profile.add_appliance(ApplianceUsage("LED Bulb (10W)",         10,    6, 10,"Lighting"))
    profile.add_appliance(ApplianceUsage("Laptop",                 50,    8, 2, "Electronics"))
    profile.add_appliance(ApplianceUsage("Desktop Computer",       200,   4, 1, "Electronics"))
    profile.add_appliance(ApplianceUsage("Electric Iron",          1000, 0.5,1, "Appliances"))

    print(f"  Household : {profile.name}, {profile.city}")
    print(f"  Occupants : {profile.occupants}")
    print(f"  Appliances: {len(profile.appliances)}")
    print(f"  Monthly   : {profile.total_monthly_kwh} kWh | ₹{profile.monthly_bill}")
    print(f"  CO₂       : {profile.carbon_footprint_monthly_kg} kg/month")

    # ── 2. Consumption Analysis ───────────────────────────────────────────────
    separator("2. Energy Consumption Analysis")
    report = analyze_household(profile)

    bm = report["benchmark"]
    print(f"  Rating    : {bm['rating']}")
    print(f"  vs Avg    : {bm['difference_pct']}% {'above' if bm['difference_pct']>0 else 'below'} national average")

    print("\n  Top Energy Consumers:")
    for c in report["top_consumers"]:
        bar = "█" * int(c["pct_of_total"] / 2)
        print(f"    {c['name']:<30} {c['monthly_kwh']:>6.1f} kWh  {bar} {c['pct_of_total']}%")

    if report["high_usage_flags"]:
        print("\n  ⚠️  High Usage Alerts:")
        for f in report["high_usage_flags"]:
            print(f"    [{f['severity']}] {f['appliance']}: +{f['excess_kwh']} kWh/month excess → ₹{f['excess_cost_inr']} wasted")

    sp = report["savings_potential"]
    print(f"\n  Savings Potential:")
    print(f"    Conservative: {sp['conservative']['saving_kwh']} kWh → ₹{sp['conservative']['saving_inr']}/month")
    print(f"    Moderate    : {sp['moderate']['saving_kwh']} kWh → ₹{sp['moderate']['saving_inr']}/month")
    print(f"    Aggressive  : {sp['aggressive']['saving_kwh']} kWh → ₹{sp['aggressive']['saving_inr']}/month")

    # ── 3. Education Module ───────────────────────────────────────────────────
    separator("3. User Education")
    print("\n  [Bill Explained]")
    print(explain_bill_breakdown(profile.total_monthly_kwh, profile.rate_per_kwh))

    print("\n  [Carbon Impact]")
    print(explain_carbon_impact(profile.total_monthly_kwh))

    print("\n  [kWh in Simple Terms]")
    print(explain_kwh_in_simple_terms(100))

    print("\n  [Did You Know?]")
    print(f"  💡 {get_random_fact()}")

    myth = get_myth_fact()
    print(f"\n  [Myth vs Fact]")
    print(f"  MYTH : {myth['myth']}")
    print(f"  FACT : {myth['fact']}")

    print("\n  [Peak Hours Guide]")
    print(get_peak_hour_explanation())

    # ── 4. Personalised Tips ──────────────────────────────────────────────────
    separator("4. Personalised Energy Saving Recommendations")
    tips = get_personalised_tips(report, max_tips=6)
    print(format_tips_as_text(tips, rate_per_kwh=profile.rate_per_kwh))

    # ── 5. Single Appliance Calculator ───────────────────────────────────────
    separator("5. Appliance Calculator — AC at 24°C vs 18°C")
    ac_24 = calculate_single_appliance("AC at 24°C", 1200, 10, rate=7.5)
    ac_18 = calculate_single_appliance("AC at 18°C", 1800, 10, rate=7.5)
    print(f"  AC at 24°C: {ac_24['monthly_kwh']} kWh/month | ₹{ac_24['monthly_cost']}")
    print(f"  AC at 18°C: {ac_18['monthly_kwh']} kWh/month | ₹{ac_18['monthly_cost']}")
    saving = ac_18['monthly_cost'] - ac_24['monthly_cost']
    print(f"  💰 Raising thermostat from 18°C → 24°C saves ₹{round(saving,2)}/month!")

    separator("Demo Complete ✅")
    print("  Run 'python agent.py' for interactive CLI chat.")
    print("  Run 'streamlit run app_ui.py' for the web UI.")
    print("  Configure .env with IBM watsonx.ai credentials to enable AI responses.\n")


if __name__ == "__main__":
    main()
