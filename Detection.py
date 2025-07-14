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
# Assuming Label.py exists and contains label_season, hypothesis_testing, and DB
from Label import label_season, hypothesis_testing, DB 


evidence_timeline = [(0, ["pricing", "season"]), (7, ["sales"]), (10, "product_popularity"), (15, "operational_efficiency")]

date = "2024-06-27"
month = date[:7]
day = None
prev_month = str(pd.Timestamp(date) - pd.DateOffset(months=1))[:7] # Corrected to months=1

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
    
    # Ensure day is within valid range for cummulated_sales index
    current_day_index = min(day - 1, len(cummulated_sales) - 1)

    if day >= 7: # Changed from > 7 to >= 7 to include day 7
        evidence["sales"] = detect_sales()
    if day >= 10: # Changed from > 10 to >= 10 to include day 10
        # FIX: Changed "popularity" to "product_popularity" to match engine.py model
        evidence["product_popularity"] = detect_popularity() 
    if day >= 15: # Changed from > 15 to >= 15 to include day 15
        evidence["operational_efficiency"] = detect_operational_efficiency()
    
    return evidence



def detect_popularity():
    popularit_df = pd.read_sql_query("SELECT month, product_name, products_sold, profit_share FROM product_metrics", conn)
    popularit_df['month_dt'] = pd.to_datetime(popularit_df['month'])
    curr_profit_share = popularit_df[popularit_df['month'] == prev_month]
    recent_df = popularit_df[(popularit_df['month_dt'] < pd.to_datetime(prev_month)) & 
                             (popularit_df['month_dt'] >= pd.to_datetime(prev_month) - pd.DateOffset(months=6))]
    
    # Calculate recent_scores_series (Series of monthly scores)
    recent_scores_series = (recent_df['products_sold'] * recent_df['profit_share']).groupby(recent_df['month']).sum()
    
    # Handle empty recent_scores_series for hypothesis_testing
    if recent_scores_series.empty:
        print("Warning: No recent historical data for product popularity. Defaulting to 'stable'.")
        return ('stable', 1.0) # Default if no historical data

    real_time_df = pd.read_sql_query(f"SELECT product_name, sum(units_sold) as sales FROM real_time_data WHERE product_name != 'operational_accidents' AND day BETWEEN 0 AND {day} GROUP BY product_name;", conn)
    real_time_df = pd.merge(real_time_df, curr_profit_share, on="product_name", how='inner')
    
    current_score = (real_time_df['sales'] * real_time_df['profit_share']).sum() if not real_time_df.empty else 0.0

    # FIX: Pass the pandas Series directly to hypothesis_testing
    current_day_index = min(day - 1, len(cummulated_sales) - 1)
    return (hypothesis_testing(recent_scores_series, current_score, ['climbing', 'declining', 'stable']), round(cummulated_sales[current_day_index], 3))


def detect_price():
    product_prices = pd.read_sql_query("SELECT product_name, price FROM real_time_data WHERE day = '0' AND product_name != 'operational_accidents';", conn)
    product_avg = pd.read_sql_query("SELECT product_name, avg(price) as avg FROM product_metrics GROUP BY product_name", conn)
    
    prod_std = pd.DataFrame(columns=['product_name', 'std'])
    for prod in product_avg["product_name"].unique():
        product_df = pd.read_sql_query(f"SELECT price FROM product_metrics WHERE product_name = '{prod}';", conn)
        # Ensure there's enough data to compute std, otherwise std() will be NaN
        if len(product_df['price']) > 1:
            prod_std.loc[len(prod_std)] = [prod, product_df["price"].std(ddof=0)]
        else:
            prod_std.loc[len(prod_std)] = [prod, 0.0] # Default std to 0 if not enough data

    merged_df = pd.merge(product_prices, product_avg, on='product_name', how='inner')
    merged_df = pd.merge(merged_df, prod_std, on='product_name', how='inner')
    
    # Handle division by zero for z_score if std is 0
    merged_df['z_score'] = merged_df.apply(lambda row: (row['price'] - row['avg']) / row['std'] if row['std'] != 0 else 0, axis=1)
    
    prev_month = str(pd.Timestamp(date) - pd.DateOffset(months=1))[:7]
    profit_share_df = pd.read_sql_query(f"SELECT product_name, profit_share FROM product_metrics WHERE month = '{prev_month}';", conn)
    merged_df = pd.merge(merged_df, profit_share_df, on='product_name', how='inner')

    price_card = merged_df
    # Handle case where profit_share might be zero or empty merged_df
    if not price_card.empty and price_card['profit_share'].sum() != 0:
        accumulated_z = (price_card['z_score'] * price_card['profit_share']).sum() / (price_card['profit_share']).sum()
    else:
        accumulated_z = 0.0 # Default if no data or no profit share

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
        # Handle invalid rates or days more gracefully, or raise a specific error if appropriate
        print("Warning: rate_per_day must be > 0 and t_days must be ≥ 0. Returning 0 probability.")
        return 0.0

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
    accidents_data = pd.read_sql_query(f"SELECT accidents FROM real_time_data WHERE product_name = 'operational_accidents' AND day BETWEEN 1 AND {day};", conn)
    accidents = accidents_data['accidents'].sum() if not accidents_data.empty else 0

    accidents_df = pd.read_sql_query("SELECT operational_accidents FROM business_metrics;", conn)
    
    if accidents_df.empty or accidents_df['operational_accidents'].std() == 0:
        # Handle cases with no historical data or no variance
        print("Warning: Not enough historical operational accident data for meaningful statistics. Defaulting to 'expected'.")
        return ("expected", 1.0)

    mean_accidents = accidents_df['operational_accidents'].mean()
    std_accidents = accidents_df['operational_accidents'].std()

    accidents_upperlimit = mean_accidents + (0.8 * std_accidents)
    accidents_lowerlimit = mean_accidents - (0.8 * std_accidents)
    rate = mean_accidents / 31 # Average monthly accidents / 31 days

    # Remaining days in the month
    remaining_days = 31 - day
    if remaining_days < 0: remaining_days = 0 # Cap at 0 if day exceeds 31

    # Calculate remaining accidents needed to fall into each category
    remaining_smooth_upper = accidents_lowerlimit - accidents
    remaining_expected_lower = accidents_lowerlimit - accidents
    remaining_expected_upper = accidents_upperlimit - accidents
    remaining_rough_lower = accidents_upperlimit - accidents

    # Ensure limits are non-negative for poisson.cdf
    remaining_smooth_upper = max(0, remaining_smooth_upper)
    remaining_expected_lower = max(0, remaining_expected_lower)
    remaining_expected_upper = max(0, remaining_expected_upper)
    remaining_rough_lower = max(0, remaining_rough_lower)

    confidence = [
        prob_events_between_limits(-math.inf, remaining_smooth_upper, remaining_days, rate), 
        prob_events_between_limits(remaining_expected_lower, remaining_expected_upper, remaining_days, rate),
        prob_events_between_limits(remaining_rough_lower, math.inf, remaining_days, rate)
    ]
    
    # Normalize confidence values if their sum is not 1 (due to rounding or edge cases)
    total_confidence = sum(confidence)
    if total_confidence > 0:
        confidence = [c / total_confidence for c in confidence]
    else:
        # If all are zero, assign 100% to 'expected' as a fallback
        confidence = [0.0, 1.0, 0.0]

    labels = ["smooth", "expected", "rough"]
    max_conf_index = confidence.index(max(confidence))
    
    return (labels[max_conf_index], round(confidence[max_conf_index], 3))


def detect_sales():
    """Detect sales pattern and confidence """
    rtd_df = pd.read_sql_query("SELECT product_name, price FROM real_time_data WHERE product_name != 'operational_accidents' AND day = 0;", conn)
    avg_sales = pd.read_sql_query("SELECT product_name, avg(price) as avg FROM product_metrics GROUP BY product_name;", conn)
    
    sales_score = 0
    # Ensure product_name exists in both dataframes before multiplication
    merged_rtd_avg = pd.merge(rtd_df, avg_sales, on='product_name', how='inner')
    
    for _, row in merged_rtd_avg.iterrows():
        # project_sales needs the product name and its average price
        projected_units = project_sales(row['product_name'], row['avg'])
        # Use the current day's price from rtd_df for the revenue calculation
        prod_revenue = row['price'] * projected_units
        sales_score += prod_revenue * row['price'] # This seems like revenue * price, check if intended

    sales_df = pd.read_sql_query("SELECT sales_items, sales_revenue FROM business_metrics", conn)
    sales_df['sales_score'] = sales_df['sales_items'] * sales_df['sales_revenue']

    # Handle cases where sales_df might be empty or std is 0
    if sales_df.empty or sales_df['sales_score'].std() == 0:
        print("Warning: Not enough historical sales data for meaningful statistics. Defaulting to 'stable'.")
        return ("stable", 1.0)

    z = (sales_score - sales_df['sales_score'].mean()) / sales_df['sales_score'].std()

    # Ensure day - 1 is a valid index for cummulated_sales
    current_day_index = min(day - 1, len(cummulated_sales) - 1)
    
    # FIX: Pass the pandas Series directly to hypothesis_testing
    return (hypothesis_testing(sales_df['sales_score'], sales_score, ['high', 'low', 'stable']), adjusted_confidence_by_sales_fraction(z, cummulated_sales[current_day_index])[1])


def project_sales(product, avg_num):
    """project sales by comparing it to graph"""
    expected = pd.DataFrame(daily_sales_portion, columns=["proportions"])
    expected["expectation_value"] = expected["proportions"] * avg_num
    expected["day"] = [i for i in range(1, 32)]

    # Use the existing global connection
    data = pd.read_sql_query(f"SELECT day, units_sold FROM real_time_data WHERE product_name = '{product}' AND day between 1 AND {day} ORDER BY day;", conn)
    
    final_table = pd.merge(expected, data, on="day", how='inner')
    
    if final_table.empty:
        # If no real-time data for the product, return avg_num or a default
        return avg_num

    final_table['units_sold'] = final_table['units_sold'].astype(float)
    final_table['expectation_value'] = final_table['expectation_value'].astype(float)
    final_table['difference'] = final_table['units_sold'] - final_table['expectation_value']
    
    # Handle case where mean() might be NaN if difference column is empty
    mean_diff = final_table['difference'].mean()
    if pd.isna(mean_diff):
        mean_diff = 0.0 # Default to 0 if no difference can be calculated

    sales = avg_num + (mean_diff * 31)
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
        # Handle invalid pct_sales_so_far, e.g., return default confidence
        print("Warning: pct_sales_so_far must be between 0 (exclusive) and 1 (inclusive). Returning 0 confidence.")
        return z_projected, 0.0

    # Adjust z-score using sqrt of information seen (i.e., sales coverage)
    adjusted_z = z_projected * math.sqrt(pct_sales_so_far)
    
    # Compute the probability that |adjusted_z| > threshold (two-tailed)
    tail_prob = (1 - norm.cdf(abs(adjusted_z))) * 2
    full_tail = (1 - norm.cdf(z_threshold)) * 2

    if full_tail == 0: # Avoid division by zero
        confidence = 0.0
    else:
        confidence = max(0.0, min(1.0, tail_prob / full_tail))

    return adjusted_z, round(confidence, 3)
