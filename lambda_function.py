# from functions import open_rds_connection
import datetime
import time

from functions import read_csv, load_module_config
from market_scanner import find_tickers
from notification import send_email, generate_mpd_html_table
import json, logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    start_time = time.time()
    # client = polygon.RESTClient(api_key=module_config['api_key'])
    # history_entries = load_ticker_history_csv("GE", client, 1, "hour", today, today, 500)
    # history_entries = load_ticker_history_raw("GE",  client, 1, "hour", today, today, 500)
    # did_dmi_alert(load_dmi_adx("GE", client, history_entries, module_config), history_entries, "GE", module_config)
    ##find data
    module_config = load_module_config('market_scanner')
    if module_config['trading_hours_only']:
        if datetime.datetime.now().hour < 17 and datetime.datetime.now().hour > 8:
            results = find_tickers()
            # do notification send
            send_email("andrew.smiley937@gmail.com", "andrew.smiley937@gmail.com",
                       f"MPB Traders (Hourly)  {datetime.datetime.now().strftime('%Y-%m-%d %H:00')}",
                       generate_mpd_html_table(results['mpb']))
        else:
            print(f"Not currently trading hours ({datetime.datetime.now()}), skipping")
    else:
        results = find_tickers()
        # do notification send
        send_email("andrew.smiley937@gmail.com", "andrew.smiley937@gmail.com",
                   f"MPB Traders (Hourly)  {datetime.datetime.now().strftime('%Y-%m-%d %H:00')}",
                   generate_mpd_html_table(results['mpb']))
    # ticker_history = load_ticker_history_raw(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)
    # ticke = load_ticker_history_pd_frame(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)

    print(
        f"\nCompleted NYSE Market Scan in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")
    # send_email("andrew.smiley937@gmail.com", "andrew.smiley937@gmail.com", "MPB Traders Hourly Report (Test)",
    #            generate_mpd_html_table(read_csv("mpb.csv")))
        # return "Added %d items to RDS MySQL table" %(item_count)
    return {
        'statusCode': 200,
        'body': json.dumps(f'Emailed {len(results)} events')
    }