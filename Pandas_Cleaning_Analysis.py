import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_pandas_portfolio_analysis(data_dir='data'):
    # 1. READ RAW MESSY DATA
    print("Reading Raw Messy Datasets...")
    customers = pd.read_csv(os.path.join(data_dir, 'customers_raw.csv'))
    products = pd.read_csv(os.path.join(data_dir, 'products_raw.csv'))
    orders = pd.read_csv(os.path.join(data_dir, 'orders_raw.csv'))

    # ========================
    # 2. DATA CLEANING (SAME AS SQL)
    # ========================
    
    # --- Clean Customers ---
    print("\n--- Cleaning Customers ---")
    # Duplicate Check
    print(f"Total Rows Before: {len(customers)}")
    customers.drop_duplicates(inplace=True)
    print(f"Total Rows After: {len(customers)}")
    
    # Filling Missing Values (NULL locations to 'Unknown')
    customers['location'].fillna('Unknown', inplace=True)
    print(f"Missing Values in location: {customers['location'].isnull().sum()}")

    # --- Clean Products ---
    print("\n--- Cleaning Products ---")
    # Handling missing categories
    products['category'].fillna('Unknown', inplace=True)
    # Ensuring price is float
    products['price'] = products['price'].astype(float)

    # --- Clean Orders ---
    print("\n--- Cleaning Orders ---")
    # Mixed Date format cleaning (Essential for freshers!)
    # pd.to_datetime is extremely powerful for mixed formats if used with errors='coerce' or manually
    orders['order_date'] = pd.to_datetime(orders['order_date'], dayfirst=False, errors='coerce')
    print(f"Missing Values in date (if any): {orders['order_date'].isnull().sum()}")

    # Handling missing quantities (filling NaNs with 0)
    orders['quantity'].fillna(0, inplace=True)
    orders['quantity'] = orders['quantity'].astype(int)

    # ========================
    # 3. DATA ANALYSIS (Equivalent to SQL)
    # ========================

    # Merge Orders with Products and Customers (Pandas JOIN)
    merged_data = orders.merge(products, on='product_id', how='left')
    merged_data = merged_data.merge(customers, on='customer_id', how='left')
    
    # Calculate Revenue (Total Sales) per Order
    merged_data['revenue'] = merged_data['quantity'] * merged_data['price']

    # Q1: Total Sales by Category
    category_revenue = merged_data.groupby('category')[['revenue', 'order_id']].agg({'revenue': 'sum', 'order_id': 'count'}).reset_index()
    category_revenue.rename(columns={'order_id': 'order_count'}, inplace=True)
    category_revenue.sort_values(by='revenue', ascending=False, inplace=True)
    print("\n--- Sales Analysis by Category (Pandas) ---")
    print(category_revenue)

    # Q2: Identify Top 5 High-Value Customers
    top_customers = merged_data.groupby(['customer_name', 'location'])['revenue'].sum().reset_index()
    top_customers = top_customers.sort_values(by='revenue', ascending=False).head(5)
    print("\n--- Top 5 Customers (Pandas) ---")
    print(top_customers)

    # Q3: Monthly Revenue Trend
    merged_data['month'] = merged_data['order_date'].dt.strftime('%Y-%m')
    monthly_revenue = merged_data.groupby('month')['revenue'].sum().reset_index()
    monthly_revenue.sort_values(by='month', ascending=True, inplace=True)
    print("\n--- Monthly Revenue Trend (Pandas) ---")
    print(monthly_revenue)

    # ========================
    # 4. VISUALIZATION
    # ========================
    plt.style.use('ggplot')
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Bar chart for Category Revenue
    sns.barplot(x='revenue', y='category', data=category_revenue, ax=axes[0], palette='magma')
    axes[0].set_title('Revenue by Category (Pandas)', fontsize=14)

    # Line chart for Monthly Sales Trend
    sns.lineplot(x='month', y='revenue', data=monthly_revenue, marker='o', ax=axes[1], color='dodgerblue')
    axes[1].set_title('Monthly Revenue Growth', fontsize=14)
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig('Pandas_Cleaning_Results.png')
    print("\nVisualization saved as 'Pandas_Cleaning_Results.png'. Data Cleaning and Analysis Complete.")

if __name__ == "__main__":
    run_pandas_portfolio_analysis()
