import datetime
import json

from functions import timestamp_to_datetime
from enums import PositionType
from indicators import load_sma,load_macd, load_dmi_adx, load_rsi
# from indicators import did_sma_alert, determine_sma_alert_type

def validate_tickers(position_type, tickers, module_config, client):
    pass


def validate_ticker(position_type, ticker, ticker_history, module_config):
    # if module_config['logging']:
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${ticker}: Validating taking a {position_type} position in ${ticker}")
    #ok so we need to validate the position type against the indicators to ensure everything is valid to enter that type of position
    results ={
        "sma":validate_sma(position_type, ticker, ticker_history, load_sma(ticker , ticker_history, module_config), module_config),
        "macd":validate_macd(position_type, ticker, ticker_history, load_macd(ticker , ticker_history, module_config), module_config),
        "dmi":validate_dmi(position_type, ticker, ticker_history, load_dmi_adx(ticker , ticker_history, module_config), module_config),
        "adx":validate_adx(position_type, ticker, ticker_history, load_dmi_adx(ticker , ticker_history, module_config), module_config),
        "rsi":validate_rsi(position_type, ticker, ticker_history, load_rsi(ticker , ticker_history, module_config), module_config)

    }
    # if module_config['logging']:
    if module_config['logging']:
        print(json.dumps({k:str(v) for k,v in results.items()}))
    return results
def validate_rsi(position_type, ticker, ticker_history, indicator_data, module_config):
    if module_config['logging']:
        print(f"{datetime.datetime.now()}:{ticker}: {timestamp_to_datetime(ticker_history[-1].timestamp).strftime('%Y-%m-%d %H:%M:%S')}: Close: {ticker_history[-1].close} RSI: {indicator_data[ticker_history[-1].timestamp]} ")
    if position_type == PositionType.LONG:
        return indicator_data[ticker_history[-1].timestamp] < module_config['rsi_overbought_threshold']-20
    else:
        return indicator_data[ticker_history[-1].timestamp] > module_config['rsi_oversold_threshold']+20
def validate_adx(position_type, ticker, ticker_history, indicator_data, module_config):
    if module_config['logging']:
        print(f"{datetime.datetime.now()}:{ticker}: {timestamp_to_datetime(ticker_history[-1].timestamp).strftime('%Y-%m-%d %H:%M:%S')}: Close: {ticker_history[-1].close} ADX[current]: {indicator_data['adx'][ticker_history[-1].timestamp]} ADX[previous]-: {indicator_data['adx'][ticker_history[-2].timestamp]} ")
    return indicator_data['adx'][ticker_history[-1].timestamp] > module_config['adx_threshold'] and indicator_data['adx'][ticker_history[-1].timestamp] > indicator_data['adx'][ticker_history[-2].timestamp]

def validate_dmi(position_type, ticker, ticker_history, indicator_data, module_config):
    if module_config['logging']:
        print(f"{datetime.datetime.now()}:{ticker}: {timestamp_to_datetime(ticker_history[-1].timestamp).strftime('%Y-%m-%d %H:%M:%S')}: Close: {ticker_history[-1].close} DMI+: {indicator_data['dmi+'][ticker_history[-1].timestamp]} DMI-: {indicator_data['dmi-'][ticker_history[-1].timestamp]} ADX: {indicator_data['adx'][ticker_history[-1].timestamp]}")
    if position_type == PositionType.LONG:
        return indicator_data['dmi+'][ticker_history[-1].timestamp] > indicator_data['dmi-'][ticker_history[-1].timestamp] and indicator_data['dmi+'][ticker_history[-1].timestamp] > module_config['adx_threshold'] and indicator_data['adx'][ticker_history[-1].timestamp] > module_config['adx_threshold'] and indicator_data['adx'][ticker_history[-1].timestamp] > indicator_data['adx'][ticker_history[-2].timestamp]
    else:
        return indicator_data['dmi+'][ticker_history[-1].timestamp] < indicator_data['dmi-'][ticker_history[-1].timestamp] and indicator_data['dmi-'][ticker_history[-1].timestamp] > module_config['adx_threshold'] and indicator_data['adx'][ticker_history[-1].timestamp] > module_config['adx_threshold'] and indicator_data['adx'][ticker_history[-1].timestamp] > indicator_data['adx'][ticker_history[-2].timestamp]
def validate_macd(position_type, ticker, ticker_history, indicator_data, module_config):
    if module_config['logging']:
        print(f"{datetime.datetime.now()}:{ticker}: {timestamp_to_datetime(ticker_history[-1].timestamp).strftime('%Y-%m-%d %H:%M:%S')}: Close: {ticker_history[-1].close} MACD: {indicator_data['macd'][ticker_history[-1].timestamp]} Signal: {indicator_data['signal'][ticker_history[-1].timestamp]}")
    if position_type == PositionType.LONG:
        return indicator_data['macd'][ticker_history[-1].timestamp] > indicator_data['signal'][ticker_history[-1].timestamp]
    else:
        return indicator_data['macd'][ticker_history[-1].timestamp] < indicator_data['signal'][ticker_history[-1].timestamp]
def validate_sma(position_type, ticker, ticker_history, indicator_data, module_config):
    if module_config['logging']:
        print(f"{datetime.datetime.now()}:{ticker}: {timestamp_to_datetime(ticker_history[-1].timestamp).strftime('%Y-%m-%d %H:%M:%S')}: Close: {ticker_history[-1].close} SMA: {indicator_data[ticker_history[-1].timestamp]}")
    if position_type == PositionType.LONG:
        return (ticker_history[-1].close > indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].low > indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].close > ticker_history[-1].open)

    else:
        return (ticker_history[-1].close < indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].high < indicator_data[ticker_history[-1].timestamp] and ticker_history[-1].close < ticker_history[-1].open)

def validate_ticker_history_integrity(ticker, ticker_history):
    invalid  = 0
    print(f"Validating {len(ticker_history)} entries")
    for i in range(0, len(ticker_history)-1):
        #case for next day
        current_bar_ts = timestamp_to_datetime(ticker_history[i].timestamp)
        next_bar_ts = timestamp_to_datetime(ticker_history[i+1].timestamp)
        if current_bar_ts.hour == 16 or current_bar_ts.hour == 15 and next_bar_ts.hour != 16:
            #case for close
            if next_bar_ts.hour != 9:
                print(f"${ticker} has gap in timeseries data: Current: {current_bar_ts.strftime('%Y-%m-%d %H:%S:%M')} Next: {next_bar_ts.strftime('%Y-%m-%d %H:%S:%M')} ")
                invalid = invalid +1
        else:
            if next_bar_ts.hour != current_bar_ts.hour+1:
                print(f"${ticker} has gap in timeseries data: Current: {current_bar_ts.strftime('%Y-%m-%d %H:%S:%M')} Next: {next_bar_ts.strftime('%Y-%m-%d %H:%S:%M')} ")
                invalid = invalid + 1


    if invalid > 0:
        print(f"${ticker} has corrupt history data")
    else:
        print(f"${ticker}'s history data is valid")
    #     pass

# def validate_line_similarity(ticker)