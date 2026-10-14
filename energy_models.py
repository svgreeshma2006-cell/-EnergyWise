"""
energy_models.py
Data models for the Electricity Consumption Awareness AI Agent.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class ApplianceUsage:
    """Represents a single appliance and its usage pattern."""
    name: str
    wattage: float                   # Watts
    daily_hours: float               # Hours per day
    quantity: int = 1
    category: str = "General"

    @property
    def daily_kwh(self) -> float:
        """Energy consumed per day in kWh."""
        return (self.wattage * self.daily_hours * self.quantity) / 1000

    @property
    def monthly_kwh(self) -> float:
        """Energy consumed per month (30 days) in kWh."""
        return self.daily_kwh * 30

    @property
    def annual_kwh(self) -> float:
        """Energy consumed per year in kWh."""
        return self.daily_kwh * 365

    def cost(self, rate_per_kwh: float = 7.5) -> Dict[str, float]:
        """Calculate cost for daily, monthly, and annual periods."""
        return {
            "daily_cost":   round(self.daily_kwh * rate_per_kwh, 2),
            "monthly_cost": round(self.monthly_kwh * rate_per_kwh, 2),
            "annual_cost":  round(self.annual_kwh * rate_per_kwh, 2),
        }


@dataclass
class HouseholdProfile:
    """Represents the full electricity consumption profile of a household."""
    name: str
    city: str
    occupants: int
    appliances: List[ApplianceUsage] = field(default_factory=list)
    rate_per_kwh: float = 7.5        # INR per kWh (default India average)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_appliance(self, appliance: ApplianceUsage):
        self.appliances.append(appliance)

    @property
    def total_daily_kwh(self) -> float:
        return round(sum(a.daily_kwh for a in self.appliances), 2)

    @property
    def total_monthly_kwh(self) -> float:
        return round(sum(a.monthly_kwh for a in self.appliances), 2)

    @property
    def total_annual_kwh(self) -> float:
        return round(sum(a.annual_kwh for a in self.appliances), 2)

    @property
    def monthly_bill(self) -> float:
        return round(self.total_monthly_kwh * self.rate_per_kwh, 2)

    @property
    def carbon_footprint_monthly_kg(self) -> float:
        """CO₂ emissions in kg based on India's grid emission factor (0.82 kg/kWh)."""
        return round(self.total_monthly_kwh * 0.82, 2)

    def top_consumers(self, n: int = 5) -> List[ApplianceUsage]:
        """Return the top N appliances by monthly kWh consumption."""
        return sorted(self.appliances, key=lambda a: a.monthly_kwh, reverse=True)[:n]

    def category_breakdown(self) -> Dict[str, float]:
        """Return monthly kWh grouped by category."""
        breakdown: Dict[str, float] = {}
        for a in self.appliances:
            breakdown[a.category] = round(
                breakdown.get(a.category, 0) + a.monthly_kwh, 2
            )
        return dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))

    def to_dict(self) -> dict:
        return {
            "name":             self.name,
            "city":             self.city,
            "occupants":        self.occupants,
            "rate_per_kwh":     self.rate_per_kwh,
            "total_daily_kwh":  self.total_daily_kwh,
            "total_monthly_kwh":self.total_monthly_kwh,
            "total_annual_kwh": self.total_annual_kwh,
            "monthly_bill_inr": self.monthly_bill,
            "carbon_footprint_monthly_kg": self.carbon_footprint_monthly_kg,
            "appliances": [
                {
                    "name":         a.name,
                    "category":     a.category,
                    "wattage":      a.wattage,
                    "daily_hours":  a.daily_hours,
                    "quantity":     a.quantity,
                    "monthly_kwh":  a.monthly_kwh,
                }
                for a in self.appliances
            ],
        }


@dataclass
class ConversationMessage:
    """A single message in the agent conversation."""
    role: str       # 'user' or 'assistant'
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ConversationSession:
    """Full conversation session with context."""
    session_id: str
    messages: List[ConversationMessage] = field(default_factory=list)
    household_profile: Optional[HouseholdProfile] = None

    def add_message(self, role: str, content: str):
        self.messages.append(ConversationMessage(role=role, content=content))

    def get_history_text(self, max_turns: int = 6) -> str:
        """Return recent conversation history as a formatted string."""
        recent = self.messages[-(max_turns * 2):]
        lines = []
        for msg in recent:
            prefix = "User" if msg.role == "user" else "Assistant"
            lines.append(f"{prefix}: {msg.content}")
        return "\n".join(lines)
