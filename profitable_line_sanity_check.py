import time
import traceback

# from enums import AlertType, PositionType
# from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime

from db_functions import load_nyse_tickers
# from db_functions import write_ticker_profitable_lines,load_profitable_line_matrix
from history import load_ticker_history_raw, load_ticker_history_db, load_ticker_history_cached
# from validation import validate_ticker
from functions import load_module_config, get_today, obtain_db_connection, process_list_concurrently
from indicators import did_profitable_lines_alert, determine_profitable_lines_alert_type, load_profitable_lines
from profitable_lines import compare_profitable_ticker_lines_to_market, load_profitable_line_matrix, dump_profitable_line_cache
from shape import compare_tickers
from shape import determine_line_similarity

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

def process_ticker_manipulation(tickers):
    module_config = load_module_config('profitable_line_scanner_db')
    alerts = []
    index=-1
    while len(alerts)== 0:
        for ticker in tickers:
            ticker_history = load_ticker_history_cached(ticker, module_config)[:-170]
            indicator_data = load_profitable_lines(ticker, ticker_history, module_config, connection=None)
            print(f"Fuck Checking ${ticker} history at index -1: {ticker_history[index].dt}:")
            alerted = did_profitable_lines_alert(indicator_data, ticker, ticker_history, module_config, connection=None)
            # th = ticker_history[-180:-1]
            # alerted = did_profitable_lines_alert(indicator_data, ticker, th, module_config, connection=connection )
            if alerted:
                alerts.append(
                    f'{ticker} {ticker_history[index].dt}:' + determine_profitable_lines_alert_type(indicator_data, ticker,
                                                                                                 ticker_history, module_config,
                                                                                                 connection=None ))
                # print(f'')

                print(f"${ticker} did alert :) {ticker_history[index].dt}:{alerts[-1]}")
        index = index-1

if __name__ == '__main__':
    # def load_ticker_history_db(ticker, module_config, connection=None):
    start_time = time.time()
    module_config = load_module_config('profitable_line_scanner_db')
    connection = obtain_db_connection(module_config)
    #
    # alerts=  []
    # try:
    dump_profitable_line_cache(connection, module_config)
    process_list_concurrently(module_config['tickers'], process_ticker_manipulation,int(len(module_config['tickers'])/12)+1)
    # process_list_concurrently(, process_ticker_manipulation,int(len(module_config['tickers'])/12)+1)
    # process_ticker_manipulation(module_config['tickers'])
    #     for ticker in module_config['tickers']:
    #         #ok so this is super dumb but here we go
    #
    #         #first, ensure the line is a match for itself
    #         # print(compare_tickers(ticker, load_ticker_history_db(ticker, module_config, connection=connection), ticker, load_ticker_history_db(ticker, module_config, connection=connection), module_config))
    #         # print(f"Compared {ticker} to itself using DB data")
    #         # print(compare_tickers(ticker, load_ticker_history_cached(ticker, module_config), ticker, load_ticker_history_cached(ticker, module_config), module_config))
    #         # print(f"Compared {ticker} to itself using cache data")
    #         # print(f"Attempting to find manipulated lines for {ticker}")
    #         ticker_history = load_ticker_history_cached(ticker, module_config)
    #         indicator_data = load_profitable_lines(ticker, ticker_history, module_config, connection=connection)
    #         alerted = did_profitable_lines_alert(indicator_data, ticker, ticker_history, module_config, connection=connection)
    #         # th = ticker_history[-180:-1]
    #         print(f"Checking ${ticker} history at index -1: {ticker_history[-1].dt}")
    #         # alerted = did_profitable_lines_alert(indicator_data, ticker, th, module_config, connection=connection )
    #         if alerted:
    #             alerts.append(f'{ticker} {ticker_history[-1].dt}:'+determine_profitable_lines_alert_type(indicator_data, ticker, ticker_history, module_config, connection=connection))
    #             # print(f'')
    #
    #             print(f"${ticker} did alert :) {ticker_history[-1].dt}:{alerts[-1]}")
    #         # for i in range(179, 250):
    #         #
    #         #     index = i*-1
    #         #     th = ticker_history[0:index]
    #         #     print(f"Checking ticker history at index {index}: {th[-1].dt}")
    #         #     alerted = did_profitable_lines_alert(indicator_data, ticker, th, module_config, connection=connection )
    #         #     if alerted:
    #         #         print(f'{ticker} did alert :)')
    #         #         print(f"{th[-1].dt}:{determine_profitable_lines_alert_type(indicator_data,ticker, ticker_history, module_config, connection=connection)}")
    # except:
    #     traceback.print_exc()
    #
    # print('\n'.join(alerts))
    # tickers = load_nyse_tickers(connection, module_config)
    #
    #
    # # def process_list_concurrently(data, process_function, batch_size):
    # # process_list_concurrently(tickers, compare_tickers_lines_to_market, int(len(tickers)/12)+1)
    # load_profitable_line_matrix(connection, module_config)
    connection.close()

    print(f"\nCompleted Profitable Line test of {len(module_config['tickers'])} tickers in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")