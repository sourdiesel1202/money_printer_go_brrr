import time
from enums import AlertType, PositionType, PriceGoalChangeType
from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime

from history import load_ticker_history_raw, load_ticker_history_cached
from validation import validate_ticker
from functions import load_module_config, get_today
# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
module_config = load_module_config('market_scanner_tester')
from options import calculate_price_change_for_entry,calculate_dte, calculate_price_change_for_exit

from pricing import determine_entry_target, determine_exit_target
'''

Use this to create options_tester.json in configs/



{
  "asset_price": 14.98,
  "position_type": "LONG",
  "ask": 0.39,
  "strike_price": 15,
  "ticker": "F",
  "expiration_date": "2023-07-28",
  "bid_price_goal_type": "ASSET_SET_PRICE",
  "ask_price_gol_type": "ASSET_SET_PRICE",
  "bid_price_goal": 14.98,
  "ask_price_goal": 14.98

}

'''

def print_options_result(options_result, module_config):
    pass


def run_pricing_test(test_positions, module_config):
    for position_type, positions in test_positions.items():
        print(f"## Testing {position_type} positions\n")

        i = 1
        for position in positions:
            if 'PERCENT' in position['bid_price_goal_type']:
                bid_price_string = f"{position['bid_price_goal']}%"
            else:
                bid_price_string = f"${position['bid_price_goal']}"

            if 'PERCENT' in position['ask_price_goal_type']:
                ask_price_string = f"{position['ask_price_goal']}%"
            else:
                ask_price_string = f"${position['ask_price_goal']}"
            #ok so we enter the position first
            print(f"\n#### TESTING POSITION {i}/{len(positions)} (ENTRY)\n Targets for {position_type} position ({PositionType.LONG_OPTION if position_type == PositionType.LONG else PositionType.SHORT_OPTION}) in $({module_config['tickers'][0]}): current asset price: ${module_config['asset_price']}: we suggest entering the position at the following asset price: ${determine_entry_target(position_type, module_config['tickers'][0],load_ticker_history_cached(module_config['tickers'][0], module_config), module_config)} \n")

            print(f"\n#### TESTING POSITION {i}/{len(positions)} (EXIT)\n Targets for {position_type} position ({PositionType.LONG_OPTION if position_type == PositionType.LONG else PositionType.SHORT_OPTION}) in $({module_config['tickers'][0]}): current asset price: ${module_config['asset_price']}: we suggest exiting the position at the following asset price: ${determine_exit_target(position_type,69.69, module_config['tickers'][0], load_ticker_history_cached(module_config['tickers'][0], module_config), module_config)} \n")
            # print
            # result = calculate_price_change_for_entry(position['bid_price_goal_type'], position_type,
            #                                          module_config['asset_price'], module_config['strike_price'],
            #                                          position['bid_price_goal'], module_config['ask'],
            #                                          calculate_dte(module_config['expiration_date']))
            # print('```')
            # print('\n'.join([f"{k}: {v}" for k, v in result.items()]))
            # # i = i+1
            # print('```\n')

            # print(f"\n#### TESTING POSITION {i}/{len(positions)} (EXIT)\n In order to exit a {position_type} position ({PositionType.LONG_OPTION if position_type == PositionType.LONG else PositionType.SHORT_OPTION}) in $({module_config['ticker']})  with goal {position['ask_price_goal_type']} of {ask_price_string} (current ask: {module_config['ask']}, current asset price: {module_config['asset_price']}), the following price change needs to occur\n")
            # # result = calculate_price_change_for_exit(position['ask_price_goal_type'], position_type,
            # #                                           module_config['asset_price'], module_config['strike_price'],
            # #                                           position['ask_price_goal'], module_config['ask'],
            # #                                           calculate_dte(module_config['expiration_date']))
            # print('```')
            # print('\n'.join([f"{k}: {v}" for k, v in result.items()]))
            i = i + 1
            print('```\n')
    pass
if __name__ == '__main__':
    start_time = time.time()

    #doing this with $15 F calls for 07/28
    test_positions = {
        PositionType.SHORT:[
            {"bid_price_goal_type": PriceGoalChangeType.ASSET_SET_PRICE,"ask_price_goal_type": PriceGoalChangeType.OPTION_PERCENTAGE, "bid_price_goal": 15.05, "ask_price_goal": 20},
            # {"bid_price_goal_type": PriceGoalChangeType.ASSET_PERCENTAGE,"ask_price_goal_type": PriceGoalChangeType.ASSET_PERCENTAGE, "bid_price_goal": 0.6, "ask_price_goal": 0.8},
            # {"ask_price_goal_type": PriceGoalChangeType.OPTION_SET_PRICE,"bid_price_goal_type": PriceGoalChangeType.OPTION_SET_PRICE, "bid_price_goal": 0.35, "ask_price_goal": 0.45},
            # {"ask_price_goal_type": PriceGoalChangeType.OPTION_TICK,"bid_price_goal_type": PriceGoalChangeType.OPTION_TICK, "bid_price_goal": 0.05, "ask_price_goal": 0.15},
            # {"ask_price_goal_type": PriceGoalChangeType.OPTION_PERCENTAGE,"bid_price_goal_type": PriceGoalChangeType.OPTION_PERCENTAGE, "bid_price_goal": 10, "ask_price_goal": 15}

        ],
        PositionType.LONG:[
            {"bid_price_goal_type": PriceGoalChangeType.ASSET_SET_PRICE,"ask_price_goal_type": PriceGoalChangeType.OPTION_PERCENTAGE, "bid_price_goal": 14.88, "ask_price_goal": 20},
            # {"bid_price_goal_type": PriceGoalChangeType.ASSET_PERCENTAGE,"ask_price_goal_type": PriceGoalChangeType.ASSET_PERCENTAGE, "bid_price_goal": 0.6, "ask_price_goal": 0.8},
            # {"ask_price_goal_type": PriceGoalChangeType.OPTION_SET_PRICE,"bid_price_goal_type": PriceGoalChangeType.OPTION_SET_PRICE, "bid_price_goal": 0.35, "ask_price_goal": 0.45},
            # {"ask_price_goal_type": PriceGoalChangeType.OPTION_TICK,"bid_price_goal_type": PriceGoalChangeType.OPTION_TICK, "bid_price_goal": 0.05, "ask_price_goal": 0.15},
            # {"ask_price_goal_type": PriceGoalChangeType.OPTION_PERCENTAGE,"bid_price_goal_type": PriceGoalChangeType.OPTION_PERCENTAGE, "bid_price_goal": 10, "ask_price_goal": 15}
        ]
    }
    # def calculate_price_change_for_entry(asset_price, position_type,strike_price, bid_price_goal, ask,  dte):
    # print('\n'.join([f"{k}: {v}" for k,v in module_config.items()]))

    run_pricing_test(test_positions, module_config)

    # we can call the same fn but use the data from module config
    # real_positions ={
    #     module_config['position_type']:[
    #         {"bid_price_goal_type": module_config['bid_price_goal_type'],"ask_price_goal_type": module_config['ask_price_goal_type'], "bid_price_goal": module_config['bid_price_goal'], "ask_price_goal": module_config['ask_price_goal']},
    #     ]
    # }
    # run_pricing_test(test_positions if module_config['test_mode'] else real_positions, module_config)




    print(f"\nCompleted testing  of ({module_config['tickers'][0]}) in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")