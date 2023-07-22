from mpb_html import build_dashboard
from functions import load_module_config, get_today
# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
module_config = load_module_config('market_scanner_tester')
# from shape import compare_tickers
build_dashboard(module_config)