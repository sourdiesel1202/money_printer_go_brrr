import traceback

from shapesimilarity import shape_similarity
# import matplotlib.pyplot as plt
import numpy as np
from statistics import mean
from functions import timestamp_to_datetime, human_readable_datetime
from functions import calculate_percentage
def compare_tickers(ticker_a, ticker_history_a,ticker_b, ticker_history_b, module_config):
    return determine_line_similarity(**format_ticker_data(ticker_a, ticker_history_a,ticker_b, ticker_history_b, module_config))


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
        raise Exception(f"Cannot calculate shape similarity between {ticker_a} (size: {len(ticker_history_a)}) and {ticker_b} (size: {len(ticker_history_b)}), not enough historical bars ")

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
                matches['timestamps'].append(ticker_history_b[-i].timestamp)

    return  matches
def determine_line_similarity(ticker_a=[], ticker_b=[], timestamps=[]):
    xs = [i for i in range(0, len(timestamps))]
    shape1 = np.column_stack((np.array(xs), np.array(ticker_a)))
    shape2 = np.column_stack((np.array(xs), np.array(ticker_b)))

    # similarity =
    return shape_similarity(shape1, shape2,checkRotation=False)
    # pass



def find_ticker_profitable_lines(ticker, ticker_history,  module_config):
    #ok so the idea here is to re-use some of the reverse loookback logic in the backtester to interate through the ticker history
    #to within the line_profit_backward_range to then determine the profitability at the forward range
    if len(ticker_history) < 20:
        raise Exception(f"Cannot backtest ticker with {len(ticker_history)} history records, need at least 20")

    backtest_results = {}
    # start ten bars in the past so we can do our forward looking
    potential_profitable_lines = {}
    for i in reversed(range(10, len(ticker_history)-10)):
        i = i * -1 #dumb lol
        profitability = determine_line_profitability(ticker, ticker_history

                                                     , i, module_config)
        if profitability  >= module_config['line_profit_minimum'] or profitability <= module_config['line_profit_minimum']*-1:
            #todo write the profitz hurr
            print(f"Found profitable line on {ticker}:{human_readable_datetime(timestamp_to_datetime(ticker_history[i].timestamp))}: Profit Percentage: {profitability}")
            if int(profitability) not in potential_profitable_lines:

                potential_profitable_lines[int(profitability)] = []
            potential_profitable_lines[int(profitability)].append(i)

    # positive_lines = []
    # negative_lines = []
    profitable_lines =  {}

    #ok so now that we'
    # re here, we need to compare each profitable line to the others to see if they have a similar shape
    # internal_matches = {}
    for percentage, intervals in potential_profitable_lines.items():
        #ok so the idea here is to iterate through each interval found and validate
        for interval in intervals:
            matched_inverse = False  # check for a match in an inverse case
            profits = [percentage]
            positive = percentage > 0
            for _percentage, _intervals in potential_profitable_lines.items():
                _positive = _percentage > 0
                if interval in _intervals:
                    if _positive != positive:
                        matched_inverse = True

                    if _percentage not in profits:
                        profits.append(_percentage)
                if not matched_inverse:
                    avg = int(mean(profits))
                    if avg not in profitable_lines:
                        profitable_lines[avg]= []
                    if interval not in profitable_lines[avg]:
                        profitable_lines[avg].append(interval)
    #ok so once we're here we need to do one final pass to clearn everything up
    return profitable_lines
    # print()
    # for percentage, intervals in potential_profitable_lines.items():
    #     #ok so the idea here is to iterate through each interval found and validate
    #     for interval in intervals:
    #         percentages = [key for key, value in profitable_lines.items() if interval in value]

        #1. does it appear in any line matches that  are the inverse
        #2. if not get the average profitability
    #     if percentage not in internal_matches:
    #         internal_matches[percentage] = {}
    #     for interval in intervals:
    #         #blah this is going to be complicated
    #         for second_pass_intervals in potential_profitable_lines.values():
    #             for second_pass_interval in second_pass_intervals:
    #                 if second_pass_interval == interval:
    #                     continue #ignore itself
    #                 else:
    #                     # compare_tickers(ticker_a, ticker_history_a, ticker_b, ticker_history_b, module_config):
    #                     try:
    #                         if compare_tickers(ticker, ticker_history[:interval], ticker, ticker_history[:second_pass_interval], module_config) > module_config['line_similarity_gt']:
    #                             if interval not in internal_matches[percentage]:
    #                                 internal_matches[percentage][interval] = []#{"similar_intervals":[], }
    #                             internal_matches[percentage][interval].append(second_pass_interval)
    #                     except:
    #                         traceback.print_exc()
    #                         continue
    #             pass
    # overall_matches = {}
    # for percentage, intervals in internal_matches.items():
    #     for interval, _interval_matches in intervals.items():
    #         matched = False
    #         for key, match_list in overall_matches.items():
    #
    #             if interval in match_list:
    #                 #if we have a match, we
    #                 for im in _interval_matches:
    #                     if im not in overall_matches[key]:
    #                         overall_matches[key].append(im)
    #                 matched = True
    #         if not matched:
    #             overall_matches[interval] =_interval_matches
    # for percentage, intervals in internal_matches.items():
    #     for interval, _interval_matches in intervals.items():
    #         matched = False
    #         for key, match_list in overall_matches.items():
    #
    #             if interval in match_list:
    #                 # if we have a match, we
    #                 for im in _interval_matches:
    #                     if im not in overall_matches[key]:
    #                         overall_matches[key].append(im)
    #                 matched = True
    #         if not matched:
    #             overall_matches[interval] = _interval_matches
                    # overall_matches[key]
    pass
    # pass
def determine_line_profitability(ticker, ticker_history, index, module_config):
    '''
    Use this functino to determine the profitability of a line, pass in a starting index and a forward range,the forward range
    being the range we compare to the index to determine profit. Profitability is calculated as a percentage of the underlying
    This function requires the following module configs:

    line_profit_minimum- the profit percentage (+/-) we need to exceed to write this to the DB as a profitable line
    line_profit_forward_range
    line_profit_backward_range
    :param ticker:
    :param ticker_history:
    :param forward_range:
    :param index:
    :param module_config:
    :return:
    '''
    # pass
    # return 1
    #ok so the idea here is to compare the history[index] to hisory[index+forward_range] and calculate the percentage
    return calculate_percentage(ticker_history[index+module_config['line_profit_forward_range']].close-ticker_history[index].close, ticker_history[index].close )


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