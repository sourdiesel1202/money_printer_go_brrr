from enums import OrderType
import datetime,io
from zoneinfo import ZoneInfo
from functions import generate_csv_string, read_csv, write_csv, delete_csv
import pandas as pd
from stockstats import wrap
def load_ticker_history_raw(ticker,client, multiplier = 1, timespan = "hour", from_ = "2023-07-06", to = "2023-07-06", limit=50):
    # ticker = ticker, multiplier = 1, timespan = "hour", from_ = "2023-07-06", to = "2023-07-06",
    # limit = 50000
    history_data =  []
    for entry in client.list_aggs(ticker=ticker,multiplier = multiplier, timespan = timespan, from_ = from_, to = to, limit=limit, sort='asc'):
        entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
        print(f"{entry_date}: {ticker}| Open: {entry.open} High: {entry.high} Low: {entry.low} Close: {entry.close} Volume: {entry.volume}")
        history_data.append(entry)
    return history_data

def load_ticker_history_csv(ticker,client, multiplier = 1, timespan = "hour", from_ = "2023-07-06", to = "2023-07-06", limit=50):

    # rows = load_ticker_history_raw(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)
    rows = [['date', 'open', 'close', 'high', 'low', 'volume']]
    for entry in load_ticker_history_raw(ticker,client,multiplier, timespan, from_,to,limit):
        rows.append([entry.timestamp, entry.open, entry.close, entry.high, entry.low, entry.volume])
    return  rows


def load_ticker_history_pd_frame(ticker,client, multiplier = 1, timespan = "hour", from_ = "2023-07-06", to = "2023-07-06", limit=50):
    _str = generate_csv_string(load_ticker_history_csv(ticker,client,multiplier, timespan, from_,to,limit))
    df = pd.read_csv(io.StringIO(generate_csv_string(load_ticker_history_csv(ticker,client,multiplier, timespan, from_,to,limit))), sep=",")
    return df

# def load_ticker_