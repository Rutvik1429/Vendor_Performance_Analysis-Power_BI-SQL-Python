# 📊 Vendor Performance Report  

This Power BI dashboard provides a comprehensive analysis of vendor performance, highlighting sales, purchases, profitability, and vendor contribution. The report enables business stakeholders to identify top-performing vendors, monitor profit margins, and track low-performing vendors to optimize vendor relationships.  
  
![Vendor Performance Dashboard](https://github.com/Rutvik1429/Vendor_Performance_Analysis-Power_BI-SQL-Python/blob/main/Vendor_performance_report.png)

This Power BI dashboard provides a comprehensive analysis of vendor performance, highlighting sales, purchases, profitability, and vendor contribution. The report enables business stakeholders to identify top-performing vendors, monitor profit margins, and track low-performing vendors to optimize vendor relationships.  

## 🎯 Objectives  
- To analyze vendor contributions to overall sales and purchases.  
- To identify **top-performing vendors and brands** driving revenue.  
- To evaluate **profitability** through gross profit and profit margin KPIs.  
- To highlight **low-performing vendors**


## 🎯 Objectives  
- To analyze vendor contributions to overall sales and purchases.  
- To identify **top-performing vendors and brands** driving revenue.  
- To evaluate **profitability** through gross profit and profit margin KPIs.  
- To highlight **low-performing vendors and sales areas** for improvement.  
- To track **unsold capital** that can affect cash flow efficiency.  


## 📌 Key KPIs  
- **Total Sales**: $441.41M  
- **Total Purchases**: $307.34M  
- **Gross Profit**: $134.07M  
- **Profit Margin**: 38.72%  
- **Unsold Capital**: $2.71M  


## 📊 Dashboard Overview  

### 1. Top 10 Purchase Contribution %  
- Visualizes vendors’ share of total purchases.  
- **Diageo North America** leads with **16.3% contribution**, followed by **Martignetti Companies (8.3%)**.  

### 2. Top 5 Vendors by Sales  
- **Diageo North America** is the top vendor with **$68M sales**, followed by **Martignetti ($39M)**.  

### 3. Top 5 Brands by Sales  
- **Jack Daniels** leads with **$8M sales**, followed closely by **Tito’s Handmade ($7.4M)** and **Grey Goose ($7.2M)**.  

### 4. Low Performing Vendors  
- Vendors such as **Alisa Carr Beverages (0.62)** and **Highland Wine Merchants (0.71)** show weaker performance.  

### 5. Low Performing Sales (Scatter Plot)  
- Highlights low-margin sales transactions, helping to track where profit margins are not meeting expectations.  


## 🔍 Insights  
1. **Strong Market Leaders**: Diageo North America dominates both sales and purchase contribution, showing strong vendor dependence.  
2. **High Gross Profit**: With a **38.72% profit margin**, overall profitability is healthy.  
3. **Brand Strength**: Jack Daniels, Tito’s, and Grey Goose are the top-selling brands, contributing significantly to vendor sales.  
4. **Vendor Gaps**: Certain vendors like Alisa Carr Beverages and Highland Wine Merchants underperform, requiring strategic review.  
5. **Unsold Capital**: $2.71M in unsold capital highlights opportunities to improve inventory turnover.  

## ✅ Conclusion  
This report provides a **360° view of vendor performance** by combining sales, purchases, and profitability metrics. It supports decision-making by identifying top vendors/brands while also pointing out underperforming areas that need intervention.  


# Python ⚡ Ingestion Process (Single Flow)
CSV files → Pandas DataFrame → SQLite Database (inventory.db) → Logging
## Step Flow in Words:
- Read all CSVs from the data/ folder.
- Convert each CSV into a DataFrame using pandas.
- Load each DataFrame into database as a table (table name = CSV filename).
- Replace old tables if already exist.
- Write logs of progress and time taken in logs/ingestion_db.log.
```
import pandas as pd
import os
from sqlalchemy import create_engine
import logging
import time

# Logging setup
logging.basicConfig(
    filename="logs/ingestion_db.log",
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Database engine (SQLite)
engine = create_engine("sqlite:///inventory.db")

def ingest_db(df, table_name, engine):
    """Ingest dataframe into database table"""
    df.to_sql(
        table_name,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=10000
    )

def Load_raw_data():
    """Load CSV files as dataframe and ingest into database"""
    start = time.time()
    for file in os.listdir('data'):
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join('data', file))
            logging.info(f'Ingesting {file} into database')
            ingest_db(df, file[:-4], engine)
    end = time.time()
    total_time = (end - start) / 60
    logging.info("----- Ingestion Complete -----")
    logging.info(f'Ingestion completed. Time taken: {total_time:.2f} minutes')

if __name__ == '__main__':
    Load_raw_data()
```
## 📌 Why is this Needed ?
- **Centralized Data Storage** → Instead of handling multiple scattered CSV files, all data is loaded into a single database.
- **Automation** → Any new CSV dropped into the data/ folder will be ingested automatically.
- **Reusability** → Once in a database, data can be queried using SQL, joined across tables, or used in BI tools like Power BI/Tableau.
- **Scalability** → Instead of loading CSVs manually, this script can handle large datasets quickly (with chunksize).
- **Logging & Monitoring** → Keeps track of ingestion runs, useful for debugging and production monitoring.
## ✅ Benefits
- **Easy Data Access** → Analysts can query directly from inventory.db.
- **Consistent Schema** → CSVs are turned into structured database tables.
- **Error Tracking** → Logging helps detect which file failed to ingest.
- **Performance** → Using chunking + SQL database is much faster than reading CSVs repeatedly.
- **Future-proof** → Can easily switch from SQLite to enterprise databases by just changing the connection string.

```
import sqlite3
import pandas as pd
import logging
from ingestion_db import ingest_db
import os

logging.basicConfig(
    filename="logs/Get_Vendor_Summary.log",
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def create_vendor_summary(conn):
    '''this function merges the different tables to get overall vendor summary'''
    vendor_sales_summary = pd.read_sql_query("""
        WITH freightsummary AS (
            SELECT VendorNumber,
                   SUM(Freight) AS Freight_Cost 
            FROM vendor_invoice
            GROUP BY VendorNumber
        ),
        purchasesummary AS (
            SELECT 
                p.VendorNumber,
                p.VendorName,
                p.Brand,
                p.Description,
                p.PurchasePrice,
                pp.Volume,
                pp.Price AS ActualPrice,
                SUM(p.Quantity) AS Totalpurchasequantity,
                SUM(p.Dollars) AS Totalpurchasedollars
            FROM purchases p
            JOIN purchase_prices pp
                ON p.Brand = pp.Brand
            WHERE p.PurchasePrice > 0
            GROUP BY p.VendorNumber, p.VendorName, p.Brand, 
                     p.Description, p.PurchasePrice, pp.Volume, pp.Price
        ),
        salessummary AS (
            SELECT
                VendorNo,
                Brand,
                SUM(SalesQuantity) AS Totalsalesquantity,
                SUM(SalesDollars) AS Totalsalesdollars,
                SUM(SalesPrice) AS Totalprice,
                SUM(exciseTax) AS Totalexcisetax
            FROM sales
            GROUP BY VendorNo, Brand
        )
        SELECT 
            ps.VendorNumber,
            ps.VendorName,
            ps.Brand,
            ps.Description,
            ps.PurchasePrice,
            ps.ActualPrice,
            ps.Volume,
            ps.Totalpurchasequantity,
            ps.Totalpurchasedollars,
            ss.Totalsalesquantity,
            ss.Totalsalesdollars,
            ss.Totalprice,
            ss.Totalexcisetax,
            fs.Freight_Cost
        FROM purchasesummary ps
        LEFT JOIN salessummary ss
            ON ps.VendorNumber = ss.VendorNo
            AND ps.Brand = ss.Brand
        LEFT JOIN freightsummary fs
            ON ps.VendorNumber = fs.VendorNumber
        ORDER BY ps.Totalpurchasedollars DESC
    """, conn)

    return vendor_sales_summary   

def clean_data(df):
    '''this function will clean the data'''
    df['Volume'] = df['Volume'].astype('float64')
    df.fillna(0, inplace=True)

    df['VendorName'] = df['VendorName'].str.strip()
    df['Description'] = df['Description'].str.strip()

    df['Grossprofit'] = df['Totalsalesdollars'] - df['Totalpurchasedollars']
    df['ProfitMargin'] = (df['Grossprofit'] / df['Totalsalesdollars']) * 100
    df['StockTurnover'] = df['Totalsalesquantity'] / df['Totalpurchasequantity']
    df['salestopurchaseratio'] = df['Totalsalesdollars'] / df['Totalpurchasedollars']

    return df

if __name__ == '__main__':
    conn = sqlite3.connect("inventory.db")

    logging.info("creating vendor summary table...")
    summary_df = create_vendor_summary(conn)
    logging.info(summary_df.head().to_string())  

    logging.info("cleaning data...")
    clean_df = clean_data(summary_df)
    logging.info(clean_df.head().to_string())   

    logging.info("ingesting data...")
    ingest_db(clean_df, 'vendor_sales_summary', conn)
    logging.info("completed")
```
## Breakdown of the SQL Query:
- **freightsummary** → Aggregates freight/shipping cost per vendor.
- **purchasesummary** → Aggregates vendor purchase details.
- Joins purchases with purchase_prices.
- Computes total purchased quantity & dollars.
- **salessummary** → Aggregates vendor sales details.
- Totals sales quantity, sales revenue, sales price, and excise tax by vendor & brand.
- **Final SELECT** → Joins all summaries:
- Matches purchases with sales (by vendor & brand).
- Adds freight cost info.
- Orders vendors by highest purchase dollars.
## Clean Data Function:
- **Data Cleaning**:
- Converts Volume to numeric.
- Replaces missing values (NaN) with 0.
- Strips whitespace from vendor and product descriptions.
- **Feature Engineering (New Metrics)**:
- Gross Profit = Sales Revenue − Purchase Cost
- Profit Margin = Profit ÷ Sales Revenue × 100
- Stock Turnover = Sales Quantity ÷ Purchase Quantity (efficiency of inventory use)
- Sales-to-Purchase Ratio = Sales Dollars ÷ Purchase Dollars (how much revenue per dollar spent)

# 🎯 Purpose of This Script
- To create a consolidated Vendor Performance table from multiple raw transactional tables.
- To enrich data with financial & operational KPIs (Profit, Margin, Stock Turnover).
- To prepare data for analytics & reporting (Power BI, Tableau, Excel).
- To create a clean, ready-to-use dataset instead of raw fragmented CSVs.

# ✅ Benefits
- **Single Source of Truth**: Combines purchase, sales, and freight into one summary table.
- **Automation**: Eliminates manual SQL joins or Excel merging every time.
- **Performance Metrics**: Provides profitability, efficiency, and ratios for each vendor.
- **Ready for BI Dashboards**: Cleaned & structured data can be used in Power BI dashboards.
- **Reproducible & Scalable**: You can re-run the script whenever new CSVs are added → auto-updates vendor summary.
- **Logging & Monitoring**: Every step is recorded for transparency and debugging.

# 🔍 In-Depth Understanding
This script is basically a data pipeline step:
- **Stage 1 (Raw Data Ingestion)**: Your first script loads CSV files into inventory.db.
- **Stage 2 (Data Transformation)**: This script merges those raw tables into a vendor_sales_summary.
- **Stage 3 (Analytics & BI)**: The summary table feeds into Power BI dashboards (the one you already built).
So this script is the bridge between raw transactional data and business insights.

## Distribution Plot For Numaric Values
```
# Distribution plot for numaric values
numaric_col = df.select_dtypes(include = np.number).columns

plt.figure(figsize=(15,10))
for i ,col in enumerate(numaric_col):
    plt.subplot(4, 4, i+1)
    sns.histplot(df[col], kde=True, bins=30)
    plt.title(col)
plt.tight_layout()
plt.savefig("distribution plot for numaric values.png", dpi=500, bbox_inches="tight")  
plt.show()
```
 **Distribution Shape**
- Shows whether the values are normally distributed (bell curve), skewed left/right, or have unusual peaks.
- Helps check data quality and transformations needed (e.g., log scaling for skewed data).
 **Outliers**
- Extreme values in the histogram tails can highlight outliers in the dataset.
 **Spread of Data**
- The width of the histogram shows the range of values.
- A wider spread = high variance, a narrow spread = low variance.
 **Central Tendency**
- The KDE curve shows where most data points are concentrated (mean/median zone).
 **Comparing Multiple Columns**
- Since every numeric column is plotted, you get a quick EDA overview of all numeric features.
- Useful before applying machine learning models because it tells whether scaling or normalization is needed.

![Distribution plot for numaric values](https://github.com/Rutvik1429/Vendor_Performance_Analysis-Power_BI-SQL-Python/blob/main/plots/distribution%20plot%20for%20numaric%20values.png)

## Correlation Heatmap
```
plt.figure(figsize=(12,8))
correlation_matrix = df[numaric_col].corr()
sns.heatmap(correlation_matrix, annot=True, fmt="0.2f",cmap="cividis",linewidths=0.5)
plt.title("Correlation Heatmap")
plt.savefig("correlation heatmap.png", dpi=500, bbox_inches="tight") 
plt.show()
```
**Correlation Strength**
- Values close to +1 → Strong positive correlation (as one variable increases, the other also increases).
- Values close to -1 → Strong negative correlation (as one increases, the other decreases).
- Values near 0 → Little to no linear relationship.
**Feature Relationships**
- Helps detect multicollinearity (when two or more features are highly correlated).
- This is important for machine learning models (like regression), because multicollinearity can cause instability.
**Feature Selection**
- By checking correlations, you can decide which features to keep, combine, or drop.
- Example: If two features have correlation > 0.9, you may remove one to avoid redundancy.

![correlation heatmap](https://github.com/Rutvik1429/Vendor_Performance_Analysis-Power_BI-SQL-Python/blob/main/plots/correlation%20heatmap.png)

## Identify Brands That Need Promotional Or Pricing Adjustments Which Exhibit Lower Sales Performance But Higher Profit Margins.
```
brand_performance = df.groupby("Description").agg({
    'Totalsalesdollars':'sum',
    'ProfitMargin':'mean'
}).reset_index()

low_sales_threshold = brand_performance['Totalsalesdollars'].quantile(0.15)
high_margin_threshold = brand_performance['ProfitMargin'].quantile(0.85)

# filter brands with low sales but high profit margins
target_brands = brand_performance[
    (brand_performance['Totalsalesdollars'] <= low_sales_threshold) &
    (brand_performance['ProfitMargin'] >= high_margin_threshold)
]
print("brands with low sales but high profit margins:")
display(target_brands.sort_values('Totalsalesdollars'))

brand_performance = brand_performance[brand_performance['Totalsalesdollars']<10000] # for better visualization
plt.figure(figsize=(10, 6))
sns.scatterplot(data=brand_performance, x='Totalsalesdollars', y='ProfitMargin', color='blue', label='all brands', alpha = 0.2)
sns.scatterplot(data=target_brands, x='Totalsalesdollars', y='ProfitMargin', color='red', label='target brands')

plt.axhline(high_margin_threshold, linestyle='--', color='black', label='high margin threshold')
plt.axvline(low_sales_threshold, linestyle='--', color='black', label='low sales threshold')

plt.xlabel("Total Sales ($)")
plt.ylabel("Profit Margin (%)")
plt.title("Brands for Promotional or Pricing Adjustments")
plt.legend()
plt.grid(True)
plt.savefig("filter brands with low sales but high profit margins.png", dpi=500, bbox_inches="tight") 
plt.show()
```
**Identifies “hidden opportunity brands”**
- Brands that don’t sell much, but are very profitable.
- Example: Niche premium products.
**Strategic insights for business**
- These brands could benefit from more promotions, better placement, or marketing investment.
- Boosting their sales would disproportionately increase profits.
**Visual Quadrants Help Decision Making**
You can quickly see which brands are:
  - 💰 High sales & high margin → Keep investing.
  - 📉 High sales & low margin → Need cost optimization or price increase.
  - 💤 Low sales & low margin → Possibly discontinue.
  - 🚀 Low sales & high margin (target brands) → Growth opportunity!

![filter brands with low sales but high profit margins](https://github.com/Rutvik1429/Vendor_Performance_Analysis-Power_BI-SQL-Python/blob/main/plots/filter%20brands%20with%20low%20sales%20but%20high%20profit%20margins.png)

## Which Vendor And Brands Demostrend Highest Sales Performance?
```
def format_dollars(value):
     if value >= 100000:
         return f"{value / 1000000:.2f}M"
     elif value >= 1000:
         return f"{value / 1000:.2f}K"
     else:
         return str(value)

# top 10 vendor and brands 
top_vendor = df.groupby("VendorName")["Totalsalesdollars"].sum().nlargest(10)
top_brands = df.groupby("Description")["Totalsalesdollars"].sum().nlargest(10)
top_vendor
top_brands.apply(lambda x: format_dollars(x))

plt.figure(figsize=(15, 5))

# --- Top Vendors ---
plt.subplot(1, 2, 1)

# Ensure top_vendor is sorted (descending by sales)
top_vendor = top_vendor.sort_values(ascending=False)

ax1 = sns.barplot(
    y=top_vendor.index, 
    x=top_vendor.values, 
    palette="Blues_r", 
    order=top_vendor.index  # order ensures correct sorting
)

plt.title("Top 10 Vendors by Sales", fontsize=14)

for bar in ax1.patches:
    ax1.text(
        bar.get_width() + (bar.get_width() * 0.02),
        bar.get_y() + bar.get_height() / 2,
        format_dollars(bar.get_width()),
        ha='left', va='center', fontsize=10, color='black'
    )

# --- Top Brands ---
plt.subplot(1, 2, 2)

top_brands = top_brands.sort_values(ascending=False)

ax2 = sns.barplot(
    y=top_brands.index.astype(str), 
    x=top_brands.values, 
    palette="Reds_r", 
    order=top_brands.index.astype(str)  # keep correct order
)

plt.title("Top 10 Brands by Sales", fontsize=14)

for bar in ax2.patches:
    ax2.text(
        bar.get_width() + (bar.get_width() * 0.02),
        bar.get_y() + bar.get_height() / 2,
        format_dollars(bar.get_width()),
        ha='left', va='center', fontsize=10, color='black'
    )

plt.tight_layout()
plt.savefig("top 10 vendors and brands by sales.png", dpi=300, bbox_inches="tight") 
plt.show()
```
**Which Vendors Drive Revenue**
- The Top Vendors chart answers:
  - Who are the key suppliers/vendors contributing the most to total sales?
  - Do a few vendors dominate sales (Pareto effect), or is it more evenly distributed?
**Which Brands Lead the Market**
- The Top Brands chart answers:
  - Which brands/products are customer favorites?
  - Are there star brands that consistently generate the majority of revenue?
**Comparison Between Vendors & Brands**
- Vendors may represent multiple brands, so this dual view gives context:
- A vendor might have many small brands that collectively generate large sales.
- A single brand might outperform entire vendor portfolios.
**Strategic Business Insights**
- High-sales vendors → Maintain strong partnerships, negotiate better terms.
- High-sales brands → Promote heavily, ensure supply availability.
- Vendors/brands missing from Top 10 → Potential candidates for portfolio review (maybe underperforming).

![top 10 vendors and brands by sales](https://github.com/Rutvik1429/Vendor_Performance_Analysis-Power_BI-SQL-Python/blob/main/plots/top%2010%20vendors%20and%20brands%20by%20sales.png)

## Which Vendor Contribute The Most To Total Purchase Dollars ?
```
vendor_performance = df.groupby('VendorName').agg({
    'Totalpurchasedollars':'sum',
    'Grossprofit':'sum',
    'Totalsalesdollars':'sum'
}).reset_index()
vendor_performance["Purchasecontribution%"] = vendor_performance["Totalpurchasedollars"] / vendor_performance["Totalpurchasedollars"].sum()*100
vendor_performance = round(vendor_performance.sort_values('Purchasecontribution%', ascending = False),2)

# display top 10 vendors
top_vendors = vendor_performance.head(10)
top_vendors['Totalsalesdollars'] = top_vendors['Totalsalesdollars'].apply(format_dollars)
top_vendors['Totalpurchasedollars'] = top_vendors['Totalpurchasedollars'].apply(format_dollars)
top_vendors['Grossprofit'] = top_vendors['Grossprofit'].apply(format_dollars)
top_vendors

top_vendors['Cumulative_contribution%'] = top_vendors['Purchasecontribution%'].cumsum()
top_vendors

fig, ax1 = plt.subplots(figsize=(10, 6))

# bar plot for purchase contribution%
sns.barplot(x=top_vendors['VendorName'], y=top_vendors['Purchasecontribution%'], palette="mako", ax=ax1)

for i, value in enumerate(top_vendors['Purchasecontribution%']):
    ax1.text(i, value -1, str(value)+'%', ha='center', fontsize=10, color='white')

# line plot for cumulative contribution%
ax2 = ax1.twinx()
ax2.plot(top_vendors['VendorName'], top_vendors['Cumulative_contribution%'], color='red',marker='o',linestyle='dashed',label='Cumulative_contribution')

ax1.set_xticklabels(top_vendors['VendorName'], rotation=90)
ax1.set_ylabel('Purchase contribution %', color='blue')
ax2.set_ylabel('Cumulative Contribution %', color='red')
ax1.set_xlabel('Vendors')
ax1.set_title('pareto chart: vendor contribution to total purchases')

ax2.axhline(y=100, color='gray', linestyle='dashed', alpha=0.7)
ax2.legend(loc='upper right')
plt.savefig("vendor contribute the most to total purchase dollars.png", dpi=500, bbox_inches="tight") 
plt.show()
```
**Vendor Concentration (80/20 Rule)**
- Pareto principle says: ~20% of vendors account for ~80% of purchases.
- This chart shows if that’s true for your data.
**Top Contributors**
- The tallest bars = vendors with the biggest purchase contribution %.
- These are critical vendors for the business.
**Strategic Insights**
- Vendors in the Top 2–3 probably supply the majority of goods.
- Strong leverage in negotiation with these vendors.
- If a few vendors contribute too much, dependency risk is high.
**Balanced View**
- The bar chart shows individual vendor contributions.
- The red Pareto line shows cumulative coverage (e.g., top 5 vendors = 70% of purchases).

This code creates a Pareto chart of vendor purchases, showing which vendors contribute the most to total purchase dollars, and whether your purchasing is concentrated among a few vendors or spread across many.

![vendor contribute the most to total purchase dollars](https://github.com/Rutvik1429/Vendor_Performance_Analysis-Power_BI-SQL-Python/blob/main/plots/vendor%20contribute%20the%20most%20to%20total%20purchase%20dollars.png)

## How Much Of Total Procurement Is Dependent On The Top Vendors ?
```
print(f"total purchase contribution of top 10 vendors is {round(top_vendors['Purchasecontribution%'].sum(),2)} %")

vendors = list(top_vendors['VendorName'].values)
purchase_contributions = list(top_vendors['Purchasecontribution%'].values)
total_contribution = sum(purchase_contributions)
remaining_contribution = 100 - total_contribution

# append 'other vendors' category
vendors.append('other vendors')
purchase_contributions.append(remaining_contribution)

# donut chart
fig, ax = plt.subplots(figsize=(8, 8))

# generate colors dynamically
cmap = plt.cm.Paired
colors = cmap(np.linspace(0, 1, len(vendors)))

wedges, texts, autotexts = ax.pie(
    purchase_contributions,
    labels=vendors,
    autopct='%1.1f%%',
    startangle=140,
    pctdistance=0.85,
    colors=colors
)

# draw a white circle in the center to create a 'donut' effect
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig.gca().add_artist(centre_circle)

# add total contribution annotation in the center
plt.text(0, 0, f"Top 10 total:\n{total_contribution:.2f}%", 
         fontsize=14, fontweight='bold', ha='center', va='center')

plt.title("Top 10 Vendor's Purchase Contribution (%)")
plt.savefig("total procurement is dependent on the top vendors.png", dpi=500, bbox_inches="tight") 
plt.show()
```
**Dependence on Top Vendors**
- Shows what % of total purchases comes from the top 10 vendors combined.
- If the top 10 contribute, say, 75%, the company is highly dependent on a few vendors.
**Concentration vs. Diversification**
- Large slices for a few vendors = concentration risk.
- More balanced slices = diversified procurement base.
**Strategic Insights**
- Top vendors dominate purchases → Strong negotiation power but also high risk if any vendor fails to deliver.
- Other vendors (remaining contribution) shows the long tail of smaller suppliers.
**Helps procurement teams decide:**
- Should we diversify suppliers?
- Which vendors to prioritize for contracts?

This donut chart provides a clear picture of vendor dependency. It highlights the share of purchases controlled by top vendors and how much the company relies on them compared to the rest.

![total procurement is dependent on the top vendors](https://github.com/Rutvik1429/Vendor_Performance_Analysis-Power_BI-SQL-Python/blob/main/plots/total%20procurement%20is%20dependent%20on%20the%20top%20vendors.png)

## What Is The 95% Confidence Intervals for Profit Margins Of Top-Performing And Low-Performing Vendors.
```
top_threshold = df['Totalsalesdollars'].quantile(0.75)
low_threshold = df['Totalsalesdollars'].quantile(0.25)
top_vendor = df[df['Totalsalesdollars'] >= top_threshold]['ProfitMargin'].dropna()
low_vendor = df[df['Totalsalesdollars'] <= low_threshold]['ProfitMargin'].dropna()

def confidence_interval(data, confidence=0.95):
    mean_val = np.mean(data)
    std_err = np.std(data, ddof=1) / np.sqrt(len(data)) # standard error
    t_critical = stats.t.ppf((1 + confidence) / 2, df=len(data) - 1)
    margin_of_error = t_critical * std_err
    return mean_val, mean_val - margin_of_error, mean_val + margin_of_error

top_mean, top_lower, top_upper = confidence_interval(top_vendor)
low_mean, low_lower, low_upper = confidence_interval(low_vendor)

print(f"Top Vendors 95% CI: ({top_lower:.2f}, {top_upper:.2f}, Mean: {top_mean:.2f})")
print(f"low Vendors 95% CI: ({low_lower:.2f}, {low_upper:.2f}, Mean: {low_mean:.2f})")

plt.figure(figsize=(12, 6))

# top vendors plot
sns.histplot(top_vendor, kde=True, color="green", bins=30, alpha=0.5, label="Top vendors")
plt.axvline(top_lower, color="green", linestyle="--", label=f"Top Lower: {top_lower:.2f}")
plt.axvline(top_upper, color="green", linestyle="--", label=f"Top upper: {top_upper:.2f}")
plt.axvline(top_mean, color="green", linestyle="--", label=f"Top mean: {top_mean:.2f}")

# low vendors plot
sns.histplot(low_vendor, kde=True, color="red", bins=30, alpha=0.5, label="Low vendors")
plt.axvline(low_lower, color="red", linestyle="--", label=f"low Lower: {low_lower:.2f}")
plt.axvline(low_upper, color="red", linestyle="--", label=f"low upper: {low_upper:.2f}")
plt.axvline(low_mean, color="red", linestyle="--", label=f"low mean: {low_mean:.2f}")

# finalize plot
plt.title("Confidence Interval Comparison: Top vs. Low vendors (Profit Margin)")
plt.xlabel("Profit Margin (%)")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.savefig("capital is locked in unsold inventory per vendor, and which vendors contribute the most.png", dpi=500, bbox_inches="tight")
plt.show()
```
**Profitability Difference**
- If top vendors have significantly higher mean profit margins, it means:
- → High-volume vendors are also more profitable.
- → Focus on strengthening relationships with them.
- If low vendors show higher or comparable profit margins, it means:
- → Smaller vendors may be niche but efficient.
- → Could be worth expanding contracts.
**Risk of Overdependence**
- If top vendors dominate sales but profit margins are low or unstable,
- → The business is locking capital in high-sales but low-profit vendors.
- → Need to reassess contract terms.
- Confidence Interval Significance
- Overlapping CIs = no statistically significant difference.
- Non-overlapping CIs = clear performance gap.
- Decision-Making Use Case
- Procurement & finance can decide whether to renegotiate, scale back, or increase reliance on certain vendor categories.

This code performs a statistical comparison of profit margins between top and low vendors, visualizes their distributions, and highlights whether high sales vendors are also driving profitability or not.

![capital is locked in unsold inventory per vendor, and which vendors contribute the most](https://github.com/Rutvik1429/Vendor_Performance_Analysis-Power_BI-SQL-Python/blob/main/plots/capital%20is%20locked%20in%20unsold%20inventory%20per%20vendor%2C%20and%20which%20vendors%20contribute%20the%20most.png)


