# EnergyWise — AI Agent for Electricity Consumption Awareness

> **Problem Statement #20** | IBM Langflow / IBM Orchestrate + IBM Granite (watsonx.ai)

---

## Overview

**EnergyWise** is an AI-powered conversational agent that helps household users:

1. 📊 **Analyse** their electricity consumption and identify high-usage areas
2. 📚 **Understand** how daily activities and appliances affect their energy bill
3. 💡 **Receive** personalised, actionable energy-saving recommendations
4. 💬 **Chat** with an IBM Granite-powered conversational assistant

---

## Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│              EnergyWise AI Agent (agent.py)              │
│                                                          │
│  ┌──────────────┐   ┌──────────────┐  ┌──────────────┐  │
│  │  Intent      │   │  Rule-Based  │  │  IBM         │  │
│  │  Router      │──▶│  Modules     │─▶│  Granite LLM │  │
│  └──────────────┘   └──────────────┘  │  watsonx.ai  │  │
│                           │           └──────────────┘  │
│              ┌────────────┼─────────────────┐           │
│              ▼            ▼                 ▼           │
│         analysis.py  education.py    suggestions.py     │
└─────────────────────────────────────────────────────────┘
    │
    ▼
Response (CLI / Streamlit UI / Langflow Chat)
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | IBM Granite (`ibm/granite-13b-chat-v2`) via watsonx.ai |
| **Orchestration** | IBM Langflow (`flows/energywise_langflow.json`) |
| **Language** | Python 3.10+ |
| **Web UI** | Streamlit |
| **Data** | JSON appliance & energy facts database |

---

## Project Structure

```
energy_agent/
├── agent.py                        # Main AI Agent (CLI entry point)
├── app_ui.py                       # Streamlit Web UI
├── demo.py                         # Demo script (no credentials needed)
├── requirements.txt
├── .env.example                    # Credential template
│
├── modules/
│   ├── energy_models.py            # Data models (Profile, Appliance, Session)
│   ├── analysis.py                 # Consumption analysis & benchmarking
│   ├── education.py                # User awareness & education
│   └── suggestions.py             # Personalised energy-saving tips
│
├── utils/
│   ├── watsonx_client.py          # IBM watsonx.ai client wrapper
│   └── prompt_templates.py        # IBM Granite prompt templates
│
├── data/
│   ├── appliances.json            # 20 appliance reference database
│   └── energy_facts.json          # Facts, myths, seasonal tips
│
└── flows/
    └── energywise_langflow.json   # IBM Langflow flow definition
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure IBM watsonx.ai

```bash
cp .env.example .env
# Edit .env with your IBM Cloud credentials
```

Get credentials from: [IBM Cloud watsonx.ai](https://cloud.ibm.com) → watsonx.ai → Project → Manage

```env
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_PROJECT_ID=your_project_id
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2
```

### 3. Run the Demo (no credentials needed)

```bash
cd energy_agent
python demo.py
```

### 4. Launch Interactive CLI Agent

```bash
cd energy_agent
python agent.py
```

### 5. Launch Streamlit Web UI

```bash
cd energy_agent
streamlit run app_ui.py
```

### 6. Import into IBM Langflow

1. Open IBM Langflow / IBM Orchestrate
2. Import `flows/energywise_langflow.json`
3. Configure the WatsonxLLMNode with your credentials
4. Deploy and test the flow

---

## Features

### 📊 Energy Consumption Analysis
- Tracks all household appliances by wattage, daily usage, and quantity
- Calculates monthly kWh, cost (₹), and CO₂ footprint
- Benchmarks against India's national average (877 kWh/month)
- Flags appliances with **HIGH** or **CRITICAL** over-usage
- Estimates 10% / 20% / 35% savings potential

### 📚 User Education
- **Did You Know?** — rotating energy facts
- **Myth vs Fact** — busts 5 common electricity myths
- **Bill Explainer** — breaks down cost per hour/day/month
- **Carbon Impact** — translates kWh to CO₂, trees, and car km
- **Peak Hours Guide** — explains ToU tariffs and load shifting
- **Seasonal Tips** — summer, winter, monsoon energy advice

### 💡 Energy Saving Suggestions
- 15 evidence-based tips categorised by effort level
- Personalised based on your top energy categories
- Includes appliance-specific tips for high-usage alerts
- Estimated monthly savings in kWh and ₹ for each tip

### 💬 Conversational Chat (IBM Granite)
- Intent-aware routing: bill → carbon → tips → general Q&A
- Conversation memory (last 6 turns)
- Household context injected into every prompt
- Quiz mode for energy literacy

---

## IBM Langflow Flow

The file `flows/energywise_langflow.json` defines the complete agent flow:

```
ChatInput → IntentRouter → EnergyTools (8 tools)
                       ↘                      ↘
                         IBM Granite (LLM) ← SystemPrompt + Memory
                                ↓
                      ResponseFormatter → ChatOutput → Memory
```

**8 built-in tools:**
1. `analyze_consumption` — Full household analysis
2. `get_energy_tips` — Personalised recommendations
3. `calculate_appliance` — Single appliance calculator
4. `explain_carbon_impact` — CO₂ footprint explanation
5. `get_energy_fact` — Random educational fact
6. `bust_energy_myth` — Myth vs fact retrieval
7. `peak_hour_guide` — Peak/off-peak explanation
8. `seasonal_energy_tips` — Season-specific advice

---

## Sample Conversation

```
You: How much does my AC cost per month?

EnergyWise: Your 1500W Air Conditioner running 8 hours/day
            consumes 360 kWh/month — that's ₹2,700 on your bill!

            That's 41% of your total electricity bill. Here's what you
            can do today:
            ✅ Set thermostat to 24°C (saves 36% vs 18°C)
            ✅ Use ceiling fans alongside AC (raise temp 2°C more)
            ✅ Clean AC filters monthly (improves efficiency 5–15%)

            👉 Start today: Change your AC setting to 24°C right now.
               That single change could save ₹800/month!
```

---

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `WATSONX_API_KEY` | IBM Cloud API Key | — (required) |
| `WATSONX_URL` | watsonx.ai endpoint | `https://us-south.ml.cloud.ibm.com` |
| `WATSONX_PROJECT_ID` | watsonx.ai Project ID | — (required) |
| `WATSONX_MODEL_ID` | IBM Granite model ID | `ibm/granite-13b-chat-v2` |
| `DEFAULT_RATE_PER_KWH` | Electricity tariff (₹/kWh) | `7.5` |

---

## License

MIT License — built for IBM Hackathon Problem Statement #20.
