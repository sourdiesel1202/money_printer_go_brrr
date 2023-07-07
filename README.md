# money_printer_go_brrr
A collection of Python scripts for automating technical analysis
## market_scanner.py (Market Scanner)
### Setup
You will need to create a directory called `configs/` at the base level of the project. In this directory, create a file called `market_scanner.json`. 
This file requires the following configs

```
{
  "api_key": "POLYGON_APIKEY",
  "tickers": ["optional list of tickers (used for testing)"],
  "logging": true, 
  "process_load_size": 300,
  "test_mode": true
}
```

<table>
<tr><th>key</th><th>expected value</th></tr>
<tr><td>api_key</td><td>your polygon api key</td></tr>
<tr><td>api_key</td><td>an optional list of tickers</td></tr>
<tr><td>api_key</td><td>whether or not to log output to console</td></tr>
<tr><td>api_key</td><td>how many tickers to process in a single process. Defaults to 300</td></tr>
<tr><td>test_mod</td><td>when using test mode, ticker list is limited to 100 (use for debug)</td></tr>
</table>
