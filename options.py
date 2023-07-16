import datetime

import mibian
from functions import calculate_percentage
from enums import PositionType, PriceGoalChangeType

def calculate_dte(expiration_date):
    return (datetime.datetime.strptime(expiration_date,'%Y-%m-%d')-datetime.datetime.now()).days
def calculate_price_change_for_entry(price_goal_change_type, position_type,asset_price,strike_price, price_goal, ask,  dte):
    ##in THEORY this should work for futures too?
    #basically, how much does the price need to change before our bid is met
    #can't think of a better way to do this than by the penny
    # _tmp_iv =

    if price_goal_change_type   in [PriceGoalChangeType.ASSET_POINTS, PriceGoalChangeType.ASSET_PERCENTAGE, PriceGoalChangeType.ASSET_SET_PRICE]:
        #ok so basically we need to figure out what the bid is at our target asking price
        if price_goal_change_type == PriceGoalChangeType.ASSET_POINTS:
            _asset_price = asset_price - price_goal
        elif price_goal_change_type == PriceGoalChangeType.ASSET_PERCENTAGE:
            p = float(float(price_goal / 100) * asset_price)
            print(f"{price_goal} percent of ${asset_price}: ${p}")
            _asset_price = asset_price - p*(1 if position_type == PositionType.LONG else -1)
        else:
            _asset_price = price_goal
        _tmp_price = asset_price
        _tmp_ask = ask
        _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
        greeks = mibian.BS([_tmp_price, strike_price, 0, dte], volatility=_tmp_iv)
        per_cent_delta = float(greeks.callDelta if position_type == PositionType.LONG else greeks.putDelta )/ 100
        while round(_tmp_price,2) != round(_asset_price,2):# and _tmp_ask > 0.05: #stop at a 0.05 ask, etrade order price min increment lol
            if round(_tmp_price, 2) == round(_asset_price, 2):
                break
            _tmp_price = _tmp_price -  0.01 *(1 if position_type == PositionType.LONG else -1) # one send decrements
            _tmp_ask = _tmp_ask - per_cent_delta * (1 if position_type == PositionType.LONG else -1)
            _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
            greeks = mibian.BS([_tmp_price, strike_price, 0, dte], volatility=_tmp_iv)
            per_cent_delta = float(greeks.callDelta if position_type == PositionType.LONG else greeks.putDelta )/ 100
        bid = _tmp_ask
        # _tmp_price = _asset_price
    else:
        _tmp_iv = mibian.BS([asset_price, strike_price, 0, dte], callPrice=ask).impliedVolatility
        greeks = mibian.BS([asset_price, strike_price, 0, dte], volatility=_tmp_iv)
        per_cent_delta = float(greeks.callDelta / 100 if position_type == PositionType.LONG else greeks.putDelta / 100)

        #basically for all cases but asset changes, we can more ore less re-use the existing code, we just need to set our bid accordingly
        # if price_goal_change_type == PriceGoalChangeType.OPTION_SET_PRICE:
        if price_goal_change_type == PriceGoalChangeType.OPTION_TICK:
            bid = ask - price_goal
        elif price_goal_change_type == PriceGoalChangeType.OPTION_PERCENTAGE:
            p = float(float(price_goal/100)*ask)
            print(f"{price_goal} percent of ${strike_price} {position_type} Option priced at ${ask}: ${p}")
            bid  = ask -p
        else:
            bid = price_goal

    bid = round(bid,2)
    # per_cent_gamma = float(gamma / 100)
    #don't care about vega rn
    _tmp_ask = ask
    _tmp_price = asset_price
    # if bid > ask:
    #     raise Exception(f"Just slap the ask {ask}, it's less than your bid {bid}")

    # while _tmp_ask > bid and _tmp_ask > 0.05: #stop at a 0.05 ask, etrade order price min increment lol
    while round(_tmp_ask,2) >= round(bid,2) and _tmp_ask > 0.05: #stop at a 0.05 ask, etrade order price min increment lol
        if round(_tmp_ask,2) <= round(bid,2):
            break
        _tmp_price = _tmp_price -  0.01 *( 1 if position_type == PositionType.LONG else -1)
        _tmp_ask = _tmp_ask - per_cent_delta *(1 if position_type == PositionType.LONG else -1)
        _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
        greeks = mibian.BS([_tmp_price, strike_price, 0, dte], volatility=_tmp_iv)
        per_cent_delta = float(greeks.callDelta if position_type == PositionType.LONG else greeks.putDelta ) /100



    if round(bid) >= round(_tmp_ask):
        #assuming we get here, we know that the order would have been filled
        return {
            "asset_price": round(_tmp_price,2),
            "asset_change": round(float(_tmp_price - asset_price),2),
            "asset_percentage_change": round(calculate_percentage(float(_tmp_price - asset_price), asset_price),2),
            "bid": bid,
            "ask": ask,
            "greeks": {
                "delta": greeks.callDelta if position_type == PositionType.LONG else greeks.putDelta,
                "theta": greeks.callTheta if position_type == PositionType.LONG else greeks.putTheta,
                "gamma": greeks.gamma,
                "vega": greeks.vega,
                "implied_violatility": _tmp_iv
            }
        }

    else:
        raise Exception(f"Decreased call price from {asset_price} ==> {_tmp_price} did not reach bid price")


def calculate_price_change_for_exit(price_goal_change_type, position_type,asset_price,strike_price, price_goal, ask,  dte):
    ##in THEORY this should work for futures too?
    #basically, how much does the price need to change before our bid is met
    #can't think of a better way to do this than by the penny
    # _tmp_iv =
    _tmp_iv = mibian.BS([asset_price, strike_price, 0, dte], callPrice=ask).impliedVolatility
    greeks = mibian.BS([asset_price, strike_price, 0, dte], volatility=_tmp_iv)
    per_cent_delta = float(greeks.callDelta / 100 if position_type == PositionType.LONG else greeks.putDelta / 100)

    if price_goal_change_type   in [PriceGoalChangeType.ASSET_POINTS, PriceGoalChangeType.ASSET_PERCENTAGE, PriceGoalChangeType.ASSET_SET_PRICE]:
        #ok so basically we need to figure out what the bid is at our target asking price
        if price_goal_change_type == PriceGoalChangeType.ASSET_POINTS:
            _asset_price = asset_price - price_goal
        elif price_goal_change_type == PriceGoalChangeType.ASSET_PERCENTAGE:
            p = float(float(price_goal / 100) * asset_price)
            print(f"{price_goal} percent of ${asset_price}: ${p}")
            _asset_price = asset_price - p*(-1 if position_type == PositionType.LONG else 1)
        else:
            _asset_price = price_goal
        _tmp_price = asset_price
        _tmp_ask = ask
        _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
        greeks = mibian.BS([_tmp_price, strike_price, 0, dte], volatility=_tmp_iv)
        per_cent_delta = float(greeks.callDelta if position_type == PositionType.LONG else greeks.putDelta )/ 100
        while round(_asset_price,2) != round(_tmp_price,2):
        # while (round(_tmp_price,2) <= round(_asset_price,2) if position_type == PositionType.LONG else _asset_price <= round(_tmp_price,2)) :# and _tmp_ask > 0.05: #stop at a 0.05 ask, etrade order price min increment lol
            # if round(_tmp_price, 2) == round(_asset_price, 2):
            #     break
            _tmp_price = _tmp_price - 0.01 * (-1 if position_type == PositionType.LONG else 1)  # one send decrements
            _tmp_ask = _tmp_ask - per_cent_delta * (-1 if position_type == PositionType.LONG else 1)
            _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
            greeks = mibian.BS([_tmp_price, strike_price, 0, dte], volatility=_tmp_iv)
            per_cent_delta = float(greeks.callDelta if position_type == PositionType.LONG else greeks.putDelta )/ 100
        bid = _tmp_ask
        # _tmp_price = _asset_price
    else:

        #basically for all cases but asset changes, we can more ore less re-use the existing code, we just need to set our bid accordingly
        # if price_goal_change_type == PriceGoalChangeType.OPTION_SET_PRICE:
        if price_goal_change_type == PriceGoalChangeType.OPTION_TICK:
            bid = ask - price_goal
        elif price_goal_change_type == PriceGoalChangeType.OPTION_PERCENTAGE:
            p = float(float(price_goal/100)*ask)
            print(f"{price_goal} percent of ${strike_price} {position_type} Option priced at ${ask}: ${p}")
            bid  = ask -p
        else:
            bid = price_goal

    # bid = bid
    # per_cent_gamma = float(gamma / 100)
    #don't care about vega rn
    _tmp_ask = ask
    _tmp_price = asset_price
    # if bid > ask:
    #     raise Exception(f"Just slap the ask {ask}, it's less than your bid {bid}")

    # while _tmp_ask < bid: #stop at a 0.05 ask, etrade order price min increment lol
    # while (round(_tmp_ask,2) < round(bid,2) if position_type == PositionType.LONG else round(bid,2) < round(_tmp_ask,2)):
    while _tmp_ask <= bid:# and _tmp_ask > 0.05: #stop at a 0.05 ask, etrade order price min increment lol


        if _tmp_ask >= bid:
            break
        _tmp_price = _tmp_price - 0.01 * (-1 if position_type == PositionType.LONG else 1)
        _tmp_ask = _tmp_ask - per_cent_delta * (-1 if position_type == PositionType.LONG else 1)
        _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
        greeks = mibian.BS([_tmp_price, strike_price, 0, dte], volatility=_tmp_iv)
        per_cent_delta = float(greeks.callDelta if position_type == PositionType.LONG else greeks.putDelta ) /100

        # if round(_tmp_ask, 2) == round(bid, 2):
        #     break


    # else:
    #     while _tmp_ask > bid and _tmp_ask > 0.05:  # stop at a 0.05 ask, etrade order price min increment lol
    #         _tmp_price = _tmp_price + 0.01  # one send decrements
    #         _tmp_ask = _tmp_ask + per_cent_delta
    #         # ok so calculate new ask and price first, we will need them to calculate the rest
    #         #
    #         _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
    #         greeks = mibian.BS([_tmp_price, strike_price, 0, dte], volatility=_tmp_iv)
    #         per_cent_delta = float(greeks.putDelta / 100)

    if round(bid,2) <= round(_tmp_ask,2):
        #assuming we get here, we know that the order would have been filled
        return {
            "asset_price": round(_tmp_price,2),
            "asset_change": round(float(_tmp_price - asset_price),2),
            "asset_percentage_change": round(calculate_percentage(float(_tmp_price - asset_price), asset_price),2),
            "bid": round(ask,2),
            "ask": round(bid,2),
            "greeks": {
                "delta": greeks.callDelta if position_type == PositionType.LONG else greeks.putDelta,
                "theta": greeks.callTheta if position_type == PositionType.LONG else greeks.putTheta,
                "gamma": greeks.gamma,
                "vega": greeks.vega,
                "implied_violatility": _tmp_iv
            }
        }

    else:
        raise Exception(f"Decreased call price from {asset_price} ==> {_tmp_price} did not reach bid price")
def calculate_price_change_percentages(stock_price, position_type, bid, ask, delta):
    pass