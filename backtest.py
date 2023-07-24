import json
import multiprocessing
import operator
import time,statistics
import traceback
import numpy as np
from enums import OrderType
import datetime,io,os
from zoneinfo import ZoneInfo
from functions import generate_csv_string, read_csv, write_csv, delete_csv, combine_csvs, calculate_percentage
from history import *
from indicators import determine_rsi_alert_type, determine_macd_alert_type,determine_adx_alert_type,determine_dmi_alert_type
from indicators import load_macd, load_sma, load_dmi_adx, load_rsi, did_macd_alert, did_rsi_alert, did_sma_alert, did_dmi_alert, did_adx_alert,determine_sma_alert_type
from indicators import load_dmi_adx, did_adx_alert, did_dmi_alert, determine_dmi_alert_type, determine_adx_alert_type
from indicators import  load_death_cross, load_golden_cross, determine_death_cross_alert_type,determine_golden_cross_alert_type, did_golden_cross_alert, did_death_cross_alert
import pandas as pd
from stockstats import wrap
from enums import *
import polygon, datetime
analyzed_backtest_keys = ['likelihood_long_3','likelihood_short_3','likelihood_long_5','likelihood_short_5','likelihood_long_7','likelihood_short_7','likelihood_long_9','likelihood_short_9','likelihood_long_ntdo','likelihood_short_ntdo','likelihood_long_ntdc','likelihood_short_ntdc','average_price_increase_percentage','average_price_decrease_percentage']
def backtest_ticker_concurrently(alert_types, ticker, ticker_history, module_config):
    start_time = time.time()

    ticker_history = ticker_history[:-20]
    print(f"{os.getpid()}: Oldest Data for {ticker}:{datetime.datetime.fromtimestamp(ticker_history[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}")
    print(f"{os.getpid()}:Newest Data for {ticker}:{datetime.datetime.fromtimestamp(ticker_history[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}")

    # client = polygon.RESTClient(api_key=module_config['api_key'])
    # _th = [tickers[i] for i in range(0, len(tickers))]
    # _dispensarys = [x for x in dispensaries.keys()]
    task_loads = [ticker_history[i:i + int(len(ticker_history)/module_config['num_processes'])+1] for i in range(0, len(ticker_history), int(len(ticker_history)/module_config['num_processes'])+1)]
    # for k,v in dispensaries.items():
    processes = {}
    print(f"Processing {len(ticker_history)} in {len(task_loads)} load(s)")
    for i in range(0, len(task_loads)):
        print(f"Blowing {i + 1}/{len(task_loads)} Loads")
        load = task_loads[i]
        p = multiprocessing.Process(target=backtest_ticker, args=(alert_types,ticker,load,module_config))
        p.start()

        processes[str(p.pid)] = p
    while any(processes[p].is_alive() for p in processes.keys()):
        # print(f"Waiting for {len([x for x in processes if x.is_alive()])} processes to complete. Going to sleep for 10 seconds")
        process_str = ','.join([str(v.pid) for v in processes.values() if v.is_alive()])
        time_str = f"{int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds"
        print(
            f"Waiting on {len(processes.keys())} processes to finish in load {i + 1}/{len(task_loads)}\nElapsed Time: {time_str}")
        time.sleep(10)
    # write_csv(f"{ticker}_backtest.csv", combine_csvs([f"{x.pid}backtest.csv" for x in processes.values()]))
    combined = combine_csvs([f"{module_config['output_dir']}{x.pid}backtest.csv" for x in processes.values()])
    header = combined[0]
    del combined[0]
    # sorted(combined, key=lambda x: int(x[-2]))
    combined.sort(key=operator.itemgetter(header.index("timestamp")))
    combined.reverse()
    # results.reverse()
    combined.insert(0, header)
    write_csv(f"{module_config['output_dir']}{ticker}_backtest.csv", combined)
    backtest_results = analyze_backtest_results(load_backtest_results(ticker, module_config))
    result_rows = [analyzed_backtest_keys]
    new_row = []
    for k in analyzed_backtest_keys:
         new_row.append(backtest_results[k])
    result_rows.append(new_row)
    write_csv(f"{module_config['output_dir']}{ticker}_backtest_analyzed.csv", result_rows)
    # combined =
def write_backtest_rawdata(lines):
    with open(f"{os.getpid()}.dat", "w+") as f:
        f.write('\n'.join(lines))

data_functions = {
    "macd": load_macd,
    "rsi": load_rsi,
    "dmi": load_dmi_adx,
    "adx": load_dmi_adx,
    "sma": load_sma,
    "golden_cross": load_golden_cross,
    "death_cross": load_death_cross
}

alert_functions = {
    "macd": did_macd_alert,
    "rsi": did_rsi_alert,
    "dmi": did_dmi_alert,
    "adx": did_adx_alert,
    "sma": did_sma_alert,
    "golden_cross": did_golden_cross_alert,
    "death_cross": did_death_cross_alert
}

# alert_type_functions = {
alert_type_functions = {
    "macd": determine_macd_alert_type,
    "rsi": determine_rsi_alert_type,
    "dmi": determine_dmi_alert_type,
    "adx": determine_adx_alert_type,
    "sma": determine_sma_alert_type,
    "golden_cross": determine_golden_cross_alert_type,
    "death_cross":determine_death_cross_alert_type

}
def generate_polygon_date_str(days_ago):
    if days_ago==0:
        new_date = datetime.datetime.now()
    else:
        new_date = datetime.datetime.now()-datetime.timedelta(days=days_ago)
    # print(new_date.strftime("%Y-%m-%d"))
    return new_date.strftime("%Y-%m-%d")
def load_backtest_ticker_data(ticker, client,module_config):
    return load_ticker_history_raw(ticker,client,30, 'hour', get_today(module_config, minus_days=720), get_today(module_config,minus_days=1),50000,module_config)
    # client = polygon.RESTClient(api_key=module_config['api_key'])
    # history_data = []
    # # for entry in client.list_aggs(ticker=ticker, multiplier=multiplier, timespan=timespan, from_=from_, to=to,limit=limit, sort='asc'):
    # for entry in client.list_aggs(ticker=ticker, multiplier=1, timespan=module_config['timespan'], from_=get_today(module_config,module_config['backtest_days']), to=module_config['test_date'],
    #                               sort='asc', limit=50000):
    #     if module_config['logging']:
    #         entry_date = datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern'))
    #         # print(f"BACKTEST:{entry_date}: {ticker}| Open: {entry.open} High: {entry.high} Low: {entry.low} Close: {entry.close} Volume: {entry.volume}")
    #     if datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern')).hour >=9 and datetime.datetime.fromtimestamp(entry.timestamp / 1e3, tz=ZoneInfo('US/Eastern')).hour <= 16:
    #         history_data.append(entry)
    # print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:${ticker}: Latest History Record: {datetime.datetime.fromtimestamp(history_data[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:Oldest History Record: {datetime.datetime.fromtimestamp(history_data[0].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:")


def backtest_ticker(alert_types, ticker, ticker_history, module_config):
    #ok so the idea here is to find each time in history where the alert type(s) fired on the ticker
    #once we find one, we add it to a result dictionary, structure listed below
    # {
    #     "timestamp":{
    #         "splus0": "", #agg bar at time of alert
    #         "splus3": "", #agg bar at time of alert +2
    #         "splus5": "", #agg bar at time of alert+4
    #         "splus7": "", ##agg bar at time of alert+6
    #         "splus9":"" #agg bar at time of alert+8
    #     }
    # }

    # once we have results, we can calculate our averages
    #turn off logging
    # module_config['logging'] = False
    if len(ticker_history) < 20:
        raise Exception(f"Cannot backtest ticker with {len(ticker_history)} history records, need at least 20")

    backtest_results = {}
    # start ten bars in the past so we can do our forward looking
    for i in reversed(range(10, len(ticker_history)-10)):
        _th  = ticker_history[:i] #basically the idea here is that we work backwards in time, calculating alerts and alert types at each increment
        #if the increment alert types match the input alert types, we write a result entry for ti
        if module_config['logging']:
            print(f"{datetime.datetime.fromtimestamp(_th[-i].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:{ticker}: Processing Backtest Data")
        _alert_types = []
        for indicator, eval in alert_functions.items():
            indicator_data = data_functions[indicator](ticker, _th, module_config)
            if eval(indicator_data, ticker, _th,module_config):
                # print(f"{datetime.datetime.fromtimestamp(_th[-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern'))}:{ticker}: {indicator} triggered")
                _at = alert_type_functions[indicator](indicator_data,ticker, _th,module_config)
                if _at != None:
                    _alert_types.append(_at)

        #ok so now that we have our alert types for this timebar, check to see if they match the input alert types
        # if not, we will just ignore them
        ignore = False
        for alert_type in alert_types:
            if alert_type not in _alert_types:
                ignore = True
                break
        if ignore or len(alert_types) != len(_alert_types):
            continue

        #ok now we can generate our results for the moment
        #     "timestamp":{
        #         "splus0": "", #agg bar at time of alert
        #         "splus3": "", #agg bar at time of alert +2
        #         "splus5": "", #agg bar at time of alert+4
        #         "splus7": "", ##agg bar at time of alert+6
        #         "splus9":"" #agg bar at time of alert+8
        #     }
        # }
        backtest_results[f"{datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')}"] = {
            'splus0':ticker_history[i],
            'splus3': ticker_history[i+2],
            'splus5': ticker_history[i+4],
            'splus7': ticker_history[i+6],
            'splus9': ticker_history[i+8],
        }
        #ok so now let's do the next trading day
        # entry_timestamp  =
        _nti = 1
        ntd_calculated = False
        while not ntd_calculated:
            try:
                if datetime.datetime.fromtimestamp(ticker_history[i+_nti].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).day > datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).day and datetime.datetime.fromtimestamp(ticker_history[i+_nti].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).hour == 9 and 'ntdo' not in backtest_results[f"{datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')}"]: #last bit ensures we are looking at open data
                    if module_config['logging']:
                        print(f"Calculated NTDO for {ticker}: {datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')} NTD ==> {datetime.datetime.fromtimestamp(ticker_history[i+_nti].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')}")
                    backtest_results[f"{datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')}"]['ntdo'] = ticker_history[i+_nti]
                    # break
                elif datetime.datetime.fromtimestamp(ticker_history[i+_nti].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).day > datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).day and datetime.datetime.fromtimestamp(ticker_history[i+_nti].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).hour == 15 and 'ntdc' not in backtest_results[f"{datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')}"]: #last bit ensures we are looking at open data
                    if module_config['logging']:
                        print(f"Calculated NTDC for {ticker}: {datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')} NTD ==> {datetime.datetime.fromtimestamp(ticker_history[i + _nti].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')}")
                    backtest_results[f"{datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')}"]['ntdc'] = ticker_history[i + _nti]
                    # break
                else:
                    _nti = _nti +1
                ntd_calculated = 'ntdo' in backtest_results[f"{datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')}"] and 'ntdc' in backtest_results[f"{datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')}"]
                if ntd_calculated:
                    if module_config['logging']:
                        print("Finished calculating NTD/C|O")
            except:
                traceback.print_exc()
                print(f"Cannot calculate NTD for {datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')} after {_nti} periods {datetime.datetime.fromtimestamp(ticker_history[i+_nti-1].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')}")
                del backtest_results[f"{datetime.datetime.fromtimestamp(ticker_history[i].timestamp / 1e3, tz=ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')}"]
                #ok so if e
                break

    for match_date, match_data in  backtest_results.items():
        print(f"{ticker} fired alert types ({','.join(alert_types)}) on {match_date}")
        _result_string = ""
        for _type, _values in match_data.items():
            print(f"{_result_string} {_type}|O:{_values.open}|H:{_values.high}|L:{_values.low}|C:{_values.close}| O|C Delta between {_type} and splus0: {float(_values.open)-float(match_data['splus0'].open)}|{float(_values.close)-float(match_data['splus0'].close)}")
    process_results_dict(backtest_results, module_config)
def process_results_dict(backtest_results, module_config):
    #ok so here we need to generate a csv from the data here
    rows = [['timestamp', 'splus0','splus0_delta','splus0_delta_percentage','splus3','splus3_delta','splus3_delta_percentage','splus5','splus5_delta','splus5_delta_percentage' ,'splus7','splus7_delta','splus7_delta_percentage','splus9','splus9_delta','splus9_delta_percentage', 'ntdo', 'ntdo_delta','ntdo_delta_percentage', 'ntdc', 'ntdc_delta', 'ntdc_delta_percentage']]
    for ts,data in backtest_results.items():
        try:
            row = ['' for x in rows[0]]
            row[rows[0].index('timestamp')]= ts
            highs = []
            lows = []
            deltas = []
            for k, v in data.items():

                highs.append(float(v.high))
                lows.append(float(v.low))
                deltas.append(float(v.close)-float(data['splus0'].close))
                if k == 'splus0':
                    del lows[-1]
                    del deltas[-1]
                    del highs[-1]

                row[rows[0].index(k)] =f"|O:{v.open}|H:{v.high}|L:{v.low}|C:{v.close}|"
                delta_key = f"{k}_delta"
                percentage_key = f"{k}_delta_percentage"
                # print(f"{os.getpid()} Keys: {json.dumps(rows[0])} key:{key}")
                _delta_index = rows[0].index(delta_key)
                _percentage_index = rows[0].index(percentage_key)
                row[_delta_index] =float(v.close)-float(data['splus0'].close)
                row[_percentage_index] =calculate_percentage(float(v.close)-float(data['splus0'].close),data['splus0'].close)

            row.append(float(data['splus9'].close)-float(data['splus0'].close)) #Total delta
            row.append(calculate_percentage(float(data['splus9'].close)-float(data['splus0'].close),float(data['splus0'].close))) #Total delta percentage
            row.append(statistics.fmean(deltas)) #average delta
            row.append(statistics.fmean(highs)) #average high delta
            row.append(max(highs)) #max high
            row.append(max(highs) - float(data['splus0'].close)) #max high delta
            row.append(calculate_percentage(max(highs) - float(data['splus0'].close),float(data['splus0'].close))) #max high percentag
            row.append(statistics.fmean(lows)) #average low delta
            row.append(min(lows)) #min low
            row.append(min(lows) - float(data['splus0'].close))  # min low delta
            row.append(calculate_percentage(min(lows) - float(data['splus0'].close),float(data['splus0'].close))) #min low percentage
            rows.append(row)
        except:
            print(f"Unable to process result entry at {ts}")
            traceback.print_exc()
    rows[0].append('total_delta')
    rows[0].append('total_delta_percentage')
    rows[0].append('average_delta')
    rows[0].append('average_high_delta')
    rows[0].append('max_high')
    rows[0].append('max_high_delta')
    rows[0].append('max_high_delta_percentage')
    rows[0].append('average_low_delta')
    rows[0].append('min_low')
    rows[0].append('min_low_delta')
    rows[0].append('min_low_delta_percentage')
    write_csv(f"{module_config['output_dir']}{os.getpid()}backtest.csv", rows)

def load_backtest_results(ticker, module_config):
    if not module_config['run_concurrently']:
        data = read_csv(f"{module_config['output_dir']}{os.getpid()}backtest.csv")
    else:
        data =  read_csv(f"{module_config['output_dir']}{ticker}_backtest.csv")
    json_data = {k:[] for k in data[0]}
    for i in range(1, len(data)):
        for ii in range(0, len(data[0])):
            try:
                json_data[data[0][ii]].append(float(data[i][ii]))
            except:
                json_data[data[0][ii]].append(data[i][ii])

    return json_data
def analyze_backtest_results(backtest_results):
    #pass
    #ok so here we are, 2 nights worth of coding to get to THESE calculations
    #first, do likelihood of long vs short
    processed_results ={}
    len(np.where(np.array(backtest_results['total_delta']) < 0)[0])
    len(np.where(np.array(backtest_results['total_delta']) > 0)[0])
    processed_results['likelihood_long_3'] = calculate_percentage(len(np.where(np.array(backtest_results['splus3_delta']) > 0)[0]), len(backtest_results['splus3_delta']))
    processed_results['likelihood_short_3'] =calculate_percentage(len(np.where(np.array(backtest_results['splus3_delta']) < 0)[0]), len(backtest_results['splus3_delta']))
    processed_results['likelihood_long_5'] = calculate_percentage(len(np.where(np.array(backtest_results['splus5_delta']) > 0)[0]), len(backtest_results['splus5_delta']))
    processed_results['likelihood_short_5'] =calculate_percentage(len(np.where(np.array(backtest_results['splus5_delta']) < 0)[0]), len(backtest_results['splus5_delta']))
    processed_results['likelihood_long_7'] = calculate_percentage(len(np.where(np.array(backtest_results['splus7_delta']) > 0)[0]), len(backtest_results['splus7_delta']))
    processed_results['likelihood_short_7'] =calculate_percentage(len(np.where(np.array(backtest_results['splus3_delta']) < 0)[0]), len(backtest_results['splus3_delta']))
    processed_results['likelihood_long_9'] = calculate_percentage(len(np.where(np.array(backtest_results['splus9_delta']) > 0)[0]), len(backtest_results['splus9_delta']))
    processed_results['likelihood_short_9'] = calculate_percentage(len(np.where(np.array(backtest_results['splus9_delta']) < 0)[0]), len(backtest_results['splus9_delta']))
    processed_results['likelihood_long_ntdo'] = calculate_percentage(len(np.where(np.array(backtest_results['ntdo_delta']) > 0)[0]), len(backtest_results['ntdo_delta']))
    processed_results['likelihood_short_ntdo'] = calculate_percentage(len(np.where(np.array(backtest_results['ntdo_delta']) < 0)[0]), len(backtest_results['ntdo_delta']))
    processed_results['likelihood_long_ntdc'] = calculate_percentage(len(np.where(np.array(backtest_results['ntdc_delta']) > 0)[0]), len(backtest_results['ntdc_delta']))
    processed_results['likelihood_short_ntdc'] = calculate_percentage(len(np.where(np.array(backtest_results['ntdc_delta']) < 0)[0]), len(backtest_results['ntdc_delta']))
    processed_results['average_price_increase_percentage'] =  statistics.fmean(backtest_results['average_high_delta']) if len(backtest_results['average_high_delta']) > 0 else 0.0
    processed_results['average_price_decrease_percentage'] = statistics.fmean(backtest_results['average_low_delta']) if len(backtest_results['average_low_delta']) > 0 else 0.0
    return processed_results
    # processed_results['likelihood_long_3']
    # processed_results['likelihood_short_3']
    # processed_results['likelihood_long_5']
    # processed_results['likelihood_short_5']
    # processed_results['likelihood_long_7']
    # processed_results['likelihood_short_7']
    # processed_results['likelihood_long_9']
    # processed_results['likelihood_short_9']
    # processed_results['likelihood_long_ntdo']
    # processed_results['likelihood_short_ntdo']
    # processed_results['likelihood_long_ntdc']
    # processed_results['likelihood_short_ntdc']
    # processed_results['average_price_increase_percentage']
    # processed_results['average_price_decrease_percentage']
    pass

