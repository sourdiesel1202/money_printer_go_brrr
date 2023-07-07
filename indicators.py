from enums import OrderType
import datetime
from zoneinfo import ZoneInfo
from history import load_ticker_history_pd_frame, load_ticker_history_csv
from stockstats import wrap
today =datetime.datetime.now().strftime("%Y-%m-%d")
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

def load_sma(ticker, client,module_config, ticker_history, **kwargs):
    sma = client.get_sma(ticker, **kwargs)
    _sma = []
    for entry in sma.values:
        if module_config['logging']:
            entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
            # entry_date.tzinfo = ZoneInfo('US/Eastern')
            print(f"{entry_date}: {ticker}: SMA {entry.value}")
        _sma.append(entry)


    return _sma
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

def load_dmi_adx(ticker, client, ticker_history, module_config, **kwargs):
    '''
    Returns a dict formatted like {'dmi+':<series_data>, 'dmi-':<series_data>, 'adx':<series_data>}
    where keys in the series are timestamps as loaded in load_ticker_history
    :param ticker:
    :param client:
    :param kwargs:
    :return:
    '''

    print(f"{datetime.datetime.fromtimestamp(ticker_history[1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}")
    # print(f"{datetime.datetime.fromtimestamp(ticker_history[1][-1] / 1e3, tz=ZoneInfo('US/Eastern'))} {ticker_history[1][0]}")
    df= wrap(load_ticker_history_pd_frame(ticker, ticker_history))
    dmi= {"dmi+":df['pdi'],"dmi-":df['ndi'], "adx":df['adx']}
    for i in reversed(range(1, len(ticker_history))):
        if module_config['logging']:
            pass
            print(f"{datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))} DMI+: {dmi['dmi+'][ticker_history[i].timestamp]} DMI-:{dmi['dmi-'][ticker_history[i].timestamp]} ADX: {dmi['adx'][ticker_history[i].timestamp]}")
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
def did_sma_alert(sma_data,ticker_data, ticker,module_config):
    # ok so in the case of
    entry_date = datetime.datetime.fromtimestamp(sma_data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
    entry_date_ticker = datetime.datetime.fromtimestamp(ticker_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
    # print(f"{entry_date}:{ticker}: SMA Alert Check ")
    # print(f"{entry_date_ticker}:{ticker}: SMA Alert Check ")
    if ((ticker_data[-1].close > sma_data[0].value and ticker_data[-1].open > sma_data[0].value and ticker_data[-1].close > ticker_data[-1].open) and ticker_data[-2].open  < sma_data[1].value ) or \
       ((ticker_data[-1].close < sma_data[0].value and ticker_data[-1].open < sma_data[0].value and ticker_data[-1].close < ticker_data[-1].open)  and ticker_data[-2].open  > sma_data[1].value ):
        if module_config['logging']:
            print(f"{entry_date_ticker}:{ticker}: SMA Crossover Alert Fired on {ticker}")
        return True
    else:
        return False


def did_adx_alert(dmi_data,ticker_data,ticker,module_config):
    '''
    Pass in the data from the client and do calculations
    :param data:
    :return:
    '''
    if (dmi_data['adx'][ticker_data[-1].timestamp] > dmi_data['adx'][ticker_data[-2].timestamp] and dmi_data['adx'][ticker_data[-1].timestamp] > module_config['adx_threshold']):
        if module_config['logging']:
            print(f"{datetime.datetime.fromtimestamp(ticker_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}: ADX Alert Triggered  ADX Value: {dmi_data['adx'][ticker_data[-1].timestamp]} adx-1 Value: {dmi_data['adx'][ticker_data[-2].timestamp]} ")
        return True
    else:
        return False


def did_dmi_alert(dmi_data,ticker_data,ticker,module_config):

    # ok so check for dmi+ crossing over dmi- AND dmi+ over adx OR dmi- crossing over dmi+ AND dmi- over adx
    if (dmi_data['dmi+'][ticker_data[-1].timestamp] > dmi_data['dmi-'][ticker_data[-1].timestamp] and dmi_data['dmi+'][ticker_data[-2].timestamp] < dmi_data['dmi-'][ticker_data[-2].timestamp] and dmi_data['dmi+'][ticker_data[-1].timestamp] >  dmi_data['adx'][ticker_data[-1].timestamp]) or (dmi_data['dmi+'][ticker_data[-1].timestamp] < dmi_data['dmi-'][ticker_data[-1].timestamp] and dmi_data['dmi+'][ticker_data[-2].timestamp] > dmi_data['dmi-'][ticker_data[-2].timestamp] and dmi_data['dmi-'][ticker_data[-1].timestamp] >  dmi_data['adx'][ticker_data[-1].timestamp]):
        if module_config['logging']:
            print(f"{datetime.datetime.fromtimestamp(ticker_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:{ticker}: DMI Alert Triggered (DMI+: {dmi_data['dmi+'][ticker_data[-1].timestamp]} DMI-:{dmi_data['dmi-'][ticker_data[-1].timestamp]} ADX: {dmi_data['adx'][ticker_data[-1].timestamp]})")
        return True
    else:
        return False



def did_rsi_alert(data, ticker,module_config):
    if data[0].value > 80 or data[0].value < 20:
        if module_config['logging']:
            entry_date = datetime.datetime.fromtimestamp(data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
            print(f"{entry_date}:{ticker}: RSI Alerted at {data[0].value} ")
        return True
    else:
        return  False

def determine_macd_direction(data):
    pass
def determine_adx_direction(data):
    pass

def determine_dmi_direction(data):
    pass
