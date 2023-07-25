import time
import traceback
from zoneinfo import ZoneInfo

# from enums import AlertType, PositionType
# from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime

from enums import PositionType
# from polygon.rest import RESTClient as RESTCLient
from history import load_ticker_history_raw, load_options_history_raw, load_ticker_history_cached
# from validation import validate_ticker
from functions import load_module_config, get_today, obtain_db_connection
from options import load_ticker_option_data#, mcv_load_options_contracts
from options import analyze_option_data
# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
module_config = load_module_config('market_scanner_tester')
# from shape import compare_tickers

if __name__ == '__main__':
    start_time = time.time()
    # polygon.OptionsClient(api_key=module_config['api_key'])
    # client = RESTClient(api_key=module_config['api_key'])
    # client = MPBOptionsClient(api_key=module_config['api_key'])
    # return client.get_options_contract()
    # ticker = "GE"
    options_client = polygon.OptionsClient(api_key=module_config['api_key'])
    module_config['logging']=True
    for ticker_a in module_config['tickers']:
        # contract_tickers = load_ticker_option_data(ticker_a, load_ticker_history_cached(ticker_a, module_config), module_config)


        # def analyze_option_data(position_type, ticker, ticker_history, module_config):

        # analyze_option_data(PositionType.LONG, ticker_a,load_ticker_history_cached(ticker_a, module_config), module_config)
        # for _date in contract_tickers:
        #     print(f"found {len(contract_tickers[_date])} contracts at date {_date}")
        # for option_contract in contract_tickers[_date]:
        #     try:
        #         contract_dat = load_options_history_raw(option_contract, options_client, module_config['timespan_multiplier'], module_config['timespan'],get_today(module_config, minus_days=30), get_today(module_config), 50000,module_config)
        #     except:
        #         traceback.print_exc()
        #     pass
        #     # load_options_history_raw(option_contract, options_client, module_config['timespan_multiplier'], module_config['timespan'])
        #once we have contract tickers, go ahead and load the prices

        pass
        # for ticker_b in module_config['compare_tickers']:

        # ticker_history_a = load_options_history_raw(ticker_a, client, module_config['timespan_multiplier'], module_config['timespan'],get_today(module_config, minus_days=6), get_today(module_config), 50000,module_config)
        # for i in range(0, len(ticker_history_a)):
        #     print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${module_config['tickers'][0]}: Previous History Record: {datetime.datetime.fromtimestamp(ticker_history_a[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}: Current History Record: {datetime.datetime.fromtimestamp(ticker_history_a[(i)].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:|O:{ticker_history_a[(i)].open}|H:{ticker_history_a[(i)].high}|L:{ticker_history_a[(i)].low}|C:{ticker_history_a[(i)].close}|: Volume: {ticker_history_a[(i)].volume}")

        #     ticker_history_b = load_ticker_history_raw(ticker_b, client, 1, module_config['timespan'],get_today(module_config, minus_days=7), get_today(module_config), 50000, module_config)
        #     compare_tickers(ticker_a, ticker_history_a, ticker_b, ticker_history_b, module_config)
        # if module_config['run_concurrently']:
            # determine_line_similarity(1,2)
            # de(module_config['position_type'],ticker,ticker_history, module_config)
        # else:
            # determine_line_similarity(1, 2)
            # validate_ticker(module_config['position_type'],ticker,ticker_history, module_config)

    print(f"\nCompleted {module_config['position_type']} validation of ({','.join([f'${x}' for x in module_config['tickers']])}) in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")