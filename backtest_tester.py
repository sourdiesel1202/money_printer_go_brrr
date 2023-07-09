import time
from enums import AlertType
from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently
import polygon, datetime
from functions import load_module_config
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
if __name__ == '__main__':
    start_time = time.time()
    client = polygon.RESTClient(api_key=module_config['api_key'])
    # import polygon, datetime
    # def backtest_ticker(alert_types, ticker, ticker_history, module_config):
    # def load_backtest_ticker_data(ticker, client, module_config):
    ticker = "EME"
    backtest_ticker_concurrently([AlertType.MACD_SIGNAL_CROSS_MACD, AlertType.RSI_OVERBOUGHT], ticker, load_backtest_ticker_data(ticker,client, module_config ), module_config)
    # client = polygon.RESTClient(api_key=module_config['api_key'])
    # history_entries = load_ticker_history_csv("GE", client, 1, "hour", today, today, 500)
    # history_entries = load_ticker_history_raw("GE",  client, 1, "hour", today, today, 500)
    # did_dmi_alert(load_dmi_adx("GE", client, history_entries, module_config), history_entries, "GE", module_config)
    # find_tickers()
    # ticker_history = load_ticker_history_raw(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)
    # ticke = load_ticker_history_pd_frame(ticker,client,1, "hour", "2023-07-06","2023-07-06",5000)

    print(f"\nCompleted Backtest of ${ticker} in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")