import os
import time

from enums import OrderType
import datetime,io
from zoneinfo import ZoneInfo
from functions import generate_csv_string, read_csv, write_csv, delete_csv, get_today, timestamp_to_datetime, human_readable_datetime
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
    dt = None
    def __init__(self, open, close, high, low, volume, timestamp):
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = volume
        self.timestamp =timestamp
        self.dt = timestamp_to_datetime(timestamp)
def convert_ticker_history_to_csv(ticker, ticker_history):
    rows = [['o','c','h','l','v','t']]
    for history in ticker_history:
        rows.append([history.open, history.close, history.high, history.low, history.volume, history.timestamp])
    return rows
def load_ticker_history_cached(ticker,module_config):
    ticker_history = []
    for entry in read_csv(f"{module_config['output_dir']}cached/{ticker}{module_config['timespan_multiplier']}{module_config['timespan']}.csv")[1:]:
        ticker_history.append(TickerHistory(*[float(x) for x in entry]))

    if module_config['test_mode']:
        if module_config['test_use_test_time']:
            # print(f"using test time")
            # rn make this work with the hours only
            for i in range(0, len(ticker_history)):
                if timestamp_to_datetime(ticker_history[-i].timestamp).hour == module_config['test_time']:
                    history_data = ticker_history[:-i + 1]
                    break

    return ticker_history
def clear_ticker_history_cache(module_config):
    os.system (f" rm -rf {module_config['output_dir']}cached/")
    os.mkdir(f"{module_config['output_dir']}cached/")
def clear_ticker_history_cache_entry(ticker, module_config):
    os.system(f"rm {module_config['output_dir']}cached/{ticker}{module_config['timespan_multiplier']}{module_config['timespan']}.csv")
    # os.mkdir(f"{module_config['output_dir']}cached/")
def load_ticker_history_raw(ticker,client, multiplier = 1, timespan = "hour", from_ = "2023-07-06", to = "2023-07-06", limit=500, module_config={}, cached=False):
    # ticker = ticker, multiplier = 1, timespan = "hour", from_ = today, to = today,
    # limit = 50000
    if timespan == 'hour':
        timespan = 'minute'
        multiplier = 30
        module_config['og_ts_multiplier'] = module_config['timespan_multiplier']
        # module_config['timespan_multiplier'] = multiplier
    if cached:
        return load_ticker_history_cached(ticker, module_config)
    else:
        if os.path.exists(f"{module_config['output_dir']}cached/{ticker}{module_config['timespan_multiplier']}{module_config['timespan']}.csv"):
            clear_ticker_history_cache_entry(ticker,module_config)
        history_data =  []
        for entry in client.list_aggs(ticker=ticker,multiplier = multiplier, timespan = timespan, from_ = from_, to = to, limit=50000, sort='asc'):
            entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
            # print(f"{entry_date}: {ticker}| Open: {entry.open} High: {entry.high} Low: {entry.low} Close: {entry.close} Volume: {entry.volume}")
            if (datetime.datetime.fromtimestamp(entry.timestamp / 1e3,tz=ZoneInfo('US/Eastern')).hour >= 9 if timespan =='minute' else 10) and (datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern')).hour <= 16 if timespan =='minute' else 15):
                if timespan == 'minute':
                    if (datetime.datetime.fromtimestamp(entry.timestamp / 1e3,tz=ZoneInfo('US/Eastern'))).hour == 9 and (datetime.datetime.fromtimestamp(entry.timestamp / 1e3,tz=ZoneInfo('US/Eastern'))).minute < 30:
                        continue
                    elif (datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))).hour >=16:
                        continue
                    else:
                        history_data.append(TickerHistory(entry.open, entry.close, entry.high, entry.low, entry.volume,entry.timestamp))

                else:
                    history_data.append(TickerHistory(entry.open, entry.close,entry.high, entry.low, entry.volume, entry.timestamp))

        if module_config['test_mode']:
            if module_config['test_use_test_time']:
                # print(f"using test time")
                #rn make this work with the hours only
                for i in range(0, len(history_data)):
                    if timestamp_to_datetime(history_data[-i].timestamp).hour == module_config['test_time']:
                        history_data = history_data[:-i+1]
                        break
        if module_config['timespan'] == 'hour':
            history_data = normalize_history_data_for_hour(ticker, history_data, module_config)
            module_config['timespan_multiplier'] = module_config['og_ts_multiplier']
            # if module_config['logging']:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${ticker}: Latest History Record: {datetime.datetime.fromtimestamp(history_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:Oldest History Record: {datetime.datetime.fromtimestamp(history_data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:Total: {len(history_data)}")
        write_ticker_history_cached(ticker, history_data, module_config)

        return history_data
def write_ticker_history_cached(ticker, ticker_history, module_config):
    write_csv(f"{module_config['output_dir']}cached/{ticker}{module_config['timespan_multiplier']}{module_config['timespan']}.csv",convert_ticker_history_to_csv(ticker, ticker_history))
def load_ticker_history_csv(ticker, ticker_history, convert_to_datetime=False, human_readable=False):

    # rows = load_ticker_history_raw(ticker,client,1, "hour", today,today,5000)
    rows = [['date', 'open', 'close', 'high', 'low', 'volume']]
    for entry in ticker_history:
        if convert_to_datetime:
            rows.append([timestamp_to_datetime(entry.timestamp) if not human_readable else human_readable_datetime(timestamp_to_datetime(entry.timestamp)) ,  entry.open, entry.close, entry.high, entry.low, entry.volume])
        else:
            rows.append([entry.timestamp, entry.open, entry.close, entry.high, entry.low, entry.volume])
    return  rows


def load_ticker_history_pd_frame(ticker, ticker_history, convert_to_datetime=False, human_readable=False):
    _str = generate_csv_string(load_ticker_history_csv(ticker,ticker_history,convert_to_datetime=convert_to_datetime, human_readable=human_readable))
    df = pd.read_csv(io.StringIO(_str), sep=",")
    return df

# def load_ticker_

def normalize_history_data_for_hour(ticker, ticker_history, module_config):
    i = 1
    complete = False

    new_ticker_history = []
    # reversed(ticker_history)
    # start = timestamp_to_datetime(ticker_history[-1].timestamp)
    _th = []
    #ok so first let's go ahead and correct all the ticker histories
    # for i in range(1, len(ticker_history)):
    #     adjusted_date = timestamp_to_datetime(ticker_history[-i].timestamp) -datetime.timedelta(minutes=module_config['timespan_multiplier'])
    #     adjusted_timestsamp  = int(float(adjusted_date.strftime('%s.%f')) * 1e3)
    #     _th.append(TickerHistory(ticker_history[-i].open, ticker_history[-i].close, ticker_history[-i].high,ticker_history[-i].low, ticker_history[-i].volume, adjusted_timestsamp))
    # for i in range(1, len(_th)+1):
    #     new_ticker_history.append(_th[-i])
    # reversed(_th)
    # last_bar_of_day = 30 if module_config['timespan'] == 'minute' or module_config['timespan'] != 'minue'
    # reversed(_th)
    # dumber = [timestamp_to_datetime(x.timestamp) for x in new_ticker_history]
    # ticker_history = new_ticker_history
    # dumb = [timestamp_to_datetime(x.timestamp) for x in ticker_history]
    i = 1
    # for i in range(1, ):
    result = []
    while True:
        if i > (len(ticker_history) - int(60 / 30)):
            break
        normalized_time = timestamp_to_datetime(ticker_history[-i].timestamp)
        if module_config['logging']:
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${ticker}: Normalizing History Record: {datetime.datetime.fromtimestamp(ticker_history[-i].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:")
        # if ((normalized_time + datetime.timedelta(minutes=module_config['timespan_multiplier'])).hour == 10  and  (normalized_time + datetime.timedelta(minutes=module_config['timespan_multiplier'])).minute < module_config['timespan_multiplier']) or (normalized_time + datetime.timedelta(minutes=module_config['timespan_multiplier'])).hour < 10:
        #     if module_config['logging']:
        #         print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${ticker}: History Record: {datetime.datetime.fromtimestamp(ticker_history[-i].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}: Is PreMarket data, Skipping")
        #     i = i+1
        #     continue
        if (normalized_time + datetime.timedelta(minutes=30)).hour == 16 and (normalized_time + datetime.timedelta(minutes=30)).minute == 0:
            result.append(ticker_history[-i])
            i = i + 1
            continue
        hour = {'opens':[ticker_history[-(i)].open],'closes':[ticker_history[-i].close],'highs':[ticker_history[-i].high], 'lows':[ticker_history[-i].low], 'volumes':[ticker_history[-i].volume], 'timestamps': [ticker_history[-i].timestamp]}
        increment_idx = 0
        for ii in range(1,int(60/30)):
            if module_config['logging']:
                print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${ticker}: Processing Previous Bar For: {datetime.datetime.fromtimestamp(ticker_history[-i].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}: {datetime.datetime.fromtimestamp(ticker_history[-(i+ii)].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:")
            hour['highs'].append(ticker_history[-(i+ii)].high)
            hour['lows'].append(ticker_history[-(i+ii)].low)
            hour['volumes'].append(ticker_history[-(i+ii)].volume)
            hour['timestamps'].append(ticker_history[-(i+ii)].timestamp)
            hour['opens'].append(ticker_history[-(i+ii)].open)
            hour['closes'].append(ticker_history[-(i+ii)].close)
            increment_idx = ii+1
            # i = i +1
        # if (timestamp_to_datetime(ticker_history[-i]) - timestamp_to_datetime(ticker_history[-(i+ii)])):
        #     pass
        now = datetime.datetime.now()
        # if normalized_time.day == now.day and normalized_time.month == now.month and normalized_time.year == now.year:#and now.minute > 30:
        # print()
        if normalized_time.minute > 30:

            th = TickerHistory(hour['opens'][-1], hour['closes'][0], max(hour['highs']), min(hour['lows']), sum(hour['volumes']), hour['timestamps'][0])
        else:
            th = TickerHistory(hour['opens'][-1], hour['closes'][0], max(hour['highs']), min(hour['lows']),
                               sum(hour['volumes']), hour['timestamps'][-1])
        # else:
        #     th = TickerHistory(hour['opens'][-1], hour['closes'][0], max(hour['highs']), min(hour['lows']), sum(hour['volumes']), hour['timestamps'][-1])
        if module_config['logging']:
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${ticker}: Normalized History Record: {datetime.datetime.fromtimestamp(th.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:")
        result.append(th)
        i = i + (increment_idx)
        # if timestamp_to_datetime(ticker_history[-i].timestamp).minute == 0 or timestamp_to_datetime(ticker_history[-i].timestamp).minute % module_config['timespan_multiplier'] == 0:
        #     new_ticker_history.append(ticker_history[-i])
        # else:
    # sorted(result, key=lambda x: x.timestamp)
    result.reverse()
    return  result
    # whilenot complete:
    #     if i == len(ticker_history):
    #         break

    pass