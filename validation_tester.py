import time
from enums import AlertType, PositionType
from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime

from history import load_ticker_history_raw
from validation import validate_ticker
from functions import load_module_config, get_today
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])

if __name__ == '__main__':
    start_time = time.time()
    client = polygon.RESTClient(api_key=module_config['api_key'])
    # ticker = "GE"
    for ticker in module_config['tickers']:
        ticker_history = load_ticker_history_raw(ticker, client, 1, module_config['timespan'],get_today(module_config, minus_days=7), get_today(module_config), 50000)
        if module_config['run_concurrently']:
            validate_ticker(module_config['position_type'],ticker,ticker_history, module_config)
        else:
            validate_ticker(module_config['position_type'],ticker,ticker_history, module_config)

    print(f"\nCompleted {module_config['position_type']} validation of ({','.join([f'${x}' for x in module_config['tickers']])}) in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")