import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

print("Starting data generation for Eko AI Worker...")

inventory_data = {
    'SKU_ID': ['SKU_101', 'SKU_102', 'SKU_103', 'SKU_104', 'SKU_105'],
    'Product_Name': ['Micro-ATM Device', 'Thermal Printer Rolls', 'Biometric Scanner', 'Merchant Standee', 'Soundbox Speaker'],
    'Current_Stock': [150, 45, 80, -15, 200],  
    'Min_Threshold': [50, 100, 20, np.nan, 50], 
    'Unit_Cost': [2500, 15, 1200, 300, 800]
}

df_inventory = pd.DataFrame(inventory_data)

df_inventory.to_csv('inventory_levels.csv', index=False)
print("✅ Created inventory_levels.csv")

end_date = datetime.today()
start_date = end_date - timedelta(days=30)
date_list = [start_date + timedelta(days=x) for x in range(30)]

transactions = []
transaction_id_counter = 1000

for current_date in date_list:
    days_ago = (end_date - current_date).days
    
    transactions.append([f"TXN_{transaction_id_counter}", current_date, 'SKU_101', random.randint(1, 3), f"MERCH_{random.randint(10, 99)}"])
    transaction_id_counter += 1

    
    if days_ago <= 7:
        qty_sold = random.randint(20, 40) 
    else:
        qty_sold = random.randint(5, 10)  
    transactions.append([f"TXN_{transaction_id_counter}", current_date, 'SKU_102', qty_sold, f"MERCH_{random.randint(10, 99)}"])
    transaction_id_counter += 1

    transactions.append([f"TXN_{transaction_id_counter}", current_date, 'SKU_104', random.randint(0, 2), f"MERCH_{random.randint(10, 99)}"])
    transaction_id_counter += 1
    transactions.append([f"TXN_{transaction_id_counter}", current_date, 'SKU_105', random.randint(1, 5), f"MERCH_{random.randint(10, 99)}"])
    transaction_id_counter += 1

df_sales = pd.DataFrame(transactions, columns=['Transaction_ID', 'Timestamp', 'SKU_ID', 'Quantity_Sold', 'Merchant_ID'])

df_sales = df_sales.sample(frac=1).reset_index(drop=True)

df_sales.to_csv('sales_transactions.csv', index=False)
print("✅ Created sales_transactions.csv")
