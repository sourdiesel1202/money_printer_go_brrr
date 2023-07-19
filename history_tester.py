import time
# from enums import AlertType, PositionType
# from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime

from history import load_ticker_history_raw
# from validation import validate_ticker
from functions import load_module_config, get_today, human_readable_datetime, timestamp_to_datetime

# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
module_config = load_module_config('market_scanner_tester')
from support_resistance import find_support_resistance_levels
# from shape import compare_tickers
from history import  load_ticker_history_cached
from indicators import load_support_resistance, is_trading_in_sr_band, determine_sr_direction

if __name__ == '__main__':
    start_time = time.time()
    client = polygon.RESTClient(api_key=module_config['api_key'])
    # ticker = "GE"
    # ticker_b = module_config['compare_ticker']
    for ticker in module_config['tickers']:
        # module_config['logging'] = True
        _th = load_ticker_history_cached(ticker, module_config)[-180:]
        for i in reversed(range(10, len(_th)-10)):
            ticker_history = _th[:i]
            if module_config['logging']:
                print(f"{human_readable_datetime(timestamp_to_datetime(ticker_history[-1].timestamp))}:${ticker}: Testing Support Resistance (Last Close ${ticker_history[-1].close})")
            if not is_trading_in_sr_band(load_support_resistance(ticker, ticker_history, module_config), ticker, ticker_history, module_config):
                output = determine_sr_direction(load_support_resistance(ticker, ticker_history, module_config), ticker, ticker_history, module_config)

                print(f"{human_readable_datetime(timestamp_to_datetime(ticker_history[-1].timestamp))}:${ticker}: Testing Support Resistance (Last Close ${ticker_history[-1].close}) Alert Fired: {output}")


    print(f"\nCompleted {module_config['position_type']} validation of ({','.join([f'${x}' for x in module_config['tickers']])}) in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")