import os
import time
import traceback

# from shapesimilarity import shape_similarity
# import matplotlib.pyplot as plt
import numpy as np
from statistics import mean

from tickers import load_ticker_symbol_by_id, load_ticker_history_by_id
from functions import execute_query, execute_update, timestamp_to_datetime, human_readable_datetime, \
    calculate_percentage
from history import load_ticker_history_db
from shape import compare_tickers_at_index


def load_profitable_line_matrix(connection,  module_config):
    #load the profitable line matrix
    execute_update(connection, f"SET SESSION group_concat_max_len = 100000000",auto_commit=True)
    # rows = execute_query(connection, f"select pl.id, forward_range, backward_range, profit_percentage,plt.id line_type_id,plt.name line_type_name,count(distinct plh.tickerhistory_id) matches ,group_concat(concat(th.ticker_id,':',plh.tickerhistory_id) separator ',') ticker_histories from lines_profitableline pl, (select profitableline_id, max(tickerhistory_id) tickerhistory_id from lines_profitableline_histories  group by profitableline_id) plh,history_tickerhistory th, lines_profitablelinetype plt  where  plt.id =pl.line_type_id and th.id=plh.tickerhistory_id and plh.profitableline_id = pl.id and th.timespan='{module_config['timespan']}' and th.timespan_multiplier='{module_config['timespan_multiplier']}' GROUP by pl.id, forward_range, backward_range, profit_percentage,plt.id,plt.name")
    rows = execute_query(connection, f"select pl.id, forward_range, backward_range, profit_percentage,plt.id line_type_id,plt.name line_type_name,count(distinct plh.tickerhistory_id) matches ,group_concat(concat(th.ticker_id,':',t.symbol,':',th.timestamp,':',plh.tickerhistory_id) separator ',') ticker_histories from lines_profitableline pl,tickers_ticker t , (select profitableline_id, max(tickerhistory_id) tickerhistory_id from lines_profitableline_histories  group by profitableline_id) plh,history_tickerhistory th, lines_profitablelinetype plt  where t.id=th.ticker_id and plt.id =pl.line_type_id and th.id=plh.tickerhistory_id and plh.profitableline_id = pl.id and th.timespan='{module_config['timespan']}' and th.timespan_multiplier='{module_config['timespan_multiplier']}' GROUP by pl.id, forward_range, backward_range, profit_percentage,plt.id,plt.name")

    results = {}
    for i in range(1, len(rows)):
        # if int(rows[i][rows[0].index('matches')])  < 100: #basically skip any that we've found that aren't really relevant yet
        #     continue
        try:
            results[rows[i][rows[0].index('line_type_name')]] = {
                "profit": int(float(rows[i][rows[0].index('profit_percentage')])),
                "matches" :[{x.split(":")[-1]:x.split(":")[0]} for x in rows[i][rows[0].index('ticker_histories')].split(',')],
                'symbol': [x.split(":")[1] for x in rows[i][rows[0].index('ticker_histories')].split(',')][0],
                'timestamp': [x.split(":")[2] for x in rows[i][rows[0].index('ticker_histories')].split(',')][0],
                "forward_range": int(float(rows[i][rows[0].index('forward_range')])),
                "backward_range": int(float(rows[i][rows[0].index('backward_range')]))
            }
        except:
            traceback.print_exc()
            print(f"Cannot load profitable line matrix entry {rows[i]}")
            raise  Exception(f"Cannot load profitable line matrix entry {rows[i]}")

        pass
    return results
def update_ticker_profitable_lines(connection,profitable_line,ticker, ticker_history, profitable_lines, module_config):

    matches = []
    for indexes in profitable_lines.values():
        for index in indexes:
            if index not in matches:
                matches.append(index)
    #ok so lock the rows first
    execute_query(connection, f"select * from lines_profitableline_histories where profitableline_id = (select id from lines_profitableline where line_type_id=(select id from lines_profitablelinetype where name='{profitable_line}'))", verbose=True)
    for index in matches:
        execute_update( connection, f"insert ignore into lines_profitableline_histories (profitableline_id, tickerhistory_id) values ((select id from lines_profitableline where line_type_id=(select id from lines_profitablelinetype where name='{profitable_line}')),(select id from history_tickerhistory where timestamp={ticker_history[index].timestamp} and timespan='{module_config['timespan']}' and timespan_multiplier='{module_config['timespan_multiplier']}' and ticker_id=(select id from tickers_ticker where symbol='{ticker}')))", verbose=True, auto_commit=False)
    connection.commit()
def write_ticker_profitable_lines(connection, ticker, ticker_history, profitable_lines, module_config):
    #ok so the idea where is that we write the line first and then
    for profit_percentage, indexes in profitable_lines.items():
        if len(indexes) >= module_config['line_profit_minimum_matches']:
            new_line_str = f"Profitable Line {str(time.time()).split('.')[0]}{os.getpid()}"
            execute_query(connection, f"select * from lines_profitablelinetype where name='{new_line_str}' ")
            execute_update(connection, sql=f"insert ignore into lines_profitablelinetype (name) values ('{new_line_str}')", auto_commit=True, verbose=True)
            execute_query(connection, "select * from lines_profitableline")

            execute_update(connection, sql=f"insert ignore into lines_profitableline (line_type_id, forward_range, backward_range, profit_percentage) values ((select id from lines_profitablelinetype where name='{new_line_str}' ),{module_config['line_profit_forward_range']},{module_config['line_profit_backward_range']},{profit_percentage})", auto_commit=True, verbose=False)

            execute_query(connection,f"select * from lines_profitableline_histories where profitableline_id = (select id from lines_profitableline where line_type_id=(select id from lines_profitablelinetype where name='{new_line_str}'))",verbose=True)

            for index in indexes:
                execute_update(connection,f"insert ignore into lines_profitableline_histories (profitableline_id, tickerhistory_id) values ((select id from lines_profitableline where forward_range={module_config['line_profit_forward_range']} and backward_range={module_config['line_profit_backward_range']} and profit_percentage={profit_percentage}), (select id from history_tickerhistory where timespan='{module_config['timespan']}' and timespan_multiplier='{module_config['timespan_multiplier']}' and timestamp={ticker_history[index].timestamp} and ticker_id=(select id from tickers_ticker where symbol='{ticker}')))",auto_commit=False, verbose=False)
            connection.commit()
            time.sleep(1)
    pass
    connection.commit()

def compare_profitable_ticker_lines_to_market(connection,ticker, ticker_history, module_config, read_only=True):
    '''
    ok so basically if we set read only we just return the matching profitable line, None if not
    :param connection:
    :param ticker:
    :param ticker_history:
    :param module_config:
    :param read_only:
    :return:
    '''
    # /find_ticker_profitable_lines(ticker, load_ticker_history_db(ticker, module_config, connection=connection), module_config)
    pass
    ticker_profitable_lines = find_ticker_profitable_lines(ticker, ticker_history,module_config)
    profitable_line_matrix = load_profitable_line_matrix(connection, module_config)
    pass
    loaded_histories ={}
    #ok so the idea here is now to iterate over the genereated profitable lines of the ticker to the profitable lines of the market
    for profit, indexes in ticker_profitable_lines.items():
        positive_profit = profit >=0
        matches = {}#keys of percentage matched vs the name of the line matched
        profits = {}
        #basically we can just compare the first to the first for now
        for line, line_data in profitable_line_matrix.items():
            positive_line_data_profit = line_data['profit'] >= 0
            #so here we load the ticker histroy
            if positive_profit != positive_line_data_profit:
                print(f"Skipping Historic Profit Line of {line_data['profit']}%, the trend is in the opposite direction of profit {profit}%")
                continue
            try:
                # compare_ticker = load_ticker_symbol_by_id(connection, [x for x in line_data['matches'][0].values()][0], module_config)
                compare_ticker = line_data['symbol']
            except:
                traceback.print_exc()
                print()
                raise Exception
            if compare_ticker not in loaded_histories:

                loaded_histories[compare_ticker]=load_ticker_history_db(compare_ticker, module_config, connection=connection)
            #ok so now we need to load the ticker history entry at the matching id
            # history_entry = load_ticker_history_by_id(connection, [x for x in line_data['matches'][0].keys()][0],compare_ticker, module_config)
            history_entry = [x for x in loaded_histories[compare_ticker] if x.timestamp == int(line_data['timestamp'])][0]
            compare_index = next((i for i, item in enumerate(loaded_histories[compare_ticker]) if item.timestamp == history_entry.timestamp), -1)

            try:
                if len(ticker_history[0:indexes[0]]) >= module_config['line_profit_backward_range'] and len(loaded_histories[compare_ticker]) >= module_config['line_profit_backward_range']:
                    match_likelihood = compare_tickers_at_index(compare_index, ticker, ticker_history[0:indexes[0]], compare_ticker, loaded_histories[compare_ticker], module_config)
                    matches[match_likelihood] = line
                    # profits[match_likelihood]= line_data['profit']

            except:
                # traceback.print_exc()
                # print(f"Cannot calculate shape similarity between {ticker} (size: {len(ticker_history[0:indexes[0]])}) and {compare_ticker} (size: {len(loaded_histories[compare_ticker])}), not enough historical bars ")
                continue

        valid_matches = [x for x in matches.keys() if x > module_config['line_similarity_gt']]
        if len(valid_matches) > 0:
            #if we have more than one, we use the most accurate
            # def write_ticker_profitable_lines(connection, ticker, ticker_history, profitable_lines, module_config):
            if not read_only:
                print(f"Updating ticker lines for {matches[max(valid_matches)]}")
                update_ticker_profitable_lines(connection, matches[max(valid_matches)], ticker, ticker_history, {profit:indexes}, module_config)
            return
            pass
        else: #otherwise we need to write the profitable lines for the ticker itself
            if not read_only:
                write_ticker_profitable_lines(connection, ticker, ticker_history, {profit:indexes}, module_config)
            pass
            #ok so once we're here, we can calculate the similarity at the index
            #the challenge is finding the index of the ticker history
        pass
def find_ticker_profitable_lines(ticker, ticker_history,  module_config):
    #ok so the idea here is to re-use some of the reverse loookback logic in the backtester to interate through the ticker history
    #to within the line_profit_backward_range to then determine the profitability at the forward range
    if len(ticker_history) < module_config['line_profit_backward_range']:
        raise Exception(f"Cannot backtest ticker with {len(ticker_history)} history records, need at least {module_config['line_profit_backward_range']}")
    _module_config = module_config
    _module_config['shape_bars']=module_config['line_profit_backward_range']
    backtest_results = {}
    # start x bars in the past so we can do our forward looking
    potential_profitable_lines = {}
    for i in reversed(range(_module_config['line_profit_backward_range'], len(ticker_history)-_module_config['line_profit_forward_range'])):
        i = i * -1 #dumb lol
        profitability = determine_line_profitability(ticker, ticker_history

                                                     , i, _module_config)
        if profitability  >= _module_config['line_profit_minimum'] or profitability <= _module_config['line_profit_minimum']*-1:
            #todo write the profitz hurr
            # print(f"Found profitable line on {ticker}:{human_readable_datetime(timestamp_to_datetime(ticker_history[i].timestamp))}: Profit Percentage: {profitability}")
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