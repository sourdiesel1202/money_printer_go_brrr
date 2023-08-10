import time
import traceback

# from enums import AlertType, PositionType
# from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime

from db_functions import load_nyse_tickers
# from db_functions import write_ticker_profitable_lines,load_profitable_line_matrix
from history import load_ticker_history_raw, load_ticker_history_db, load_ticker_history_cached
# from validation import validate_ticker
from functions import load_module_config, get_today, obtain_db_connection, process_list_concurrently

from profitable_lines import compare_profitable_ticker_lines_to_market, load_profitable_line_matrix, find_ticker_profitable_lines


# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])

# from shape import compare_tickers
def compare_tickers_lines_to_market(tickers):
    # module_config = load_module_config('profitable_line_scanner_db')
    # tickers = load_nyse_tickers(connection, module_config)
    module_config = load_module_config('profitable_line_scanner_db')
    connection = obtain_db_connection(module_config)
    for ticker in tickers:
        try:
            print(f"Loading profitable lines for {tickers.index(ticker)+1}/{len(tickers)}: {ticker}")
            # profitable_lines = find_ticker_profitable_lines(ticker, load_ticker_history_db(ticker, module_config, connection=connection), module_config)


            # def write_profitable_lines(connection, ticker, ticker_history, profitable_lines, module_config):
            # write_ticker_profitable_lines(connection, ticker, load_ticker_history_db(ticker, module_config, connection=connection),profitable_lines,module_config)
            # find_ticker_profitable_lines(ticker, load_ticker_history_db(ticker, module_config, connection=connection), module_config)
            # load_ticker_history_db(ticker, module_config, connection=connection)
            # load_profitable_line_matrix(connection, module_config)
            compare_profitable_ticker_lines_to_market(connection,ticker, load_ticker_history_cached(ticker, module_config,), module_config, read_only=False)
            print(f"Loaded profitable lines for {tickers.index(ticker)+1}/{len(tickers)}: {ticker}")
        except:
            print(f"Could not find profitable lines for {ticker}")
            traceback.print_exc()
    connection.close()
if __name__ == '__main__':
    # def load_ticker_history_db(ticker, module_config, connection=None):
    start_time = time.time()
    module_config = load_module_config('profitable_line_scanner_db')
    connection = obtain_db_connection(module_config)
    # tickers = load_nyse_tickers(connection, module_config)
    tickers=  ["AURC","ATIF","BJ","BFC","AMZN","BIG","CACI","BIPC","CARA","AMEH","AMD","AQST","APCA","CCRN","AX","BAP","BTTX","AWIN","BOF","ACON","BDL","ACAC","BIOL","AGAC","BASE","CBOE","CCLD","AZTA","ADUS","BOTJ","APTV","ADP","BBIO","AMST","ASTR","BZFD","BIMI","ACHR","CAE","ANGI","BFAC","APPH","ALSN","ASGN","BFRG","C","BCEL","BNTC","BGC","ACCD","ANAB","BHE","BTBT","AUPH","BBU","AVDX","APT","ASRT","ASUR","BXRX","AMRK","ADCT","AEHR","CARR","BL","BPOP","APH","AIV","AAME","AKU","BKYI","BA","CCD","ADTH","AGNC","AQMS","BJRI","ADSK","APLE","CAG","ADI","ACLS","AQN","BMO","BWA","BPYPN","CALM","AGO","AUUD","BHG","ASRV","AMPL","BH","ARQT","BCSF","AMPY","ATS","ALNY","ANY","BAND","AMTB","AEM","AIM","BELFA","AMSF","APXI","AVTX","AVT","AGL","AOSL","CAC","BAH","CDXS","AEO","AKTS","CACO","ACAD","ATNI","BLND","BRZE","ACBA","AWX","BENF","AAPL","BLD","BPMC","BROG","BYND","CASS","BCOW","BFH","ARIS","ATXI","BDC","CBFV","CARV","BCRX","BLK","AP","BRD","AZEK","AMG","ACEL","AUDC","BEN","CARG","ARAY","ADBE","BITF","BCAL","ANEB","BCC","AE","CEI","AMBC","AGNCO","APGN","AURA","ATAK","BF.B","CENT","AMGN","ASNS","AFG","ARTNA","ALGS","CDRO","BANF","BGI","AVD","BGLC","AKBA","BANL","BMEA","AKA","BYNO","CAMT","ADPT","BPYPM","ARRY","AMNB","BAM","APP","ARCE","CABO","BHFAO","AMPH","CAVA","BTBD","AGAE","BERY","ASTE","CDMO","BKSY","AEL","BOC","ALE","APMI","AGM.A","BIAF","ABUS","BRKL","CASI","BHB","BSRR","CBRG","CABA","ATXG","ADTX","ACIW","AMCR","BHLB","BACK","BSQR","AAON","BODY","AMR","AVNS","BRN","AGLE","BYN","ASO","CANO","BXMT","ANGO","BBY","AA","ARWR","ACU","AVGO","BGS","ANDE","BLAC","CELZ","ALVO","BX","CCTS","BFAM","ASCA","APLT","BRP","AMKR","AMK","AXON","BFIN","BFS","BLX","BURL","AACI","AAU","BJDX","ABL","BECN","AAN","ABST","CCO","ATLC","ALK","BTG","ARR","BDN","CAR","ATI","AON","AGS","APA","AEZS","ACAQ","ACAX","AGFY","BCBP","BCML","CALB","BRSH","BBDC","AMP","ALTU","ALG","AFYA","BGFV","AEVA","BHFAM","ARES","BSM","AEI","BLBX","BROS","AMTX","APTO","ATKR","BHAT","BATRA","APOG","CEIX","AAC","ACLX","ASMB","BYTS","AOMR","ATER","CACC","AEAE","ARVN","CASH","ALLE","CBRL","BRDG","CCAP","BRID","AFRM","ALCC","ARNC","AZZ","BAER","BIIB","BMRN","BRT","CCS","AREB","AUGX","AFTR","BPT","BKKT","AMWD","ARCT","BCOV","CCEL","ALSA","AYTU","APO","BKCC","ADEX","BORR","AQU","AVIR","ARKO","BKE","BEPC","CCJ","BDTX","ASTI","BNMV","CCSI","BH.A","BNED","APYX","ARBG","BACA","BG","CB","ATIP","AKR","ARCB","ATOM","AG","AGRX","BIO","BANR","BHR","BATL","ANIX","ABIO","AMSC","AREN","BIO.B","BLUE","BRCC","AOS","AKLI","BCSA","ALLO","CDNS","BBIG","AMTI","ACB","AVXL","ARAV","BTCY","AES","CDLX","AMCX","ACM","CELU","AMPX","APPN","AZYO","AQB","BKTI","BTU","ATO","BON","BYD","AIB","ATEK","ARHS","CBAY","AXTA","AMPS","BNRG","BRX","AGM","CASA","AHCO","BLIN","ADM","ASPS","BEAT","AUID","CBSH","CCK","BHVN","ADER","ACR","AIN","AGTI","AGRI","ACCO","BAFN","AROC","BCAN","BTB","BWBBP","ADIL","AVGR","BZH","CATO","ARRW","BPYPO","ALX","AOGO","AEPPZ","BLBD","AACT","CCEP","CELL","CCLP","CCRD","APPS","BEP","AIT","BHC","BXP","BMRA","CENN","APG","BOCN","AMT","ACER","BSX","ARKR","CCB","BOWL","AOUT","ARQQ","AFRI","BSET","AAMC","BNRE","ASPA","CCL","AADI","ACRV","CDE","CBAN","BHRB","BRLI","ALLT","ALCY","CCAI","ABCL","BMY","ABCB","ACN","ALOT","ASTC","ACHC","AUMN","AVID","ALEC","ALLG","CATY","ATRO","AVHI","BFST","AMLI","ALPP","CDZI","BDSX","ABC","ATR","ALXO","ACRS","ARTE","ATRI","AXLA","CEG","AMPE","BSIG","AZTR","AIMD","ABM","AGE","ADRT","APAC","CASY","BYFC","ATTO","AVTR","AFMD","BPTH","ARE","BSBK","BRTX","AXL","APGE","AMOT","CE","ALOR","AMRS","AYI","BOKF","AAIC","BSFC","ANIP","AXDX","APLM","AEYE","ACI","ARCH","CCI","BIOX","AUBN","BNL","BARK","BTWN","BOOT","ADVM","ALYA","BIOR","BWXT","ALTR","ALDX","ATRC","AVTE","BLDR","AMPG","AR","ATAI","BLDP","ARBB","ASYS","AIZ","BNIX","BCAB","BLZE","BMBL","AMBA","BRK.A","BWV","ACA","ATMC","AMC","ARCO","AAT","ATSG","AVA","ACOR","ALBT","AEE","APD","ALL","ASLE","ATEX","BCLI","AWR","AYX","AGMH","CALX","BALY","AGCO","AIRG","AXS","BOOM","CC","AEG","BRY","AIRS","AER","ALZN","CARE","AFIB","BLUA","ATEC","BTTR","BKSC","AGNCL","AESI","ADMP","AMH","ARLP","BBUC","BOAC","BRBS","BRK.B","CADE","BKNG","BMRC","ACRE","ARBE","CCVI","AWH","ALEX","AIRC","BIOS","BAOS","AAOI","ADOC","ATXS","BSGM","ALRM","ABNB","AMBI","AFL","BATRK","BSY","ADEA","AY","ABR","BDX","AUR","BCPC","AVAV","AENT","ATNF","AWRE","ALGN","BF.A","ACET","BHIL","BREZ","ATVI","AZ","CCBG","ATLX","ALGT","ANSS","BAC","ARGO","ALLR","AHT","ARL","ANVS","AMBP","ARTW","ASC","BURU","CAAS","BOXL","AGI","CARM","APTM","AFBI","BYSI","AGIO","ALPN","ARYD","ACRX","BHM","AIHS","BOH","CAH","ABSI","AJG","APLS","CBNK","AVPT","BFLY","BCTX","ATEN","BTOG","ASPN","ATHX","BUSE","CAPR","ABEO","ALKS","BIP","BWEN","AVNT","CAKE","BKD","AIP","ALTO","ACST","APDN","ASCB","BILL","BANC","BMAC","BUR","BLNK","ADV","BBW","ATUS","BWFG","AEHL","ANZU","AN","BSVN","CCCS","BEAM","BCO","ANTX","BBGI","BWB","ALGM","ADC","AGRO","ABOS","AUVI","AIRT","BBCP","ANGH","ACAB","BBAI","ARC","BBSI","BTMD","BWC","CBRE","CALC","CELH","ALVR","BHF","ARVL","CCCC","ARTL","BRDS","BRBR","CBIO","CCF","ADN","ARMK","BV","CATC","BTDR","BBLG","APRN","BKI","CDRE","BN","BAX","AEP","BFRI","BLKB","BXSL","AMRC","CDIO","ATOS","AXR","ASPI","ALRN","ARDX","ASIX","AVAH","APPF","ALTG","AMLX","BYRN","ANF","ACMR","AMAT","AVNW","BRAG","AMAO","BMTX","ASST","ALV","ATHA","BKR","CBL","AMN","BANX","CATX","BLCO","APRE","AXTI","AUST","ANIK","AVRO","ACXP","AHH","CELC","AGX","AROW","AGR","AM","ABT","B","AMAL","CADL","CBAT","ATMV","BRLT","ALLY","BIRD","BSAQ","ACVA","ALT","AMSWA","ARMP","ASTL","AMWL","BOLT","CDAY","BB","AYRO","BC","BTE","BWMN","CAL","AGEN","AFCG","ARCC","ADMA","BOSC","AUB","ACIU","CDXC","ADT","ADTN","BHFAN","BLFY","BMI","AORT","BLNG","AULT","ANET","ARLO","CEAD","AB","AFAR","CBU","CCV","ALLK","CBUS","ACDC","BLPH","A","BLDE","AVTA","BGSF","AMS","BWAQ","ACAH","AKYA","ASXC","CDW","ASH","CBT","APGB","AJX","BFI","ACNT","BW","BXC","AWK","APM","CARS","AEIS","AIR","BITE","ALKT","AXSM","BEEM","BRC","BRFH","AKAM","AL","ATNM","ABG","ADSE","BREA","BRKR","ACGN","BRQS","ASB","AEY","AIG","ALCO","ALIM","ATAQ","BNGO","BKU","ATRA","BE","AGBA","ATGE","BOX","ASAN","APWC","ADNT","ARI","BK","AINC","CDTX","ACGL","ALC","AREC","BELFB","ADD","APLD","ANNX","BCE","AIRI","ABVC","BVH","ASTS","ACT","BLMN","APCX","ABBV","BPRN","BWMX","AGYS","BLFS","ACNB","AKRO","APEI","AGIL","AMRX","BLEU","BRKH","BVS","BIGC","BBWI","BIOC","ACHV","ALIT","BCDA","AI","ARW","AXP","BHFAL","CBZ","AEMD","AZO","AAP","ALTI","CDAQ","BTM","BRSP","CAT","BTAI","AZPN","BALL","ACTG","ACRO","ATLO","AWI","BY","ARIZ","BGXX","CAMP","AC","AXNX","ALRS","BIVI","ASM","AVY","ALHC","BKH","BRO","ALB","BHAC","AME","CAPL","AXGN","BNS","APVO","CDNA","APAM","ACGLN","AVB","CCNE","CECO","AMED","AKAN","BRAC","AAL","AJRD","BMR","ADES","CAAP","AVO","CCOI","BR","ATMU","BTCS"]

    # def process_list_concurrently(data, process_function, batch_size):
    process_list_concurrently(tickers, compare_tickers_lines_to_market, int(len(tickers)/12)+1)
    # find_ticker_profitable_lines(tickers[0], load_ticker_history_cached(tickers[0], module_config), module_config)
    # compare_profitable_ticker_lines_to_market(connection, tickers[0], load_ticker_history_cached(tickers[0], module_config, ),module_config, read_only=False)
    # load_profitable_line_matrix(connection, module_config)
    connection.close()

    print(f"\nCompleted Profitable Line test of {len(tickers)} tickers in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")