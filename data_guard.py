import pandas as pd
import logging
import os

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/worker_activity.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def ingest_and_validate():
    logging.info("Starting Data Ingestion & Quality Guard...")
    
    try:
        inventory = pd.read_csv('data/inventory_levels.csv')
        sales = pd.read_csv('data/sales_transactions.csv')
        
        if inventory['Min_Threshold'].isnull().any():
            bad_skus = inventory[inventory['Min_Threshold'].isnull()]['SKU_ID'].tolist()
            error_msg = f"CRITICAL: Missing Min_Threshold for SKUs: {bad_skus}"
            logging.error(error_msg)
            print(f"❌ Worker Halted: {error_msg}")
            generate_escalation_ticket("Missing Schema Exception", error_msg)
            return None, None, "Failed"
            
        if (inventory['Current_Stock'] < 0).any():
            bad_skus = inventory[inventory['Current_Stock'] < 0]['SKU_ID'].tolist()
            error_msg = f"CRITICAL: Negative inventory detected for SKUs: {bad_skus}"
            logging.error(error_msg)
            print(f"❌ Worker Halted: {error_msg}")
            generate_escalation_ticket("Negative Value Exception", error_msg)
            return None, None, "Failed"

        logging.info("Data Validation Passed. Proceeding to calculations.")
        print("✅ Data is clean. Worker proceeding.")
        return inventory, sales, "Success"

    except Exception as e:
        logging.error(f"System Error during ingestion: {str(e)}")
        return None, None, "Failed"

def generate_escalation_ticket(reason, details):
    os.makedirs('outputs', exist_ok=True)
    with open('outputs/human_escalations.md', 'w', encoding='utf-8') as f:
        f.write(f"# 🚨 URGENT: Human Escalation Required\n\n")
        f.write(f"**Reason:** {reason}\n")
        f.write(f"**Details:** {details}\n")
        f.write(f"**Action Required:** Please review the raw inventory CSV and correct the data entry errors before the AI Worker can proceed.\n")
    print("🎫 Human Escalation Ticket generated in /outputs/human_escalations.md")

if __name__ == "__main__":
    inv, sales, status = ingest_and_validate()