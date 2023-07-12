from enums import OrderType
import datetime,io
from zoneinfo import ZoneInfo
from functions import generate_csv_string, read_csv, write_csv, delete_csv, get_today
import pandas as pd
from stockstats import wrap
# today =datetime.datetime.now().strftime("%Y-%m-%d")

def load_ticker_history_raw(ticker,client, multiplier = 1, timespan = "hour", from_ = "2023-07-06", to = "2023-07-06", limit=500):
    # ticker = ticker, multiplier = 1, timespan = "hour", from_ = today, to = today,
    # limit = 50000
    history_data =  []
    for entry in client.list_aggs(ticker=ticker,multiplier = multiplier, timespan = timespan, from_ = from_, to = to, limit=50000, sort='asc'):
        entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
        # print(f"{entry_date}: {ticker}| Open: {entry.open} High: {entry.high} Low: {entry.low} Close: {entry.close} Volume: {entry.volume}")
        if datetime.datetime.fromtimestamp(entry.timestamp / 1e3,
                                           tz=ZoneInfo('US/Eastern')).hour >= 9 and datetime.datetime.fromtimestamp(
                entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern')).hour <= 16:
            history_data.append(entry)
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${ticker}: Latest History Record: {datetime.datetime.fromtimestamp(history_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:Oldest History Record: {datetime.datetime.fromtimestamp(history_data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:")
    return history_data

def load_ticker_history_csv(ticker, ticker_history):

    # rows = load_ticker_history_raw(ticker,client,1, "hour", today,today,5000)
    rows = [['date', 'open', 'close', 'high', 'low', 'volume']]
    for entry in ticker_history:
        rows.append([entry.timestamp, entry.open, entry.close, entry.high, entry.low, entry.volume])
    return  rows


def load_ticker_history_pd_frame(ticker, ticker_history):
    _str = generate_csv_string(load_ticker_history_csv(ticker,ticker_history))
    df = pd.read_csv(io.StringIO(_str), sep=",")
    return df

# def load_ticker_