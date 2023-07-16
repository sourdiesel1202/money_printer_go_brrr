import time
from enums import AlertType, PositionType
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
if __name__ == '__main__':
    start_time = time.time()


    #doing this with $15 F calls for 07/28
    # def calculate_price_change_for_entry(asset_price, position_type,strike_price, bid_price_goal, ask,  dte):
    # print('\n'.join([f"{k}: {v}" for k,v in module_config.items()]))

    print(f"#### TESTING ENTRY POSITIONS ####")
    module_config['bid_price_goal'] = module_config['asset_price'] - 0.10
    print(f"\nIn order to take a {module_config['position_type']} position ({PositionType.LONG_OPTION if module_config['position_type'] == PositionType.LONG else PositionType.SHORT_OPTION}) in $({module_config['ticker']}) at bid price ${module_config['bid_price_goal']} (current ask: {module_config['ask']}), the following price change needs to occur")
    # def calculate_price_change_for_entry(price_goal_change_type, position_type, asset_price, strike_price, price_goal,ask, dte):
    result = calculate_price_change_for_entry(module_config['bid_price_goal_type'], module_config['position_type'],
                                             module_config['asset_price'], module_config['strike_price'],
                                             module_config['bid_price_goal'], module_config['ask'],
                                             calculate_dte(module_config['expiration_date']))
    print('\n'.join([f"{k}: {v}" for k, v in result.items()]))

    module_config['bid_price_goal'] = module_config['asset_price'] + 0.10
    print(
        f"\nIn order to take a {PositionType.SHORT} position ({PositionType.SHORT_OPTION}) in $({module_config['ticker']}) at bid price ${module_config['bid_price_goal']} (current ask: {module_config['asset_price']}), the following price change needs to occur")
    result = calculate_price_change_for_entry(module_config['bid_price_goal_type'], PositionType.SHORT,
                                             module_config['asset_price'],
                                             module_config['strike_price'], module_config['bid_price_goal'],
                                             module_config['ask'],
                                             calculate_dte(module_config['expiration_date']))
    print('\n'.join([f"{k}: {v}" for k, v in result.items()]))



    print(f"#### TESTING EXIT POSITIONS ####")
    module_config['ask_price_goal'] = module_config['asset_price']+0.20
    print(f"\nIn order to exit  a {module_config['position_type']} position ({PositionType.LONG_OPTION if module_config['position_type'] == PositionType.LONG else PositionType.SHORT_OPTION}) in $({module_config['ticker']}) at bid price ${module_config['ask_price_goal']} (current ask: {module_config['ask']}), the following price change needs to occur")
    # def calculate_price_change_for_entry(price_goal_change_type, position_type, asset_price, strike_price, price_goal,ask, dte):
    result = calculate_price_change_for_exit(module_config['bid_price_goal_type'],module_config['position_type'],module_config['asset_price'], module_config['strike_price'],module_config['ask_price_goal'], module_config['ask'], calculate_dte(module_config['expiration_date']) )
    print('\n'.join([f"{k}: {v}" for k,v in result.items()]))

    module_config['ask_price_goal'] = module_config['asset_price'] - 0.20
    print(f"\nIn order to exit a {PositionType.SHORT} position ({PositionType.SHORT_OPTION }) in $({module_config['ticker']}) at goal {module_config['ask_price_goal']} {module_config['ask_price_goal']}  (current ask: {module_config['asset_price']}), the following price change needs to occur")
    result = calculate_price_change_for_exit(module_config['bid_price_goal_type'], PositionType.SHORT, module_config['asset_price'],
                                              module_config['strike_price'], module_config['ask_price_goal'], module_config['ask'],
                                              calculate_dte(module_config['expiration_date']))
    print('\n'.join([f"{k}: {v}" for k, v in result.items()]))
    # pass



    print(f"\nCompleted testing  of ({module_config['ticker']}) {PositionType.LONG_OPTION if module_config['position_type'] == PositionType.LONG else PositionType.SHORT_OPTION} in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")