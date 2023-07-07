# This is a sample Python script.

# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
# from polygon import RESTClient,
import polygon, datetime
import time
from zoneinfo import ZoneInfo
from indicators import load_macd, load_sma, load_dmi_adx, load_rsi, did_macd_alert, did_rsi_alert
from history import load_ticker_history_raw, load_ticker_history_pd_frame
from functions import  load_module_config, read_csv
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    client = polygon.RESTClient(api_key=module_config['api_key'])
    # ticker = "GE"
    data_lines = read_csv("data/nyse.csv")
    for i in range(1, len(data_lines)):
        ticker = data_lines[i][0]
        if '$' in ticker:
            continue
        try:
            print(f"Checking ticker: {ticker}")
            macd_data =load_macd(ticker, client,module_config,timespan="hour", )
            if did_macd_alert(macd_data, ticker=ticker):
                print("alert worked")
            if did_rsi_alert(load_rsi(ticker, client,module_config,), ticker=ticker):
                print("RSI Alerted")
            # sma_data =load_sma(ticker, client,module_config,timespan="hour", )
            # # ticker_history = load_ticker_history(ticker, client,module_config,multiplier=1, timespan="hour", from_="2023-07-06", to="2023-07-06",limit=50)
            #
            # aggs = []
            # dmi = load_dmi_adx(ticker,client)
            # rsi = load_rsi(ticker, client)
        except:
            print(f"Cannot process ticker: {ticker}")
    # ticker_history = load_ticker_history_raw(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)
    # ticke = load_ticker_history_pd_frame(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)

