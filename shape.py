from shapesimilarity import shape_similarity
# import matplotlib.pyplot as plt
import numpy as np
from functions import timestamp_to_datetime, human_readable_datetime
def compare_tickers(ticker_a, ticker_history_a,ticker_b, ticker_history_b, module_config):
    return determine_line_similarity(**format_ticker_data(ticker_a, ticker_history_a,ticker_b, ticker_history_b, module_config))


def format_ticker_data(ticker_a, ticker_history_a,ticker_b, ticker_history_b, module_config):
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
    for i in range(1, module_config['shape_bars']):
        #only really care about n bars in the past, configured in module_config
        if ticker_history_a[-i].timestamp == ticker_history_b[-i].timestamp:
            matches['ticker_a'].append(ticker_history_a[-i].close)
            matches['ticker_b'].append(ticker_history_b[-i].close)
            matches['timestamps'].append(ticker_history_b[-i].timestamp)
    return  matches
def determine_line_similarity(ticker_a=[], ticker_b=[], timestamps=[]):
    xs = [i for i in range(0, len(timestamps))]
    shape1 = np.column_stack((np.array(xs), np.array(ticker_a)))
    shape2 = np.column_stack((np.array(xs), np.array(ticker_b)))

    # similarity =
    return shape_similarity(shape1, shape2,checkRotation=False)
    # pass

# def determine_line_similarity(_x, _y):
#
#     x = np.linspace(1, -1, num=200)
#
#     y1 = 2*x**2 + 1
#     y2 = 2*x**2 + 2
#
#     shape1 = np.column_stack((x, y1))
#     shape2 = np.column_stack((x, y2))
#
#     similarity = shape_similarity(shape1, shape2,checkRotation=False)
#
#     # plt.plot(shape1[:,0], shape1[:,1], linewidth=2.0)
#     # plt.plot(shape2[:,0], shape2[:,1], linewidth=2.0)
#     #
#     # plt.title(f'Shape similarity is: {similarity}', fontsize=14, fontweight='bold')
#     # plt.show()