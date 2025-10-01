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
