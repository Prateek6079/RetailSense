import pandas as pd
import numpy as np

# note 1 Bad , 0 Good
def get_month_number(month_str):
    return pd.to_datetime(month_str).month

def label_profits(df):
    return (df['profits'].diff() < 0).astype(int)  # 2 months ka adjacent difference if negative, label as 1

def label_sales(df):
    return ((df['sales_revenue'].diff() < 0) | (df['sales_items'].diff() < 0)).astype(int) # subtracting sales revenue 2 adjacent months OR sales items, if negative, label as 1

def label_costs(df):
    return (df['costs'].diff() > 0).astype(int)  # 2 months ka adjacent cost difference if "positive", label as 1 cost badana is bad

def label_competition(df):
    #80 % threshold 
    threshold = df['new_customers'].mean() * 0.8  
    # agar 80% se kam new customers aaye ya repeat customers ka difference negative hai, label as 1
    return ((df['new_customers'] < threshold) | (df['repeat_customers'].diff() < 0)).astype(int)

def label_pricing(file2):
    # Calculate average price by month weighted by products sold
    avg_price_by_month = file2.groupby('month').apply(lambda x: np.average(x['price'], weights=x['products_sold']))
    # Identify months where the average price is less than 90% of the mean price
    mean_price = avg_price_by_month.mean()
    return (avg_price_by_month < mean_price * 0.9).astype(int).values

def label_economy(df):
    return (df['economy'] < 50).astype(int)

def label_operational_efficiency(df):
    return ((df['operational_accidents'] > 300) | (df['operational_accidents'].diff() > 0)).astype(int)

def label_stocking(file2):
    stock_life_by_month = file2.groupby('month')['stock_life'].mean()
    return ((stock_life_by_month < 15) | (stock_life_by_month > 90)).astype(int).values

def calc_popularity(df):
    total = df['products_sold'].sum()
    top_20_percent = df.sort_values('products_sold', ascending=False).head(max(1, len(df)//5))
    top_contrib = top_20_percent['products_sold'].sum() / total
    return 1 if top_contrib > 0.8 else 0

def label_product_popularity(file2):
    return file2.groupby('month').apply(calc_popularity).values

def label_season(df):
    season_bad_months = [11, 12]
    return ((df['month_num'].isin(season_bad_months)) & (df['profits'] < df['profits'].mean())).astype(int)

def main():
    file1 = pd.read_csv("dataset/file1b.csv")
    file2 = pd.read_csv("dataset/file2p.csv")
    file1['month_num'] = file1['month'].apply(get_month_number)

    labels = pd.DataFrame()
    labels['month'] = file1['month']
    labels['profits'] = label_profits(file1)
    labels['sales'] = label_sales(file1)
    labels['costs'] = label_costs(file1)
    labels['competition'] = label_competition(file1)
    labels['pricing'] = label_pricing(file2)
    labels['economy'] = label_economy(file1)
    labels['operational_efficiency'] = label_operational_efficiency(file1)
    labels['stocking'] = label_stocking(file2)
    labels['product_popularity'] = label_product_popularity(file2)
    labels['season'] = label_season(file1)

    labels.to_csv("label.csv", index=False)
    print("label.csv generated")

if __name__ == "__main__":
    main()
