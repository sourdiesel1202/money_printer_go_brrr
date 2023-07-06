# This is a sample Python script.

# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from polygon import RESTClient
from functions import  load_module_config
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    client = RESTClient(api_key=module_config['api_key'])
    ticker = "AAPL"

    quote = client.get_last_quote(ticker=ticker)
    print(quote)
    # List Aggregates (Bars)
    # aggs = []
    # for a in client.list_aggs(ticker=ticker, multiplier=1, timespan="minute", from_="2023-01-01", to="2023-01-02",
    #                           limit=50):
    #     aggs.append(a)
    #
    # print(aggs)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
