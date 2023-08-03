# This is a sample Python script.
# import operator import itemgetter
import urllib.parse

from db_functions import load_ticker_last_updated, process_ticker_history, load_mpb_report
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
from options import analyze_option_data, load_ticker_option_data, load_ticker_option_contracts as _load_ticker_option_contracts, load_ticker_contract_history as _load_ticker_contract_history
from zoneinfo import ZoneInfo
from history import load_ticker_history_raw, load_ticker_history_pd_frame, load_ticker_history_csv, \
    clear_ticker_history_cache, load_ticker_history_cached
from functions import load_module_config, read_csv, write_csv, combine_csvs, get_today, process_list_concurrently
from enums import  PositionType
from options import load_tickers_option_data
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
# module_config = load_module_config("market_scanner")
from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results,analyze_backtest_results, analyzed_backtest_keys
# today =datetime.datetime.now().strftime("%Y-%m-%d")
today =get_today(module_config)
required_indicators = ["macd", 'rsi', 'sma', 'dmi', "sr_band_breakout", 'golden_cross', 'death_cross']
from plotting import build_indicator_dict, plot_ticker_with_indicators



def process_tickers(tickers):
    # client = RESTClient(api_key=module_config['api_key'])
    ticker_results = {}
    # latest_entry = ""
    connection = obtain_db_connection(load_module_config('market_scanner'))
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

# def load_contract_histories(_tickers):
#     client = RESTClient(api_key=module_config['api_key'])
#     _module_config  =load_module_config(__file__.split("/")[-1].split(".py")[0])
#     connection= obtain_db_connection(_module_config)
#     try:
#         # successes = []
#         # failures = [['symbol']]
#         for ticker in _tickers:
#             #ok so first we need to load the ticker history
#             print(f"{os.getpid()}: Loading contract data for {_tickers.index(ticker)+1}/{len(_tickers)} ")
#             th = load_ticker_history_cached(ticker, module_config, connection=connection)
#             try:
#                 #ok so what we need to do here is load our contract data now
#                 pass
#
#                 _ = load_ticker_option_data(ticker, th, module_config, connection=connection)
#             except:
#                 pass
#                 traceback.print_exc()
#                 print(f"could not load ticker history for {ticker}")
#                 # failures.append([ticker])
#         # write_csv(f"{module_config['output_dir']}mpb_load_failures.csv",failures)
#     except:
#         traceback.print_exc()
#     # return  successes
#     connection.close()
def load_ticker_option_contracts(ticker_list):
    _module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
    connection = obtain_db_connection(_module_config)

    # def load_ticker_option_contracts(ticker, ticker_history, module_config, connection=None):
    for ticker in ticker_list:

        try:
                _load_ticker_option_contracts(ticker, load_ticker_history_cached(ticker, module_config, connection=connection), module_config, connection=connection)
                print(f"Loaded contracts for {ticker_list.index(ticker)}/{len(ticker_list)-1}")
        except:
            traceback.print_exc()
            print(f"Could not load contracts for {ticker}")
    connection.close()

def load_ticker_contract_history(contract_data):
    _module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
    _module_config['num_processes'] = 12
    connection = obtain_db_connection(_module_config)

    contract_dict = {}
    for data in contract_data:
        if data[-1] not in contract_dict:
            contract_dict[data[-1]]=[data[1]]
        else:
            contract_dict[data[-1]].append(data[1])

    # def load_ticker_contract_history(contracts, ticker, ticker_history, module_config, connection):
    for ticker, contracts in contract_dict.items():
        # ticker = data[-1]
        try:
                _load_ticker_contract_history(contracts,ticker, load_ticker_history_cached(ticker, module_config, connection=connection), module_config, connection=connection)
                print(f"Loaded contract history for {[x for x in contract_dict.keys()].index(ticker)}/{len([x for x in contract_dict.keys()])-1} tickers, ({len(contracts)} contracts)")
        except:
            traceback.print_exc()
            print(f"Could not load contract history for {ticker}")
    connection.close()
def load_contract_histories(contract_list, module_config):
    print(f"Loading history data for {len(contract_list)} contracts")
    if module_config['run_concurrently']:

        # process_list_concurrently(ticker_list, load_contract_histories,int(len(ticker_list)/module_config['num_processes'])+1)
        # process_list_concurrently(contract_list, load_ticker_option_contracts,int(len(contract_list) / module_config['num_processes']) + 1)
        # contract_list = execute_query()
        process_list_concurrently(contract_list, load_ticker_contract_history,int(len(contract_list) / 12) + 1)
        # process_list_concurrently(ticker_list, load_contract_histories,int(len(ticker_list)/module_config['num_processes'])+1)
    else:
        load_ticker_option_contracts(contract_list)


def load_contracts(ticker_list, module_config):

    # _tickers = load_contract_histories(_tickers)
    print(f"Loading contract data for {len(ticker_list)} tickers")
    if module_config['run_concurrently']:

        # process_list_concurrently(ticker_list, load_contract_histories,int(len(ticker_list)/module_config['num_processes'])+1)
        process_list_concurrently(ticker_list, load_ticker_option_contracts,int(len(ticker_list)/module_config['num_processes'])+1)
        # contract_list = execute_query()
        # process_list_concurrently(contract_list, load_ticker_contract_history,int(len(ticker_list)/module_config['num_processes'])+1)
        # process_list_concurrently(ticker_list, load_contract_histories,int(len(ticker_list)/module_config['num_processes'])+1)
    else:
        load_ticker_option_contracts(ticker_list)

def find_contracts():
    start_time = time.time()
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
        load_contracts(_tickers, module_config)
        connection.commit()
        print(f"#### Loaded Contracts for {len(_tickers)} Tickers ####")
        time.sleep(30)
        load_contract_histories(execute_query(connection, "select tc.id, tc.symbol contract, tc.name, tc.type, tc.expry, tc.description, tc.strike_price, t.symbol ticker from tickers_contract tc, tickers_ticker t where t.id =tc.ticker_id and STR_TO_DATE(expry, '%Y-%m-%d') >= current_date")[1:], module_config)

        print(f"#### Completed load of contract histories ####")
        # print(f"#### Loaded Contract history for {len(execute_query(connection, 'select tc.id, tc.symbol contract, tc.name, tc.type, tc.expry, tc.description, tc.strike_price, t.symbol ticker from tickers_contract tc, tickers_ticker t where t.id =tc.ticker_id and STR_TO_DATE(expry, \'%Y-%m-%d\') >= current_date')[1:])} Tickers ####")
        time.sleep(30)
        print(f"API KEY: {module_config['api_key']}")
    except:
        traceback.print_exc()
    connection.close()




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # freeze_support()
    start_time = time.time()
    ##find data
    connection = obtain_db_connection(module_config)
    if module_config['trading_hours_only']:
        if datetime.datetime.now().hour < 17 and datetime.datetime.now().hour > 8:
            try:

                find_contracts()
                #do notification send
                # if len(load_mpb_report(connection, module_config)) > 1:
                #     send_email("andrew.smiley937@gmail.com","andrew.smiley937@gmail.com", f"MPB Traders ({module_config['timespan_multiplier']} {module_config['timespan']})  {datetime.datetime.now().strftime('%Y-%m-%d %H:00')}", f"Found {len(load_mpb_report(connection, module_config))-1} new stocks alerting. Click <a href=''>here</a> to view")
            # build_dashboard(module_config)

            except:
                traceback.print_exc()
        else:
            print(f"Not currently trading hours ({datetime.datetime.now()}), skipping")
    else:
        find_contracts()
        # if len(load_mpb_report(connection, module_config)) > 1:
        #     send_email("andrew.smiley937@gmail.com", "andrew.smiley937@gmail.com",
        #                f"MPB Traders ({module_config['timespan_multiplier']} {module_config['timespan']})  {datetime.datetime.now().strftime('%Y-%m-%d %H:00')}",
        #                f"Found {len(load_mpb_report(connection, module_config)) - 1} new stocks alerting. Click <a href=''>here</a> to view")

        # do notification send
        # send_email("andrew.smiley937@gmail.com", "andrew.smiley937@gmail.com",f"MPB Traders (Hourly)  {datetime.datetime.now().strftime('%Y-%m-%d %H:00')}",generate_mpd_html_table(results['mpb']))
    connection.close()
    # /    build_dashboard(module_config)
        # generate_mpd_html_table(results['mpb'])
    # ticker_history = load_ticker_history_raw(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)
    # ticke = load_ticker_history_pd_frame(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)

    print(f"\nCompleted NYSE Market Scan in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")