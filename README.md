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

