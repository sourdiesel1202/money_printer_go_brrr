from enums import OrderType
import datetime
from zoneinfo import ZoneInfo
from history import load_ticker_history_pd_frame, load_ticker_history_csv
from stockstats import wrap
def load_macd(ticker, client, **kwargs):
    macd = client.get_macd(ticker=ticker, **kwargs)
    for entry in macd.values:
        if entry.value > entry.signal:
            entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
            # entry_date.tzinfo = ZoneInfo('US/Eastern')
            print(f"{entry_date}: {ticker}: MACD {entry.value} was over signal {entry.signal}: histogram {entry.histogram}")
        else:
            entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
            # entry_date.tzinfo = ZoneInfo('US/Eastern')
            print(f"{entry_date}: {ticker}: Signal {entry.signal} was over MACD {entry.value}: histogram {entry.histogram}")
    return macd

def load_sma(ticker, client, **kwargs):
    sma = client.get_sma(ticker, **kwargs)
    for entry in sma.values:
        entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
        # entry_date.tzinfo = ZoneInfo('US/Eastern')
        print(f"{entry_date}: {ticker}: SMA {entry.value}")

    return sma
def load_obv(ticker, client, **kwargs):
    pass
def load_adx(ticker, client, **kwargs):
    pass
def load_dmi(ticker, client, **kwargs):
    history_entries = load_ticker_history_csv(ticker,  client, 1, "hour", "2023-07-06", "2023-07-06", 500)
    print(f"{datetime.datetime.fromtimestamp(history_entries[1][0] / 1e3, tz=ZoneInfo('US/Eastern'))} {history_entries[1][0]}")
    print(f"{datetime.datetime.fromtimestamp(history_entries[1][-1] / 1e3, tz=ZoneInfo('US/Eastern'))} {history_entries[1][0]}")
    df= wrap(load_ticker_history_pd_frame(ticker, client, 1, "hour", "2023-07-06", "2023-07-06", 500))
    dmi= [df['pdi'].get(history_entries[-1][0]), df['ndi'].get(history_entries[-1][0]), df['adx'].get(history_entries[-1][0])]
    # for i in range(1, len(history_entries)):
    #     print(f"{datetime.datetime.fromtimestamp(history_entries[i][0] / 1e3, tz=ZoneInfo('US/Eastern'))} DMI+: {dmi[0]} DMI-:{dmi[1]} ADX: {dmi[2]}")
    # # raw_data =
    return dmi


def did_macd_alert(data):
    '''
    Pass in the data from the client and do calculations
    :param data:
    :return:
    '''
    pass
def determine_macd_direction(data):
    pass
