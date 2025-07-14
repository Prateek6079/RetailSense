# This module is supposed to detect the current business environment, market state and declining performance
# Collect evidence on constrainted timelines
# day 1 evidence : pricing, season
# day 7 evidence : sales

# we will use beta distribution to project sales
# gamma distribution to project operational_accidents
import pandas as pd
import sqlite3
from scipy.stats import norm, poisson
import math
from Label import label_season, hypothesis_testing, DB


evidence_timeline = [(0, ["pricing", "season"]), (7, ["sales"]), (10, "product_popularity"), (15, "operational_efficiency")]

date = "2024-06-27"
month = date[:7]
day = None
prev_month = str(pd.Timestamp(date) - pd.DateOffset(month=1))[:7]

pricing = None
season = (label_season(month), 1)

# Learned daily sales trend
daily_sales_portion = [0.059, 0.055, 0.053, 0.055, 0.057, 0.050, 0.045, 0.040, 0.036, 0.032, 0.031, 0.030, 0.030, 0.029,  
                       0.029, 0.028, 0.027, 0.027, 0.026, 0.025, 0.025, 0.024, 0.023, 0.023, 0.022, 0.021, 0.021, 0.020,
                       0.019, 0.018, 0.015]

cummulated_sales = daily_sales_portion.copy()
for i in range(1, len(daily_sales_portion), 1):
    cummulated_sales[i] = cummulated_sales[i-1] + cummulated_sales[i]

conn = sqlite3.connect(DB, check_same_thread=False)


def detect(d_day):
    global day
    day = d_day
    evidence = {"season" : season, "pricing" : detect_price()}
    for i in range(day):
        if day > 7:
            evidence["sales"] = detect_sales()
        if day > 10:
            evidence["popularity"] = detect_popularity()
        if day > 15:
            evidence["operational_efficiency"] = detect_operational_efficiency()
    
    return evidence



def detect_popularity():
    popularit_df = pd.read_sql_query("SELECT month, product_name, products_sold, profit_share FROM product_metrics", conn)
    popularit_df['month_dt'] = pd.to_datetime(popularit_df['month'])
    curr_profit_share = popularit_df[popularit_df['month'] == prev_month]
    recent_df = popularit_df[(popularit_df['month_dt'] < pd.to_datetime(prev_month)) & 
                        (popularit_df['month_dt'] >= pd.to_datetime(prev_month) - pd.DateOffset(months=6))]
    recent_scores = cummulated_sales[day - 1] * (recent_df['products_sold'] * recent_df['profit_share']).groupby(recent_df['month']).sum()
    real_time_df = pd.read_sql_query(f"SELECT product_name, sum(units_sold) as sales FROM real_time_data WHERE product_name != 'operational_accidents' AND day BETWEEN 0 AND {day} GROUP BY product_name;", conn)
    real_time_df = pd.merge(real_time_df, curr_profit_share, on="product_name", how='inner')
    current_score = (real_time_df['sales'] * real_time_df['profit_share']).sum()
    return (hypothesis_testing(recent_scores, current_score, ['climbing', 'declining', 'stable']), round(cummulated_sales[day - 1], 3))


def detect_price():
    product_prices = pd.read_sql_query("SELECT product_name, price FROM real_time_data WHERE day = '0' AND product_name != 'operational_accidents';", conn)
    product_avg = pd.read_sql_query("SELECT product_name, avg(price) as avg FROM product_metrics GROUP BY product_name", conn)
    prod_std = pd.DataFrame(columns=['product_name', 'std'])
    for prod in product_avg["product_name"].unique():
        product_df = pd.read_sql_query(f"SELECT price FROM product_metrics WHERE product_name = '{prod}';", conn)
        prod_std.loc[len(prod_std)] = [prod, product_df["price"].std(ddof=0)]

    merged_df = pd.merge(product_prices, product_avg, on='product_name', how='inner')
    merged_df = pd.merge(merged_df, prod_std, on='product_name', how='inner')
    merged_df['z_score'] = (merged_df['price'] - merged_df['avg']) / merged_df['std']
    prev_month = str(pd.Timestamp(date) - pd.DateOffset(month=1))[:7]
    profit_share_df = pd.read_sql_query(f"SELECT product_name, profit_share FROM product_metrics WHERE month = '{prev_month}';", conn)
    merged_df = pd.merge(merged_df, profit_share_df, on='product_name', how='inner')

    price_card = merged_df
    accumulated_z = (price_card['z_score'] * price_card['profit_share']).sum() / (price_card['profit_share']).sum()
    if (accumulated_z >= 0.6):
        return ('high', 1)
    elif (accumulated_z <= -0.6):
        return ('low', 1)
    else:
        return ('stable', 1)



def prob_events_between_limits(lower_limit, upper_limit, t_days, rate_per_day):
    """
    Computes the probability that the number of events falls between lower_limit and upper_limit
    (inclusive) over a given number of days in a Poisson process.

    Parameters:
        lower_limit (int or float): Inclusive lower limit of number of events (can be -inf)
        upper_limit (int or float): Inclusive upper limit of number of events (can be inf)
        t_days (float): Number of days
        rate_per_day (float): Event rate per day

    Returns:
        prob (float): Probability that number of events in t_days ∈ [lower_limit, upper_limit]
    """
    if rate_per_day <= 0 or t_days < 0:
        raise ValueError("rate_per_day must be > 0 and t_days must be ≥ 0.")

    mu = rate_per_day * t_days

    # Handle infinities
    if lower_limit == -math.inf:
        lower_cdf = 0.0
    else:
        lower_cdf = poisson.cdf(lower_limit - 1, mu)

    if upper_limit == math.inf:
        upper_cdf = 1.0
    else:
        upper_cdf = poisson.cdf(upper_limit, mu)

    prob = upper_cdf - lower_cdf
    return round(max(0.0, min(1.0, prob)), 3)



def detect_operational_efficiency():
    """Provides with a probability and label of operational_efficiency"""
    accidents = pd.read_sql_query(f"SELECT sum(accidents) as accidents FROM real_time_data WHERE accidents = 1 AND day BETWEEN 1 AND {day};", conn)['accidents'].values[0]
    accidents_df = pd.read_sql_query("SELECT operational_accidents FROM business_metrics;", conn)
    accidents_upperlimit = accidents_df['operational_accidents'].mean() + (0.8 * accidents_df['operational_accidents'].std())
    accidents_lowerlimit = accidents_df['operational_accidents'].mean() - (0.8 * accidents_df['operational_accidents'].std())
    rate = accidents_df['operational_accidents'].mean() / 31
    evidence = ["smooth", "expected", "rough"]
    confidence = [prob_events_between_limits(-math.inf, accidents_lowerlimit - accidents, 31 - day, rate), 
                  prob_events_between_limits(accidents_lowerlimit - accidents, accidents_upperlimit - accidents, 31 - day, rate),
                  prob_events_between_limits(accidents_upperlimit - accidents, math.inf, 31 - day, rate)]
    
    return (evidence[confidence.index(max(confidence))], max(confidence))


def detect_sales():
    """Detect sales pattern and confidence """
    rtd_df = pd.read_sql_query("SELECT product_name, price FROM real_time_data WHERE product_name != 'operational_accidents' AND day = 0;", conn)
    avg_sales = pd.read_sql_query("SELECT product_name, avg(price) as avg FROM product_metrics GROUP BY product_name;", conn)
    sales_score = 0
    for prod in rtd_df['product_name']:
        prod_revenue = rtd_df[rtd_df['product_name'] == prod]['price'].values[0] * project_sales(prod, avg_sales[avg_sales["product_name"] == prod]['avg'].values[0])
        sales_score += prod_revenue * rtd_df[rtd_df['product_name'] == prod]['price'].values[0]
    
    sales_df = pd.read_sql_query("SELECT sales_items, sales_revenue FROM business_metrics", conn)
    sales_df['sales_score'] = sales_df['sales_items'] * sales_df['sales_revenue']

    z = (sales_score - sales_df['sales_score'].mean()) / sales_df['sales_score'].std()

    return (hypothesis_testing(sales_df['sales_score'], sales_score, ['high', 'low', 'stable']), adjusted_confidence_by_sales_fraction(z, cummulated_sales[day - 1])[1])


def project_sales(product, avg_num):
    """project sales by comparing it to graph"""
    expected = pd.DataFrame(daily_sales_portion, columns=["proportions"])
    expected["expectation_value"] = expected["proportions"] * avg_num
    expected["day"] = [i for i in range(1, 32)]

    conn = sqlite3.connect(DB)
    data = pd.read_sql_query(f"SELECT day, units_sold FROM real_time_data WHERE product_name = '{product}' AND day between 1 AND {day} ORDER BY day;", conn)
    final_table = pd.merge(expected, data, on="day", how='inner')
    final_table['units_sold'] = final_table['units_sold'].astype(float)
    final_table['expectation_value'] = final_table['expectation_value'].astype(float)
    final_table['difference'] = final_table['units_sold'] - final_table['expectation_value']
    sales = avg_num + (final_table['difference'].mean() * 31)
    return sales



def adjusted_confidence_by_sales_fraction(z_projected, pct_sales_so_far, z_threshold=0.8):
    """
    Adjust confidence in a projected z-score based on what fraction of expected monthly sales
    has occurred, using a two-tailed threshold (i.e., checking for significant deviation in either direction).

    Parameters:
        z_projected (float): z-score of the projected full-month sales (positive or negative)
        pct_sales_so_far (float): Fraction of month’s sales expected to have occurred by today (0 < p ≤ 1)
        z_threshold (float): Absolute z-threshold beyond which deviation is considered significant

    Returns:
        adjusted_z (float): z-score adjusted for partial observation
        confidence (float): Confidence (0 to 1) that deviation is significant (i.e., |z| > z_threshold)
    """
    if not (0 < pct_sales_so_far <= 1):
        raise ValueError("pct_sales_so_far must be between 0 (exclusive) and 1 (inclusive).")

    # Adjust z-score using sqrt of information seen (i.e., sales coverage)
    adjusted_z = z_projected * math.sqrt(pct_sales_so_far)
    
    # Compute the probability that |adjusted_z| > threshold (two-tailed)
    tail_prob = (1 - norm.cdf(abs(adjusted_z))) * 2
    full_tail = (1 - norm.cdf(z_threshold)) * 2

    confidence = max(0.0, min(1.0, tail_prob / full_tail))

    return adjusted_z, round(confidence, 3)


