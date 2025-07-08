import pandas as pd 
import sqlite3
from scipy import stats

DB = "Retail_Data.db"

def hypothesis_testing(series, value, labels):
    z = (value - series.mean())/series.std(ddof = 0)
    # ddof = 0(delta degrees of freedom) means hum yhan pupolation S.D ko 0 le rhe hai because we are comparing new value(value) 
    # against the entire population represented by series 
    # jbb hum sample ko as a full know data use krte hain(not sample) tbb population S.D use krte hai 
    if z >= 0.8:
        return labels[0] # high/increasing
    elif z <= -0.8:
        return labels[1] # low/declining
    else:
        return labels[2] # stable/expected
    
def label_sales(df, row):
    # sales_score for all months
    df = df.copy()
    df['sales_score'] = df['sales_items'] * df['sales_revenue']
    # sales_score = quantity_sold*total_revenue
    # if many items are sold at high price == high score
    #combining demand and monetory
    
    # Compute score for current row
    current_score = row['sales_items'] * row['sales_revenue']
     
    return hypothesis_testing(df['sales_score'], current_score, ['high', 'low', 'stable'])


def label_profits(df, row):
    return hypothesis_testing(df['profits'], row['profits'], ['high', 'low', 'stable'])

def label_costs(df, row):
    return hypothesis_testing(df['costs'], row['costs'], ['high', 'low', 'stable'])

# for economy labling 
# improved and using hypothesis testing now w
def label_economy(df, row):
    return hypothesis_testing(df['economy'], row['economy'], ['good', 'bad', 'neutral'])

    
def label_operational_efficiency(df, row):
    return hypothesis_testing(df['operational_accidents'], row['operational_accidents'], ['rough', 'smooth', 'expected'])


## chnaged label_pricing 

def label_pricing(df_prod, month):#takes the product metrics dataframe and a target month as inputs and return a label for overall pricing on that month 
    month_df = df_prod[df_prod['month'] == month]#filters the dataset to get rows for the currrent month only 
    z_scores = []# stores the weighted z-scores of each product's pricing 
    weights = []# their corresponding profit_share weights 

    for product in month_df['product_name'].unique():#loop through each unique prodict sold in the cureent month 
        product_df = df_prod[df_prod['product_name'] == product].copy()#get the entire historical data for this product across the all months ,this will be used to calculate the z-score
        product_df['pricing_score'] = product_df['price'] 
        #computes a custom pricing metric
        #high price but low profit share implies expensive or poor value 
        #the ratio captures if the product is overpriced for its contribution

        current_score = product_df[product_df['month'] == month]['pricing_score'].values[0]#get the pricing score of the product in the corrent month 
        series = product_df['pricing_score']# series stores the historical pricing scores for this product across all months 

        z = (current_score - series.mean()) / series.std(ddof=0)
        # computes the z-score 
        # measures how diffferent the current score is from historical avg 
        # positive :- higher than normal 
        # negative :- lower than normal 

       
        weight = month_df[month_df['product_name'] == product]['profit_share'].mean()
        # use the profit_share of the product in the current month as a weight 
        # higher weight = more impact on final label
        # mean() used to avoid errors if product appear multiple times 

        z_scores.append(z * weight)
        weights.append(weight)
        # multiply the product's z-score by its weight and store both


    if not weights or sum(weights) == 0:
        return 'stable'
    # edge case ,if no product or weights = 0 , return stable by default 

    weighted_z = sum(z_scores) / sum(weights)
    # compute overall weighted z-score for the month's pricing 
    # this builds the formula
    # weighted z = (sum Z's*W's)/(sum W's)

    if weighted_z >= 0.6:
        return 'high'
    elif weighted_z <= -0.6:
        return 'low'
    else:
        return 'stable'


def label_stocking(df_prod, month):
    df = df_prod[df_prod['month'] == month]
    stock_life = df['stock_life'].mean()
    return hypothesis_testing(df_prod['stock_life'], stock_life, ['abundant', 'short', 'balanced'])

def label_product_popularity(df_prod, month, window=6):
    # Convert month to datetime for filtering
    df_prod['month_dt'] = pd.to_datetime(df_prod['month'])
    target_month = pd.to_datetime(month)

    # Select recent window
    recent_df = df_prod[(df_prod['month_dt'] < target_month) & 
                        (df_prod['month_dt'] >= target_month - pd.DateOffset(months=window))]

    # Only include months with enough history
    if recent_df.empty or recent_df['month'].nunique() < window // 2:
        return 'stable'

    # Now calculate product-wise composite score (sold × profit_share)
    recent_scores = (recent_df['products_sold'] * recent_df['profit_share']).groupby(recent_df['month']).sum()

    
    
    # Current month score
    current_df = df_prod[df_prod['month'] == month]
    current_score = (current_df['products_sold'] * current_df['profit_share']).sum()

    

    # Use hypothesis testing with recent scores
    return hypothesis_testing(recent_scores, current_score, ['climbing', 'declining', 'stable'])


# competition variable buisness ya product schema mmai nhi hai 
# but ise derive kr skte hai existing variables se 

#option 1 
def label_competition(df_biz, row):
    z_new = (row['new_customers'] - df_biz['new_customers'].mean()) / df_biz['new_customers'].std(ddof=0)
    z_repeat = (row['repeat_customers'] - df_biz['repeat_customers'].mean()) / df_biz['repeat_customers'].std(ddof=0)
    z_basket = (row['avg_basket_size'] - df_biz['avg_basket_size'].mean()) / df_biz['avg_basket_size'].std(ddof=0)
    # z>0 -> value is above average && z<0 -> value is below average 

    #Low new customers = competitors are attracting them.

    #High repeat customers = your loyal base = less threat.

    #High avg basket size = good consumer spend = less competitive pressure.


    # Composite competition score (weight new customers more)
    score = -0.5 * z_new + 0.3 * z_repeat + 0.2 * z_basket
    #z-new -> weight -> -0.5 strong negative weight -> lower new customer means higher competition
    #z-repeate -> weight -> 0.3 more loyal repeate customers -> lower competition 
    #z-baslet -> weight -> 0.2 high basket sizs indicates healthy customer behavior

    if score >= 0.8:
        return 'low'        # strong repeat + spend → less external competition
    elif score <= -0.8:
        return 'high'       # weak metrics → more competition
    else:
        return 'stable'


 

# option 2 
"""def label_competition(df_biz, row):
    pct_new = (df_biz['new_customers'] < row['new_customers']).mean()
    # how many past months had fewer customers than the current row
    pct_repeat = (df_biz['repeat_customers'] < row['repeat_customers']).mean()
    pct_basket = (df_biz['avg_basket_size'] < row['avg_basket_size']).mean()

    # Strong indicators → low competition
    score = 0
    score += 1 if pct_repeat > 0.75 else -1 if pct_repeat < 0.25 else 0
    #pct-repeate < 0.25 -> comntribution to score -1 -> poor repeate cusstomer retention 
    #pct-repeate > 0.75 -> contribution to score +1 -> good retention 
    score += 1 if pct_basket > 0.75 else -1 if pct_basket < 0.25 else 0
    #pct-basket < 0.25 -> contribution to score -1 -> poor avg basket size 
    #pct-basket > 0.75 -> contribution to score +1 -> goos baket size
    score += -1 if pct_new < 0.25 else 1 if pct_new > 0.75 else 0
    #pct-new < 0.25 -> contribution to score -1 -> poor new customer flow
    #pct-new > 0.75 -> contriution to score -> strong new customer flow 

    if score >= 2:
        return 'low'
    elif score <= -2:
        return 'high'
    else:
        return 'stable' """

# festival, usual or off season marking 
def label_season(month):
    m = int(month[-2:])
    if m in [10, 11, 12]:
        return 'festive'
    elif m in [1, 2]:
        return 'off'
    else:
        return 'usual'
    
def label_external_factors(economy, season, competition):
    score = 0

    # Economy scoring
    score += {'good': 1, 'neutral': 0, 'bad': -1}.get(economy, 0)

    # Season scoring
    score += {'festive': 1, 'usual': 0, 'off': -1}.get(season, 0)

    # Competition scoring
    score += {'low': 1, 'stable': 0, 'high': -1}.get(competition, 0)

    # Total score range: -3 to +3
    if score >= 2:
        return 'favourable'
    elif score <= -2:
        return 'unfavourable'
    else:
        return 'moderate'


def label_strategic_levers(pricing, stocking):
    score = 0

    # Pricing — lower prices = stronger lever
    score += {'low': 1, 'stable': 0, 'high': -1}.get(pricing, 0)

    # Stocking — abundant/balanced = stronger lever
    score += {'abundant': 1, 'balanced': 0, 'short': -1}.get(stocking, 0)

    if score >= 2:
        return 'high'
    elif score <= -1:
        return 'low'
    else:
        return 'moderate'


    
def save_labelled_row(cur, data):
    placeholders = ', '.join(['?'] * len(data))
    columns = ', '.join(data.keys())
    sql = f"INSERT OR REPLACE INTO labelled_data ({columns}) VALUES ({placeholders})"
    cur.execute(sql, list(data.values()))

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    df_biz = pd.read_sql_query("SELECT * FROM business_metrics", conn)
    df_prod = pd.read_sql_query("SELECT * FROM product_metrics", conn)

    # Drop existing table if any
    cur.execute("DROP TABLE IF EXISTS labelled_data")
    cur.execute("""
        CREATE TABLE labelled_data (
            month TEXT PRIMARY KEY,
            profits TEXT CHECK (profits IN ('high', 'low', 'stable')),
            sales TEXT CHECK (sales IN ('high', 'low', 'stable')),
            costs TEXT CHECK (costs IN ('high', 'low', 'stable')),
            competition TEXT CHECK (competition IN ('high', 'low', 'stable')),
            pricing TEXT CHECK (pricing IN ('high', 'low', 'stable')),
            economy TEXT CHECK (economy IN ('good', 'bad', 'neutral')),
            operational_efficiency TEXT CHECK (operational_efficiency IN ('smooth', 'rough', 'expected')),
            stocking TEXT CHECK (stocking IN ('abundant', 'short', 'balanced')),
            product_popularity TEXT CHECK (product_popularity IN ('climbing', 'declining', 'stable')),
            season TEXT CHECK (season IN ('festive', 'off', 'usual')),
            external_factors TEXT CHECK (external_factors IN ('favourable', 'moderate', 'unfavourable')),
            strategic_levers TEXT CHECK (strategic_levers IN ('high', 'moderate', 'low')),
            FOREIGN KEY (month) REFERENCES business_metrics(month)
        )
    """)

    for i in range(len(df_biz)):
        row = df_biz.loc[i]
        month = row['month']

        profits = label_profits(df_biz, row)
        sales = label_sales(df_biz, row)
        costs = label_costs(df_biz, row)
        competition = label_competition(df_biz, row)
        pricing = label_pricing(df_prod, month)
        economy = label_economy(df_biz, row)
        operational_efficiency = label_operational_efficiency(df_biz, row)
        stocking = label_stocking(df_prod, month)
        product_popularity = label_product_popularity(df_prod, month)
        season = label_season(month)

        external_factors = label_external_factors(economy, season, competition,)
        strategic_levers = label_strategic_levers(pricing, stocking,)

        data = {
            'month': month,
            'profits': profits,
            'sales': sales,
            'costs': costs,
            'competition': competition,
            'pricing': pricing,
            'economy': economy,
            'operational_efficiency': operational_efficiency,
            'stocking': stocking,
            'product_popularity': product_popularity,
            'season': season,
            'external_factors': external_factors,
            'strategic_levers': strategic_levers
        }

        save_labelled_row(cur, data)

    conn.commit()
    conn.close()
    print("✅ Labelled data saved to `labelled_data` table.")

# remove the comment sytax to print count of labelled data for each metric
"""conn = sqlite3.connect(DB)
df_labels = pd.read_sql_query("SELECT * FROM labelled_data", conn)
for col in df_labels.columns[1:]:
    print(f"\n{col}:\n", df_labels[col].value_counts())"""

if __name__ == "__main__":
    main()
