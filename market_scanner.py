# This is a sample Python script.
import os
import traceback
import multiprocessing
# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
# from polygon import RESTClient,
import polygon, datetime
import time
from zoneinfo import ZoneInfo
from indicators import load_macd, load_sma, load_dmi_adx, load_rsi, did_macd_alert, did_rsi_alert
from history import load_ticker_history_raw, load_ticker_history_pd_frame
from functions import  load_module_config, read_csv, write_csv,combine_csvs
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
def process_tickers(tickers):
    client = polygon.RESTClient(api_key=module_config['api_key'])
    # ticker = "GE"
    # data_lines = read_csv("data/nyse.csv")
    # if module_config['logging']:
    # print(f"Loaded {len(data_lines) - 1} tickers on NYSE")
    ticker_results = {}
    for i in range(0, len(tickers)):
        # for i in range(1, len(module_config['tickers'])):
        # for ticker in module_config['tickers']:
        ticker = tickers[i]
        ticker_results[ticker] ={}
        #     ticker = module_config['tickers'][i]
        if '$' in ticker:
            continue
        try:
            print(f"{os.getpid()}:{datetime.datetime.now()} Checking ticker ({i}/{len(tickers) - 1}): {ticker}")
            macd_data = load_macd(ticker, client, module_config, timespan="hour", )
            ticker_results[ticker]['macd']= did_macd_alert(macd_data, ticker, module_config)
                # print("alert worked")
            ticker_results[ticker]['rsi']= did_rsi_alert(load_rsi(ticker, client, module_config), ticker, module_config)
                # print("RSI Alerted")
            # sma_data = load_sma(ticker, client, module_config, timespan="hour", )
            # # ticker_history = load_ticker_history(ticker, client,module_config,multiplier=1, timespan="hour", from_="2023-07-06", to="2023-07-06",limit=50)
            #
            # aggs = []
            # dmi = load_dmi_adx(ticker,client)
            # rsi = load_rsi(ticker, client)
        except:
            traceback.print_exc()
            print(f"Cannot process ticker: {ticker}")
    results = [['symbol','macd_flag', 'rsi_flag']]
    for k, v in ticker_results.items():
        try:
            results.append([k, v['macd'],v['rsi']])
        except:
            print(f"Cannot process results for ticker {ticker}")
            traceback.print_exc()
    write_csv(f"{os.getpid()}.csv", results)
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start_time = time.time()
    n = module_config['process_load_size']
    # tickers = read_csv("data/nyse.csv")
    # tickers = module_config['tickers']
    tickers = read_csv("data/nyse.csv")
    del tickers[0]
    if module_config['test_mode']:
        tickers = tickers[:100]
    _tickers = [tickers[i][0] for i in range(0,len(tickers))]
    # _dispensarys = [x for x in dispensaries.keys()]
    task_loads = [_tickers[i:i + n] for i in range(0, len(_tickers), n)]
    # for k,v in dispensaries.items():
    processes = {}
    print(f"Processing {len(tickers)} in {len(task_loads)} load(s)")
    for i in range(0, len(task_loads)):
        print(f"Blowing {i + 1}/{len(task_loads)} Loads")
        load = task_loads[i]
        p = multiprocessing.Process(target=process_tickers, args=(load, ))
        p.start()

        processes[str(p.pid)] = p
    while any(processes[p].is_alive() for p in processes.keys()):
        # print(f"Waiting for {len([x for x in processes if x.is_alive()])} processes to complete. Going to sleep for 10 seconds")
        process_str = ','.join([str(v.pid) for v in processes.values() if v.is_alive()])
        time_str = f"{int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds"
        print(
            f"Waiting on {len(processes.keys())} processes to finish in load {i + 1}/{len(task_loads)}\nElapsed Time: {time_str}")
        time.sleep(10)

    print(f"All loads have been blown, generating your report")

    write_csv("mpb.csv", combine_csvs([f"{x.pid}.csv" for x in processes.values()]))
    # ticker_history = load_ticker_history_raw(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)
    # ticke = load_ticker_history_pd_frame(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)

    print(f"\nCompleted NYSE Market Scan in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")