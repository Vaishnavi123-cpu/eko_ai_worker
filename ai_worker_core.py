import os
import json
import pandas as pd
import numpy as np
import requests
import logging
from data_guard import ingest_and_validate

logging.basicConfig(
    filename='logs/worker_activity.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")

SYSTEM_PROMPT = """
You are an automated supply chain AI Worker for Eko. 
Your objective is to evaluate product sales velocity and inventory levels to decide whether to issue an automated reorder or escalate to a human manager. Optimize for cash preservation and zero stockouts.

You will receive a JSON payload containing the calculated metrics for a specific SKU.

BUSINESS RULES:
1. If Days of Inventory (DOI) > 14: Action is "HOLD".
2. If DOI <= 14 AND Velocity Shift is < 40%: Action is "AUTO_ORDER". Reorder enough stock to reach a 15-day buffer based on the 7-day average sales.
3. If DOI <= 14 AND Velocity Shift is >= 40%: Action is "HUMAN_ESCALATION".

You must reply ONLY with a valid JSON object matching this exact schema, with no additional markdown or conversational text:
{
    "sku_id": "string",
    "action": "HOLD" | "AUTO_ORDER" | "HUMAN_ESCALATION",
    "reorder_quantity": integer,
    "operational_reasoning": "string"
}
"""

def calculate_metrics(inventory, sales):
    sales['Timestamp'] = pd.to_datetime(sales['Timestamp'])
    max_date = sales['Timestamp'].max()
    seven_days_ago = max_date - pd.Timedelta(days=7)
    
    metrics_list = []
    
    for _, row in inventory.iterrows():
        sku = row['SKU_ID']
        stock = row['Current_Stock']
        threshold = row['Min_Threshold']
        cost = row['Unit_Cost']
        
        sku_sales = sales[sales['SKU_ID'] == sku]
        
        total_sales_30 = sku_sales['Quantity_Sold'].sum()
        avg_sales_30 = total_sales_30 / 30.0
        
        sku_sales_7 = sku_sales[sku_sales['Timestamp'] >= seven_days_ago]
        total_sales_7 = sku_sales_7['Quantity_Sold'].sum()
        avg_sales_7 = total_sales_7 / 7.0
        
        if avg_sales_30 == 0:
            velocity_shift = 0.0
        else:
            velocity_shift = ((avg_sales_7 - avg_sales_30) / avg_sales_30) * 100.0
            
        if avg_sales_7 == 0:
            doi = 999.0
        else:
            doi = stock / avg_sales_7
            
        metrics_list.append({
            "sku_id": sku,
            "product_name": row['Product_Name'],
            "current_stock": int(stock),
            "min_threshold": float(threshold),
            "unit_cost": float(cost),
            "avg_sales_30": float(avg_sales_30),
            "avg_sales_7": float(avg_sales_7),
            "velocity_shift_pct": float(velocity_shift),
            "days_of_inventory": float(doi)
        })
        
    return metrics_list

def call_groq_ai(metrics):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(metrics)}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.0
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            logging.error(f"Groq API Error: {response.text}")
            return None
    except Exception as e:
        logging.error(f"Failed to connect to Groq: {str(e)}")
        return None

def process_supply_chain():
    inventory, sales, status = ingest_and_validate()
    
    if status != "Success":
        logging.error("Core engine execution aborted due to data quality guard failure.")
        print("❌ Core Engine Aborted: Please resolve the data issues flagged in logs/worker_activity.log")
        return
        
    print("🤖 Processing inventory math and querying AI Worker...")
    metrics = calculate_metrics(inventory, sales)
    
    orders = []
    escalations = []
    
    for item in metrics:
        ai_response_raw = call_groq_ai(item)
        if not ai_response_raw:
            continue
            
        try:
            decision = json.loads(ai_response_raw)
            logging.info(f"Decision for {item['sku_id']}: {decision['action']}")
            
            if decision['action'] == "AUTO_ORDER":
                orders.append({
                    "sku_id": item['sku_id'],
                    "product_name": item['product_name'],
                    "quantity": decision['reorder_quantity'],
                    "estimated_cost": decision['reorder_quantity'] * item['unit_cost'],
                    "reason": decision['operational_reasoning']
                })
            elif decision['action'] == "HUMAN_ESCALATION":
                escalations.append(f"### ⚠️ Escalation for {item['sku_id']} ({item['product_name']})\n- **Reasoning:** {decision['operational_reasoning']}\n- **Current Stock:** {item['current_stock']}\n- **7-Day Avg Sales:** {item['avg_sales_7']:.2f}\n- **Velocity Shift:** {item['velocity_shift_pct']:.2f}%\n\n")
        except Exception as e:
            logging.error(f"Failed to parse AI output for {item['sku_id']}: {str(e)}")

    if orders:
        with open('outputs/automated_reorders.json', 'w', encoding='utf-8') as f:
            json.dump(orders, f, indent=4)
        print("📦 Automated procurement orders written to outputs/automated_reorders.json")
        
    if escalations:
        with open('outputs/human_escalations.md', 'a', encoding='utf-8') as f:
            f.writelines(escalations)
        print("🎫 Operational exception updates appended to outputs/human_escalations.md")

if __name__ == "__main__":
    process_supply_chain()