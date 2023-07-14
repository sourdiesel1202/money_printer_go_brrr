# This is a sample Python script.
# import operator import itemgetter
from iteration_utilities import chained
from functools import partial
import os, operator
import traceback
import multiprocessing
from notification import send_email, generate_mpd_html_table
# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
# from polygon import RESTClient,
import polygon, datetime
import time
from zoneinfo import ZoneInfo
from indicators import load_macd, load_sma, load_dmi_adx, load_rsi, did_macd_alert, did_rsi_alert, did_sma_alert, did_dmi_alert, did_adx_alert,determine_sma_alert_type
from indicators import determine_rsi_alert_type, determine_macd_alert_type,determine_adx_alert_type,determine_dmi_alert_type
from indicators import  load_death_cross, load_golden_cross, determine_death_cross_alert_type,determine_golden_cross_alert_type, did_golden_cross_alert, did_death_cross_alert
from history import load_ticker_history_raw, load_ticker_history_pd_frame, load_ticker_history_csv
from functions import  load_module_config, read_csv, write_csv,combine_csvs, get_today
from enums import  PositionType
from validation import validate_ticker
# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results,analyze_backtest_results, analyzed_backtest_keys
# today =datetime.datetime.now().strftime("%Y-%m-%d")
today =get_today(module_config)
required_indicators = ["macd", 'rsi', 'sma', 'dmi', 'adx']

def build_ticker_results(ticker, ticker_results,ticker_history, client):

    sma = load_sma(ticker, ticker_history, module_config)
    macd_data = load_macd(ticker, ticker_history, module_config)
    dmi_adx_data = load_dmi_adx(ticker, ticker_history, module_config)
    rsi_data = load_rsi(ticker, ticker_history, module_config)
    golden_cross_data = load_golden_cross(ticker, ticker_history, module_config)
    death_cross_data = load_death_cross(ticker, ticker_history, module_config)

    # def did_macd_alert(indicator_data, ticker, ticker_history, module_config):
    ticker_results[ticker]['long_validation'] = ','.join([k for k, v in validate_ticker(PositionType.LONG, ticker, ticker_history, module_config).items() if v])
    ticker_results[ticker]['short_validation'] = ','.join([k for k, v in validate_ticker(PositionType.SHORT, ticker, ticker_history, module_config).items() if v])
    ticker_results[ticker]['sma'] = did_sma_alert(sma, ticker, ticker_history, module_config)
    ticker_results[ticker]['macd'] = did_macd_alert(macd_data, ticker, ticker_history, module_config)
    ticker_results[ticker]['rsi'] = did_rsi_alert(rsi_data, ticker, ticker_history, module_config)
    ticker_results[ticker]['dmi'] = did_dmi_alert(dmi_adx_data, ticker, ticker_history, module_config)
    ticker_results[ticker]['adx'] = did_adx_alert(dmi_adx_data, ticker, ticker_history, module_config)
    ticker_results[ticker]['golden_cross'] = did_golden_cross_alert(golden_cross_data, ticker, ticker_history,
                                                                    module_config)
    ticker_results[ticker]['death_cross'] = did_death_cross_alert(death_cross_data, ticker, ticker_history,
                                                                  module_config)
    if ticker_results[ticker]['macd']:
        ticker_results[ticker]['directions'].append(
            determine_macd_alert_type(macd_data, ticker, ticker_history, module_config))
    if ticker_results[ticker]['rsi']:
        ticker_results[ticker]['directions'].append(
            determine_rsi_alert_type(rsi_data, ticker, ticker_history, module_config))
    if ticker_results[ticker]['dmi']:
        ticker_results[ticker]['directions'].append(
            determine_dmi_alert_type(dmi_adx_data, ticker, ticker_history, module_config))
    if ticker_results[ticker]['adx']:
        ticker_results[ticker]['directions'].append(
            determine_adx_alert_type(dmi_adx_data, ticker_history, ticker, module_config))
    if ticker_results[ticker]['sma']:
        ticker_results[ticker]['directions'].append(
            determine_sma_alert_type(sma, ticker, ticker_history, module_config))
    if ticker_results[ticker]['golden_cross']:
        ticker_results[ticker]['directions'].append(
            determine_golden_cross_alert_type(golden_cross_data, ticker, ticker_history, module_config))
    if ticker_results[ticker]['death_cross']:
        ticker_results[ticker]['directions'].append(
            determine_death_cross_alert_type(death_cross_data, ticker, ticker_history, module_config))

def process_tickers(tickers):


    client = polygon.RESTClient(api_key=module_config['api_key'])
    # _report_headers = ['timestamp','symbol','price','volume', 'macd_flag', 'rsi_flag', 'sma_flag', 'dmi_flag', 'adx_flag','golden_cross_flag','death_cross_flag', 'pick_level', 'conditions_matched','reasons', 'backtested']
    _report_headers = ['timestamp','symbol','price','volume','long_validation', 'short_validation', 'pick_level', 'conditions_matched','alerts triggered', 'backtested']
    for k in analyzed_backtest_keys:
        _report_headers.append(k)
    # ticker = "GE"
    # data_lines = read_csv(f"data/nyse.csv")
    # if module_config['logging']:
    # print(f"Loaded {len(data_lines) - 1} tickers on NYSE")
    ticker_results = {}
    latest_entry = ""

    for i in range(0, len(tickers)):

        # for i in range(1, len(module_config['tickers'])):
        # for ticker in module_config['tickers']:
        #     ticker = module_config['tickers'][i]
        ticker = tickers[i]
        if '$' in ticker or '.' in ticker:
            continue
        ticker_results[ticker] = {'directions': []}
        try:

            if module_config['logging']:
                print(f"{os.getpid()}:{datetime.datetime.now()} Checking ticker ({i}/{len(tickers) - 1}): {ticker}")
            ticker_history = load_ticker_history_raw(ticker, client, 1, module_config['timespan'],get_today(module_config, minus_days=365), today, 10000)
            test_timestamps = [datetime.datetime.fromtimestamp(x.timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime("%Y-%m-%d %H:%M:%S") for x in ticker_history]
            if ticker_history[-1].volume < module_config['volume_limit'] or ticker_history[-1].close < module_config['price_limit']:
                # if module_  config['logging']:
                print(f"${ticker} has Volume: {ticker_history[-1].volume} Price: {ticker_history[-1].close}, skipping")
                continue
            # if latest_entry == "":
            latest_entry = ticker_history[-1].timestamp
            ticker_results[ticker]['volume'] = ticker_history[-1].volume
            ticker_results[ticker]['close'] = ticker_history[-1].close

            build_ticker_results(ticker,ticker_results,ticker_history, client)

        except:
            traceback.print_exc()
            print(f"Cannot process ticker: {ticker}")
            del ticker_results[ticker]
    # results = [['symbol','macd_flag', 'rsi_flag', 'sma_flag', 'pick_level', 'conditions_matched']]
    results = []
    for k, v in ticker_results.items():
        missing_key = False
        for required_key in required_indicators:
            missing_key = required_key not in v

        if missing_key:
            if module_config['logging']:
                print(f"{k} is missing a required config: Found {[x for x in v.keys()]} Required: {required_indicators}")
            continue

        try:
            cond_dict = {'macd':v['macd'],'rsi':v['rsi'], 'sma': v['sma'],'dmi': v['dmi'], 'adx': v['adx'], 'golden_cross': v['golden_cross'], 'death_cross': v['death_cross']}
            matched_conditions = []
            for kk, vv in cond_dict.items():
                if vv:
                    matched_conditions.append(kk)
            if len(matched_conditions) >= module_config['report_alert_min']:


                results.append([datetime.datetime.fromtimestamp(latest_entry / 1e3, tz=ZoneInfo('US/Eastern')).strftime("%Y-%m-%d %H:%M:%S"),k,v['close'], v['volume'],v['long_validation'],v['short_validation']])
                results[-1].append(len(matched_conditions))
                results[-1].append(','.join(matched_conditions))
                results[-1].append(','.join(v['directions']))
                ##stub in backtest entries
                results[-1].append(False)
                for _k in analyzed_backtest_keys:
                    results[-1].append('')
        except:
            print(f"Cannot process results for ticker {k}")
            traceback.print_exc()
    # new_results = []
    # results.sort(key=lambda x:int(x[-2]))
    # sorted(results, key=lambda x: x[-2])
    # results.reverse()
    results.insert(0,_report_headers  )
    # new_results = reversed(list(sorted(results, key=lambda x: x[-2])))
    # new
    write_csv(f"{module_config['output_dir']}{os.getpid()}.csv", results)
def find_tickers():
    start_time = time.time()
    # n = module_config['process_load_size']
    # if module_config['test_mode']:
    #     if not module_config['test_use_input_tickers']:
    #         tickers = read_csv(f"data/nyse.csv")
    if not module_config['test_mode'] or (module_config['test_mode'] and not module_config['test_use_input_tickers']):

        if module_config['test_mode']:
            tickers = read_csv(f"data/nyse.csv")[1:module_config['test_population_size']]
            _tickers = [tickers[i][0] for i in range(0, len(tickers))]
            # tickers
        else:
            if module_config['test_use_input_tickers']:
                _tickers = module_config['tickers']
            else:
                tickers = read_csv(f"data/nyse.csv")[1:]
        # del tickers[0]
                _tickers = [tickers[i][0] for i in range(0, len(tickers))]
    else:
        _tickers = module_config['tickers']
    client = polygon.RESTClient(api_key=module_config['api_key'])

    # del tickers[0]
        # tickers =
        # tickers = tickers[:module_config['test_population_size']]

    _new_tickers = []
    for _ticker in _tickers:
        if '$' not in _ticker:
            _new_tickers.append(_ticker)
    _tickers = _new_tickers
    # _dispensarys = [x for x in dispensaries.keys()]
    if module_config['run_concurrently']:
        task_loads = [_tickers[i:i + int(len(_tickers)/12)+1] for i in range(0, len(_tickers), int(len(_tickers)/12)+1)]
        # for k,v in dispensaries.items():
        processes = {}
        print(f"Processing {len(_tickers)} in {len(task_loads)} load(s)")
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
        combined = combine_csvs([f"{module_config['output_dir']}{x.pid}.csv" for x in processes.values()])
    else:
        process_tickers(_tickers)
        combined = read_csv(f"{module_config['output_dir']}{os.getpid()}.csv")
    header = combined[0]
    del combined[0]
    # sorted(combined, key=lambda x: int(x[-2]))
    itemgetter_int = chained(operator.itemgetter(*[header.index(x) for x in module_config['sort_fields']]), partial(map, float), tuple)
    combined.sort(key=itemgetter_int)
    combined.reverse()
    # results.reverse()
    combined.insert(0, header)
    try:
        write_csv("mpb.csv", combined)
    except:
        print(f"cannot write file")
    results = {"mpb": combined, "mpb_backtested":None}
    if module_config['backtest']:
        print("##############\nRunning Market Scanner Backtest\n##############")

        for i in range(1, len(combined)):
            if int(combined[i][combined[0].index('pick_level')]) == module_config['backtest_alert_count']:
                try:
                    combined[i][combined[0].index('backtested')] = True
                    # if module_config['logging']:
                    print(f"Ticker {combined[i][combined[0].index('symbol')]} alerted {','.join(combined[i][combined[0].index('reasons')].split(','))}, running backtest for {module_config['backtest_days']} days")
                    backtest_ticker_concurrently(combined[i][combined[0].index('reasons')].split(','), combined[i][combined[0].index('symbol')],
                                                 load_backtest_ticker_data(combined[i][combined[0].index('symbol')], client, module_config), module_config)
                    backtest_results = analyze_backtest_results(load_backtest_results(combined[i][combined[0].index('symbol')], module_config))
                    for _backtest_key in analyzed_backtest_keys:
                    # for ii in range(combined[0].index('backtested') + 1, len(combined[0])):
                            # print(f"Report_headers {_report_headers[i]}")
                        combined[i][combined[0].index(_backtest_key)] = backtest_results[_backtest_key]
                except:
                    combined[i][combined[0].index('backtested')] = False
                    traceback.print_exc()
                    print(f"Could not backtest ticker {combined[i][0]}")
        results['mpb_backtested'] = combined
        try:
            write_csv("mpb_backtested.csv", combined)
        except:
            print(f"Cannot write file")
    print(f"API KEY: {module_config['api_key']}")
    return results
    #ok so once we are here, let's go ahead and find the tickers that we need to backtest and run int

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
        ##find data
        if module_config['trading_hours_only']:
            if datetime.datetime.now().hour < 17 and datetime.datetime.now().hour > 8:
                results = find_tickers()
                #do notification send
                send_email("andrew.smiley937@gmail.com","andrew.smiley937@gmail.com", f"MPB Traders (Hourly)  {datetime.datetime.now().strftime('%Y-%m-%d %H:00')}", generate_mpd_html_table(results['mpb']))
            else:
                print(f"Not currently trading hours ({datetime.datetime.now()}), skipping")
        else:
            results = find_tickers()
            # do notification send
            send_email("andrew.smiley937@gmail.com", "andrew.smiley937@gmail.com",f"MPB Traders (Hourly)  {datetime.datetime.now().strftime('%Y-%m-%d %H:00')}",generate_mpd_html_table(results['mpb']))
        # ticker_history = load_ticker_history_raw(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)
        # ticke = load_ticker_history_pd_frame(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)

        print(f"\nCompleted NYSE Market Scan in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")