Eko AI Worker – AI Supply Chain Forecasting Engine

An AI-powered supply chain forecasting project built using Python and Llama 3.1 (Groq API). This project analyzes inventory and sales velocity, detects stock risks, and generates intelligent procurement recommendations while keeping AI usage cost-efficient.

Features

- Automated inventory risk analysis.
- 7-day sales velocity calculation using Python.
- Days of Inventory (DOI) prediction.
- AI-generated procurement and escalation decisions.
- Data validation layer to detect missing or invalid records.
- Human-readable escalation reports for critical issues.

Tech Stack

- Python
- Pandas & NumPy
- Requests
- Groq API (Llama 3.1)
- CSV-based data pipeline

Project Workflow

1. Load daily inventory and transaction data.
2. Validate data using a data guard layer.
3. Calculate inventory metrics and velocity shifts.
4. Send processed insights to Llama 3.1 for decision-making.
5. Generate procurement recommendations and escalation reports.

Project Structure

- "generate_mock_data.py" – Generates sample inventory data.
- "data_guard.py" – Validates incoming data.
- "ai_worker_core.py" – Runs forecasting and AI decision logic.
- "outputs/" – Stores generated reports.
- "logs/" – Stores execution logs.

Future Improvements

- SQL database integration.
- Seasonal demand forecasting.
- Slack/Email alert automation.
- Interactive dashboard using Streamlit or Power BI.

Author

Vaishnavi Singh

B.Tech CSE | Aspiring Data Analyst & AI Developer
