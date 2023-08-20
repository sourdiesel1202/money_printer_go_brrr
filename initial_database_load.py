# This is a sample Python script.
import os, operator
import traceback
import multiprocessing

from db_functions import combine_db_update_files, execute_bulk_update_file
from notification import send_email, generate_mpd_html_table
# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
# from polygon import RESTClient
import polygon, datetime
from polygon.rest import RESTClient
import time
from zoneinfo import ZoneInfo
# from indicators import load_macd, load_sma, load_dmi_adx, load_rsi, did_macd_alert, did_rsi_alert, did_sma_alert, did_dmi_alert, did_adx_alert
# from indicators import determine_rsi_direction, determine_macd_alert_type,determine_adx_alert_type,determine_dmi_alert_type
# from history import load_ticker_history_raw, load_ticker_history_pd_frame, load_ticker_history_csv
from functions import  load_module_config, read_csv, write_csv,combine_csvs, get_today
from functions import timestamp_to_datetime, process_list_concurrently
# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
module_config = load_module_config("market_scanner")
from history import load_ticker_history_raw
from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results,analyze_backtest_results, analyzed_backtest_keys
# today =datetime.datetime.now().strftime("%Y-%m-%d")
today =get_today(module_config)
required_indicators = ["macd", 'rsi', 'sma', 'dmi', 'adx']
from functions import obtain_db_connection, execute_query
from tickers import load_nyse_tickers, load_nyse_tickers_cached, write_tickers_to_db
def load_ticker_histories(_tickers):
    connection = obtain_db_connection(module_config)
    try:
        client = RESTClient(api_key=module_config['api_key'])
        _module_config  =load_module_config("market_scanner")
        successes = []
        failures = [['symbol']]
        for ticker in _tickers:
            print(f"Attempting to load data for {_tickers.index(ticker)}/{len(_tickers)}")
            try:
                # if not module_config['test_mode']:
                _ = load_ticker_history_raw(ticker['symbol'],  client, module_config['timespan_multiplier'], module_config['timespan'], get_today(module_config, minus_days=730), get_today(module_config,), 50000, module_config, connection=connection)
                # else:
                # _ = load_ticker_history_raw(ticker, client,1, module_config['timespan'],get_today(module_config, minus_days=365), 11, limit=50000, module_config=_module_config)
                successes.append(ticker)
            except:
                traceback.print_exc()
                failures.append([ticker])
        write_csv(f"{module_config['output_dir']}mpb_load_failures.csv",failures)
    except:
        connection.close()


if __name__ == '__main__':

    start_time = time.time()
    connection = obtain_db_connection(module_config)
    try:
        tickers = load_nyse_tickers_cached(module_config)
        print(f"Writing Ticker Data for {len(tickers)} tickers")
        # write_tickers_to_db(connection, tickers, module_config)
        unloaded_tickers = []
        rows = execute_query(connection, "select t.* from tickers_ticker t where symbol='YUM'")
        for i in range(1, len(rows)):
            entry = {}
            for ii in range(0, len(rows[0])):
                entry[rows[0][ii]] = rows[i][ii]
            unloaded_tickers.append(entry)
            # unloaded_tickers.append({x[]})

        client = RESTClient(api_key=module_config['api_key'])
        # load_ticker_histories(unloaded_tickers)
        if module_config['run_concurrently']:
            process_list_concurrently(unloaded_tickers, load_ticker_histories, int(len(unloaded_tickers)/module_config['num_processes'])+1)
        else:
            load_ticker_histories([unloaded_tickers[-1]])
            # load_ticker_histories(unloaded_tickers)

        combine_db_update_files(module_config)
        execute_bulk_update_file(connection, module_config)

    except:
        connection.close()
    print(f"\nCompleted MPB Initial Database Load in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")