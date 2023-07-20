import time
from zoneinfo import ZoneInfo

# from enums import AlertType, PositionType
# from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime

from history import load_ticker_history_raw,load_ticker_history_cached
# from validation import validate_ticker
from functions import load_module_config, get_today
# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
module_config = load_module_config('market_scanner_tester')
# from shape import compare_tickers
# from plotting import plot_ticker_with_indicators, plot_indicator_data,plot_indicator_data_dual_y_axis, plot_sr_lines
# from indicators import load_macd, load_sma, load_dmi_adx, load_rsi,load_support_resistance
# from indicators import load_dmi_adx
# from indicators import  load_death_cross, load_golden_cross, determine_death_cross_alert_type,determine_golden_cross_alert_type, did_golden_cross_alert, did_death_cross_alert
from s3 import upload_file
if __name__ == '__main__':
    start_time = time.time()
    client = polygon.RESTClient(api_key=module_config['api_key'])
    upload_file("dashboard.html", "mpb-traders")
    # module_config['logging']=True
    # for ticker_a in module_config['tickers']:
    #     # for ticker_b in module_config['compare_tickers']:
    #     ticker_history_a = load_ticker_history_cached(ticker_a, module_config)
    #     indicator_dict = {
    #         "sma": {
    #             "plot": plot_indicator_data(ticker_a, ticker_history_a[-80:], load_sma(ticker_a, ticker_history_a,module_config), module_config, name='sma10'),
    #             "overlay":True
    #                 },
    #         "ema50": {
    #             "plot": plot_indicator_data(ticker_a, ticker_history_a[-80:], load_golden_cross(ticker_a, ticker_history_a,module_config)['sma_short'], module_config, name='ema50', color='yellow'),
    #             "overlay":True
    #                 },
    #         "ema200": {
    #             "plot": plot_indicator_data(ticker_a, ticker_history_a[-80:],
    #                                         load_golden_cross(ticker_a, ticker_history_a, module_config)['sma_long'],
    #                                         module_config, name='ema200', color='purple'),
    #             "overlay": True
    #         },
    #
    #         "rsi": {
    #             "plot": plot_indicator_data(ticker_a, ticker_history_a[-80:],
    #                                         load_rsi(ticker_a, ticker_history_a, module_config),
    #                                         module_config, name='rsi', color='Blue'),
    #             "overlay": False
    #         },
    #         "macd": {
    #             "plot": plot_indicator_data_dual_y_axis(ticker_a, ticker_history_a[-80:],
    #                                         load_macd(ticker_a, ticker_history_a, module_config),
    #                                         module_config,keys=['macd', 'signal'], colors=['green','red'] ),
    #             "overlay": False
    #         },
    #         "dmi": {
    #             "plot": plot_indicator_data_dual_y_axis(ticker_a, ticker_history_a[-80:],
    #                                                     load_dmi_adx(ticker_a, ticker_history_a, module_config),
    #                                                     module_config, keys=['dmi+', 'dmi-', 'adx'],
    #                                                     colors=['green', 'red', 'blue']),
    #             "overlay": False
    #         },
    #         "s/r levels": {
    #             "plot": plot_sr_lines(ticker_a, ticker_history_a[-80:],
    #                                                     load_support_resistance(ticker_a, ticker_history_a, module_config, flatten=True),
    #                                                     module_config),
    #             "overlay": True
    #         }
    #
    #     }
    #     plot_ticker_with_indicators(ticker_a,ticker_history_a,indicator_dict, module_config)

    print(f"\nCompleted {module_config['position_type']} validation of ({','.join([f'${x}' for x in module_config['tickers']])}) in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")