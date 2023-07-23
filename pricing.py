from support_resistance import find_support_resistance_levels, find_nearest_resistance_level, find_nearest_support_level
from enums import PositionType, PriceGoalChangeType
from options import calculate_price_change_for_entry, calculate_price_change_for_exit, calculate_dte
def determine_entry_target(position_type, ticker, ticker_history, module_config):
    # sr_levels = find_support_resistance_levels(ticker, ticker_history, module_config,flatten=True)
    if position_type == PositionType.LONG: # so if it's long , we want to target the next SR level dowm (basically buy on the dip)
        return find_nearest_support_level(find_support_resistance_levels(ticker, ticker_history, module_config,flatten=True), ticker, ticker_history, module_config )
    else:# so if it's short, we want to target the next SR level up (basically buy on the rip)
        return find_nearest_resistance_level(find_support_resistance_levels(ticker, ticker_history, module_config,flatten=True), ticker, ticker_history, module_config )
    #add logic here
    pass

def determine_exit_target(position_type,asset_entry_price, ticker, ticker_history, module_config):
    # option_position = mibian.BS([asset_entry_price, module_config['strike_price'], 1, calculate_dte(module_config['expiration_date'])], volatility=20)
    #ok so here we need to do some logic
    if position_type == PositionType.LONG:
        #check to see what our exit target is, let's compare that to  the nearest resistance level
        #if it's over the nearest target, move to the next resistance level

        if module_config['ask_price_goal_type'] == PriceGoalChangeType.OPTION_PERCENTAGE:
            #first things first lets find out what the asset price is at our exit target

            calculate_price_change_for_exit(module_config['ask_price_goal_type'], position_type,
                                            asset_entry_price, module_config['strike_price'],
                                            module_config['ask_price_goal'], module_config['ask'],calculate_dte(module_config['expiration_date']))
            # find_nearest_resistance_level(find_support_resistance_levels(ticker, ticker_history, module_config, flatten=True), ticker,ticker_history, module_config)
            pass
        # bid_price_goal_type

        return find_nearest_support_level(find_support_resistance_levels(ticker, ticker_history, module_config, flatten=True), ticker, ticker_history,module_config)
    else:  # so if it's short, we want to target the next SR level up (basically buy on the rip)
        return find_nearest_resistance_level(find_support_resistance_levels(ticker, ticker_history, module_config, flatten=True), ticker, ticker_history,module_config)
    # add logic here
    # pass