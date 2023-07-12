from enums import OrderType
import datetime
from zoneinfo import ZoneInfo
from history import load_ticker_history_pd_frame, load_ticker_history_csv
from stockstats import wrap
from enums import *
# today =datetime.datetime.now().strftime("%Y-%m-%d")

def load_macd(ticker,ticker_history, module_config):
    df = wrap(load_ticker_history_pd_frame(ticker, ticker_history))
    return {'macd':df['macd'],'signal':df['macds'], 'histogram': df['macdh']}
# def load_macd(ticker, client,module_config,  **kwargs):
#     macd = client.get_macd(ticker=ticker, **kwargs)
#     _macd = []
#     for entry in macd.values:
#         if module_config['logging']:
#             if entry.value > entry.signal:
#                 entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
#                 # entry_date.tzinfo = ZoneInfo('US/Eastern')
#                 if module_config['logging']:
#                     print(f"{entry_date}: {ticker}: MACD {entry.value} was over signal {entry.signal}: histogram {entry.histogram}")
#             else:
#                 entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
#                 # entry_date.tzinfo = ZoneInfo('US/Eastern')
#                 if module_config['logging']:
#                     print(f"{entry_date}: {ticker}: Signal {entry.signal} was over MACD {entry.value}: histogram {entry.histogram}")
#         _macd.append(entry)
#     return _macd
def load_sma(ticker,ticker_history, module_config, window=0):
    df = wrap(load_ticker_history_pd_frame(ticker, ticker_history))
    if window >0:
        # print(f"Returning {window} SMA")
        return df[f'close_{window}_sma']
    else:
        return df[f'close_{module_config["sma_window"]}_sma']
def load_golden_cross(ticker,ticker_history, module_config):
    return {"sma_long":load_sma(ticker,ticker_history,module_config, window=module_config['gc_long_sma_window']), f"sma_short":load_sma(ticker,ticker_history,module_config, window=module_config['gc_short_sma_window'])}
def load_death_cross(ticker,ticker_history, module_config):
    return {"sma_long":load_sma(ticker,ticker_history,module_config, window=module_config['dc_long_sma_window']), f"sma_short":load_sma(ticker,ticker_history,module_config, window=module_config['dc_short_sma_window'])}

# def load_sma(ticker, client,module_config, ticker_history, **kwargs):
#     sma = client.get_sma(ticker, **kwargs)
#     _sma = []
#     for entry in sma.values:
#         if module_config['logging']:
#             entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
#             # entry_date.tzinfo = ZoneInfo('US/Eastern')
#             print(f"{entry_date}: {ticker}: SMA {entry.value}")
#         _sma.append(entry)
#
#
#
def load_rsi(ticker, ticker_history, module_config):
    df = wrap(load_ticker_history_pd_frame(ticker, ticker_history))
    return df['rsi']

    # return _sma
# def load_rsi(ticker, client,module_config, **kwargs):
#     rsi = client.get_rsi(ticker, timespan='hour')
#     _rsi = []
#     for entry in rsi.values:
#         if module_config['logging']:
#             entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
#             # entry_date.tzinfo = ZoneInfo('US/Eastern')
#             print(f"{entry_date}: {ticker}: RSI {entry.value}")
#         _rsi.append(entry)
#     return _rsi
def load_obv(ticker, client,module_config, **kwargs):
    pass
# def load_adx(ticker, client, **kwargs):
    # load_dmi(ticker,client,**kwargs)

def load_dmi_adx(ticker, ticker_history, module_config, **kwargs):
    '''
    Returns a dict formatted like {'dmi+':<series_data>, 'dmi-':<series_data>, 'adx':<series_data>}
    where keys in the series are timestamps as loaded in load_ticker_history
    :param ticker:
    :param client:
    :param kwargs:
    :return:
    '''

    # print(f"{datetime.datetime.fromtimestamp(ticker_history[1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}")
    # print(f"{datetime.datetime.fromtimestamp(ticker_history[1][-1] / 1e3, tz=ZoneInfo('US/Eastern'))} {ticker_history[1][0]}")
    df= wrap(load_ticker_history_pd_frame(ticker, ticker_history))
    dmi= {"dmi+":df['pdi'],"dmi-":df['ndi'], "adx":df['adx']}
    for i in reversed(range(0, len(ticker_history))):
        if module_config['logging']:
        # if True:

            print(f"{datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:{ticker}: DMI+: {dmi['dmi+'][ticker_history[i].timestamp]} DMI-:{dmi['dmi-'][ticker_history[i].timestamp]} ADX: {dmi['adx'][ticker_history[i].timestamp]}")
    return dmi

def did_macd_alert(indicator_data,ticker,ticker_history, module_config):
    if module_config['logging']:
        print(f"Checking MACD Alert, Comparing Value at {datetime.datetime.fromtimestamp(ticker_history[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:{ticker}: to value at {datetime.datetime.fromtimestamp(ticker_history[-2].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}")
    # print(f"{ticker_history[-1]}:{ticker}: RSI determined to be {AlertType.RSI_OVERSOLD}: RSI: {indicator_data[ticker_history[-1].timestamp]} ")
    # if (data[0].value > data[0].signal and data[1].value < data[1].signal)  or (data[0].value < data[0].signal and data[1].value > data[1].signal):
    if (indicator_data['macd'][ticker_history[-1].timestamp] > indicator_data['signal'][ticker_history[-1].timestamp] and indicator_data['macd'][ticker_history[-2].timestamp] < indicator_data['signal'][ticker_history[-2].timestamp] and (indicator_data['histogram'][ticker_history[-1].timestamp] > indicator_data['histogram'][ticker_history[-2].timestamp] and indicator_data['histogram'][ticker_history[-1].timestamp] > 0) ) or \
            (indicator_data['macd'][ticker_history[-1].timestamp] < indicator_data['signal'][ticker_history[-1].timestamp] and indicator_data['macd'][ticker_history[-2].timestamp] > indicator_data['signal'][ticker_history[-2].timestamp] and (indicator_data['histogram'][ticker_history[-1].timestamp] < indicator_data['histogram'][ticker_history[-2].timestamp] and indicator_data['histogram'][ticker_history[-1].timestamp] < 0)):
        return True
    else:
        return  False

# def did_macd_alert(data, ticker,module_config):
#     if module_config['logging']:
#         print(f"checking macd for {ticker}")
#     #ok so the idea here is to look at the data for n vs  n-1 where n is the most recent macd reading
#     if (data[0].value > data[0].signal and data[1].value < data[1].signal)  or (data[0].value < data[0].signal and data[1].value > data[1].signal):
#
#         if module_config['logging']:
#             entry_date = datetime.datetime.fromtimestamp(data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
#             print(f"{entry_date}:{ticker}: MAC/Signal Crossover ")
#         return True
#     else:
#         return False
#     pass

def did_sma_alert(indicator_data,ticker,ticker_history, module_config):
    if module_config['logging']:
        print(f"Checking SMA Alert, Comparing Value at {datetime.datetime.fromtimestamp(ticker_history[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))} to value at {datetime.datetime.fromtimestamp(ticker_history[-2].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}")
    if ((ticker_history[-1].close > indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].low > indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].close > ticker_history[-1].open) and ticker_history[-2].open < indicator_data[ticker_history[-2].timestamp]) or\
            ((ticker_history[-1].close < indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].high < indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].close < ticker_history[-1].open) and ticker_history[-2].open > indicator_data[ticker_history[-2].timestamp]):
        return True
    else:
        return False

def did_golden_cross_alert(indicator_data,ticker,ticker_history, module_config):
    if module_config['logging']:
        print(f"Checking Golden Cross Alert, Comparing Value at {datetime.datetime.fromtimestamp(ticker_history[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:Long SMA {indicator_data['sma_long'][ticker_history[-1].timestamp]} Short SMA: {indicator_data['sma_short'][ticker_history[-1].timestamp]}: to value at {datetime.datetime.fromtimestamp(ticker_history[-2].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:Long SMA {indicator_data['sma_long'][ticker_history[-2].timestamp]} Short SMA: {indicator_data['sma_short'][ticker_history[-2].timestamp]}:")
    return indicator_data['sma_short'][ticker_history[-1].timestamp] > indicator_data['sma_long'][ticker_history[-1].timestamp] and indicator_data['sma_short'][ticker_history[-2].timestamp] < indicator_data['sma_long'][ticker_history[-2].timestamp]

def did_death_cross_alert(indicator_data, ticker, ticker_history, module_config):
    if module_config['logging']:
        print(
            f"Checking Death Cross Alert, Comparing Value at {datetime.datetime.fromtimestamp(ticker_history[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:Long SMA {indicator_data['sma_long'][ticker_history[-1].timestamp]} Short SMA: {indicator_data['sma_short'][ticker_history[-1].timestamp]}: to value at {datetime.datetime.fromtimestamp(ticker_history[-2].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:Long SMA {indicator_data['sma_long'][ticker_history[-2].timestamp]} Short SMA: {indicator_data['sma_short'][ticker_history[-2].timestamp]}:")
    return indicator_data['sma_short'][ticker_history[-1].timestamp] < indicator_data['sma_long'][ticker_history[-1].timestamp] and indicator_data['sma_short'][ticker_history[-2].timestamp] > indicator_data['sma_long'][ticker_history[-2].timestamp]

    # if ((ticker_history[-1].close > indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].low > indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].close > ticker_history[-1].open) and ticker_history[-2].open < indicator_data[ticker_history[-2].timestamp]) or\
    #         ((ticker_history[-1].close < indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].high < indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].close < ticker_history[-1].open) and ticker_history[-2].open > indicator_data[ticker_history[-2].timestamp]):
    #     return True
    # else:
    #     return False
# def did_sma_alert(sma_data,ticker_data, ticker,module_config):
#     # ok so in the case of
#     entry_date = datetime.datetime.fromtimestamp(sma_data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
#     entry_date_ticker = datetime.datetime.fromtimestamp(ticker_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
#     # print(f"{entry_date}:{ticker}: SMA Alert Check ")
#     # print(f"{entry_date_ticker}:{ticker}: SMA Alert Check ")
#     if ((ticker_data[-1].close > sma_data[0].value and ticker_data[-1].open > sma_data[0].value and ticker_data[-1].close > ticker_data[-1].open) and ticker_data[-2].open  < sma_data[1].value ) or \
#        ((ticker_data[-1].close < sma_data[0].value and ticker_data[-1].open < sma_data[0].value and ticker_data[-1].close < ticker_data[-1].open)  and ticker_data[-2].open  > sma_data[1].value ):
#         if module_config['logging']:
#             print(f"{entry_date_ticker}:{ticker}: SMA Crossover Alert Fired on {ticker}")
#         return True
#     else:
#         return False


def did_adx_alert(dmi_data,ticker,ticker_data,module_config):
    '''
    Pass in the data from the client and do calculations
    :param data:
    :return:
    '''
    if (dmi_data['adx'][ticker_data[-1].timestamp] > dmi_data['adx'][ticker_data[-2].timestamp] and dmi_data['adx'][ticker_data[-1].timestamp] > module_config['adx_threshold']):
        if module_config['logging']:
            print(f"{datetime.datetime.fromtimestamp(ticker_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:{ticker}:: ADX Alert Triggered  ADX Value: {dmi_data['adx'][ticker_data[-1].timestamp]} adx-1 Value: {dmi_data['adx'][ticker_data[-2].timestamp]} ")
        return True
    else:
        return False


def did_dmi_alert(dmi_data,ticker,ticker_data,module_config):

    # ok so check for dmi+ crossing over dmi- AND dmi+ over adx OR dmi- crossing over dmi+ AND dmi- over adx
    if (dmi_data['dmi+'][ticker_data[-1].timestamp] > dmi_data['dmi-'][ticker_data[-1].timestamp] and dmi_data['dmi+'][ticker_data[-2].timestamp] < dmi_data['dmi-'][ticker_data[-2].timestamp] and dmi_data['dmi+'][ticker_data[-1].timestamp] >  dmi_data['adx'][ticker_data[-1].timestamp]) or (dmi_data['dmi+'][ticker_data[-1].timestamp] < dmi_data['dmi-'][ticker_data[-1].timestamp] and dmi_data['dmi+'][ticker_data[-2].timestamp] > dmi_data['dmi-'][ticker_data[-2].timestamp] and dmi_data['dmi-'][ticker_data[-1].timestamp] >  dmi_data['adx'][ticker_data[-1].timestamp]):
        if module_config['logging']:
            print(f"{datetime.datetime.fromtimestamp(ticker_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:{ticker}::{ticker}: DMI Alert Triggered (DMI+: {dmi_data['dmi+'][ticker_data[-1].timestamp]} DMI-:{dmi_data['dmi-'][ticker_data[-1].timestamp]} ADX: {dmi_data['adx'][ticker_data[-1].timestamp]})")
        return True
    else:
        return False



def did_rsi_alert(indicator_data,ticker,ticker_history, module_config):
    if module_config['logging']:
        print(f"${ticker}: Checking RSI Alert, Comparing Value at {datetime.datetime.fromtimestamp(ticker_history[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:{ticker}: to value at {datetime.datetime.fromtimestamp(ticker_history[-2].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:{ticker}:")
    if indicator_data[ticker_history[-1].timestamp] > module_config['rsi_overbought_threshold'] or indicator_data[ticker_history[-1].timestamp] < module_config['rsi_oversold_threshold']:
        return True
    else:
        return False

# def did_rsi_alert(data, ticker,module_config):
#     if data[0].value > module_config['rsi_overbought_threshold'] or data[0].value < module_config['rsi_oversold_threshold']:
#         if module_config['logging']:
#             entry_date = datetime.datetime.fromtimestamp(data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
#             print(f"{entry_date}:{ticker}: RSI Alerted at {data[0].value} ")
#         return True
#     else:
#         return  False


def determine_macd_alert_type(indicator_data,ticker,ticker_history, module_config):
    if (indicator_data['macd'][ticker_history[-1].timestamp] > indicator_data['signal'][ticker_history[-1].timestamp] and indicator_data['macd'][ticker_history[-2].timestamp] < indicator_data['signal'][ticker_history[-2].timestamp] and (indicator_data['histogram'][ticker_history[-1].timestamp] > indicator_data['histogram'][ticker_history[-2].timestamp] and indicator_data['histogram'][ticker_history[-1].timestamp] > 0)) :
        return AlertType.MACD_MACD_CROSS_SIGNAL
    elif (indicator_data['macd'][ticker_history[-1].timestamp] < indicator_data['signal'][ ticker_history[-1].timestamp] and indicator_data['macd'][ticker_history[-2].timestamp] > indicator_data['signal'][ticker_history[-2].timestamp] and (indicator_data['histogram'][ticker_history[-1].timestamp] < indicator_data['histogram'][ticker_history[-2].timestamp] and indicator_data['histogram'][ticker_history[-1].timestamp] < 0)):
        return AlertType.MACD_SIGNAL_CROSS_MACD
    else:
        raise Exception("Unable to determine MACD alert type ")

# def determine_macd_alert_type(data, ticker,module_config):
#     # ok so the idea here is to look at the data for n vs  n-1 where n is the most recent macd reading
#     if (data[0].value > data[0].signal and data[1].value < data[1].signal) :
#
#         if module_config['logging']:
#             entry_date = datetime.datetime.fromtimestamp(data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
#             print(f"{entry_date}:{ticker}: MAC/Signal Crossover ")
#         return AlertType.MACD_MACD_CROSS_SIGNAL
#     elif (data[0].value < data[0].signal and data[1].value > data[1].signal):
#         return AlertType.MACD_SIGNAL_CROSS_MACD
#     else:
#         raise Exception(f"Could not determine MACD direction for: {ticker}")
def determine_rsi_alert_type(indicator_data,ticker,ticker_history, module_config):
    if indicator_data[ticker_history[-1].timestamp] >= module_config['rsi_overbought_threshold']:
        if module_config['logging']:
            entry_date = datetime.datetime.fromtimestamp(ticker_history[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
            print(f"{entry_date}:{ticker}: RSI determined to be {AlertType.RSI_OVERSOLD}: RSI: {indicator_data[ticker_history[-1].timestamp]} ")
        return AlertType.RSI_OVERBOUGHT
    elif indicator_data[ticker_history[-1].timestamp] < module_config['rsi_oversold_threshold']:
        if module_config['logging']:
            entry_date = datetime.datetime.fromtimestamp(ticker_history[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
            print(f"{entry_date}:{ticker}: RSI determined to be {AlertType.RSI_OVERSOLD}: RSI: {indicator_data[ticker_history[-1].timestamp]} ")
        return AlertType.RSI_OVERSOLD
    else:
        raise Exception(f"Could not determine RSI Direction for {ticker}")
# def determine_rsi_direction(data, ticker, module_config):
#     if data[0].value > module_config['rsi_overbought_threshold']:
#         if module_config['logging']:
#             entry_date = datetime.datetime.fromtimestamp(data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
#             print(f"{entry_date}:{ticker}: RSI determined to be {AlertType.RSI_OVERSOLD}: RSI: {data[0].value} ")
#         return AlertType.RSI_OVERBOUGHT
#     elif data[0].value < module_config['rsi_oversold_threshold']:
#         if module_config['logging']:
#             entry_date = datetime.datetime.fromtimestamp(data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
#             print(f"{entry_date}:{ticker}: RSI determined to be {AlertType.RSI_OVERSOLD}: RSI: {data[0].value} ")
#         return AlertType.RSI_OVERSOLD
#     else:
#         raise Exception(f"Could not determine RSI Direction for {ticker}")

def determine_adx_alert_type(data, ticker,ticker_data,  module_config):
    return AlertType.ADX_THRESHOLD_UPWARD

def determine_dmi_alert_type(data, ticker, ticker_data, module_config):
    if (data['dmi+'][ticker_data[-1].timestamp] > data['dmi-'][ticker_data[-1].timestamp] and data['dmi+'][ticker_data[-2].timestamp] < data['dmi-'][ticker_data[-2].timestamp] and data['dmi+'][ticker_data[-1].timestamp] > data['adx'][ticker_data[-1].timestamp]):
        if module_config['logging']:
            print(f"{datetime.datetime.fromtimestamp(ticker_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:{ticker}: DMI Alert Determined Directio: {AlertType.DMIPLUS_CROSSOVER_DMINEG} (DMI+: {data['dmi+'][ticker_data[-1].timestamp]} DMI-:{data['dmi-'][ticker_data[-1].timestamp]} ADX: {data['adx'][ticker_data[-1].timestamp]})")
        return AlertType.DMIPLUS_CROSSOVER_DMINEG
    elif (data['dmi+'][ticker_data[-1].timestamp] < data['dmi-'][ticker_data[-1].timestamp] and data['dmi+'][ticker_data[-2].timestamp] > data['dmi-'][ticker_data[-2].timestamp] and data['dmi-'][ticker_data[-1].timestamp] > data['adx'][ticker_data[-1].timestamp]):
        if module_config['logging']:
            print(f"{datetime.datetime.fromtimestamp(ticker_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:{ticker}: DMI Alert Determined Directio: {AlertType.DMIPLUS_CROSSOVER_DMINEG} (DMI+: {data['dmi+'][ticker_data[-1].timestamp]} DMI-:{data['dmi-'][ticker_data[-1].timestamp]} ADX: {data['adx'][ticker_data[-1].timestamp]})")
        return AlertType.DMINEG_CROSSOVER_DMIPLUS


    else:
        raise Exception(f"Could not determine RSI Direction for {ticker}")


def determine_death_cross_alert_type(indicator_data,ticker,ticker_history, module_config):
    if indicator_data['sma_short'][ticker_history[-1].timestamp] < indicator_data['sma_long'][ticker_history[-1].timestamp] and indicator_data['sma_short'][ticker_history[-2].timestamp] > indicator_data['sma_long'][ticker_history[-2].timestamp]:
        return AlertType.DEATH_CROSS_APPEARED
    else:
        raise Exception(f"Could not determine Golden Cross Alert for {ticker}")
def determine_golden_cross_alert_type(indicator_data,ticker,ticker_history, module_config):
    if did_golden_cross_alert(indicator_data,ticker,ticker_history,module_config):
        return AlertType.GOLDEN_CROSS_APPEARED
    else:
        raise Exception(f"Could not determine Golden Cross Alert for {ticker}")
# def determine_death_cross_alert_type(indicator_data,ticker,ticker_history, module_config):
def determine_sma_alert_type(indicator_data,ticker,ticker_history, module_config):
    if ((ticker_history[-1].close > indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].low >
         indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].close > ticker_history[-1].open) and
        ticker_history[-2].open < indicator_data[ticker_history[-2].timestamp]):
        return AlertType.SMA_CROSSOVER_UPWARD
    elif ((ticker_history[-1].close < indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].high <
      indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].close < ticker_history[-1].open) and
     ticker_history[-2].open > indicator_data[ticker_history[-2].timestamp]):
        return AlertType.SMA_CROSSOVER_DOWNWARD
    else:
        raise Exception(f"Could not determine SMA Direction for {ticker}")
