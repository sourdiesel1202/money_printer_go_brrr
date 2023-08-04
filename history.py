import os
import time, polygon

import mibian
from polygon import OptionSymbol

from enums import OrderType, PositionType
import datetime,io
from zoneinfo import ZoneInfo
from functions import generate_csv_string, read_csv, write_csv, delete_csv, get_today, timestamp_to_datetime, human_readable_datetime, execute_query, execute_update
import pandas as pd
import polygon
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

class ContractHistory(TickerHistory):
    implied_volatility = 0.0
    delta = 0.0
    theta = 0.0
    gamma = 0.0
    rho = 0.0
    underlying_close = 0.0
    contract = ''
    def __init__(self,contract,underlying_close, open, close, high, low, volume, timestamp):

        super().__init__( open, close, high, low, volume, timestamp)
        self.contract = contract
        self.underlying_close = underlying_close
        self.calculate_greeks()
        #ok so once we've called the constructor, we can go ahead and set our  greeks

    def calculate_greeks(self):
        if len(self.contract) == 0:
            raise  Exception("Cannot calculate greeks for a ContractHistory with no contract attribute specified")
        # contract_details = polygon.parse_option_symbol(self.contract)
        option_symbol = OptionSymbol(self.contract)
        dte = (datetime.datetime(*option_symbol.expiry.timetuple()[:-4]) - datetime.datetime.now()).days
        position_type = PositionType.LONG if option_symbol.call_or_put.upper() == PositionType.LONG_OPTION[0].upper() else PositionType.SHORT
        if position_type == PositionType.LONG:
            _tmp_iv = mibian.BS([self.underlying_close, float(option_symbol.strike_price), 0, dte],
                                callPrice=self.close).impliedVolatility

        else:
            _tmp_iv = mibian.BS([self.underlying_close, float(option_symbol.strike_price), 0, dte],
                                putPrice=self.close).impliedVolatility
        self.implied_volatility = _tmp_iv
        greeks = mibian.BS([self.underlying_close, float(option_symbol.strike_price), 0, dte],
                           volatility=_tmp_iv)
        if position_type == PositionType.LONG:
            self.theta = greeks.callTheta
            self.delta = greeks.callDelta
            self.gamma = greeks.gamma
            self.rho = greeks.callRho
        else:
            self.theta = greeks.putTheta
            self.delta = greeks.putDelta
            self.gamma = greeks.gamma
            self.rho = greeks.putRho

def write_ticker_history_db_entries(connection, ticker, ticker_history, module_config):
    values_entries =[]
    for th in ticker_history:
        values_entries.append(f"((select id from tickers_ticker where symbol='{ticker}'), {th.open}, {th.close}, {th.high}, {th.low}, {th.volume},{th.timestamp},'{module_config['timespan']}','{module_config['timespan_multiplier']}')")
        # write_ticker_history_db_entry(connection,ticker, th, module_config)
    #ok so dumb but before we run this let's do a select
    if len(execute_query(connection, f"select * from history_tickerhistory where timespan='{module_config['timespan']}' and timespan_multiplier='{module_config['timespan_multiplier']}' and ticker_id=(select id from tickers_ticker where symbol='{ticker}')", verbose=False)) == 1:

        # for values in values_entries:

        history_sql = f"INSERT ignore INTO history_tickerhistory ( ticker_id,open, close, high, low, volume, timestamp, timespan, timespan_multiplier) VALUES {','.join(values_entries)}"
            # history_sql = f"INSERT ignore INTO history_tickerhistory ( ticker_id,open, close, high, low, volume, timestamp, timespan, timespan_multiplier) VALUES {values}"
        execute_update(connection,history_sql,verbose=False, auto_commit=False)
    connection.commit()

    # execute_query(connection, f"select count(timestamp) from history_tickerhistory  where ticker_id=(select id from tickers_ticker where symbol='{ticker}') and timespan='{module_config['timespan']}' and timespan_multiplier='{module_config['timespan_multiplier']}'")
    # try:
    #     history_sql = f"INSERT ignore INTO history_tickerhistory ( ticker_id,open, close, high, low, volume, timestamp, timespan, timespan_multiplier) VALUES {','.join(values_entries)}"
    #     execute_update(connection,history_sql,verbose=True, auto_commit=True)
    # except:
    #     try:
    #         history_sql = f"INSERT ignore INTO history_tickerhistory ( ticker_id,open, close, high, low, volume, timestamp, timespan, timespan_multiplier) VALUES {','.join(values_entries)}"
    #         execute_update(connection, history_sql, verbose=True, auto_commit=True)
    #     except Exception as e:
    #         print(f"Could not process ticker history for {ticker}")
    #         raise e
    connection.commit()
def convert_ticker_history_to_csv(ticker, ticker_history):
    rows = [['o','c','h','l','v','t']]
    for history in ticker_history:
        rows.append([history.open, history.close, history.high, history.low, history.volume, history.timestamp])
    return rows
def load_ticker_history_cached(ticker,module_config, connection=None):
    ticker_history = []

    if connection is None:
        for entry in read_csv(f"{module_config['output_dir']}cached/{ticker}{module_config['timespan_multiplier']}{module_config['timespan']}.csv")[1:]:
            ticker_history.append(TickerHistory(*[float(x) for x in entry]))
    else:
        records =execute_query(connection, f"select open, close, high, low, volume, timestamp from history_tickerhistory where timespan='{module_config['timespan']}' and timespan_multiplier='{module_config['timespan_multiplier']}' and ticker_id=(select id from tickers_ticker where symbol='{ticker}') order by timestamp asc")
        ticker_history =[TickerHistory(*[float(x) if '.' in x else int(x) for x in records[i]]) for i in range(1, len(records))]

    if module_config['test_mode']:
        if module_config['test_use_test_time']:
            # print(f"using test time")
            # rn make this work with the hours only
            for i in range(0, len(ticker_history)):
                if timestamp_to_datetime(ticker_history[-i].timestamp).hour == module_config['test_time']:
                    return ticker_history[:-i + 1]
                    # break

    return ticker_history
def clear_ticker_history_cache(module_config):
    os.system (f" rm -rf {module_config['output_dir']}cached/")
    os.mkdir(f"{module_config['output_dir']}cached/")
def clear_ticker_history_cache_entry(ticker, module_config):
    os.system(f"rm {module_config['output_dir']}cached/{ticker}{module_config['timespan_multiplier']}{module_config['timespan']}.csv")
    # os.mkdir(f"{module_config['output_dir']}cached/")
def load_ticker_history_raw(ticker,client, multiplier = 1, timespan = "hour", from_ = "2023-07-06", to = "2023-07-06", limit=500, module_config={}, cached=False, connection=None):
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
        if connection is not None:
            write_ticker_history_db_entries(connection, ticker, history_data, {"timespan":timespan, "timespan_multiplier":multiplier})
        if module_config['timespan'] == 'hour':
            history_data = normalize_history_data_for_hour(ticker, history_data, module_config)
            module_config['timespan_multiplier'] = module_config['og_ts_multiplier']
            if connection is not None:
                write_ticker_history_db_entries(connection, ticker, history_data, module_config)
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
            # if "O:" in ticker
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


def load_options_history_raw(contract, ticker_history,client, multiplier = 1, timespan = "hour", from_ = "2023-07-06", to = "2023-07-06", limit=500, module_config={}, connection=None):
    # contract = contract, multiplier = 1, timespan = "hour", from_ = today, to = today,
    # limit = 50000
    if timespan == 'hour':
        timespan = 'minute'
        multiplier = 30
        module_config['og_ts_multiplier'] = module_config['timespan_multiplier']
        # module_config['timespan_multiplier'] = multiplier
    # if cached:
    #     return load_ticker_history_cached(contract, module_config)
    # if os.path.exists(f"{module_config['output_dir']}cached/{contract}{module_config['timespan_multiplier']}{module_config['timespan']}.csv"):
    #     clear_ticker_history_cache_entry(contract,module_config)
    history_data =  []
    for entry in client.get_full_range_aggregate_bars(contract,from_, to,multiplier = multiplier, timespan = timespan, sort='asc', run_parallel=False):
        entry = ContractHistory(contract, ticker_history[-1].close,entry['o'],entry['c'],entry['h'],entry['l'],entry['v'],entry['t'])
        entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
        # print(f"{entry_date}: {contract}| Open: {entry.open} High: {entry.high} Low: {entry.low} Close: {entry.close} Volume: {entry.volume}")
        if (datetime.datetime.fromtimestamp(entry.timestamp / 1e3,tz=ZoneInfo('US/Eastern')).hour >= 9 if timespan =='minute' else 10) and (datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern')).hour <= 16 if timespan =='minute' else 15):
            if timespan == 'minute':
                if (datetime.datetime.fromtimestamp(entry.timestamp / 1e3,tz=ZoneInfo('US/Eastern'))).hour == 9 and (datetime.datetime.fromtimestamp(entry.timestamp / 1e3,tz=ZoneInfo('US/Eastern'))).minute < 30:
                    continue
                elif (datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))).hour >=16:
                    continue
                else:
                    history_data.append(ContractHistory(contract, ticker_history[-1].close, entry.open, entry.close, entry.high, entry.low, entry.volume,entry.timestamp))

            else:
                history_data.append(ContractHistory(contract, ticker_history[-1].close,entry.open, entry.close,entry.high, entry.low, entry.volume, entry.timestamp))

    if module_config['test_mode']:
        if module_config['test_use_test_time']:
            # print(f"using test time")
            #rn make this work with the hours only
            for i in range(0, len(history_data)):
                if timestamp_to_datetime(history_data[-i].timestamp).hour == module_config['test_time']:
                    history_data = history_data[:-i+1]
                    break
    # if len(history_data) >0:
    #     print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${contract}: Latest History Record: {datetime.datetime.fromtimestamp(history_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:Oldest History Record: {datetime.datetime.fromtimestamp(history_data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:Total: {len(history_data)}")
    #     write_ticker_history_cached(contract, history_data, module_config)
    if len(history_data) > 0:
        if connection is not None:
            write_contract_history_db_entries(connection, contract, history_data,
                                            {"timespan": timespan, "timespan_multiplier": multiplier})
        if module_config['timespan'] == 'hour':
            history_data = normalize_contract_history_data_for_hour(contract, history_data,ticker_history, module_config)
            module_config['timespan_multiplier'] = module_config['og_ts_multiplier']
            if connection is not None:
                if len(history_data) > 0:
                    write_contract_history_db_entries(connection, contract, history_data, module_config)
            # if module_config['logging']:
    if len(history_data) > 0:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:Contract ${contract}: Latest History Record: {datetime.datetime.fromtimestamp(history_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:Oldest History Record: {datetime.datetime.fromtimestamp(history_data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:Total: {len(history_data)}")
    connection.commit()
    return history_data

def write_contract_history_db_entries(connection, ticker, contract_history, module_config):
    values_entries =[]
    for th in contract_history:
        values_entries.append(f"((select id from tickers_contract where symbol='{ticker}'), {th.open}, {th.close}, {th.high}, {th.low}, {th.volume},{th.timestamp},'{module_config['timespan']}','{module_config['timespan_multiplier']}', {th.implied_volatility}, {th.delta}, {th.theta},{th.gamma}, {th.rho})")
        # write_contract_history_db_entry(connection,ticker, th, module_config)
    #ok so dumb but before we run this let's do a select
    if len(execute_query(connection, f"select * from history_contracthistory where timestamp >= {contract_history[0].timestamp} and timespan='{module_config['timespan']}' and timespan_multiplier='{module_config['timespan_multiplier']}' and contract_id=(select id from tickers_ticker where symbol='{ticker}')", verbose=False)) == 1:

        history_sql = f"INSERT ignore INTO history_contracthistory ( contract_id,open, close, high, low, volume, timestamp, timespan, timespan_multiplier, implied_volatility, delta, theta, gamma, rho) VALUES {','.join(values_entries)}"
        execute_update(connection,history_sql,verbose=True, auto_commit=False)


def load_cached_option_tickers(ticker, module_config):
    return [x.split(f"{module_config['timespan_multiplier']}{module_config['timespan']}.csv")[0] for x in os.listdir(f"{module_config['output_dir']}cached/") if f"O:{ticker}" in x]


def normalize_contract_history_data_for_hour(ticker, contract_history,ticker_history, module_config):
    i = 1
    complete = False

    new_contract_history = []
    # reversed(contract_history)
    # start = timestamp_to_datetime(contract_history[-1].timestamp)
    _th = []
    #ok so first let's go ahead and correct all the ticker histories
    # for i in range(1, len(contract_history)):
    #     adjusted_date = timestamp_to_datetime(contract_history[-i].timestamp) -datetime.timedelta(minutes=module_config['timespan_multiplier'])
    #     adjusted_timestsamp  = int(float(adjusted_date.strftime('%s.%f')) * 1e3)
    #     _th.append(TickerHistory(contract_history[-i].open, contract_history[-i].close, contract_history[-i].high,contract_history[-i].low, contract_history[-i].volume, adjusted_timestsamp))
    # for i in range(1, len(_th)+1):
    #     new_contract_history.append(_th[-i])
    # reversed(_th)
    # last_bar_of_day = 30 if module_config['timespan'] == 'minute' or module_config['timespan'] != 'minue'
    # reversed(_th)
    # dumber = [timestamp_to_datetime(x.timestamp) for x in new_contract_history]
    # contract_history = new_contract_history
    # dumb = [timestamp_to_datetime(x.timestamp) for x in contract_history]
    i = 1
    # for i in range(1, ):
    result = []
    while True:
        if i > (len(contract_history) - int(60 / 30)):
            break

        try:
            underlying_entry = [x for x in ticker_history if x.timestamp == contract_history[-i].timestamp][0]
        except:
            i = i + 1
            print(f"Cannot determine underlying value for: {ticker}:{contract_history[-i].timestamp}")
            continue
        normalized_time = timestamp_to_datetime(contract_history[-i].timestamp)
        if module_config['logging']:
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${ticker}: Normalizing History Record: {datetime.datetime.fromtimestamp(contract_history[-i].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:")
        # if ((normalized_time + datetime.timedelta(minutes=module_config['timespan_multiplier'])).hour == 10  and  (normalized_time + datetime.timedelta(minutes=module_config['timespan_multiplier'])).minute < module_config['timespan_multiplier']) or (normalized_time + datetime.timedelta(minutes=module_config['timespan_multiplier'])).hour < 10:
        #     if module_config['logging']:
        #         print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${ticker}: History Record: {datetime.datetime.fromtimestamp(contract_history[-i].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}: Is PreMarket data, Skipping")
        #     i = i+1
        #     continue
        if (normalized_time + datetime.timedelta(minutes=30)).hour == 16 and (normalized_time + datetime.timedelta(minutes=30)).minute == 0:
            result.append(contract_history[-i])
            i = i + 1
            continue
        hour = {'opens':[contract_history[-(i)].open],'closes':[contract_history[-i].close],'highs':[contract_history[-i].high], 'lows':[contract_history[-i].low], 'volumes':[contract_history[-i].volume], 'timestamps': [contract_history[-i].timestamp]}

        increment_idx = 0
        for ii in range(1,int(60/30)):
            if module_config['logging']:
                print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${ticker}: Processing Previous Bar For: {datetime.datetime.fromtimestamp(contract_history[-i].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}: {datetime.datetime.fromtimestamp(contract_history[-(i+ii)].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:")
            hour['highs'].append(contract_history[-(i+ii)].high)
            hour['lows'].append(contract_history[-(i+ii)].low)
            hour['volumes'].append(contract_history[-(i+ii)].volume)
            hour['timestamps'].append(contract_history[-(i+ii)].timestamp)
            hour['opens'].append(contract_history[-(i+ii)].open)
            hour['closes'].append(contract_history[-(i+ii)].close)
            increment_idx = ii+1
            # i = i +1
        # if (timestamp_to_datetime(contract_history[-i]) - timestamp_to_datetime(contract_history[-(i+ii)])):
        #     pass
        now = datetime.datetime.now()
        # if normalized_time.day == now.day and normalized_time.month == now.month and normalized_time.year == now.year:#and now.minute > 30:
        # print()
        if normalized_time.minute > 30:
            # if "O:" in ticker

            th = ContractHistory(ticker,underlying_entry.close,hour['opens'][-1], hour['closes'][0], max(hour['highs']), min(hour['lows']), sum(hour['volumes']), hour['timestamps'][0])
        else:
            # underlying_entry = [x for x in ticker_history if x.timestamp == hour['timestamps'][-1]][0]
            th = ContractHistory(ticker,underlying_entry.close,hour['opens'][-1], hour['closes'][0], max(hour['highs']), min(hour['lows']),
                               sum(hour['volumes']), hour['timestamps'][-1])
        # else:
        #     th = TickerHistory(hour['opens'][-1], hour['closes'][0], max(hour['highs']), min(hour['lows']), sum(hour['volumes']), hour['timestamps'][-1])
        if module_config['logging']:
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${ticker}: Normalized History Record: {datetime.datetime.fromtimestamp(th.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:")
        result.append(th)
        i = i + (increment_idx)
        # if timestamp_to_datetime(contract_history[-i].timestamp).minute == 0 or timestamp_to_datetime(contract_history[-i].timestamp).minute % module_config['timespan_multiplier'] == 0:
        #     new_contract_history.append(contract_history[-i])
        # else:
    # sorted(result, key=lambda x: x.timestamp)
    result.reverse()
    return  result
    # whilenot complete:
    #     if i == len(ticker_history):
    #         break

    pass