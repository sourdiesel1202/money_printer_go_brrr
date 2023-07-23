import os, datetime
import time

while True:
    if datetime.datetime.now().minute in [18,48]:
        os.system("/var/virtual_environments/mpb/bin/python3 ./market_scanner.py")
    else:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%D:%S')}:It's not time to run yet, going to sleep")
        time.sleep(30)