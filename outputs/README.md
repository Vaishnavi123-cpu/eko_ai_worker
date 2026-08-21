# Eko AI Worker: Supply Chain & Forecasting Engine

## The Workflow
This AI Data Worker acts as a proactive operations agent. Instead of a human staring at dashboards to guess reorder quantities, this worker ingests daily transaction logs, calculates velocity shifts deterministically using Python, and uses an open-weight model (Llama 3.1) to decide whether to auto-procure or escalate.

## Architecture & Cost-Efficiency
To align with Eko's open-source-first and low-cost mandate:
1. **Math in Python, Logic in AI:** The LLM is NOT used for calculations. Python computes the Days of Inventory (DOI) and 7-day velocity shifts. The AI is only invoked for final risk assessment and natural language synthesis, drastically reducing API token costs.
2. **Open-Weight Model:** Powered by Meta's Llama-3.1 via Groq API.

## Handling Messy Data & Exceptions
The pipeline features a strict `data_guard.py` ingestion layer. If critical schema data is missing (e.g., `Min_Threshold`) or physically impossible values appear (e.g., negative stock), the worker intentionally halts before making expensive API calls, logs the error, and generates a human escalation ticket.

## Future Improvements (V2)
* **Database Integration:** Swap CSV ingestion for direct SQL database connections.
* **Seasonality Context:** Pass historical seasonal multipliers to the LLM to differentiate between a random spike and an expected holiday rush.
* **Slack/Email Webhooks:** Automatically push the `human_escalations.md` alerts directly to the operations team's Slack channel.