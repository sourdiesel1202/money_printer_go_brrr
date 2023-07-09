import time
from enums import AlertType
from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently
import polygon, datetime
from functions import load_module_config
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
if __name__ == '__main__':
    start_time = time.time()
    client = polygon.RESTClient(api_key=module_config['api_key'])
    ticker = "AMC"
    backtest_ticker_concurrently([AlertType.DMIPLUS_CROSSOVER_DMINEG, AlertType.RSI_OVERSOLD], ticker, load_backtest_ticker_data(ticker,client, module_config ), module_config)


    print(f"\nCompleted Backtest of ${ticker} in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")