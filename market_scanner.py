# This is a sample Python script.
import os, operator
import traceback
import multiprocessing
# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
# from polygon import RESTClient,
import polygon, datetime
import time
from zoneinfo import ZoneInfo
from indicators import load_macd, load_sma, load_dmi_adx, load_rsi, did_macd_alert, did_rsi_alert, did_sma_alert, did_dmi_alert, did_adx_alert
from history import load_ticker_history_raw, load_ticker_history_pd_frame, load_ticker_history_csv
from functions import  load_module_config, read_csv, write_csv,combine_csvs
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
today =datetime.datetime.now().strftime("%Y-%m-%d")
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
        #     ticker = module_config['tickers'][i]

        try:
            ticker = tickers[i]
            ticker_results[ticker] = {}

            if '$' in ticker:
                continue
            print(f"{os.getpid()}:{datetime.datetime.now()} Checking ticker ({i}/{len(tickers) - 1}): {ticker}")
            ticker_history = load_ticker_history_raw(ticker, client, 1, "hour", today, today, 500)
            sma = load_sma(ticker, client, module_config, ticker_history, timespan="hour")
            ticker_results[ticker]['sma'] = did_sma_alert(sma, ticker_history, "GE", module_config)

            macd_data = load_macd(ticker, client, module_config, timespan="hour", )
            ticker_results[ticker]['macd']= did_macd_alert(macd_data, ticker, module_config)
                # print("alert worked")
            ticker_results[ticker]['rsi']= did_rsi_alert(load_rsi(ticker, client, module_config), ticker, module_config)
            ticker_results[ticker]['dmi'] = did_dmi_alert(load_dmi_adx(ticker, client, ticker_history, module_config), ticker_history, "GE", module_config)
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
    # results = [['symbol','macd_flag', 'rsi_flag', 'sma_flag', 'pick_level', 'conditions_matched']]
    results = []
    for k, v in ticker_results.items():
        try:
            cond_dict = {'macd':v['macd'],'rsi':v['rsi'], 'sma': v['sma'],'dmi': v['dmi']}
            results.append([k, cond_dict['macd'], cond_dict['rsi'],cond_dict['sma'], cond_dict['dmi']])
            matched_conditions = []
            for kk, vv in cond_dict.items():
                if vv:
                    matched_conditions.append(kk)
            results[-1].append(len(matched_conditions))
            results[-1].append(','.join(matched_conditions))
        except:
            print(f"Cannot process results for ticker {ticker}")
            traceback.print_exc()
    # new_results = []
    # results.sort(key=lambda x:int(x[-2]))
    # sorted(results, key=lambda x: x[-2])
    # results.reverse()
    results.insert(0,['symbol','macd_flag', 'rsi_flag', 'sma_flag','dmi_flag', 'pick_level', 'conditions_matched'] )
    # new_results = reversed(list(sorted(results, key=lambda x: x[-2])))
    # new
    write_csv(f"{os.getpid()}.csv", results)
def find_tickers():
    n = module_config['process_load_size']
    # tickers = read_csv("data/nyse.csv")
    # tickers = module_config['tickers']
    tickers = read_csv("data/nyse.csv")
    del tickers[0]
    if module_config['test_mode']:
        tickers = tickers[:module_config['test_population_size']]
    _tickers = [tickers[i][0] for i in range(0, len(tickers))]
    # _dispensarys = [x for x in dispensaries.keys()]
    task_loads = [_tickers[i:i + n] for i in range(0, len(_tickers), n)]
    # for k,v in dispensaries.items():
    processes = {}
    print(f"Processing {len(tickers)} in {len(task_loads)} load(s)")
    for i in range(0, len(task_loads)):
        print(f"Blowing {i + 1}/{len(task_loads)} Loads")
        load = task_loads[i]
        p = multiprocessing.Process(target=process_tickers, args=(load,))
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
    combined = combine_csvs([f"{x.pid}.csv" for x in processes.values()])
    header = combined[0]
    del combined[0]
    # sorted(combined, key=lambda x: int(x[-2]))
    combined.sort(key=operator.itemgetter(-2))
    combined.reverse()
    # results.reverse()
    combined.insert(0, header)
    write_csv("mpb.csv", combined)
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start_time = time.time()
    # client = polygon.RESTClient(api_key=module_config['api_key'])
    # history_entries = load_ticker_history_csv("GE", client, 1, "hour", today, today, 500)
    # history_entries = load_ticker_history_raw("GE",  client, 1, "hour", today, today, 500)
    # did_dmi_alert(load_dmi_adx("GE", client, history_entries, module_config), history_entries, "GE", module_config)
    find_tickers()
    # ticker_history = load_ticker_history_raw(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)
    # ticke = load_ticker_history_pd_frame(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)

    print(f"\nCompleted NYSE Market Scan in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")