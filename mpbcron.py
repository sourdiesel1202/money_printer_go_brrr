import os, datetime
import time

while True:
    if datetime.datetime.now().minute ==18:
        os.system("source /var/virtual_environments/mpb/bin/activate && cd /var/app/money_printer_go_brrr && python market_scanner.py > /var/log/mpb.log")
    else:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%D:%S')}:It's not time to run yet, going to sleep")
        time.sleep(30)