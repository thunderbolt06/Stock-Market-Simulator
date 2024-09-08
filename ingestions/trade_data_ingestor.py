import os
import pandas as pd
from datetime import datetime

from assessment_app.models.schema import TradeData
from assessment_app.repository.database import get_db


stocks = ["HDFCBANK", "ICICIBANK", "RELIANCE", "TATAMOTORS"]
#  Read .csv from `data` folder and ingest to database
def ingest_trade_data_to_db():
    db = get_db()
    # Read all files from `data` folder and ingest to database
    for file in os.listdir(os.path.join(os.path.dirname(__file__), "..", "..", "data")):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "..", "data", file))
            df["date"] = pd.to_datetime(df["Date"])
            for index, row in df.iterrows():
                trade_data = TradeData(symbol=file.split('.')[0], date=row["date"], open=row["Open"], high=row["High"], low=row["Low"], close=row["Close"], adj_close=row["Adj Close"], volume=row["Volume"])
                db.add(trade_data)
            db.commit()


ingest_trade_data_to_db()

