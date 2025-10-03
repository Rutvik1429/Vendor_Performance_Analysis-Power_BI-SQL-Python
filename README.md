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


# Python 
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

  
