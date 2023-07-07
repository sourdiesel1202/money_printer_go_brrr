from enums import OrderType
import datetime
from zoneinfo import ZoneInfo
from history import load_ticker_history_pd_frame, load_ticker_history_csv
from stockstats import wrap
def load_macd(ticker, client,module_config,  **kwargs):
    macd = client.get_macd(ticker=ticker, **kwargs)
    _macd = []
    for entry in macd.values:
        if module_config['logging']:
            if entry.value > entry.signal:
                entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
                # entry_date.tzinfo = ZoneInfo('US/Eastern')
                print(f"{entry_date}: {ticker}: MACD {entry.value} was over signal {entry.signal}: histogram {entry.histogram}")
            else:
                entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
                # entry_date.tzinfo = ZoneInfo('US/Eastern')
                print(f"{entry_date}: {ticker}: Signal {entry.signal} was over MACD {entry.value}: histogram {entry.histogram}")
        _macd.append(entry)
    return _macd

def load_sma(ticker, client,module_config, **kwargs):
    sma = client.get_sma(ticker, **kwargs)
    _sma = []
    for entry in sma.values:
        if module_config['logging']:
            entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
            # entry_date.tzinfo = ZoneInfo('US/Eastern')
            print(f"{entry_date}: {ticker}: SMA {entry.value}")
        _sma.append(entry)


    return sma
def load_rsi(ticker, client,module_config, **kwargs):
    rsi = client.get_rsi(ticker, timespan='hour')
    _rsi = []
    for entry in rsi.values:
        if module_config['logging']:
            entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
            # entry_date.tzinfo = ZoneInfo('US/Eastern')
            print(f"{entry_date}: {ticker}: RSI {entry.value}")
        _rsi.append(entry)
    return _rsi
def load_obv(ticker, client,module_config, **kwargs):
    pass
# def load_adx(ticker, client, **kwargs):
    # load_dmi(ticker,client,**kwargs)

def load_dmi_adx(ticker, client,module_config, **kwargs):
    '''
    Returns a dict formatted like {'dmi+':<series_data>, 'dmi-':<series_data>, 'adx':<series_data>}
    where keys in the series are timestamps as loaded in load_ticker_history
    :param ticker:
    :param client:
    :param kwargs:
    :return:
    '''
    history_entries = load_ticker_history_csv(ticker,  client, 1, "hour", "2023-07-06", "2023-07-06", 500)
    print(f"{datetime.datetime.fromtimestamp(history_entries[1][0] / 1e3, tz=ZoneInfo('US/Eastern'))} {history_entries[1][0]}")
    print(f"{datetime.datetime.fromtimestamp(history_entries[1][-1] / 1e3, tz=ZoneInfo('US/Eastern'))} {history_entries[1][0]}")
    df= wrap(load_ticker_history_pd_frame(ticker, client, 1, "hour", "2023-07-06", "2023-07-06", 500))
    dmi= {"dmi+":df['pdi'],"dmi-":df['ndi'], "adx":df['adx']}
    for i in range(1, len(history_entries)):
        print(f"{datetime.datetime.fromtimestamp(history_entries[i][0] / 1e3, tz=ZoneInfo('US/Eastern'))} DMI+: {dmi['dmi+'][history_entries[i][0]]} DMI-:{dmi['dmi-'][history_entries[i][0]]} ADX: {dmi['adx'][history_entries[i][0]]}")
    # # raw_data =
    return dmi


def did_macd_alert(data, ticker,module_config):
    print(f"checking macd for {ticker}")
    #ok so the idea here is to look at the data for n vs  n-1 where n is the most recent macd reading
    if (data[0].value > data[0].signal and data[1].value < data[1].signal)  or (data[0].value < data[0].signal and data[1].value > data[1].signal):

        entry_date = datetime.datetime.fromtimestamp(data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
        print(f"{entry_date}:{ticker}: MAC/Signal Crossover ")
        return True
    else:
        return False
    pass
def did_dmi_alert(data, ticker,module_config):
    pass

def did_rsi_alert(data, ticker,module_config):
    if data[0].value > 80 or data[0].value < 20:
        if module_config['logging']:
            entry_date = datetime.datetime.fromtimestamp(data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
            print(f"{entry_date}:{ticker}: RSI Alerted at {data[0].value} ")
        return True
    else:
        return  False
def did_adx_alert(data):
    pass
    '''
    Pass in the data from the client and do calculations
    :param data:
    :return:
    '''
    pass
def determine_macd_direction(data):
    pass
def determine_adx_direction(data):
    pass

def determine_dmi_direction(data):
    pass
