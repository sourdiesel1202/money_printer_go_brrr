import time
import traceback

# from enums import AlertType, PositionType
# from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime

from db_functions import load_nyse_tickers
# from db_functions import write_ticker_profitable_lines,load_profitable_line_matrix
from history import load_ticker_history_raw, load_ticker_history_db, load_ticker_history_cached
# from validation import validate_ticker
from functions import load_module_config, get_today, obtain_db_connection, process_list_concurrently, execute_query
# from indicators import did_profitable_lines_alert, determine_profitable_lines_alert_type, load_profitable_lines
from profitable_lines import compare_profitable_ticker_lines_to_market, load_profitable_line_matrix, dump_profitable_line_cache
from shape import compare_tickers
from shape import determine_line_similarity


def validate_profitable_line(line_data):
    pass
def load_profitable_line_records(connection):
    # sql =
    return execute_query(connection, f"select pl.*, plt.name from lines_profitableline pl, lines_profitablelinetype plt where plt.id=pl.line_type_id")

if __name__ == '__main__':
    # def load_ticker_history_db(ticker, module_config, connection=None):
    start_time = time.time()
    module_config = load_module_config('profitable_line_scanner_db')
    connection = obtain_db_connection(module_config)
    profitable_lines = load_profitable_line_records(connection)
    try:
        for i in range(1, len(profitable_lines)):
            line_id = profitable_lines[i][profitable_lines[0].index('id')]
            line_entries =execute_query(connection, f"select * from (select pl.*, t.symbol, plh.tickerhistory_id, th.timestamp, from_unixtime(th.timestamp/1000) hr_date from lines_profitableline_histories plh, lines_profitableline pl, tickers_ticker t, history_tickerhistory th, lines_profitablelinetype plt where pl.id=plh.profitableline_id and  th.ticker_id =t.id and plh.tickerhistory_id=th.id and plt.id=pl.line_type_id and plt.id='{line_id}') line_aggs order by line_aggs.timestamp desc")
            _keys = [x for x in line_entries]
            n = module_config['num_processes']
            loads = [_keys[i:i + n] for i in range(0, len(_keys), n)]
            pass
    except:
        pass

    connection.close()

    print(f"\nCompleted Profitable Line test of {len(module_config['tickers'])} tickers in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")