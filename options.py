import datetime
import traceback
# from ctypes import _CData

import requests
import mibian
from functions import calculate_percentage, get_today, load_module_config, execute_update
from enums import PositionType, PriceGoalChangeType
from polygon import OptionsClient
import json
import polygon
from history import load_options_history_raw, load_ticker_history_cached, load_cached_option_tickers
from functions import human_readable_datetime, timestamp_to_datetime
from polygon.options import OptionSymbol

from plotting import plot_ticker_with_indicators, build_indicator_dict


# class MPBOptionsClient():
#     _api_endpoint = "https://api.polygon.io"
#     # def __init__(self):
#     def __init__(self,api_key, *args, **kwargs):
#         self.api_key=api_key
#         # super().__init__(*args, **kwargs)
#         # self.time = datetime.now()
#     def load_options_contracts(self, ticker, module_config):
#
#         #ok so the idea here is start at 31 days DTE and look forward
#         now = datetime.datetime.now()
#
#         for i in range(31, 90): #look 90 days out for contracts
#             url = f"{self._api_endpoint}/v3/reference/options/contracts?apiKey={self.api_key}&underlying_ticker={ticker}&expiration_date=2023-08-19&expired=false"
#             r = requests.get(url)
#             raw_data = json.loads(r.text)
#             if len(raw_data['result']) > 0:
#                 return [x['ticker'] for x in raw_data['results']]
#             print(json.loads(r.text))
#         return
#     # pass
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
        if position_type == PositionType.LONG:
            _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
        else:
            _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], putPrice=_tmp_ask).impliedVolatility
        greeks = mibian.BS([_tmp_price, strike_price, 0, dte], volatility=_tmp_iv)
        per_cent_delta = float(greeks.callDelta if position_type == PositionType.LONG else greeks.putDelta )/ 100
        while round(_tmp_price,2) <= round(_asset_price,2):# and _tmp_ask > 0.05: #stop at a 0.05 ask, etrade order price min increment lol
            if round(_tmp_price, 2) == round(_asset_price, 2):
                break
            _tmp_price = _tmp_price -  0.01 *(1 if position_type == PositionType.LONG else -1) # one send decrements
            _tmp_ask = _tmp_ask - per_cent_delta * (1 if position_type == PositionType.LONG else -1)
            if position_type == PositionType.LONG:
                _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
            else:
                _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], putPrice=_tmp_ask).impliedVolatility
            greeks = mibian.BS([_tmp_price, strike_price, 0, dte], volatility=_tmp_iv)
            per_cent_delta = float(greeks.callDelta if position_type == PositionType.LONG else greeks.putDelta )/ 100
        bid = _tmp_ask
        # _tmp_price = _asset_price
    else:
        if position_type == PositionType.LONG:
            _tmp_iv = mibian.BS([asset_price, strike_price, 0, dte], callPrice=ask).impliedVolatility
        else:
            _tmp_iv = mibian.BS([asset_price, strike_price, 0, dte], putPrice=ask).impliedVolatility
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
    while _tmp_ask >= bid and _tmp_ask > 0.05: #stop at a 0.05 ask, etrade order price min increment lol
        if _tmp_ask <= bid:
            break
        _tmp_price = _tmp_price -  0.01 *( 1 if position_type == PositionType.LONG else -1)
        _tmp_ask = _tmp_ask - per_cent_delta *(1 if position_type == PositionType.LONG else -1)
        if position_type == PositionType.LONG:
            _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
        else:
            _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], putPrice=_tmp_ask).impliedVolatility
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
    if position_type == PositionType.LONG:
        _tmp_iv = mibian.BS([asset_price, strike_price, 0, dte], callPrice=ask).impliedVolatility
    else:
        _tmp_iv = mibian.BS([asset_price, strike_price, 0, dte], putPrice=ask).impliedVolatility
    # _tmp_iv = mibian.BS([asset_price, strike_price, 0, dte], callPrice=ask).impliedVolatility
    greeks = mibian.BS([asset_price, strike_price, 0, dte], volatility=_tmp_iv)
    per_cent_delta = float(greeks.callDelta / 100 if position_type == PositionType.LONG else greeks.putDelta / 100)
    # _ticker_price_change_value = (0.1/100) * asset_price
    if price_goal_change_type   in [PriceGoalChangeType.ASSET_POINTS, PriceGoalChangeType.ASSET_PERCENTAGE, PriceGoalChangeType.ASSET_SET_PRICE]:
        #ok so basically we need to figure out what the bid is at our target asking price
        if price_goal_change_type == PriceGoalChangeType.ASSET_POINTS:
            _asset_price = asset_price - price_goal
        elif price_goal_change_type == PriceGoalChangeType.ASSET_PERCENTAGE:
            p = float(float(price_goal / 100) * asset_price)
            print(f"{price_goal} percent of ${asset_price}: ${p}")
            _asset_price = asset_price - p *(-1 if position_type == PositionType.LONG else 1)
        else:
            _asset_price = price_goal
        _tmp_price = asset_price
        _tmp_ask = ask
        if position_type == PositionType.LONG:
            _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
        else:
            _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], putPrice=_tmp_ask).impliedVolatility
        # _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
        greeks = mibian.BS([_tmp_price, strike_price, 0, dte], volatility=_tmp_iv)
        per_cent_delta = float(greeks.callDelta if position_type == PositionType.LONG else greeks.putDelta )/ 100
        while round(_asset_price,2) != round(_tmp_price,2):
        # while (round(_tmp_price,2) <= round(_asset_price,2) if position_type == PositionType.LONG else _asset_price <= round(_tmp_price,2)) :# and _tmp_ask > 0.05: #stop at a 0.05 ask, etrade order price min increment lol
            # if round(_tmp_price, 2) == round(_asset_price, 2):
            #     break
            _tmp_price = _tmp_price - 0.01 * (-1 if position_type == PositionType.LONG else 1)  # one send decrements
            _tmp_ask = _tmp_ask - per_cent_delta * (-1 if position_type == PositionType.LONG else 1)
            if position_type == PositionType.LONG:
                _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
            else:
                _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], putPrice=_tmp_ask).impliedVolatility
            greeks = mibian.BS([_tmp_price, strike_price, 0, dte], volatility=_tmp_iv)
            per_cent_delta = float(greeks.callDelta if position_type == PositionType.LONG else greeks.putDelta )/ 100
        bid = _tmp_ask
        # _tmp_price = _asset_price
    else:

        #basically for all cases but asset changes, we can more ore less re-use the existing code, we just need to set our bid accordingly
        # if price_goal_change_type == PriceGoalChangeType.OPTION_SET_PRICE:
        if price_goal_change_type == PriceGoalChangeType.OPTION_TICK:
            bid = ask + price_goal
        elif price_goal_change_type == PriceGoalChangeType.OPTION_PERCENTAGE:
            p = float(float(price_goal/100)*ask)# * (-1 if position_type == PositionType.LONG else 1 )
            print(f"{price_goal} percent of ${strike_price} {position_type} Option priced at ${ask}: ${p}")
            bid  = ask +p
            pass
            # _tmp_ask =
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

        # print(_tmp_price)
        if _tmp_ask >= bid:
            break
        _tmp_price = _tmp_price - 0.01 * (-1 if position_type == PositionType.LONG else 1)
        _tmp_ask = _tmp_ask - per_cent_delta * (-1 if position_type == PositionType.LONG else 1)
        if position_type == PositionType.LONG:
            _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], callPrice=_tmp_ask).impliedVolatility
        else:
            _tmp_iv = mibian.BS([_tmp_price, strike_price, 0, dte], putPrice=_tmp_ask).impliedVolatility
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


def load_active_contracts(ticker,client, module_config):
    pass
    #ok so here we load the active contracts for the ticker

# def load_options_contracts(ticker, module_config):
#
#     # ok so the idea here is start at 31 days DTE and look forward
#     now = datetime.datetime.now()
#
#     for i in range(31, 90):  # look 90 days out for contracts
#         url = f"{module_config['api_endpoint']}/v3/reference/options/contracts?apiKey={module_config['api_key']}&underlying_ticker={ticker}&expiration_date={(now+datetime.timedelta(days=i)).strftime('%Y-%m-%d')}"
#         r = requests.get(url)
#         raw_data = json.loads(r.text)
#         if len(raw_data['results']) > 0:
#             return [x['ticker'] for x in raw_data['results']]
#         print(json.loads(r.text))
#     return


    # contract_tickers
def analyze_option_data(position_type,ticker, ticker_history, module_config):

    # client = polygon.OptionsClient(api_key=module_config['api_key'])
    # [x.split(".csv")[0] for x in os.listdir(f"{module_config['output_dir']}cached/")]
    results = []
    for contract_ticker in load_cached_option_tickers(ticker, module_config):
        contract_history = load_ticker_history_cached(contract_ticker, module_config)
        if (timestamp_to_datetime(contract_history[-1].timestamp).day != timestamp_to_datetime(ticker_history[-1].timestamp).day) or (timestamp_to_datetime(contract_history[-1].timestamp).month != timestamp_to_datetime(ticker_history[-1].timestamp).month) or (timestamp_to_datetime(contract_history[-1].timestamp).hour != timestamp_to_datetime(ticker_history[-1].timestamp).hour) or (timestamp_to_datetime(contract_history[-1].timestamp).minute != timestamp_to_datetime(ticker_history[-1].timestamp).minute):
            continue
        option_symbol = OptionSymbol(contract_ticker)
        dte  = (datetime.datetime(*option_symbol.expiry.timetuple()[:-4]) - datetime.datetime.now()).days
        if option_symbol.call_or_put.upper() == (PositionType.LONG_OPTION if position_type == PositionType.LONG else PositionType.SHORT_OPTION )[0].upper():
            if position_type == PositionType.LONG:
                _tmp_iv = mibian.BS([ticker_history[-1].close, float(option_symbol.strike_price), 0, dte], callPrice=contract_history[-1].close).impliedVolatility
            else:
                _tmp_iv = mibian.BS([ticker_history[-1].close, float(option_symbol.strike_price), 0, dte], putPrice=contract_history[-1].close).impliedVolatility
            # _tmp_iv = mibian.BS([asset_price, strike_price, 0, dte], callPrice=ask).impliedVolatility
            greeks = mibian.BS([ticker_history[-1].close, float(option_symbol.strike_price), 0, dte], volatility=_tmp_iv)
            # greeks.
            results.append({
                "total_volume":sum([x.volume for x in contract_history]),
                "last_traded": timestamp_to_datetime(contract_history[-1].timestamp),
                "ticker": contract_ticker,
                "iv": _tmp_iv,
                "delta":float(greeks.callDelta / 100 if position_type == PositionType.LONG else greeks.putDelta / 100),
                "theta":float(greeks.callTheta / 100 if position_type == PositionType.LONG else greeks.putTheta / 100),
                "ask":contract_history[-1].close
            })

    results.sort(key=lambda x: x['total_volume'], reverse=True)
        #
    #expecting contract data to be a dict of expiry dates that contain  a dict containing the option symbols and the history list
    #idk what hte right approach here is, highest volume for now?
    # results = {}
    # for expry_date, contracts  in contract_data.items():

    results = results[:5]
    results.sort(key=lambda x: x['delta'], reverse=True)
    return results

def load_tickers_option_data(tickers, module_config={}):
    if len([x for x in module_config.keys()]) == 0:
        module_config = load_module_config("market_scanner") #doing this to allow for concurrency
    for ticker in tickers:
        #just iterate through and load the data
        ticker_history = load_ticker_history_cached(ticker, module_config)
        load_ticker_option_data(ticker, ticker_history, module_config)
def write_discovered_contracts(contracts, ticker, ticker_history, module_config, connection = None):

    for contract in contracts:
        option_symbol = OptionSymbol(contract)
        sql = f"insert ignore into tickers_contract (symbol, name, type, expry, description, strike_price, ticker_id) values ('{contract}', '{option_symbol.expiry} {option_symbol.strike_price} {PositionType.LONG_OPTION if option_symbol.call_or_put == 'C' else PositionType.SHORT_OPTION} ', '{PositionType.LONG_OPTION if option_symbol.call_or_put == 'C' else PositionType.SHORT_OPTION}','{option_symbol.expiry}', '{option_symbol.strike_price} {option_symbol.expiry} {PositionType.LONG_OPTION if option_symbol.call_or_put == 'C' else PositionType.SHORT_OPTION}S on {ticker}', {float(option_symbol.strike_price)}, (select id from tickers_ticker where symbol='{ticker}'))"
        execute_update(connection, sql, verbose=True,auto_commit=True)


def load_ticker_contract_history(contracts, ticker, ticker_history,module_config, connection):
    options_client = polygon.OptionsClient(api_key=module_config['api_key'])
    for option_contract in contracts:
        try:
            contract_dat = load_options_history_raw(option_contract, ticker_history, options_client,
                                                    module_config['timespan_multiplier'], module_config['timespan'],
                                                    get_today(module_config,
                                                              minus_days=module_config['contract_history_window']),
                                                    get_today(module_config), 50000, module_config,
                                                    connection=connection)


        except:
            traceback.print_exc()
        pass
    # return contract_dat

def load_ticker_option_contracts(ticker, ticker_history, module_config, connection = None ):

    # ok so the idea here is start at 1 day DTE and look forward
    now = datetime.datetime.now()
    expires = {}
    for i in range(0, module_config['contract_days_out']):  # look 90 days out for contracts
        tin_per = float(float(module_config['contract_ticker_percentage']/100) * ticker_history[-1].close) #basically we are looking for contracts within 20% of the
        strike_price_query = f"strike_price.gte={ticker_history[-1].close - tin_per}&strike_price.lte={ticker_history[-1].close + tin_per}"
        # urls =[f"{module_config['api_endpoint']}/v3/reference/options/contracts?apiKey={module_config['api_key']}&underlying_ticker={ticker}&expiration_date={(now+datetime.timedelta(days=i)).strftime('%Y-%m-%d')}&contract_type=put&{strike_price_query}",f"{module_config['api_endpoint']}/v3/reference/options/contracts?apiKey={module_config['api_key']}&underlying_ticker={ticker}&expiration_date={(now+datetime.timedelta(days=i)).strftime('%Y-%m-%d')}&{strike_price_query}&limit=500"]
        urls =[f"{module_config['api_endpoint']}/v3/reference/options/contracts?apiKey={module_config['api_key']}&underlying_ticker={ticker}&expiration_date={(now+datetime.timedelta(days=i)).strftime('%Y-%m-%d')}&{strike_price_query}&limit={module_config['contract_pullback_limit']}&contract_type=call", f"{module_config['api_endpoint']}/v3/reference/options/contracts?apiKey={module_config['api_key']}&underlying_ticker={ticker}&expiration_date={(now+datetime.timedelta(days=i)).strftime('%Y-%m-%d')}&{strike_price_query}&limit={module_config['contract_pullback_limit']}&contract_type=put"]
        for url in urls:
            r = requests.get(url)
            raw_data = json.loads(r.text)
            if len(raw_data['results']) > 0:
                if (now+datetime.timedelta(days=i)).strftime('%Y-%m-%d')  not in expires:
                    expires[(now+datetime.timedelta(days=i)).strftime('%Y-%m-%d')] = []#=[x['ticker'] for x in raw_data['results']]
                for x in raw_data['results']:
                    expires[(now + datetime.timedelta(days=i)).strftime('%Y-%m-%d')].append(x['ticker'])
                    # print(f"{x['ticker']}:{x['contract_type']}:{x['strike_price']}")


    # ok so once we have our contracts and dates, we can load the data for the contracts/dates
    for contracts in expires.values():
        write_discovered_contracts(contracts, ticker, ticker_history,module_config, connection)
def load_ticker_option_data(ticker, ticker_history, module_config, connection = None ):

    # ok so the idea here is start at 1 day DTE and look forward
    now = datetime.datetime.now()
    expires = {}
    for i in range(1, 48):  # look 90 days out for contracts
        tin_per = float(float(module_config['contract_ticker_percentage']/100) * ticker_history[-1].close) #basically we are looking for contracts within 20% of the
        strike_price_query = f"strike_price.gte={ticker_history[-1].close - tin_per}&strike_price.lte={ticker_history[-1].close + tin_per}"
        # urls =[f"{module_config['api_endpoint']}/v3/reference/options/contracts?apiKey={module_config['api_key']}&underlying_ticker={ticker}&expiration_date={(now+datetime.timedelta(days=i)).strftime('%Y-%m-%d')}&contract_type=put&{strike_price_query}",f"{module_config['api_endpoint']}/v3/reference/options/contracts?apiKey={module_config['api_key']}&underlying_ticker={ticker}&expiration_date={(now+datetime.timedelta(days=i)).strftime('%Y-%m-%d')}&{strike_price_query}&limit=500"]
        urls =[f"{module_config['api_endpoint']}/v3/reference/options/contracts?apiKey={module_config['api_key']}&underlying_ticker={ticker}&expiration_date={(now+datetime.timedelta(days=i)).strftime('%Y-%m-%d')}&{strike_price_query}&limit=500"]
        for url in urls:
            r = requests.get(url)
            raw_data = json.loads(r.text)
            if len(raw_data['results']) > 0:
                if (now+datetime.timedelta(days=i)).strftime('%Y-%m-%d')  not in expires:
                    expires[(now+datetime.timedelta(days=i)).strftime('%Y-%m-%d')] = []#=[x['ticker'] for x in raw_data['results']]
                for x in raw_data['results']:
                    expires[(now + datetime.timedelta(days=i)).strftime('%Y-%m-%d')].append(x['ticker'])
                    # print(f"{x['ticker']}:{x['contract_type']}:{x['strike_price']}")


    # ok so once we have our contracts and dates, we can load the data for the contracts/dates
    for contracts in expires.values():
        write_discovered_contracts(contracts, ticker, ticker_history,module_config, connection)
    # for ticker_a in module_config['tickers']:
    #     contract_tickers = mcv_load_options_contracts(ticker_a, module_config)
    options_client = polygon.OptionsClient(api_key=module_config['api_key'])
    # contract_data = {}
    _contract_data = []
    for _date in expires:
        print(f"Found {len(expires[_date])} contracts at date {_date}")
        for option_contract in expires[_date]:
            try:
                contract_dat = load_options_history_raw(option_contract,ticker_history, options_client, module_config['timespan_multiplier'], module_config['timespan'],get_today(module_config, minus_days=module_config['contract_history_window']), get_today(module_config), 50000,module_config, connection=connection)
                if len(contract_dat)> 0:
                    _contract_data.append(option_contract)
                    # plot_ticker_with_indicators(option_contract, contract_dat, build_indicator_dict(ticker, contract_dat, module_config),module_config)

            except:
                traceback.print_exc()
            pass


    #once we get HERE, we can determine the contracts with the most volumne
    return _contract_data
    # return expires

