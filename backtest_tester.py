import time
from enums import AlertType
from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime
from functions import load_module_config
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
if __name__ == '__main__':
    start_time = time.time()
    client = polygon.RESTClient(api_key=module_config['api_key'])
    # ticker = "GE"
    for ticker in module_config['tickers']:
        if module_config['run_concurrently']:
            backtest_ticker_concurrently(["MACD_SIGNAL_CROSS_MACD","SMA_CROSSOVER_DOWNWARD"], ticker, load_backtest_ticker_data(ticker,client, module_config ), module_config)
        else:
            backtest_ticker([AlertType.GOLDEN_CROSS_APPEARED], ticker, load_backtest_ticker_data(ticker,client, module_config ), module_config)
        analyze_backtest_results(load_backtest_results(ticker,module_config))

    print(f"\nCompleted Backtest of ({','.join([f'${x}' for x in module_config['tickers']])}) in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")