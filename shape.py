import time
import traceback

from shapesimilarity import shape_similarity
# import matplotlib.pyplot as plt
import numpy as np
from statistics import mean

# from db_functions import load_ticker_symbol_by_id, load_ticker_history_by_id
# from db_functions import load_profitable_line_matrix
from functions import timestamp_to_datetime, human_readable_datetime, execute_query, execute_update
# from functions import calculate_percentage
# from history import load_ticker_history_db



def compare_tickers(ticker_a, ticker_history_a,ticker_b, ticker_history_b, module_config):
    return determine_line_similarity(**format_ticker_data(ticker_a, ticker_history_a,ticker_b, ticker_history_b, module_config))

def compare_tickers_at_index(index, ticker_a, ticker_history_a,ticker_b, ticker_history_b, module_config):
    #ok just so we're clear on the idea here
    #basically just call compare_tickers but pre-filter the ticker history
    #and stub in the shape_bars for line_profit_backward_range
    _module_config = module_config
    _module_config['shape_bars'] = module_config['line_profit_backward_range']
    return compare_tickers(ticker_a, ticker_history_a, ticker_b, ticker_history_b[:index+1], module_config)















def format_ticker_data(ticker_a, ticker_history_a,ticker_b, ticker_history_b, module_config, ignore_timestamps=False):
    '''
    Ok so the idea here is that we need to format the ticker data in a way that is in line with the other ticker
    :param ticker:
    :param ticker_history:
    :param module_config:
    :return:
    '''
    matches= {"ticker_a":[], "ticker_b":[], "timestamps":[]}
    # a_timestamps = [x.timestamp for x in ticker_history_a]
    # b_timestamps = [x.timestamp for x in ticker_history_b]
    if len(ticker_history_a) < module_config['shape_bars'] or len(ticker_history_b) < module_config['shape_bars']:
        raise Exception(f"Cannot calculate shape similarity between {ticker_a} (size: {len(ticker_history_a)}) and {ticker_b} (size: {len(ticker_history_b)}), not enough historical bars for {module_config['shape_bars']} ")

    for i in range(1, module_config['shape_bars']):
        #only really care about n bars in the past, configured in module_config
        if not ignore_timestamps:
            if ticker_history_a[-i].timestamp == ticker_history_b[-i].timestamp:
                matches['ticker_a'].append(ticker_history_a[-i].close)
                matches['ticker_b'].append(ticker_history_b[-i].close)
                matches['timestamps'].append(ticker_history_b[-i].timestamp)
            else:
                matches['ticker_a'].append(ticker_history_a[-i].close)
                matches['ticker_b'].append(ticker_history_b[-i].close)
                matches['timestamps'].append(ticker_history_a[-i].timestamp)

    return  matches
def determine_line_similarity(ticker_a=[], ticker_b=[], timestamps=[]):


    # similarity =
    try:
        xs = [i for i in range(0, len(timestamps))]
        shape1 = np.column_stack((np.array(xs), np.array(ticker_a)))
        shape2 = np.column_stack((np.array(xs), np.array(ticker_b)))
        return shape_similarity(shape1, shape2,checkRotation=False)
    except Exception as e:
        raise e
    # pass



