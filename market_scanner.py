# This is a sample Python script.
# import operator import itemgetter
from multiprocessing import freeze_support
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
from indicators import load_macd, load_sma, load_dmi_adx, load_rsi, did_macd_alert, did_rsi_alert, did_sma_alert, did_dmi_alert, did_adx_alert,determine_sma_alert_type
from indicators import determine_rsi_alert_type, determine_macd_alert_type,determine_adx_alert_type,determine_dmi_alert_type,load_ticker_similar_trends
from indicators import  load_death_cross, load_golden_cross, determine_death_cross_alert_type,determine_golden_cross_alert_type, did_golden_cross_alert, did_death_cross_alert
from indicators import load_support_resistance, is_trading_in_sr_band, determine_sr_direction
from history import load_ticker_history_raw, load_ticker_history_pd_frame, load_ticker_history_csv, \
    clear_ticker_history_cache, load_ticker_history_cached
from functions import load_module_config, read_csv, write_csv, combine_csvs, get_today, process_list_concurrently
from enums import  PositionType
from options import load_tickers_option_data
from validation import validate_ticker
# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
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
                results.append([datetime.datetime.fromtimestamp(v['latest'] / 1e3, tz=ZoneInfo('US/Eastern')).strftime(
                    "%Y-%m-%d %H:%M:%S"), f"<a href='{module_config['timespan_multiplier']}{module_config['timespan']}{k}.html'>{k}</a>", f"${v['close']}", v['volume'], v['long_validation'],'', v['short_validation'], ''])
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
def build_ticker_results(ticker, ticker_results,ticker_history, client):
    _th = ticker_history
    ticker_history = ticker_history[:-1] #since the last bar hasn't closed yet
    sma = load_sma(ticker, ticker_history, module_config)
    macd_data = load_macd(ticker, ticker_history, module_config)
    dmi_adx_data = load_dmi_adx(ticker, ticker_history, module_config)
    rsi_data = load_rsi(ticker, ticker_history, module_config)
    golden_cross_data = load_golden_cross(ticker, ticker_history, module_config)
    death_cross_data = load_death_cross(ticker, ticker_history, module_config)
    sr_data = load_support_resistance(ticker, ticker_history, module_config)

    # def did_macd_alert(indicator_data, ticker, ticker_history, module_config):
    ticker_results[ticker]['long_validation'] = ','.join([k for k, v in validate_ticker(PositionType.LONG, ticker, _th, module_config).items() if v])
    ticker_results[ticker]['short_validation'] = ','.join([k for k, v in validate_ticker(PositionType.SHORT, ticker, _th, module_config).items() if v])
    ticker_results[ticker]['sma'] = did_sma_alert(sma, ticker, ticker_history, module_config)
    ticker_results[ticker]['macd'] = did_macd_alert(macd_data, ticker, ticker_history, module_config)
    ticker_results[ticker]['rsi'] = did_rsi_alert(rsi_data, ticker, ticker_history, module_config)
    ticker_results[ticker]['dmi'] = did_dmi_alert(dmi_adx_data, ticker, ticker_history, module_config)
    # ticker_results[ticker]['adx'] = did_adx_alert(dmi_adx_data, ticker, ticker_history, module_config)
    ticker_results[ticker]['golden_cross'] = did_golden_cross_alert(golden_cross_data, ticker, ticker_history,module_config)
    ticker_results[ticker]['death_cross'] = did_death_cross_alert(death_cross_data, ticker, ticker_history,module_config)
    ticker_results[ticker]['sr_band_breakout'] = not is_trading_in_sr_band(sr_data, ticker, ticker_history,module_config)
    if ticker_results[ticker]['macd']:
        ticker_results[ticker]['directions'].append(
            determine_macd_alert_type(macd_data, ticker, ticker_history, module_config))
    if ticker_results[ticker]['dmi']:
        ticker_results[ticker]['directions'].append(
            determine_dmi_alert_type(dmi_adx_data, ticker, ticker_history, module_config))
    # if ticker_results[ticker]['adx']:
    #     ticker_results[ticker]['directions'].append(
    #         determine_adx_alert_type(dmi_adx_data, ticker_history, ticker, module_config))
    if ticker_results[ticker]['sma']:
        ticker_results[ticker]['directions'].append(
            determine_sma_alert_type(sma, ticker, ticker_history, module_config))
    if ticker_results[ticker]['golden_cross']:
        ticker_results[ticker]['directions'].append(
            determine_golden_cross_alert_type(golden_cross_data, ticker, ticker_history, module_config))
    if ticker_results[ticker]['death_cross']:
        ticker_results[ticker]['directions'].append(
            determine_death_cross_alert_type(death_cross_data, ticker, ticker_history, module_config))
    if ticker_results[ticker]['sr_band_breakout']:
            ticker_results[ticker]['directions'].append(determine_sr_direction(sr_data, ticker, ticker_history, module_config))
            #ignore if under sr_breakout_percentage
            if AlertType.BREAKOUT_SR_UP in ticker_results[ticker]['directions'][-1] or AlertType.BREAKOUT_SR_DOWN in ticker_results[ticker]['directions'][-1]:
                breakout_percentage = float(ticker_results[ticker]['directions'][-1].split('/')[-1].split('%')[0].replace('-',''))
                if breakout_percentage < module_config['sr_breakout_percentage']:
                    ticker_results[ticker]['sr_band_breakout'] = False
                    del ticker_results[ticker]['directions'][-1]
    if ticker_results[ticker]['rsi']:
        ticker_results[ticker]['directions'].append(determine_rsi_alert_type(rsi_data, ticker, ticker_history, module_config))
        #basically if any bullish alerst and overbought, ignore
        if ((ticker_results[ticker]['macd'] and determine_macd_alert_type(macd_data, ticker, ticker_history, module_config) == AlertType.MACD_MACD_CROSS_SIGNAL) or
           (ticker_results[ticker]['sma'] and determine_sma_alert_type(sma, ticker, ticker_history, module_config) == AlertType.SMA_CONFIRMATION_UPWARD) or
           (ticker_results[ticker]['dmi'] and determine_dmi_alert_type(dmi_adx_data, ticker, ticker_history, module_config) == AlertType.DMIPLUS_CROSSOVER_DMINEG))  and determine_rsi_alert_type(rsi_data, ticker, ticker_history, module_config) == AlertType.RSI_OVERBOUGHT:
            ticker_results[ticker]['rsi'] = False
            del ticker_results[ticker]['directions'][-1]
        elif ((ticker_results[ticker]['macd'] and determine_macd_alert_type(macd_data, ticker, ticker_history, module_config) == AlertType.MACD_SIGNAL_CROSS_MACD) or
           (ticker_results[ticker]['sma'] and determine_sma_alert_type(sma, ticker, ticker_history, module_config) == AlertType.SMA_CONFIRMATION_DOWNWARD) or
           (ticker_results[ticker]['dmi'] and determine_dmi_alert_type(dmi_adx_data, ticker, ticker_history, module_config) == AlertType.DMINEG_CROSSOVER_DMIPLUS))  and determine_rsi_alert_type(rsi_data, ticker, ticker_history, module_config) == AlertType.RSI_OVERSOLD:
            ticker_results[ticker]['rsi'] = False
            del ticker_results[ticker]['directions'][-1]


        # if ticker_results[ticker]['rsi']:
    #generate plot for the ticker
    if len(ticker_results[ticker]['directions']) >= module_config['report_alert_min']:
        plot_ticker_with_indicators(ticker, _th,build_indicator_dict(ticker, _th, module_config), module_config)
def process_tickers(tickers):
    client = RESTClient(api_key=module_config['api_key'])
    # client = RESTClient(api_key=module_config['api_key'])
    # _report_headers = ['timestamp','symbol','price','volume', 'macd_flag', 'rsi_flag', 'sma_flag', 'dmi_flag', 'adx_flag','golden_cross_flag','death_cross_flag', 'pick_level', 'conditions_matched','reasons', 'backtested']
    # ticker = "GE"
    # data_lines = read_csv(f"data/nyse.csv")
    # if module_config['logging']:
    # print(f"Loaded {len(data_lines) - 1} tickers on NYSE")
    ticker_results = {}
    # latest_entry = ""

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
            # ticker_history = load_ticker_history_raw(ticker, client, 1, module_config['timespan'],get_today(module_config, minus_days=365), today, 10000, module_config)
            ticker_history = load_ticker_history_cached(ticker, module_config)
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

            build_ticker_results(ticker,ticker_results,ticker_history, client)

        except:
            traceback.print_exc()
            print(f"Cannot process ticker: {ticker}")
            del ticker_results[ticker]
    # results = [['symbol','macd_flag', 'rsi_flag', 'sma_flag', 'pick_level', 'conditions_matched']]
    process_results(ticker_results)

def load_ticker_histories(_tickers):
    client = RESTClient(api_key=module_config['api_key'])
    _module_config  =load_module_config(__file__.split("/")[-1].split(".py")[0])
    successes = []
    failures = [['symbol']]
    for ticker in _tickers:
        try:
            # if not module_config['test_mode']:
            _ = load_ticker_history_raw(ticker, client,1, module_config['timespan'],get_today(module_config, minus_days=365), today, limit=50000, module_config=_module_config)
            # else:
                # _ = load_ticker_history_raw(ticker, client,1, module_config['timespan'],get_today(module_config, minus_days=365), 11, limit=50000, module_config=_module_config)
            successes.append(ticker)
        except:
            # traceback.print_exc()
            failures.append([ticker])
    write_csv(f"{module_config['output_dir']}mpb_load_failures.csv",failures)
    # return  successes


def generate_report(_tickers, module_config):
    # _tickers = load_ticker_histories(_tickers)
    print(f"Loading history data for {len(_tickers)} tickers")
    if module_config['run_concurrently']:
        process_list_concurrently(_tickers, load_ticker_histories,int(len(_tickers)/module_config['num_processes'])+1)
    else:
        load_ticker_histories(_tickers)
    _tickers = [x.split(f"{module_config['timespan_multiplier']}{module_config['timespan']}.csv")[0] for x in os.listdir(f"{module_config['output_dir']}cached/") if "O:" not in x]
    if module_config['run_concurrently']:
        task_loads = [_tickers[i:i + int(len(_tickers)/module_config['num_processes'])+1] for i in range(0, len(_tickers), int(len(_tickers)/module_config['num_processes'])+1)]
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
    return combined
def find_tickers():
    start_time = time.time()
    # n = module_config['process_load_size']
    # if module_config['test_mode']:
    #     if not module_config['test_use_input_tickers']:
    #         tickers = read_csv(f"data/nyse.csv")
    #rebuild cache on each run
    clear_ticker_history_cache(module_config)
    if not module_config['test_mode'] or (module_config['test_mode'] and not module_config['test_use_input_tickers']):

        if module_config['test_mode']:
            if module_config['test_use_test_population']:
                tickers = read_csv(f"data/nyse.csv")[1:module_config['test_population_size']]
            else:
                tickers = read_csv(f"data/nyse.csv")[1:]
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
    # client = RESTClient(api_key=module_config['api_key'])

    # del tickers[0]
        # tickers =
        # tickers = tickers[:module_config['test_population_size']]

    _new_tickers = []
    for _ticker in _tickers:
        if '$' not in _ticker:
            _new_tickers.append(_ticker)
    _tickers = _new_tickers
    # _dispensarys = [x for x in dispensaries.keys()]
    combined = generate_report(_tickers, module_config)
    try:
        write_csv("mpb.csv", combined)
    except:
        print(f"cannot write file")

    results = {"mpb": combined, "mpb_backtested":None}
    #ok so once we get down here go ahead and load the option data
    load_option_data(results,module_config)
    run_backtests(results, module_config)
    print(f"API KEY: {module_config['api_key']}")

    return results
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
        # long_option = analyze_option_data(PositionType.LONG,ticker,load_ticker_history_cached(ticker,module_config), module_config)[0]
        short_option_str = f"<a href='{module_config['timespan_multiplier']}{module_config['timespan']}{short_option['ticker']}.html'>{short_option['ticker']}</a>"
        long_option_str = f"<a href='{module_config['timespan_multiplier']}{module_config['timespan']}{long_option['ticker']}.html'>{long_option['ticker']}</a>"
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
        try:
            write_csv("mpb_backtested.csv", combined)
        except:
            print(f"Cannot write file")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # freeze_support()
    start_time = time.time()
    # client = RESTClient(api_key=module_config['api_key'])
    # history_entries = load_ticker_history_csv("GE", client, 1, "hour", today, today, 500)
    # history_entries = load_ticker_history_raw("GE",  client, 1, "hour", today, today, 500)
    # did_dmi_alert(load_dmi_adx("GE", client, history_entries, module_config), history_entries, "GE", module_config)
    ##find data
    if module_config['trading_hours_only']:
        if datetime.datetime.now().hour < 17 and datetime.datetime.now().hour > 8:
            results = find_tickers()
            #do notification send
            send_email("andrew.smiley937@gmail.com","andrew.smiley937@gmail.com", f"MPB Traders (Hourly)  {datetime.datetime.now().strftime('%Y-%m-%d %H:00')}", generate_mpd_html_table(results['mpb']))
            build_dashboard(module_config)
        else:
            print(f"Not currently trading hours ({datetime.datetime.now()}), skipping")
    else:
        results = find_tickers()
        # do notification send
        send_email("andrew.smiley937@gmail.com", "andrew.smiley937@gmail.com",f"MPB Traders (Hourly)  {datetime.datetime.now().strftime('%Y-%m-%d %H:00')}",generate_mpd_html_table(results['mpb']))
        build_dashboard(module_config)
        # generate_mpd_html_table(results['mpb'])
    # ticker_history = load_ticker_history_raw(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)
    # ticke = load_ticker_history_pd_frame(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)

    print(f"\nCompleted NYSE Market Scan in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")