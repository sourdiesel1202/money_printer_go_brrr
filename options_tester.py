import time
from enums import AlertType, PositionType
from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime

from history import load_ticker_history_raw
from validation import validate_ticker
from functions import load_module_config, get_today
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
from options import calculate_price_change_for_entry,calculate_dte
if __name__ == '__main__':
    start_time = time.time()


    #doing this with $15 F calls for 07/28
    # def calculate_price_change_for_entry(asset_price, position_type,strike_price, bid_price_goal, ask,  dte):
    # print('\n'.join([f"{k}: {v}" for k,v in module_config.items()]))


    module_config['bid_price_goal'] = module_config['asset_price']-0.10
    print(f"\nIn order to take a {module_config['position_type']} position ({PositionType.LONG_OPTION if module_config['position_type'] == PositionType.LONG else PositionType.SHORT_OPTION}) in $({module_config['ticker']}) at bid price ${module_config['bid_price_goal']} (current ask: {module_config['ask']}), the following price change needs to occur")
    # def calculate_price_change_for_entry(price_goal_change_type, position_type, asset_price, strike_price, price_goal,ask, dte):
    result = calculate_price_change_for_entry(module_config['bid_price_goal_type'],module_config['position_type'],module_config['asset_price'], module_config['strike_price'],module_config['bid_price_goal'], module_config['ask'], calculate_dte(module_config['expiration_date']) )
    print('\n'.join([f"{k}: {v}" for k,v in result.items()]))

    module_config['bid_price_goal'] = module_config['asset_price'] + 0.10
    print(f"\nIn order to take a {PositionType.SHORT} position ({PositionType.SHORT_OPTION }) in $({module_config['ticker']}) at bid price ${module_config['bid_price_goal']} (current ask: {module_config['asset_price']}), the following price change needs to occur")
    result = calculate_price_change_for_entry(module_config['bid_price_goal_type'], PositionType.SHORT, module_config['asset_price'],
                                              module_config['strike_price'], module_config['bid_price_goal'], module_config['ask'],
                                              calculate_dte(module_config['expiration_date']))
    print('\n'.join([f"{k}: {v}" for k, v in result.items()]))
    pass
    # client = polygon.RESTClient(api_key=module_config['api_key'])
    # # ticker = "GE"
    # for ticker in module_config['tickers']:
    #     ticker_history = load_ticker_history_raw(ticker, client, 1, module_config['timespan'],get_today(module_config, minus_days=7), get_today(module_config), 50000, module_config)
    #     if module_config['run_concurrently']:
    #         validate_ticker(module_config['position_type'],ticker,ticker_history, module_config)
    #     else:
    #         validate_ticker(module_config['position_type'],ticker,ticker_history, module_config)

    print(f"\nCompleted testing  of ({module_config['ticker']}) {PositionType.LONG_OPTION if module_config['position_type'] == PositionType.LONG else PositionType.SHORT_OPTION} in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")