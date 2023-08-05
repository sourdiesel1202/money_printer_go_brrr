import time
import traceback

# from enums import AlertType, PositionType
# from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime

from db_functions import load_nyse_tickers
# from db_functions import write_ticker_profitable_lines,load_profitable_line_matrix
from history import load_ticker_history_raw, load_ticker_history_cached
# from validation import validate_ticker
from functions import load_module_config, get_today, obtain_db_connection
from profitable_lines import  compare_profitable_ticker_lines_to_market

# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
module_config = load_module_config('profitable_line_scanner_db')
# from shape import compare_tickers

if __name__ == '__main__':
    # def load_ticker_history_cached(ticker, module_config, connection=None):
    start_time = time.time()

    connection = obtain_db_connection(module_config)
    tickers = load_nyse_tickers(connection, module_config)
    for ticker in tickers:
        try:
            print(f"Loading profitable lines for {tickers.index(ticker)+1}/{len(tickers)}: {ticker}")
            # profitable_lines = find_ticker_profitable_lines(ticker, load_ticker_history_cached(ticker, module_config, connection=connection), module_config)


            # def write_profitable_lines(connection, ticker, ticker_history, profitable_lines, module_config):
            # write_ticker_profitable_lines(connection, ticker, load_ticker_history_cached(ticker, module_config, connection=connection),profitable_lines,module_config)
            # load_ticker_history_cached(ticker, module_config, connection=connection)
            # load_profitable_line_matrix(connection, module_config)
            compare_profitable_ticker_lines_to_market(connection,ticker, load_ticker_history_cached(ticker, module_config, connection=connection), module_config)
            print(f"Loaded profitable lines for {tickers.index(ticker)+1}/{len(tickers)}: {ticker}")
        except:
            print(f"Could not find profitable lines for {ticker}")
            traceback.print_exc()
    connection.close()
    print(f"\nCompleted Profitable Line test of ({','.join([f'${x}' for x in module_config['tickers']])}) in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")