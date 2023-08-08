import time

import numpy as np
# from enums import AlertType, PositionType
# from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime
from matplotlib import pyplot as plt
from shapesimilarity import shape_similarity

from history import load_ticker_history_raw, load_ticker_history_cached
# from validation import validate_ticker
from functions import load_module_config, get_today
# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
module_config = load_module_config('market_scanner')
from shape import compare_tickers

if __name__ == '__main__':
    start_time = time.time()
    # client = polygon.RESTClient(api_key=module_config['api_key'])


    # ticker = "GE"
    # ticker_b = module_config['compare_ticker']
    for ticker_a in module_config['tickers']:
        for ticker_b in module_config['compare_tickers']:
            ticker_history_a = load_ticker_history_cached(ticker_a,module_config)
            ticker_history_b = load_ticker_history_cached(ticker_b, module_config)


            # x = np.linspace(module_config['shape_bars'], 0, num=module_config['shape_bars'])
            x = np.linspace(1, -1, num=module_config['shape_bars'])

            # x = [x for x in ticker_history_a[module_config['shape_bars']*-1:]]
            # x = [x for x in range(0, module_config['shape_bars'])]
            # y1 = 2 * x ** 2 + 1
            # y2 = 2 * x ** 2 + 2

            shape1 = np.column_stack((x, [x.close for x in reversed(ticker_history_a[module_config['shape_bars']*-1:])]))
            shape2 = np.column_stack((x, [x.close for x in reversed(ticker_history_b[module_config['shape_bars']*-1:])]))

            similarity = shape_similarity(shape1, shape2, checkRotation=False)
            plt.plot(shape1[:, 0], shape1[:, 1], linewidth=2.0)
            plt.plot(shape2[:, 0], shape2[:, 1], linewidth=2.0)

            plt.title(f'Shape similarity between {ticker_b} and {ticker_a} is: {similarity}', fontsize=14, fontweight='bold')
            plt.show()
            pass
            # compare_tickers(ticker_a, ticker_history_a, ticker_b, ticker_history_b, module_config)
        # if module_config['run_concurrently']:
            # determine_line_similarity(1,2)
            # de(module_config['position_type'],ticker,ticker_history, module_config)
        # else:
            # determine_line_similarity(1, 2)
            # validate_ticker(module_config['position_type'],ticker,ticker_history, module_config)

    print(f"\nCompleted {module_config['position_type']} validation of ({','.join([f'${x}' for x in module_config['tickers']])}) in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")