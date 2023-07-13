from functions import timestamp_to_datetime


def validate_ticker_history_integrity(ticker, ticker_history):
    invalid  = 0
    print(f"Validating {len(ticker_history)} entries")
    for i in range(0, len(ticker_history)-1):
        #case for next day
        current_bar_ts = timestamp_to_datetime(ticker_history[i].timestamp)
        next_bar_ts = timestamp_to_datetime(ticker_history[i+1].timestamp)
        if current_bar_ts.hour == 16 or current_bar_ts.hour == 15 and next_bar_ts.hour != 16:
            #case for close
            if next_bar_ts.hour != 9:
                print(f"${ticker} has gap in timeseries data: Current: {current_bar_ts.strftime('%Y-%m-%d %H:%S:%M')} Next: {next_bar_ts.strftime('%Y-%m-%d %H:%S:%M')} ")
                invalid = invalid +1
        else:
            if next_bar_ts.hour != current_bar_ts.hour+1:
                print(f"${ticker} has gap in timeseries data: Current: {current_bar_ts.strftime('%Y-%m-%d %H:%S:%M')} Next: {next_bar_ts.strftime('%Y-%m-%d %H:%S:%M')} ")
                invalid = invalid + 1


    if invalid > 0:
        print(f"${ticker} has corrupt history data")
    else:
        print(f"${ticker}'s history data is valid")
    #     pass