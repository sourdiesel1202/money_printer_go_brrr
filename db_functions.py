import traceback

from enums import AlertType, PositionType, strategy_type_dict, InventoryFunctionTypes
from validation import validate_ticker
from functions import execute_query, execute_update, obtain_db_connection
from indicators import load_macd, load_sma, load_dmi_adx, load_rsi, did_macd_alert, did_rsi_alert, did_sma_alert, \
    did_dmi_alert, did_adx_alert, determine_sma_alert_type, get_indicator_inventory
from indicators import determine_rsi_alert_type, determine_macd_alert_type,determine_adx_alert_type,determine_dmi_alert_type,load_ticker_similar_trends
from indicators import  load_death_cross, load_golden_cross, determine_death_cross_alert_type,determine_golden_cross_alert_type, did_golden_cross_alert, did_death_cross_alert
from indicators import load_support_resistance, is_trading_in_sr_band, determine_sr_direction
# strategy_type_dict


def load_mpb_report(connection, module_config):
    return execute_query(connection, f"select distinct  th.timestamp, t.symbol, th.close,th.volume, group_concat(distinct tv.strategy_type separator  ',') strategies_validated, count(distinct ta.alert_type) pick_level,group_concat(distinct ta.alert_type separator  ',') alerts_triggered,group_concat(distinct tlt.symbol separator  ',') similar_ticker_lines, group_concat(distinct tbv.strategy_type separator  ',') backtested_positions  from history_tickerhistory th , tickers_ticker t, validation_tickervalidation tv, alerts_tickeralert ta, lines_similarline tl, tickers_ticker tlt, backtests_backtest tb, validation_tickervalidation tbv where tbv.id=tb.validation_id and tb.validation_id=tv.id and tl.ticker_history_id =th.id and tl.ticker_id=tlt.id and  ta.ticker_history_id=th.id and tv.ticker_history_id=th.id and t.id=th.ticker_id and th.timestamp= (select max(timestamp) from history_tickerhistory where timespan_multiplier='{module_config['timespan_multiplier']}' and timespan='{module_config['timespan']}') and th.timespan_multiplier='{module_config['timespan_multiplier']}' and th.timespan='{module_config['timespan']}' group by th.id, th.timestamp, t.symbol, th.close,th.volume")

def load_ticker_last_updated(ticker, connection, module_config):
    return int(execute_query(connection, f"select coalesce(max(timestamp), round(1000 * unix_timestamp(date_sub(now(), interval 365 day)))) from history_tickerhistory where ticker_id=(select id from tickers_ticker where symbol='{ticker}') and timespan='{module_config['timespan']}' and timespan_multiplier='{module_config['timespan_multiplier']}'")[1][0])
def load_timespan_last_updated(ticker, connection, module_config):
    return execute_query(connection, f"select max(timestamp) from history_tickerhistory where timespan='{module_config['timespan']}' and timespan_multiplier='{module_config['timespan_multiplier']}'")[1][0]


def load_nyse_tickers(connection, module_config):
    return [x[0] for x in execute_query(connection,"select t.symbol from tickers_ticker t left join history_tickerhistory ht on t.id = ht.ticker_id where ht.id is not null")[1:]]


def write_ticker_alert(connection,  alert_type, ticker, ticker_history,module_config):
    execute_update(connection,f"insert into alerts_tickeralert (alert_type, ticker_history_id) values ('{alert_type}',(select id from history_tickerhistory where timestamp={ticker_history[-1].timestamp} and ticker_id=(select id from tickers_ticker where symbol='{ticker}') and timespan='{module_config['timespan']}' and timespan_multiplier='{module_config['timespan_multiplier']}'))", auto_commit=True, verbose=True)

def write_ticker_validation(connection,  strategy_type,indicator, ticker, ticker_history,module_config):
    #first, write the validation
    execute_update(connection,f"insert into validation_tickervalidation (validation_type, strategy_type, ticker_history_id) values ('{indicator}','{strategy_type}', (select id from history_tickerhistory where timestamp={ticker_history[-1].timestamp} and ticker_id=(select id from tickers_ticker where symbol='{ticker}') and timespan='{module_config['timespan']}' and timespan_multiplier='{module_config['timespan_multiplier']}'))", auto_commit=True, verbose=True)
    #second, stub in the backtest
    execute_update(connection,f"insert into backtests_backtest ( results, validation_id) values ('"+'{}'+f"', (select id from validation_tickervalidation where strategy_type='{strategy_type}' and validation_type='{indicator}' and ticker_history_id=((select id from history_tickerhistory where timestamp={ticker_history[-1].timestamp} and ticker_id=(select id from tickers_ticker where symbol='{ticker}') and timespan='{module_config['timespan']}' and timespan_multiplier='{module_config['timespan_multiplier']}'))  ))", auto_commit=True, verbose=True)
def process_ticker_validation(connection, ticker, ticker_history, module_config):
    '''
    bassically iterate through the position_type:strategies dict and deterine for
    long, short and neutral positions whether the ticker is currently valid to enter the position type
    :param ticker:
    :param ticker_history:
    :param module_config:
    :return:
    '''

    # ticker_results[ticker]['long_validation'] = ','.join([k for k, v in validate_ticker(PositionType.LONG, ticker, _th, module_config).items() if v])
    # ticker_results[ticker]['short_validation'] = ','.join([k for k, v in validate_ticker(PositionType.SHORT, ticker, _th, module_config).items() if v])
    # ok so here we're going to do our validations and write validation for any position types that match the position type (i.e. long call, long put, etc)b

    for position_type, strategies in strategy_type_dict.items():
        for k, v in validate_ticker(position_type, ticker, ticker_history, module_config).items():
            # if module_config['logging']:
            if v:
                print(f"Validated {position_type} position in {ticker} ({k}), writing {len(strategies)} strategies")
                for strategy in strategies:
                    try:
                        write_ticker_validation(connection,strategy, k, ticker, ticker_history, module_config )
                    except:
                        traceback.print_exc()


def process_ticker_similar_lines(ticker, ticker_history, module_config):
    pass
def process_ticker_alerts(connection, ticker, ticker_history, module_config):
    '''
    Similar to above, this function is to process ticker history and flag any alerts
    :param ticker:
    :param ticker_history:
    :param module_config:
    :return:
    '''
    _th = ticker_history
    # ok so first things first, we will go ahead and check the alerts
    ticker_history = ticker_history[:-1] #since the last bar hasn't closed yet

    #ok so we're going to try something different here
    indicator_inventory = get_indicator_inventory()
    for indicator, function_dict in indicator_inventory.items():
        # def load_macd(ticker, ticker_history, module_config):
        # def did_golden_cross_alert(indicator_data, ticker, ticker_history, module_config)
        # def determine_macd_alert_type(indicator_data,ticker,ticker_history, module_config):
        if function_dict[InventoryFunctionTypes.DID_ALERT](function_dict[InventoryFunctionTypes.LOAD](ticker, ticker_history,module_config), ticker, ticker_history, module_config):
            #alert did fire, so now we need to write the alert
            try:
                write_ticker_alert(connection, function_dict[InventoryFunctionTypes.DETERMINE_ALERT_TYPE](function_dict[InventoryFunctionTypes.LOAD](ticker, ticker_history,module_config), ticker, ticker_history, module_config), ticker, _th,module_config )
            except:
                traceback.print_exc()
    #iterate back through, but this time we only fire the ignore functions, which should simply load the alerts for the period from the DB and then
    # ignore any alerts based upon other alerts
    for indicator, function_dict in indicator_inventory.items():
        # def ignore_golden_cross_alert(connection, alert_direction, ticker, ticker_history, module_config):
        #pass in as callable,
        function_dict[InventoryFunctionTypes.IGNORE](connection, function_dict[InventoryFunctionTypes.DETERMINE_ALERT_TYPE], ticker, _th, module_config)

    # sma = load_sma(ticker, ticker_history, module_config)
    # macd_data = load_macd(ticker, ticker_history, module_config)
    # dmi_adx_data = load_dmi_adx(ticker, ticker_history, module_config)
    # rsi_data = load_rsi(ticker, ticker_history, module_config)
    # golden_cross_data = load_golden_cross(ticker, ticker_history, module_config)
    # death_cross_data = load_death_cross(ticker, ticker_history, module_config)
    # sr_data = load_support_resistance(ticker, ticker_history, module_config)

    # ticker_results[ticker]['sma'] = did_sma_alert(sma, ticker, ticker_history, module_config)
    # ticker_results[ticker]['macd'] = did_macd_alert(macd_data, ticker, ticker_history, module_config)
    # ticker_results[ticker]['rsi'] = did_rsi_alert(rsi_data, ticker, ticker_history, module_config)
    # ticker_results[ticker]['dmi'] = did_dmi_alert(dmi_adx_data, ticker, ticker_history, module_config)
    # # ticker_results[ticker]['adx'] = did_adx_alert(dmi_adx_data, ticker, ticker_history, module_config)
    # ticker_results[ticker]['golden_cross'] = did_golden_cross_alert(golden_cross_data, ticker, ticker_history,
    #                                                                 module_config)
    # ticker_results[ticker]['death_cross'] = did_death_cross_alert(death_cross_data, ticker, ticker_history,
    #                                                               module_config)
    # ticker_results[ticker]['sr_band_breakout'] = not is_trading_in_sr_band(sr_data, ticker, ticker_history,
    #                                                                        module_config)
    # if ticker_results[ticker]['macd']:
    #     ticker_results[ticker]['directions'].append(
    #         determine_macd_alert_type(macd_data, ticker, ticker_history, module_config))
    # if ticker_results[ticker]['dmi']:
    #     ticker_results[ticker]['directions'].append(
    #         determine_dmi_alert_type(dmi_adx_data, ticker, ticker_history, module_config))
    # # if ticker_results[ticker]['adx']:
    #     ticker_results[ticker]['directions'].append(
    #         determine_adx_alert_type(dmi_adx_data, ticker_history, ticker, module_config))
    # if ticker_results[ticker]['sma']:
    #     ticker_results[ticker]['directions'].append(
    #         determine_sma_alert_type(sma, ticker, ticker_history, module_config))
    # if ticker_results[ticker]['golden_cross']:
    #     ticker_results[ticker]['directions'].append(
    #         determine_golden_cross_alert_type(golden_cross_data, ticker, ticker_history, module_config))
    # if ticker_results[ticker]['death_cross']:
    #     ticker_results[ticker]['directions'].append(
    #         determine_death_cross_alert_type(death_cross_data, ticker, ticker_history, module_config))
    # if ticker_results[ticker]['sr_band_breakout']:
    #     ticker_results[ticker]['directions'].append(
    #         determine_sr_direction(sr_data, ticker, ticker_history, module_config))
    #     # ignore if under sr_breakout_percentage
    #     if AlertType.BREAKOUT_SR_UP in ticker_results[ticker]['directions'][-1] or AlertType.BREAKOUT_SR_DOWN in \
    #             ticker_results[ticker]['directions'][-1]:
    #         breakout_percentage = float(
    #             ticker_results[ticker]['directions'][-1].split('/')[-1].split('%')[0].replace('-', ''))
    #         if breakout_percentage < module_config['sr_breakout_percentage']:
    #             ticker_results[ticker]['sr_band_breakout'] = False
    #             del ticker_results[ticker]['directions'][-1]
    # if ticker_results[ticker]['rsi']:
    #     ticker_results[ticker]['directions'].append(
    #         determine_rsi_alert_type(rsi_data, ticker, ticker_history, module_config))
    #     # basically if any bullish alerst and overbought, ignore
    #     if ((ticker_results[ticker]['macd'] and determine_macd_alert_type(macd_data, ticker, ticker_history,
    #                                                                       module_config) == AlertType.MACD_MACD_CROSS_SIGNAL) or
    #         (ticker_results[ticker]['sma'] and determine_sma_alert_type(sma, ticker, ticker_history,
    #                                                                     module_config) == AlertType.SMA_CONFIRMATION_UPWARD) or
    #         (ticker_results[ticker]['dmi'] and determine_dmi_alert_type(dmi_adx_data, ticker, ticker_history,
    #                                                                     module_config) == AlertType.DMIPLUS_CROSSOVER_DMINEG)) and determine_rsi_alert_type(
    #         rsi_data, ticker, ticker_history, module_config) == AlertType.RSI_OVERBOUGHT:
    #         ticker_results[ticker]['rsi'] = False
    #         del ticker_results[ticker]['directions'][-1]
    #     elif ((ticker_results[ticker]['macd'] and determine_macd_alert_type(macd_data, ticker, ticker_history,
    #                                                                         module_config) == AlertType.MACD_SIGNAL_CROSS_MACD) or
    #           (ticker_results[ticker]['sma'] and determine_sma_alert_type(sma, ticker, ticker_history,
    #                                                                       module_config) == AlertType.SMA_CONFIRMATION_DOWNWARD) or
    #           (ticker_results[ticker]['dmi'] and determine_dmi_alert_type(dmi_adx_data, ticker, ticker_history,
    #                                                                       module_config) == AlertType.DMINEG_CROSSOVER_DMIPLUS)) and determine_rsi_alert_type(
    #         rsi_data, ticker, ticker_history, module_config) == AlertType.RSI_OVERSOLD:
    #         ticker_results[ticker]['rsi'] = False
    #         del ticker_results[ticker]['directions'][-1]
def process_ticker_history(connection, ticker,ticker_history, module_config):
    '''
    This function is where we're going to process our overall ticker history entries
    basically call each piece that we are writing to the db wtih as a fn, for example, process_ticker_validatino, process_ticker_alerts, etc
    :param ticker:
    :param ticker_results:
    :param ticker_history:
    :param module_config:
    :return:
    '''
    # _th = ticker_history
    #ok so first things first, we will go ahead and check the alerts
    # ticker_history = ticker_history[:-1] #since the last bar hasn't closed yet

    #ok so first we need to process any and all alerts
    # connection = obtain_db_connection()
    # def process_ticker_alerts(connection, ticker, ticker_history, module_config):
    process_ticker_alerts(connection, ticker,ticker_history, module_config)
    #now we process validation
    process_ticker_validation(connection, ticker, ticker_history, module_config)
    execute_update(connection, f"insert into lines_similarline (ticker_id, ticker_history_id) values ((select id from tickers_ticker where symbol='{ticker}'), (select id from history_tickerhistory where timestamp={load_ticker_last_updated(ticker, connection, module_config)} and timespan='{module_config['timespan']}' and timespan_multiplier='{module_config['timespan_multiplier']}' and ticker_id=(select id from tickers_ticker where symbol='{ticker}')))")
    # process_ticker_validation(connection, ticker, ticker_history, module_config)
