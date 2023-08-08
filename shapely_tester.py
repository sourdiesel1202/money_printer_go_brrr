import math
import time
import traceback

import numpy as np
# from enums import AlertType, PositionType
# from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime
from shapesimilarity import procrustes_normalize_curve, curve_length

from db_functions import load_nyse_tickers
# from db_functions import write_ticker_profitable_lines,load_profitable_line_matrix
from history import load_ticker_history_raw, load_ticker_history_db, load_ticker_history_cached
# from validation import validate_ticker
from functions import load_module_config, get_today, obtain_db_connection, process_list_concurrently
from indicators import did_profitable_lines_alert, determine_profitable_lines_alert_type, load_profitable_lines
from profitable_lines import compare_profitable_ticker_lines_to_market, load_profitable_line_matrix, dump_profitable_line_cache
from shape import  determine_line_similarity
from shapely import LineString, frechet_distance

# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])

# from shape import compare_tickers
# def compare_tickers_lines_to_market(tickers):
#     # module_config = load_module_config('profitable_line_scanner_db')
#     # tickers = load_nyse_tickers(connection, module_config)
#     module_config = load_module_config('profitable_line_scanner_db')
#     connection = obtain_db_connection(module_config)
#     for ticker in tickers:
#         try:
#             print(f"Loading profitable lines for {tickers.index(ticker)+1}/{len(tickers)}: {ticker}")
#             # profitable_lines = find_ticker_profitable_lines(ticker, load_ticker_history_db(ticker, module_config, connection=connection), module_config)
#
#
#             # def write_profitable_lines(connection, ticker, ticker_history, profitable_lines, module_config):
#             # write_ticker_profitable_lines(connection, ticker, load_ticker_history_db(ticker, module_config, connection=connection),profitable_lines,module_config)
#             # load_ticker_history_db(ticker, module_config, connection=connection)
#             # load_profitable_line_matrix(connection, module_config)
#             compare_profitable_ticker_lines_to_market(connection,ticker, load_ticker_history_db(ticker, module_config, connection=connection), module_config, read_only=False)
#             print(f"Loaded profitable lines for {tickers.index(ticker)+1}/{len(tickers)}: {ticker}")
#         except:
#             print(f"Could not find profitable lines for {ticker}")
#             traceback.print_exc()
#     connection.close()

# def compare_tickers(ticker_a, ticker_history_a,ticker_b, ticker_history_b, module_config):
#     return determine_line_similarity(ticker_history_a,ticker_history_b,module_config)
    # return determine_line_similarity(**format_ticker_data(ticker_a, ticker_history_a,ticker_b, ticker_history_b, module_config))
def _determine_line_similarity(ticker_history_a,ticker_history_b,module_config):
    y1s = [x.close for x in ticker_history_a[module_config['shape_bars'] * -1:]]
    xs=  [i for i in range(0, module_config['shape_bars'])]
    y2s = [x.close for x in ticker_history_b[module_config['shape_bars'] * -1:]]
    ticker_a_line = LineString([[xs[i], y1s[i]] for i in range(0, len(xs))])
    ticker_b_line = LineString([[xs[i], y2s[i]] for i in range(0, len(xs))])
    f= frechet_distance(ticker_a_line, ticker_b_line)
    x = np.linspace(1, -1, num=module_config['shape_bars'])
    shape1 = np.column_stack((x, [x.close for x in reversed(ticker_history_a[module_config['shape_bars'] * -1:])]))
    shape2 = np.column_stack((x, [x.close for x in reversed(ticker_history_b[module_config['shape_bars'] * -1:])]))
    procrustes_normalized_curve1 = procrustes_normalize_curve(shape1)
    procrustes_normalized_curve2 = procrustes_normalize_curve(shape2)
    geo_avg_curve_len = math.sqrt(
        curve_length(procrustes_normalized_curve1) *
        curve_length(procrustes_normalized_curve2)
    )
    return max(1 - f / (geo_avg_curve_len / math.sqrt(2)), 0)


    pass
    # for i in range()
    # line1 = LineString([[i, ]])
# def process_ticker_manipulation(tickers):
#     module_config = load_module_config('profitable_line_scanner_db')
#     alerts = []
#     index=-1
#     while len(alerts)== 0:
#         for ticker in tickers:
#             ticker_history = load_ticker_history_cached(ticker, module_config)
#             indicator_data = load_profitable_lines(ticker, ticker_history, module_config, connection=None)
#             alerted = did_profitable_lines_alert(indicator_data, ticker, ticker_history, module_config, connection=None)
#             # th = ticker_history[-180:-1]
#             print(f"Checking ${ticker} history at index -1: {ticker_history[index].dt}")
#             # alerted = did_profitable_lines_alert(indicator_data, ticker, th, module_config, connection=connection )
#             if alerted:
#                 alerts.append(
#                     f'{ticker} {ticker_history[index].dt}:' + determine_profitable_lines_alert_type(indicator_data, ticker,
#                                                                                                  ticker_history, module_config,
#                                                                                                  connection=None ))
#                 # print(f'')
#
#                 print(f"${ticker} did alert :) {ticker_history[index].dt}:{alerts[-1]}")
#         index = index-1

if __name__ == '__main__':
    # def load_ticker_history_db(ticker, module_config, connection=None):
    start_time = time.time()
    module_config = load_module_config('profitable_line_scanner_db')
    connection = obtain_db_connection(module_config)
    alerts = []
    index= -1
    for ticker in module_config['tickers']:
        ticker_history = load_ticker_history_cached(ticker, module_config)
        # indicator_data = load_profitable_lines(ticker, ticker_history, module_config, connection=None)
        # alerted = did_profitable_lines_alert(indicator_data, ticker, ticker_history, module_config, connection=None)
        # th = ticker_history[-180:-1]
        print(f"Checking ${ticker} history at index -1: {ticker_history[index].dt}")
        determine_line_similarity(ticker_history, load_ticker_history_cached("FFIE", module_config)[:-1], module_config)
        # print(f"${ticker} did alert :) {ticker_history[index].dt}:{alerts[-1]}")

    #
    # alerts=  []
    # try:
    # dump_profitable_line_cache(connection, module_config)
    # process_list_concurrently(module_config['tickers'], process_ticker_manipulation,int(len(module_config['tickers'])/12)+1)


    # connection.close()

    print(f"\nCompleted Profitable Line test of {len(module_config['tickers'])} tickers in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")