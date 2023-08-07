# This is a sample Python script.
# import operator import itemgetter
import urllib.parse

from db_functions import  process_ticker_history, load_mpb_report
from tickers import load_ticker_last_updated
from functions import obtain_db_connection, execute_query, timestamp_to_datetime
from multiprocessing import freeze_support

from indicators import load_ticker_similar_trends
from mpb_html import build_dashboard
from iteration_utilities import chained
from functools import partial
import os, operator
import traceback
import multiprocessing
from enums import AlertType
from polygon.rest import RESTClient
from notification import send_email, generate_mpd_html_table
# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
# from polygon import RESTClient,
import polygon, datetime
import time
from options import analyze_option_data
from zoneinfo import ZoneInfo
from history import load_ticker_history_raw, load_ticker_history_pd_frame, load_ticker_history_csv, \
    clear_ticker_history_cache, load_ticker_history_cached
from functions import load_module_config, read_csv, write_csv, combine_csvs, get_today, process_list_concurrently
from enums import  PositionType
from options import load_tickers_option_data
# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
module_config = load_module_config("market_scanner_db")
from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results,analyze_backtest_results, analyzed_backtest_keys
# today =datetime.datetime.now().strftime("%Y-%m-%d")
today =get_today(module_config)
required_indicators = ["macd", 'rsi', 'sma', 'dmi', "sr_band_breakout", 'golden_cross', 'death_cross']
from plotting import build_indicator_dict, plot_ticker_with_indicators

def process_results(ticker_results):
    #this gets called after all the ticker data is loaded, thus we can use cached data
    _report_headers = ['timestamp','symbol','price','volume','long_validation','suggested_call', 'short_validation','suggested_put', 'pick_level', 'conditions_matched','alerts_triggered','similar_tickers', 'backtested']
    for k in analyzed_backtest_keys:
        _report_headers.append(k)
    results = []
    for k, v in ticker_results.items():
        missing_key = False
        for required_key in required_indicators:
            missing_key = required_key not in v

        if missing_key:
            if module_config['logging']:
                print(
                    f"{k} is missing a required config: Found {[x for x in v.keys()]} Required: {required_indicators}")
            continue

        try:
            cond_dict = {'macd': v['macd'], 'rsi': v['rsi'], 'sma': v['sma'], 'dmi': v['dmi'],
                         'golden_cross': v['golden_cross'], 'death_cross': v['death_cross'], 'sr_band_breakout':v['sr_band_breakout']}
            matched_conditions = []
            for kk, vv in cond_dict.items():
                if vv:
                    matched_conditions.append(kk)
            if len(matched_conditions) >= module_config['report_alert_min']:
                # matched_conditions.sort(key=lambda x:x)
                ticker_link = urllib.parse.quote(f"{module_config['timespan_multiplier']}{module_config['timespan']}{k}.html", safe='')
                results.append([datetime.datetime.fromtimestamp(v['latest'] / 1e3, tz=ZoneInfo('US/Eastern')).strftime(
                    "%Y-%m-%d %H:%M:%S"), f"<a href='{ticker_link}'>{k}</a>", f"${v['close']}", v['volume'], v['long_validation'],'', v['short_validation'], ''])
                results[-1].append(len(matched_conditions))
                results[-1].append(','.join(matched_conditions).upper())
                results[-1].append(','.join(v['directions']).upper())
                #ok so here we can do our test of similar tickers
                if len(matched_conditions) > module_config['report_alert_min']:
                    results[-1].append(','.join(load_ticker_similar_trends(k, module_config)))
                else:
                    results[-1].append('')
                ##stub in backtest entries
                results[-1].append(False)
                for _k in analyzed_backtest_keys:
                    results[-1].append('')
        except:
            print(f"Cannot process results for ticker {k}")
            traceback.print_exc()

    results.insert(0, _report_headers)
    # new_results = reversed(list(sorted(results, key=lambda x: x[-2])))
    # new
    write_csv(f"{module_config['output_dir']}{os.getpid()}.csv", results)

def process_tickers(tickers):
    # client = RESTClient(api_key=module_config['api_key'])
    ticker_results = {}
    # latest_entry = ""
    connection = obtain_db_connection(load_module_config('market_scanner_db'))
    try:
        for i in range(0, len(tickers)):

            ticker = tickers[i]
            if '$' in ticker or '.' in ticker:
                continue
            ticker_results[ticker] = {'directions': []}
            try:

                if module_config['logging']:
                    print(f"{os.getpid()}:{datetime.datetime.now()} Checking ticker ({i}/{len(tickers) - 1}): {ticker}")
                # ticker_history = load_ticker_history_raw(ticker, client, 1, module_config['timespan'],get_today(module_config, minus_days=365), today, 10000, module_config)
                ticker_history = load_ticker_history_cached(ticker, module_config, connection=connection)
                test_timestamps = [datetime.datetime.fromtimestamp(x.timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime("%Y-%m-%d %H:%M:%S") for x in ticker_history]
                if ticker_history[-1].volume < module_config['volume_limit'] or ticker_history[-1].close < module_config['price_limit']:
                    # if module_  config['logging']:
                    print(f"${ticker} has Volume: {ticker_history[-1].volume} Price: {ticker_history[-1].close}, skipping")
                    continue
                # if latest_entry == "":
                latest_entry = ticker_history[-1].timestamp
                ticker_results[ticker]['volume'] = ticker_history[-1].volume
                ticker_results[ticker]['latest'] = ticker_history[-1].timestamp
                ticker_results[ticker]['close'] = ticker_history[-1].close

                process_ticker_history(connection, ticker, ticker_history, module_config)
                # process_ticker_history(ticker,ticker_history, module_config)

            except:
                traceback.print_exc()
                print(f"Cannot process ticker: {ticker}")
                del ticker_results[ticker]
        # results = [['symbol','macd_flag', 'rsi_flag', 'sma_flag', 'pick_level', 'conditions_matched']]
    except:
        traceback.print_exc()
        # traceback.print_exc()
    connection.close()

    # process_results(ticker_results)

def load_ticker_histories(_tickers):
    client = RESTClient(api_key=module_config['api_key'])
    _module_config  =load_module_config(__file__.split("/")[-1].split(".py")[0])
    connection= obtain_db_connection(_module_config)
    try:
        successes = []
        failures = [['symbol']]
        for ticker in _tickers:
            print(f"{os.getpid()}: Loading {_tickers.index(ticker)+1}/{len(_tickers)} ticker datas")
            try:
                # if not module_config['test_mode']:
                _ = load_ticker_history_raw(ticker, client,module_config['timespan_multiplier'], module_config['timespan'],get_today(module_config, minus_days=4), today, limit=50000, module_config=_module_config, connection=connection)
                # else:
                    # _ = load_ticker_history_raw(ticker, client,1, module_config['timespan'],get_today(module_config, minus_days=365), 11, limit=50000, module_config=_module_config)
                successes.append(ticker)
            except:
                # traceback.print_exc()
                failures.append([ticker])
        # write_csv(f"{module_config['output_dir']}mpb_load_failures.csv",failures)
    except:
        traceback.print_exc()
    # return  successes
    connection.close()

def generate_report(ticker_list, module_config):
    # _tickers = load_ticker_histories(_tickers)
    print(f"Loading history data for {len(ticker_list)} tickers")
    if module_config['run_concurrently']:
        process_list_concurrently(ticker_list, load_ticker_histories,int(len(ticker_list)/module_config['num_processes'])+1)
    else:
        load_ticker_histories(ticker_list)
    # _tickers = [x.split(f"{module_config['timespan_multiplier']}{module_config['timespan']}.csv")[0] for x in os.listdir(f"{module_config['output_dir']}cached/") if "O:" not in x]
    if module_config['run_concurrently']:
        task_loads = [ticker_list[i:i + int(len(ticker_list)/module_config['num_processes'])+1] for i in range(0, len(ticker_list), int(len(ticker_list)/module_config['num_processes'])+1)]
        # for k,v in dispensaries.items():
        processes = {}
        print(f"Processing {len(ticker_list)} in {len(task_loads)} load(s)")
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

        print(f"All loads have been blown")
        # combined = combine_csvs([f"{module_config['output_dir']}{x.pid}.csv" for x in processes.values()])
    else:
        process_tickers(ticker_list)
        # combined = read_csv(f"{module_config['output_dir']}{os.getpid()}.csv")
    # header = combined[0]
    # del combined[0]
    # sorted(combined, key=lambda x: int(x[-2]))
    # itemgetter_int = chained(operator.itemgetter(*[header.index(x) for x in module_config['sort_fields']]), partial(map, float), tuple)
    # combined.sort(key=itemgetter_int)
    # combined.reverse()
    # # results.reverse()
    # combined.insert(0, header)
    # return combined
def find_tickers():
    start_time = time.time()
    # n = module_config['process_load_size']
    # if module_config['test_mode']:
    #     if not module_config['test_use_input_tickers']:
    #         tickers = read_csv(f"data/nyse.csv")
    #rebuild cache on each run
    # clear_ticker_history_cache(module_config)
    results = {"mpb": None, "mpb_backtested": None}
    connection = obtain_db_connection(module_config)
    try:
        if not module_config['test_mode'] or (module_config['test_mode'] and not module_config['test_use_input_tickers']):

            if module_config['test_mode']:
                if module_config['test_use_test_population']:
                    # tickers = read_csv(f"data/nyse.csv")[1:module_config['test_population_size']]
                    _tickers =  [x[0] for x in  execute_query(connection, "select distinct t.symbol from tickers_ticker t left join history_tickerhistory ht on t.id = ht.ticker_id where ht.id is not null")[1:module_config['test_population_size']]]
                else:
                    _tickers =  [x[0] for x in  execute_query(connection, "select distinct t.symbol from tickers_ticker t left join history_tickerhistory ht on t.id = ht.ticker_id where ht.id is not null")[1:]]
                # _tickers = [tickers[i][0] for i in range(0, len(tickers))]
                # tickers
            else:
                if module_config['test_use_input_tickers']:
                    _tickers = module_config['tickers']
                else:
                    _tickers =  [x[0] for x in  execute_query(connection, "select distinct t.symbol from tickers_ticker t left join history_tickerhistory ht on t.id = ht.ticker_id where ht.id is not null")[1:]]
                    # _tickers = [tickers[i][0] for i in range(0, len(tickers))]
        else:
            _tickers = module_config['tickers']
        # client = RESTClient(api_key=module_config['api_key'])

        # del tickers[0]
        # tickers =
        # tickers = tickers[:module_config['test_population_size']]

        # _new_tickers = []
        # for _ticker in _tickers:
        #     if '$' not in _ticker:
        #         _new_tickers.append(_ticker)
        # _tickers = _new_tickers
        # _dispensarys = [x for x in dispensaries.keys()]
        generate_report(_tickers, module_config)
        # try:
        #     write_csv("mpb.csv", combined)
        # except:
        #     print(f"cannot write file")
        #
        # results = {"mpb": combined, "mpb_backtested":None}
        # #ok so once we get down here go ahead and load the option data
        # load_option_data(results,module_config)
        # run_backtests(results, module_config)
        print(f"API KEY: {module_config['api_key']}")
    except:
        traceback.print_exc()
    connection.close()

    # return results
    #ok so once we are here, let's go ahead and find the tickers that we need to backtest and run int


def load_option_data(results, module_config):
    combined = results['mpb']
    # if module_config['backtest']:
    print("##############\nLoading Market Scanner Option Data\n##############")
    # ticker =
    tickers = [combined[i][combined[0].index('symbol')].split("'>")[1].split("</")[0].strip() for i in range(1, len(combined))]
    process_list_concurrently(tickers,load_tickers_option_data, int(len(tickers)/module_config['num_processes'])+1 )
    print("##############\nLoaded Market Scanner Option Data\n##############")
    # combined[0].insert(combined[0].index('long_validation'), 'suggested_call')
    # combined[0].insert(combined[0].index('short_validation'), 'suggested_put')
    # combined[0].insert(combined[0].index('long_validation'), 'recommended_put')
    for i in range(1, len(combined)):
        # combined[i].insert(combined[0].index('short_validation'), 'suggested_put')
        ticker = combined[i][combined[0].index('symbol')].split("'>")[1].split("</")[0].strip()
        short_options = analyze_option_data(PositionType.SHORT,ticker,load_ticker_history_cached(ticker,module_config), module_config)
        if len(short_options) == 0:
            short_option = {'ticker':''}
        else:
            short_option = short_options[0]

        long_options = analyze_option_data(PositionType.LONG, ticker,
                                            load_ticker_history_cached(ticker, module_config), module_config)
        if len(long_options) == 0:
            long_option = {'ticker': ticker}
        else:
            long_option = long_options[0]
        put_link = urllib.parse.quote(f"{module_config['timespan_multiplier']}{module_config['timespan']}{short_option['ticker']}.html",safe='')
        call_link = urllib.parse.quote(f"{module_config['timespan_multiplier']}{module_config['timespan']}{long_option['ticker']}.html",safe='')
        # long_option = analyze_option_data(PositionType.LONG,ticker,load_ticker_history_cached(ticker,module_config), module_config)[0]
        short_option_str = f"<a href='{put_link}'>{short_option['ticker']}</a>"
        long_option_str = f"<a href='{call_link}'>{long_option['ticker']}</a>"
        combined[i][combined[0].index('suggested_put')]= short_option_str
        combined[i][combined[0].index('suggested_call')]= long_option_str
        # combined[i].insert(combined[0].index('long_validation'), long_option_str)

    write_csv("mpb.csv", combined)
    #once we get here, we need to update the report to include our preferred contracts for long and short

    long_contract = []
    # for i in range(1, len(combined)):
    #     if int(combined[i][combined[0].index('pick_level')]) >= module_config['report_alert_min']:
    #         pass


def run_backtests(results, module_config):
    combined = results['mpb']
    if module_config['backtest']:
        print("##############\nRunning Market Scanner Backtest\n##############")

        for i in range(1, len(combined)):
            if int(combined[i][combined[0].index('pick_level')]) == module_config['backtest_alert_count']:
                try:
                    combined[i][combined[0].index('backtested')] = True
                    # if module_config['logging']:
                    ticker = combined[i][combined[0].index('symbol')].split("'>")[1].split("</")[0].strip()
                    print(f"Ticker {combined[i][combined[0].index('symbol')]} alerted {','.join(combined[i][combined[0].index('alerts_triggered')].split(','))}, running backtest for {module_config['backtest_days']} days")
                    backtest_ticker_concurrently(combined[i][combined[0].index('alerts_triggered')].split(','), ticker,
                                                 load_ticker_history_cached(ticker, module_config), module_config)
                    backtest_results = analyze_backtest_results(load_backtest_results(ticker, module_config))
                    for _backtest_key in analyzed_backtest_keys:
                    # for ii in range(combined[0].index('backtested') + 1, len(combined[0])):
                            # print(f"Report_headers {_report_headers[i]}")
                        combined[i][combined[0].index(_backtest_key)] = backtest_results[_backtest_key]
                except:
                    combined[i][combined[0].index('backtested')] = False
                    traceback.print_exc()
                    print(f"Could not backtest ticker {combined[i][0]}")
        results['mpb_backtested'] = combined
        # try:
        #     # write_csv("mpb_backtested.csv", combined)
        # except:
        #     print(f"Cannot write file")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # freeze_support()
    start_time = time.time()
    # client = RESTClient(api_key=module_config['api_key'])
    # history_entries = load_ticker_history_csv("GE", client, 1, "hour", today, today, 500)
    # history_entries = load_ticker_history_raw("GE",  client, 1, "hour", today, today, 500)
    # did_dmi_alert(load_dmi_adx("GE", client, history_entries, module_config), history_entries, "GE", module_config)
    ##find data
    connection = obtain_db_connection(module_config)
    if module_config['trading_hours_only']:
        if datetime.datetime.now().hour < 17 and datetime.datetime.now().hour > 8:
            try:

                find_tickers()
                #do notification send
                if len(load_mpb_report(connection, module_config)) > 1:
                    send_email("andrew.smiley937@gmail.com","andrew.smiley937@gmail.com", f"MPB Traders ({module_config['timespan_multiplier']} {module_config['timespan']})  {datetime.datetime.now().strftime('%Y-%m-%d %H:00')}", f"Found {len(load_mpb_report(connection, module_config))-1} new stocks alerting. Click <a href=''>here</a> to view")
            # build_dashboard(module_config)

            except:
                traceback.print_exc()
        else:
            print(f"Not currently trading hours ({datetime.datetime.now()}), skipping")
    else:
        find_tickers()
        if len(load_mpb_report(connection, module_config)) > 1:
            send_email("andrew.smiley937@gmail.com", "andrew.smiley937@gmail.com",
                       f"MPB Traders ({module_config['timespan_multiplier']} {module_config['timespan']})  {datetime.datetime.now().strftime('%Y-%m-%d %H:00')}",
                       f"Found {len(load_mpb_report(connection, module_config)) - 1} new stocks alerting. Click <a href=''>here</a> to view")

        # do notification send
        # send_email("andrew.smiley937@gmail.com", "andrew.smiley937@gmail.com",f"MPB Traders (Hourly)  {datetime.datetime.now().strftime('%Y-%m-%d %H:00')}",generate_mpd_html_table(results['mpb']))
    connection.close()
    # /    build_dashboard(module_config)
        # generate_mpd_html_table(results['mpb'])
    # ticker_history = load_ticker_history_raw(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)
    # ticke = load_ticker_history_pd_frame(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)

    print(f"\nCompleted NYSE Market Scan in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")