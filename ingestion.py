import pandas as pd
import os
from sqlalchemy import create_engine
import logging
import time

logging.basicConfig(
    filename="logs/ingestion_db.log",             
    filemode="a",                   
    level=logging.DEBUG,             
    format="%(asctime)s - %(levelname)s - %(message)s"
)

engine = create_engine("sqlite:///inventory.db")

def ingest_db(df,table_name, engine):
    '''this fuctions will ingest dataframe into database table'''
    df.to_sql(table_name , con = engine, if_exists = "replace" , index = False ,chunksize=10000)
    
def Load_raw_data():
    '''this function will load the csv as dataframe and ingest of db'''
    start = time.time()
    for file in os.listdir('data'):
        if '.csv' in file:
            df = pd.read_csv('data/'+file)
            logging.info(f'ingesting {file} in db')
            ingest_db(df , file[:-4],engine)
    end = time.time()
    total_time = (end - start)/60
    logging.info("-----ingestion complete-----")
    logging.info(f'ingestion completed time Taken: {total_time} minutes')

if __name__ == '__main__':
    Load_raw_data()