import os

from enums import OrderType
import datetime,io
from zoneinfo import ZoneInfo
from functions import generate_csv_string, read_csv, write_csv, delete_csv, get_today
import pandas as pd
from stockstats import wrap
# today =datetime.datetime.now().strftime("%Y-%m-%d")

class TickerHistory:
    open = 0
    close = 0
    high = 0
    low = 0
    volume = 0
    timestamp = 0
    def __init__(self, open, close, high, low, volume, timestamp):
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = volume
        self.timestamp =timestamp

def convert_ticker_history_to_csv(ticker, ticker_history):
    rows = [['o','c','h','l','v','t']]
    for history in ticker_history:
        rows.append([history.open, history.close, history.high, history.low, history.volume, history.timestamp])
    return rows
def load_ticker_history_cached(ticker,module_config):
    ticker_history = []
    for entry in read_csv(f"{module_config['output_dir']}{ticker}.csv")[1:]:
        ticker_history.append(TickerHistory(*[x for x in entry]))
    return ticker_history
def clear_ticker_history_cache(module_config):
    os.system (f" rm -rf {module_config['output_dir']}cached/")
    os.mkdir(f"{module_config['output_dir']}cached/")
def clear_ticker_history_cache_entry(ticker, module_config):
    os.system(f"rm {module_config['output_dir']}cached/{ticker}.csv")
    # os.mkdir(f"{module_config['output_dir']}cached/")
def load_ticker_history_raw(ticker,client, multiplier = 1, timespan = "hour", from_ = "2023-07-06", to = "2023-07-06", limit=500, module_config={}, cached=False):
    # ticker = ticker, multiplier = 1, timespan = "hour", from_ = today, to = today,
    # limit = 50000
    if cached:
        return load_ticker_history_cached(ticker, module_config)
    else:
        if os.path.exists(f"{module_config['output_dir']}cached/{ticker}.csv"):
            clear_ticker_history_cache_entry(module_config)
        history_data =  []
        for entry in client.list_aggs(ticker=ticker,multiplier = multiplier, timespan = timespan, from_ = from_, to = to, limit=50000, sort='asc'):
            entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
            # print(f"{entry_date}: {ticker}| Open: {entry.open} High: {entry.high} Low: {entry.low} Close: {entry.close} Volume: {entry.volume}")
            if datetime.datetime.fromtimestamp(entry.timestamp / 1e3,
                                               tz=ZoneInfo('US/Eastern')).hour >= 10 and datetime.datetime.fromtimestamp(
                    entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern')).hour <= 15:
                history_data.append(TickerHistory(entry.open, entry.close,entry.high, entry.low, entry.volume, entry.timestamp))
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${ticker}: Latest History Record: {datetime.datetime.fromtimestamp(history_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:Oldest History Record: {datetime.datetime.fromtimestamp(history_data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:")
        write_ticker_history_cached(ticker, history_data, module_config)
        return history_data
def write_ticker_history_cached(ticker, ticker_history, module_config):
    write_csv(f"{module_config['output_dir']}cached/{ticker}.csv",convert_ticker_history_to_csv(ticker, ticker_history))
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