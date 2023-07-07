# This is a sample Python script.

# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
# from polygon import RESTClient,
import polygon, datetime
import time
from zoneinfo import ZoneInfo
from indicators import load_macd, load_sma, load_dmi
from history import load_ticker_history_raw, load_ticker_history_pd_frame
from functions import  load_module_config
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    client = polygon.RESTClient(api_key=module_config['api_key'])
    ticker = "GE"

    macd_data =load_macd(ticker, client,timespan="hour", )
    sma_data =load_sma(ticker, client,timespan="hour", )
    # ticker_history = load_ticker_history(ticker, client,multiplier=1, timespan="hour", from_="2023-07-06", to="2023-07-06",limit=50)

    aggs = []
    dmi = load_dmi(ticker,client)
    # ticker_history = load_ticker_history_raw(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)
    # ticke = load_ticker_history_pd_frame(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)

    pass
    # aggs = []
    # for a in client.list_aggs(ticker=ticker, multiplier=1, timespan="hour", from_="2023-07-06", to="2023-07-06",
    #                           limit=50000):
    #     aggs.append(a)
    #
    # print(aggs)
    # List Aggregates (Bars)
        # aggs = []

        # for a in client.list_aggs(ticker=ticker, multiplier=1, timespan="hour", from_="2023-07-06", to="2023-07-06",
        #                           limit=50):
        #     pass
            # aggs.append(a)
        #
        # print(aggs)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
