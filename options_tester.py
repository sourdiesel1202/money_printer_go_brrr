import time
from enums import AlertType, PositionType, PriceGoalChangeType
from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime

from history import load_ticker_history_raw
from validation import validate_ticker
from functions import load_module_config, get_today
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
from options import calculate_price_change_for_entry,calculate_dte, calculate_price_change_for_exit
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


def run_options_test(test_positions, module_config):
    for position_type, positions in test_positions.items():
        print(f"## Testing {position_type} positions\n")

        i = 1
        for position in positions:
            if 'PERCENT' in position['price_goal_type']:
                bid_price_string = f"{position['bid_price_goal']}%"
            else:
                bid_price_string = f"${position['bid_price_goal']}"

            if 'PERCENT' in position['price_goal_type']:
                ask_price_string = f"{position['ask_price_goal']}%"
            else:
                ask_price_string = f"${position['ask_price_goal']}"
            #ok so we enter the position first
            print(f"\n#### TESTING POSITION {i}/{len(positions)} (ENTRY)\n In order to enter a {position_type} position ({PositionType.LONG_OPTION if position_type == PositionType.LONG else PositionType.SHORT_OPTION}) in $({module_config['ticker']}) at bid price with goal {position['price_goal_type']} of {bid_price_string} (current ask: {module_config['ask']}, current asset price: {module_config['asset_price']}), the following price change needs to occur\n")
            result = calculate_price_change_for_entry(position['price_goal_type'], position_type,
                                                     module_config['asset_price'], module_config['strike_price'],
                                                     position['bid_price_goal'], module_config['ask'],
                                                     calculate_dte(module_config['expiration_date']))
            print('```')
            print('\n'.join([f"{k}: {v}" for k, v in result.items()]))
            # i = i+1
            print('```\n')

            print(f"\n#### TESTING POSITION {i}/{len(positions)}(EXIT)\n In order to exit a {position_type} position ({PositionType.LONG_OPTION if position_type == PositionType.LONG else PositionType.SHORT_OPTION}) in $({module_config['ticker']}) at bid price with goal {position['price_goal_type']} of {ask_price_string} (current ask: {module_config['ask']}, current asset price: {module_config['asset_price']}), the following price change needs to occur\n")
            result = calculate_price_change_for_exit(position['price_goal_type'], position_type,
                                                      module_config['asset_price'], module_config['strike_price'],
                                                      position['ask_price_goal'], module_config['ask'],
                                                      calculate_dte(module_config['expiration_date']))
            print('```')
            print('\n'.join([f"{k}: {v}" for k, v in result.items()]))
            i = i + 1
            print('```\n')
    pass
if __name__ == '__main__':
    start_time = time.time()

    test_positions = {
        PositionType.SHORT:[
            {"price_goal_type": PriceGoalChangeType.ASSET_SET_PRICE, "bid_price_goal": 15.05, "ask_price_goal": 14.82},
            {"price_goal_type": PriceGoalChangeType.ASSET_PERCENTAGE, "bid_price_goal": 0.6, "ask_price_goal": 0.8},
            {"price_goal_type": PriceGoalChangeType.OPTION_SET_PRICE, "bid_price_goal": 0.35, "ask_price_goal": 0.45},
            {"price_goal_type": PriceGoalChangeType.OPTION_TICK, "bid_price_goal": 0.05, "ask_price_goal": 0.15},
            {"price_goal_type": PriceGoalChangeType.OPTION_PERCENTAGE, "bid_price_goal": 10, "ask_price_goal": 15}

        ],
        PositionType.LONG:[
            {"price_goal_type": PriceGoalChangeType.ASSET_SET_PRICE, "bid_price_goal": 14.88, "ask_price_goal": 15.09},
            {"price_goal_type": PriceGoalChangeType.ASSET_PERCENTAGE, "bid_price_goal": 0.6, "ask_price_goal": 0.8},
            {"price_goal_type": PriceGoalChangeType.OPTION_SET_PRICE, "bid_price_goal": 0.35, "ask_price_goal": 0.45},
            {"price_goal_type": PriceGoalChangeType.OPTION_TICK, "bid_price_goal": 0.05, "ask_price_goal": 0.15},
            {"price_goal_type": PriceGoalChangeType.OPTION_PERCENTAGE, "bid_price_goal": 10, "ask_price_goal": 15}
        ]
    }
    #doing this with $15 F calls for 07/28
    # def calculate_price_change_for_entry(asset_price, position_type,strike_price, bid_price_goal, ask,  dte):
    # print('\n'.join([f"{k}: {v}" for k,v in module_config.items()]))

    run_options_test(test_positions, module_config)

    # print(f"#### TESTING ENTRY POSITIONS ####")
    # module_config['bid_price_goal'] = module_config['asset_price'] - 0.10
    # print(f"\nIn order to take a {module_config['position_type']} position ({PositionType.LONG_OPTION if module_config['position_type'] == PositionType.LONG else PositionType.SHORT_OPTION}) in $({module_config['ticker']}) at bid price ${module_config['bid_price_goal']} (current ask: {module_config['ask']}), the following price change needs to occur")
    # # def calculate_price_change_for_entry(price_goal_change_type, position_type, asset_price, strike_price, price_goal,ask, dte):
    # result = calculate_price_change_for_entry(module_config['bid_price_goal_type'], module_config['position_type'],
    #                                          module_config['asset_price'], module_config['strike_price'],
    #                                          module_config['bid_price_goal'], module_config['ask'],
    #                                          calculate_dte(module_config['expiration_date']))
    # print('\n'.join([f"{k}: {v}" for k, v in result.items()]))
    #
    # module_config['bid_price_goal'] = module_config['asset_price'] + 0.10
    # print(
    #     f"\nIn order to take a {PositionType.SHORT} position ({PositionType.SHORT_OPTION}) in $({module_config['ticker']}) at bid price ${module_config['bid_price_goal']} (current ask: {module_config['asset_price']}), the following price change needs to occur")
    # result = calculate_price_change_for_entry(module_config['bid_price_goal_type'], PositionType.SHORT,
    #                                          module_config['asset_price'],
    #                                          module_config['strike_price'], module_config['bid_price_goal'],
    #                                          module_config['ask'],
    #                                          calculate_dte(module_config['expiration_date']))
    # print('\n'.join([f"{k}: {v}" for k, v in result.items()]))
    #
    #
    #
    # print(f"#### TESTING EXIT POSITIONS ####")
    # module_config['ask_price_goal'] = module_config['asset_price']+0.20
    # print(f"\nIn order to exit  a {module_config['position_type']} position ({PositionType.LONG_OPTION if module_config['position_type'] == PositionType.LONG else PositionType.SHORT_OPTION}) in $({module_config['ticker']}) at bid price ${module_config['ask_price_goal']} (current ask: {module_config['ask']}), the following price change needs to occur")
    # # def calculate_price_change_for_entry(price_goal_change_type, position_type, asset_price, strike_price, price_goal,ask, dte):
    # result = calculate_price_change_for_exit(module_config['bid_price_goal_type'],module_config['position_type'],module_config['asset_price'], module_config['strike_price'],module_config['ask_price_goal'], module_config['ask'], calculate_dte(module_config['expiration_date']) )
    # print('\n'.join([f"{k}: {v}" for k,v in result.items()]))
    #
    # module_config['ask_price_goal'] = module_config['asset_price'] - 0.20
    # print(f"\nIn order to exit a {PositionType.SHORT} position ({PositionType.SHORT_OPTION }) in $({module_config['ticker']}) at goal {module_config['ask_price_goal']} {module_config['ask_price_goal']}  (current ask: {module_config['asset_price']}), the following price change needs to occur")
    # result = calculate_price_change_for_exit(module_config['bid_price_goal_type'], PositionType.SHORT, module_config['asset_price'],
    #                                           module_config['strike_price'], module_config['ask_price_goal'], module_config['ask'],
    #                                           calculate_dte(module_config['expiration_date']))
    # print('\n'.join([f"{k}: {v}" for k, v in result.items()]))
    # pass



    print(f"\nCompleted testing  of ({module_config['ticker']}) {PositionType.LONG_OPTION if module_config['position_type'] == PositionType.LONG else PositionType.SHORT_OPTION} in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")