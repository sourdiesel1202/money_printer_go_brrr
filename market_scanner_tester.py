# This is a sample Python script.
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
from indicators import load_macd, load_sma, load_dmi_adx, load_rsi, did_macd_alert, did_rsi_alert, did_sma_alert, did_dmi_alert, did_adx_alert
from indicators import determine_rsi_direction, determine_macd_alert_type,determine_adx_alert_type,determine_dmi_alert_type
from history import load_ticker_history_raw, load_ticker_history_pd_frame, load_ticker_history_csv
from functions import  load_module_config, read_csv, write_csv,combine_csvs, get_today
# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results,analyze_backtest_results, analyzed_backtest_keys
# today =datetime.datetime.now().strftime("%Y-%m-%d")
today =get_today(module_config)
required_indicators = ["macd", 'rsi', 'sma', 'dmi', 'adx']
from market_scanner import find_tickers, process_tickers
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