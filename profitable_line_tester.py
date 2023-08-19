import time
import traceback

# from enums import AlertType, PositionType
# from backtest import backtest_ticker, load_backtest_ticker_data, backtest_ticker_concurrently, load_backtest_results, analyze_backtest_results
import polygon, datetime

from db_functions import load_nyse_tickers, combine_db_update_files, execute_bulk_update_file
# from db_functions import write_ticker_profitable_lines,load_profitable_line_matrix
from history import load_ticker_history_raw, load_ticker_history_db, load_ticker_history_cached
# from validation import validate_ticker
from functions import load_module_config, get_today, obtain_db_connection, process_list_concurrently
from market_scanner_db import is_ticker_eligible

from profitable_lines import compare_profitable_ticker_lines_to_market, load_profitable_line_matrix, find_ticker_profitable_lines


# module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])

# from shape import compare_tickers
def compare_tickers_lines_to_market(tickers):
    # module_config = load_module_config('profitable_line_scanner_db')
    # tickers = load_nyse_tickers(connection, module_config)
    module_config = load_module_config('profitable_line_scanner_db')
    connection = obtain_db_connection(module_config)
    for ticker in tickers:
        # if is_ticker_eligible(ticker, t)
        ticker_history = load_ticker_history_cached(ticker, module_config)
        if not is_ticker_eligible(ticker, ticker_history, module_config):
            continue
        try:
            print(f"Loading profitable lines for {tickers.index(ticker)+1}/{len(tickers)}: {ticker}")
            # profitable_lines = find_ticker_profitable_lines(ticker, ticker_history, module_config)


            # def write_profitable_lines(connection, ticker, ticker_history, profitable_lines, module_config):
            # write_ticker_profitable_lines(connection, ticker, load_ticker_history_db(ticker, module_config, connection=connection),profitable_lines,module_config)
            # find_ticker_profitable_lines(ticker, load_ticker_history_db(ticker, module_config, connection=connection), module_config)
            # load_ticker_history_db(ticker, module_config, connection=connection)
            # load_profitable_line_matrix(connection, module_config)
            compare_profitable_ticker_lines_to_market(connection,ticker,ticker_history, module_config, read_only=False)
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
    tickers = load_nyse_tickers(connection, module_config)
    # tickers=  ["NFYS","SNCR","FBIZ","CHD","DLX","KNDI","SEED","DWAC","DKL","OGI","DTI","NGD","HHGC","NNBR","OSA","PROC","MGY","OHAA","TBLT","ICMB","STEP","LTRPA","ROOT","NECB","TPHS","SMWB","SPHR","EQH","ITAQ","UAA","ELSE","CNC","WNC","ZAPP","XPOF","HBB","TPCS","OCS","NSP","PDM","PSTL","TRC","SSSS","TKR","WAVS","LKCO","TMO","CXT","M","MCHP","SASI","COF","EVEX","GHRS","FLNG","GETY","LEV","PRTK","MFA","NOA","GH","NG","EQR","RIOT","SUN","RYAN","CURI","IGTA","HHLA","JAQC","PHG","DT","IMGN","PWR","VTGN","VBLT","EBON","DYN","MAX","PEGR","INZY","FTV","OSBC","CNQ","NEGG","VICR","MGTA","FLXS","NET","PTHR","SUM","PIRS","GORO","LAND","TGTX","VIRX","GEVO","WISA","GEL","NRDY","IPXX","CPG","NATI","PFIN","TNP","NXGN","LYRA","EMLD","NVEI","PPG","FYBR","ZJYL","IMKTA","KALA","TXT","TNC","SHC","UVV","DISA","TIVC","GAINL","USPH","CNXA","FE","HSHP","PRPH","UVSP","ENVA","LGO","MPAA","SBOW","TRST","VPG","CLAR","INTZ","LTRN","OIG","PMD","FTHM","CUEN","INM","LIVB","GMED","MODV","TITN","STHO","FRT","INDO","MGRX","PRCH","SANA","NCSM","GLTO","TORO","VAXX","VRM","LSEA","GDDY","SMLP","TOP","GAQ","GLYC","EEFT","VS","DXCM","FNWD","VIRI","VMC","EP","CRSP","HSY","KLXE","OMEX","RPHM","HUM","PRDS","YELP","MCS","MATX","CNK","KAR","ESP","INNV","TDOC","SKYX","NLSP","SANW","GO","CF","HSDT","FBRT","WEYS","TWOU","LNKB","JPM","XFOR","FIBK","IOBT","CI","VRTV","CSV","UBA","GPS","TIRX","TBLA","UDR","JCTCF","HURC","CFFI","WING","CHKP","PACB","KD","KO","ESGR","SLRX","XPDB","RMAX","UHG","DMTK","HEES","INFN","JBSS","HWBK","NCPL","PENN","MEDP","FTI","ETD","IIIN","ISRG","FCN","ONTF","RBBN","CULL","DIST","KGS","CKPT","TRIP","MEC","FULT","SND","EGO","MTB","JNJ","XGN","HLGN","FLO","VINC","RAPT","GD","ROL","COLD","MBINO","MIST","QCOM","ONCT","EPAC","TRVN","SES","UIS","MCRI","CSSE","FORM","MDLZ","RRBI","JRSH","WIRE","EVE","MAG","EVOK","DDD","NSTB","UBSI","GBDC","PFMT","THMO","HUGE","HP","VALU","LMNL","SUNW","LPTH","HTCR","PCTY","UBFO","REFI","VLGEA","HPCO","HRT","RYTM","LSTA","MNMD","PALI","PCT","SOFI","MQ","SBLK","SISI","TMC","FSV","HBANM","CFMS","FNWB","NKTX","KIRK","GLDG","COOL","NCRA","VGR","WELL","WSM","HAL","EIGR","ODP","NARI","FUSN","PGY","RPT","STLD","WIX","JBGS","PPIH","FL","IPI","LINK","ELDN","MCLD","OCG","LCTX","RGEN","ELME","LHX","UBS","PTCT","SCYX","CIA","NWBI","EG","PETZ","CEQP","CRCT","SFL","PBF","REKR","HTLF","MGNX","H","MNTK","PLM","TPST","OMI","DALS","ELBM","JILL","VERX","ODC","DMS","OTRK","PL","XXII","KINS","CKX","SUPV","CGA","KEX","DNA","IGMS","SHLS","SPG","RACE","NCNO","JZXN","FRHC","NMG","EGLX","NFG","FISI","SITM","UHAL","DLTR","COCP","PNC","KLIC","SHAP","ZOM","OBDC","NVOS","SHO","CVLG","VII","CNSP","LAZ","ESTA","VXRT","FTDR","HNST","WBA","FSNB","DESP","GEF.B","RGC","FIP","RPD","IQV","RYI","OWLT","RMTI","EYE","EFSC","FCX","RSSS","SMMF","USB","DOW","EXAS","CRUS","INMB","LYFT","SSIC","CTM","GAME","MODN","LICN","NVGS","SMAR","COGT","CVU","GLBS","JBI","FBIN","SPWR","PRPC","VSTM","GPOR","MULN","RSI","NVAC","SGH","CYN","CLBK","FNLC","FITB","HR","NDSN","DLNG","LMND","STZ","NHC","EXPO","LGST","DCTH","FWRD","ESPR","CXAC","IP","ODD","CVGW","MOVE","WMPN","CLWT","IPWR","VRSK","RC","RNW","PTLO","UTI","VAC","NVAX","EPM","MOBV","WLFC","UHS","NOW","CTRE","UFCS","HES","PTON","WLDN","CLIR","GLBE","LTRPB","PHUN","SBFM","OPRT","SLCA","STNE","RFAC","SLF","SPRC","JRVR","TCBK","CPK","MCBC","POR","FVRR","CYH","DFFN","HCWB","DMYY","GGE","PM","WORX","FRPH","WU","TMUS","PERI","DAKT","OSPN","IMO","SAVA","SWK","FTII","HAFC","COEP","WEST","NUVA","LGHL","OXY","USFD","EHAB","IOR","CLRO","MCK","PAYX","CIEN","MAT","CUTR","SII","SAL","LUCY","MWG","MDNA","ERO","VIGL","TKNO","EOLS","DVAX","TGLS","MAPS","CFB","FIAC","WRAC","MSBI","HOFV","WWR","WH","DAN","HOV","INTS","CWBR","MTR","ITGR","NM","TEX","MKUL","PZG","CISS","FRBN","OSI","CFFE","FITBO","EPD","VERO","STRC","CLEU","PLTR","SNV","WSO","STRT","CERS","LTH","PSTG","HLT","DOX","INBS","HYMC","RSVR","OXSQG","JMSB","TCOA","CNSL","CSR","HRL","TTNP","CSCO","PTVE","DINO","ONL","TFSL","OLP","GDC","SCOR","INDV","DARE","MRVL","TCRX","TRN","PINE","MRTX","PHGE","RMD","DFLI","GBR","FULTP","RXO","HBCP","CHWY","LOAN","HUBG","MRCY","MGRC","UAVS","VTR","DO","COTY","FRSH","RXST","CNTY","IMRX","SPRB","LAUR","NVST","SNEX","TLGY","POWL","PRTG","ODFL","CRWD","NVT","WHG","GTEC","CSWCZ","GIA","HA","DCI","LPLA","CUBE","SRI","DOV","OPA","PCOR","PYCR","SSU","PIPR","CRGO","WSBF","CNNE","MARA","K","NOVV","PAR","SAVE","LNW","CYT","QOMO","GMFI","SWKS","LBBB","STRS","MCO","FREE","VNCE","GPRE","GRWG","LTRY","RITM","RWOD","OTIS","LULU","FSLR","SVRA","SBFG","UHAL.B","EYPT","PCYG","HCC","MTTR","EQIX","VRPX","U","DENN","IRAA","KFRC","PECO","OABI","NRP","XLO","TROO","YORW","ENTG","COUR","TENX","CETY","GCBC","GGG","PNNT","KA","CPA","CVNA","WE","O","CNP","LSXMB","ONEW","KPRX","RNR","LEGH","HLMN","FXLV","IART","OXUS","KMDA","PCTI","CSBR","LUV","SWKH","PLCE","TDC","FPAY","LILA","PEBK","LBTYB","HURN","GHC","WTER","SAIC","EFXT","GWRE","XAIR","CGNX","EFX","HHC","COYA","PRLH","FRST","MRDB","OXSQL","PNBK","TCMD","HUSA","STIM","WALD","CVE","ESHA","TATT","TRNS","WPC","HITI","LOGI","ME","PROK","GKOS","QUAD","LPRO","WERN","VRA","SHPW","GMRE","NXGL","GRTX","HWM","MCBS","OPOF","EMBK","EGRX","ESGRP","FSFG","HRB","NRC","CXAI","FIS","OMF","RILYN","IBCP","ITRG","ISUN","STER","IBOC","INFU","MGM","MITT","TRON","OSUR","COOP","SNPS","ZVIA","LRN","CTCX","OTTR","WINV","VICI","LEU","NOVN","NMRD","FULC","HLLY","NTIP","DXYN","DM","INAB","GAINZ","KMPR","LGVC","IRNT","NLS","NXPL","ZKIN","XHR","REAX","WD","LITM","MGTX","KTTA","LIFE","NBST","ROSE","CNXN","MOS","HTBI","IHRT","RICK","TRIS","CURV","REAL","HCKT","RXRX","LASE","GCT","NVCT","NMTR","JKHY","EMX","CLRB","DBGI","NVTA","SHBI","NATH","OMER","EDUC","GRNT","TECK","ESLT","ULH","PRE","INVZ","CNM","FROG","DOMH","NVNO","OFC","PX","MGYR","NXTP","ENV","CHEF","OEC","ORLY","CING","OLLI","SG","SRE","WOW","RILYK","FGI","MMM","MRUS","RLYB","SABS","SCRM","KRNT","VRT","MCY","CYCN","IIPR","FCCO","PNRG","UPH","STOK","CYD","IVT","MNTS","CUZ","PNR","LYTS","TTOO","LRFC","DELL","CVM","MBC","IMPL","LTBR","MACK","VZ","IPW","LSXMK","ESAC","LBPH","TK","TOPS","VET","SNCY","KOD","RLMD","ISPR","WTFC","SOHO","HPQ","EQX","MITQ","HCSG","NEWP","TECH","OR","TGH","YUM","DRH","EBF","ENLV","HALL","JAZZ","CNOB","CODI","NTRB","PSHG","YS","GTY","MOFG","PLMI","SCCO","WHD","SJM","CQP","PRAX","CVS","EQC","JCSE","DNOW","JXJT","MBTC","NGMS","RTL","TMP","MDWD","WAFU","SMBC","KNTE","NXST","ML","EAC","KDP","CHCI","SHEN","CRNT","LGND","LGL","TSE","WTW","EDRY","FIZZ","DBI","ERII","GPK","ITCI","SXI","STEM","XRX","TFFP","GTLS","GNTX","PXS","SMLR","CYCC","UTL","WFG","GILD","LUMN","PFG","VTNR","EAT","MAQC","MP","RMBL","CNO","YTRA","EFOI","MMC","CRM","ZM","PRK","WSC","RCAC","CTKB","HOLI","LAMR","RBA","RLI","NBHC","WULF","RAMP","YVR","CFSB","EZGO","PEPL","PPSI","MDIA","KNX","LBRDK","RUSHB","GATX","SLRN","OCFC","HGV","OB","RVSB","STRM","TRCA","EFSH","NAPA","XYL","NVRI","DRVN","SSKN","PH","RFL","TIO","ORIC","NFTG","FRME","MPLX","SGRY","INO","VIAV","FEXD","HOPE","IBKR","HBANL","ELF","FLWS","SEAT","TRUE","EQRX","ISPC","NREF","TTGT","PLUR","COST","VOXX","IDN","OAKU","ICPT","MAS","KAMN","ZD","XERS","PKST","INOD","UPC","LOW","PSMT","WEAV","SNX","CEVA","MTDR","OPTT","PGC","STKL","EHC","MKL","CRVS","GGR","SVVC","ZIVO","EFC","HVT","MG","SHYF","SASR","XMTR","CXDO","STXS","CFR","CXM","LKQ","PTMN","GOGO","DTE","TJX","NDRA","NYMT","DIT","STAG","CNGL","EPOW","CNI","WTI","FTRE","SNCE","KTRA","TT","TARS","EIX","HNRG","NINE","KXIN","NISN","TROW","LAD","LAW","SWN","TTMI","CRL","DCGO","PBTS","UCBIO","RWLK","CNX","KURA","PXLW","REI","OSTK","TCN","CME","CYBN","DX","INCY","GNRC","MDVL","NOTV","COOK","SIF","SVV","HIBB","PED","LII","TRKA","NWFL","NXPI","OPAD","MOXC","NGVT","TMST","TYRA","CSLM","HVT.A","MNST","KBR","CTS","RSLS","EVH","MMMB","GLPI","SPNT","UROY","PIXY","WGO","INTU","EGP","SMPL","VERY","PDEX","SFNC","FRTX","ZBH","HALO","DASH","GASS","MRT","OKTA","FATBB","TMBR","TNON","DALN","LANDO","NBSE","KTOS","KYMR","TRINL","IT","VSTO","SURF","IVDA","FNA","ZUO","CULP","CVAC","HIPO","HUDA","TTWO","FARO","GRI","NWL","COLL","INSM","OXSQ","UPWK","IR","EBIX","NUTX","DRCT","ONVO","DUNE","LIBY","IFRX","XRTX","MNTX","KNSA","PRLD","LFST","LL","CZNC","TOI","XBIT","WEL","CMI","HMPT","PLXS","WSR","CHCT","NUE","SABR","ICLR","UAMY","ITRN","MSSA","TSBK","TGAN","HUBB","CHUY","MXC","PDSB","CERE","TER","SRG","VBFC","HGTY","GNW","ID","TRP","PEGA","CHH","GPN","CMRX","MDT","DLPN","EXK","PMTS","GBLI","RVSN","TELA","VOR","NCR","OFG","ICU","NOC","CVCY","CRNC","ET","UDMY","EARN","VCNX","IDA","UTSI","GHIX","INMD","TNXP","VAQC","CNS","DRS","RCFA","VLO","GEN","PEV","WHLR","HSII","GSL","QS","SKIL","UK","ZFOX","MBAC","CGO","MOBQ","STN","XEL","SLG","PFIE","PSQH","TFIN","IAUX","CLPR","JELD","VC","MTW","KLTR","CLAY","DBX","ZING","DUK","RNXT","SWBI","KR","SBR","DSGR","GCTK","EGY","PARR","INSP","XRAY","KYCH","SIDU","SONN","ICCC","R","THCH","GRBK","UCBI","OESX","OGN","PPL","TWI","COMS","WEC","PXD","NATR","NKSH","SIX","CFLT","ENLT","MBI","MIND","MVO","PTC","SLI","HSTM","SMP","NRDS","UAL","GIII","CRNX","CMPO","FGEN","FRO","IHS","ITT","KELYA","CNET","MFH","MMS","OXLCZ","NAK","SCL","SFBC","NFBK","SLDP","PODD","RY","VITL","NEOV","HOFT","NWPX","GSBD","PRLB","VHNA","IMTX","MNDY","TGL","VMEO","VERU","MGRM","WT","PLL","XNCR","GRIN","SHW","FCFS","NRSN","GENQ","SZZL","WDC","LMNR","IIIV","KNSL","MOG.A","FFBC","RAIL","MDV","MKTW","ENER","HRTX","JUPW","LEA","ENOV","MSCI","DTM","EVR","LBC","MSA","NAMS","OLN","HROWL","PLBC","HTOO","NL","INDB","MT","OCCI","YCBD","GPRK","SLVR","EEX","ROIC","OXBR","GROV","SMRT","NYMTL","GEF","LBTYK","ORA","RILYT","COMM","LVLU","VZLA","DUOT","RJF","TACT","OKE","STNG","KALU","NN","PAYC","ETAO","HL","NJR","REUN","UPBD","PDS","TILE","SANM","SJ","TRMK","SPR","HOMB","EXP","CJET","EMCG","EMP","NWSA","CP","GAMB","RM","ENCP","TRS","WTMA","EDSA","WMG","LOCL","CSTL","ESNT","CNTG","FWONA","FSK","KROS","FWRG","OLMA","ROAD","TNGX","ELA","KITT","WSBC","USCB","CGTX","VMW","GLG","HFBL","OCC","WLDS","SOPA","FG","CMP","EB","PRI","HBIO","CRGY","YMAB","JOUT","KCGI","MCW","PEP","FUNC","SPCB","STEL","LQDA","TOL","EVCM","VRTS","JSPR","MSM","MA","SEM","CSTM","KFY","PCRX","NEP","CMRA","POAI","RVP","SRDX","IE","WKME","COLB","INLX","MBCN","HSCS","HLIT","RCUS","MYSZ","DHT","NHWK","GRTS","INTA","SFIX","SOBR","MAXN","CRS","DKNG","OBE","ELVN","S","YOTA","PCCT","MEG","EMBC","WTT","GPC","SWI","TREE","PWFL","PFX","ZVSA","FORG","WILC","DYNT","EA","SLAC","ONYX","MSFT","SMSI","HRMY","KOP","ORMP","SAM","MLNK","CZWI","NSTS","SNDA","FENC","LPG","GRIL","FBRX","SEVN","DSAQ","FRLA","GE","LKFN","LUNR","GLLI","EL","GECC","GEG","KVUE","PRO","EUDA","REPL","CGRN","CINF","FTFT","GAN","VSCO","CHCO","KIDS","NVEC","OGS","PACW","CPUH","EVTC","CLST","IONQ","CFG","UEIC","VKTX","NWE","FLL","NTB","PNW","KEY","CEPU","JAN","EPRT","MCHX","PLAY","CSIQ","GFS","MAIN","IEP","PATK","PRGS","CODA","EFHT","COHN","NOVA","RDWR","PWOD","VLY","WINA","SSBK","UVE","IOVA","NCAC","NEPT","VCSA","ZION","SPRY","TSLA","PRDO","DLTH","PRVA","FDP","SYTA","FWONK","LZ","RGLS","RSG","PCVX","RLGT","WWAC","CTLT","ROG","VBIV","SCWX","SEDG","HPE","IMAQ","OPRX","LCW","GAIA","NOVT","EWTX","DLB","FHLT","GPRO","NXRT","REPX","MLI","TPB","LC","SMBK","PBT","VNDA","DAVE","LVS","PTN","SFM","KE","NEX","CMS","XPRO","SENS","ESI","TSEM","SKX","SNPO","LECO","SENEA","FAT","MYPS","PORT","VCYT","CMA","JAMF","MUX","MTA","SGBX","SMFL","HAIA","OPEN","ISSC","RRC","SPRU","PLG","SA","CLRC","PINS","OBT","TWIN","FOXF","ES","CHS","LAC","SIBN","SIRI","CNHI","LH","GWH","OMIC","PRFX","DBVT","KALV","CVLY","MORF","ISIG","GSAT","OXM","LXRX","RPM","DHI","OPI","TLRY","DIOD","DIS","PBA","KFS","SRAD","VEDU","POL","CHY","MPW","WWD","SPTN","TWNK","LPTX","SYK","HLTH","KRG","HYFM","RL","LARK","RTX","NSYS","SITC","WDFC","EZFL","HWC","NCLH","SGMO","TRV","WHLM","EVC","RAYA","YTEN","RVLP","CYTK","GANX","CFBK","JVA","GAU","PLBY","MLYS","MATH","DSGN","MOH","REFR","OI","NIC","DSKE","MRBK","DNUT","KRBP","PZZA","IMAX","STAF","NMIH","SUNL","NXL","NHI","THRY","OCCIN","PRMW","DATS","PUCK","MLKN","RMNI","HNNA","ICAD","FFIN","KMX","LOPE","LWLG","UFPI","RBC","TBNK","HELE","NTRA","PMCB","LIFW","PGRU","WAFD","KBH","CHRS","NXE","LOVE","OPHC","MCD","GEHC","UTAA","MELI","TOWN","NVR","OPY","HZNP","SYNH","IEX","HOLO","LEDS","GBNY","VRTX","GFF","KMB","ONTO","WLYB","PRSR","RRX","NRT","TIGR","CIM","DAL","TBI","PERF","EGHT","RUM","HBAN","CSL","INVE","LRCX","NTIC","PRFT","GBBK","RDIB","LPSN","VCXB","PATH","WLY","JBT","FCF","IVVD","NETI","TCBI","MINM","KODK","LVWR","PDFS","FELE","TGB","PSA","ICVX","CMLS","VBNK","MWA","SAGE","FTEK","WABC","INTT","X","ILLM","WMS","SCLX","EMKR","SF","NFNT","VERB","WFCF","CTXR","IBIO","ESSA","TTC","ZUMZ","FSTR","PUBM","QNST","VERI","TAOP","FCEL","WBX","PLMR","SDHY","CLMT","PBI","JOE","ESE","MAN","MDU","MLR","PHR","CLVR","MYE","DDOG","TANH","CFIV","LBRDA","IRWD","NBY","MBWM","DJCO","MKSI","QLYS","MMYT","FOXO","MBOT","CRD.B","HROW","TRHC","IVZ","VRSN","HAS","CRIS","IGIC","LUCD","DYAI","VTVT","WSO.B","EVBG","GIFI","LTRX","JBL","SIEN","SRZN","WBS","SPI","THO","WFRD","DUOL","IINN","PHAT","FBIO","DXLG","TFII","SAMA","LIXT","EVRI","DB","IDXX","ONCY","NUVB","MITA","EBTC","LNTH","MTC","GSBC","SBGI","CRK","HCI","HFFG","GFOR","HBI","POWW","OLPX","PAY","VLCN","PETQ","PANL","GILT","PKE","LSTR","TIL","YNDX","NVTS","KAVL","CVI","HOTH","HRI","PAAS","SNSE","DTOC","TRGP","XPO","JBHT","WTM","SAGA","HOOD","CMND","OLO","GL","QCRH","LEXX","NGL","EAST","DOCN","ZIMV","PPHP","MLAB","TKAT","VIRT","LFLY","MTAC","IMPP","MITK","NTNX","GES","MGLD","DCO","PLAO","LABP","MKC","TXRH","GDTC","CZOO","OPFI","PEAK","IBEX","XPL","SRCL","LW","TISI","GTHX","CETU","TLS","CLMB","SR","TRX","FFWM","QIPT","MOD","GROY","TTEK","PEPG","CTMX","ELAN","PGR","ICE","HSPO","WOLF","CMPR","LAZY","IMPPP","COP","CION","MPWR","MVLA","ICCM","DTIL","FRBA","CRDO","PROF","IRBT","NLY","DNB","ISTR","MTRX","HTBK","QNCX","OCEA","XCUR","RARE","CLB","GURE","LDOS","DUET","OP","PKOH","FHN","PVL","FDS","GRND","CGEM","GME","CXW","GSD","MRO","NOG","GFL","MGA","MODD","MRNS","FBP","NPK","PTIX","QUBT","EKSO","WATT","HPP","IBRX","PTGX","WCN","STRW","PSEC","VLD","CNOBP","DRQ","FNKO","HGBL","CTO","FATH","GLAD","NYT","LITE","GATE","TXN","RGP","STTK","WFC","DC","OPK","SFE","PYPL","DLO","QTWO","JWN","LANC","NXT","FINW","JSM","RCKT","MOV","JJSF","MNDO","DCPH","OXLCO","VEV","XBIO","TWST","IRRX","TPL","INTR","LODE","CTGO","LYEL","SKLZ","LSAK","SUP","UTRS","MOG.B","CHRW","PLOW","USM","LADR","WWW","RNST","IMMR","MOGO","WYNN","DVA","CMCL","LCUT","LXU","TPG","PRPO","EOSE","LNZA","QDEL","HOLX","WAT","LEE","RILY","LHC","SNBR","LSBK","GGAA","ROCL","GCMG","NWS","TXMD","VANI","LRMR","PMVP","OST","TPX","GRPN","LVTX","NABL","CORR","TU","OUST","SCHL","WLMS","CENTA","G","CRC","KVHI","RYAM","YELL","CR","CLBT","REG","SONO","PRQR","RVPH","MMAT","CMCO","GBX","IRDM","OCTO","HASI","NYXH","SHPH","NRAC","TURN","HSAI","FUN","PATI","WOOF","MERC","FOLD","XTNT","DZSI","FWAC","TCS","GMVD","VNT","HI","MFC","LFUS","STE","VTOL","PSTX","TERN","VAPO","HII","MNTN","SPPI","XPEL","VLN","SDA","PRST","KERN","TNET","EXR","NUVL","PKG","FSEA","WASH","COMP","DPSI","RGF","SSNT","UNIT","OXAC","EVLO","POLA","MSN","MDB","SM","INVA","D","WYY","COHU","GENK","NODK","VRCA","RBB","EAR","OGE","SATL","VIVK","SGHT","HSIC","LGIH","VGAS","XPON","THCP","MEI","EZPW","NIR","RELL","CNMD","CSPI","ETWO","MPB","NOMD","EXPD","JXN","MRNA","RMCF","SOUN","PII","POET","LMFA","CPRT","DIBS","HUDI","PNAC","POWI","CPAA","USAC","THM","DGHI","MVST","FTK","SB","COHR","HOUS","NRXP","MGIH","PANW","ORRF","CPTN","VEL","SCM","CSX","FRPT","FZT","WINT","REXR","NPO","ONBPO","SSY","THRM","POCI","EVA","FOA","MLGO","CWST","CYTH","FAF","FND","JWEL","RBKB","RETO","LFAC","RS","CVBF","MSGE","LXFR","ZENV","JANX","SXT","PLUS","DHCNL","ORC","SLRC","JYD","SDAC","MASS","PIK","DMAC","PGNY","IONM","PRM","SD","WTBA","NEWR","NCMI","DBRG","WKSP","MSTR","SERA","TMDX","FLFV","TRNR","FTNT","IRMD","T","GTN","USCT","DFIN","ODV","VVX","LICY","ORI","OXSQZ","WAFDP","MCOM","RBLX","VABK","LTCH","SP","CPRX","IREN","TR","SGEN","LBRT","SGMA","SLAB","CLOV","EPR","VINO","OPCH","FCAP","HQY","TTD","EWCZ","ORCL","VNRX","RENE","ZWS","TPET","ELLO","NFE","KRTX","ELOX","SMMT","IGC","DLA","NBRV","SMX","SCHN","TOON","ZG","IFIN","MHK","NS","SDPI","CTG","DNLI","TMTC","HEI.A","FOR","RIGL","LOOP","YETI","LNT","PRA","ISDR","RCI","OFED","OFLX","SMTC","SVII","USLM","NAVB","NTCT","OBK","NOTE","FRGE","PRGO","SXC","ZIONL","GREEL","GROW","SMHI","ESAB","EFTR","QUIK","RKT","SYF","CIVI","LOB","TROX","ECOR","MRC","RCLF","NKTR","PYR","GP","JUN","GOOD","SPCE","OFS","TBLD","STR","PBYI","MGAM","NE","FHB","LQDT","TFC","GB","PAVM","PLYM","UHT","NYMTZ","SCWO","GLNG","LAZR","THFF","MTNB","TIPT","VINE","DLHC","KEYS","KRMD","LUNA","MSEX","OSK","TXG","HCTI","CGAU","CTIB","HCCI","LEN","CMAX","CPOP","IFS","GDYN","NWTN","PKBK","ICCH","METX","MGEE","PNTG","ZYME","FIXX","CWAN","DBTX","ITW","KZR","NXU","SKYT","TLYS","JNPR","NYAX","OTEC","YGF","PNFP","MRVI","XELB","FLR","ESCA","EVRG","MIRM","LPX","PYPD","OLED","FKWL","RIG","TPIC","DRRX","MGOL","COLM","NAT","SDC","MFIN","FA","RWAY","PARA","PTEN","OTEX","SOFO","VINP","CLOE","PRTA","EXFY","IRM","LNC","QFTA","NDLS","CVX","RMGC","RRAC","WK","ELS","CMTL","KGC","MNSBP","VRAX","LTHM","VRDN","GNK","MANH","OPXS","IROQ","YMM","VNOM","SUAC","IAC","KNW","MGPI","EGLE","SPFI","SVA","GETR","CSTE","DXPE","FTAI","LCID","SNFCA","COKE","SSNC","FSLY","CHK","CW","FSBC","VERV","CVCO","WEN","FNCH","LFVN","SNTI","ICD","TWO","PCSA","HRZN","HYLN","NUBI","DVN","RSKD","KELYB","PBH","SNA","FRGT","SLGN","SGRP","STRO","CPSI","LVOX","ITOS","MAC","NRGV","ETRN","MPTI","PBAX","WWE","IHT","KREF","SO","MYNZ","TIXT","ROKU","RYN","PLPC","PRIM","DWSN","SSB","PLNT","RGA","HZO","FIHL","EMAN","CYTO","EPAM","HIHO","MCAC","TD","PRTS","CSGP","GDOT","ESEA","VIRC","HT","CMC","FRD","RNA","GTN.A","SGMT","ROK","PHIO","TAST","UBER","DKDCA","KACL","NGS","HY","NDAQ","INFA","WTRG","MCRB","HTGC","CIZN","MTEK","GSUN","RADI","TW","TFPM","LIVE","WNW","WVE","XOMA","NVEE","FHI","OKYO","DTST","NVDA","MNPR","LBAI","SIG","QURE","WHF","OMC","SHCO","USEG","TTSH","TWKS","PAA","DCFC","MASI","URBN","SSP","SYBT","PXMD","IDAI","TUSK","ENOB","KNOP","NBR","OMQS","RACY","SSRM","IBM","GRPH","EGAN","CHTR","DICE","NEOG","HYPR","PSFE","SBEV","CPS","SCI","SAND","EDTX","WISH","HAE","LGMK","SOPH","HOOK","MARK","WHR","QRTEA","CLNN","ZVRA","DAWN","SLNO","FICV","RDVT","GOLD","GRNA","TYGO","SNPX","NEE","CG","EPC","WNEB","ZTEK","VRNS","CSTR","LE","PRSO","PHAR","CHX","DTC","LSPD","DPZ","OSIS","DOOR","PVH","USDP","SRT","OFIX","PLX","CMCSA","CFFN","QSR","FNF","KOS","HBT","MHLD","GALT","TGVC","FERG","NSPR","IVR","PWP","TSLX","MYMD","STAA","LAKE","RDFN","NGVC","SLGC","TRTX","QSI","CHMI","CPLP","ISRL","SBET","OM","ICFI","GOOGL","SALM","MCAA","DTSS","MSVB","MTH","GLST","CREX","SWTX","SLAM","XWEL","CTHR","PIII","PRU","SANG","CMRE","MPU","UBP","HKIT","EVER","CWD","UTME","PYXS","THRX","SHCR","TSHA","INKT","DHCA","SLNH","TZOO","FUSB","PTSI","EMR","ROP","ESQ","PSNL","WY","RTC","SSTK","IAG","SJT","CTLP","NEXA","RGS","HBM","WAL","FLGC","TRNO","DISH","FOUR","VREX","KWE","LILAK","FRGI","RZLT","SYY","RIBT","HUMA","TRI","GRMN","CL","MRKR","TWLO","CORT","GTIM","JHG","NEXI","CVRX","SIGA","KNTK","CHSN","EMN","FHTX","DHR","HQI","ENLC","GIB","TWOA","IMTE","MU","SPOK","ENSC","MLTX","NBIX","RDN","RVTY","PD","PINC","PRME","GHL","FBNC","IGT","MYFW","RMBS","SCKT","ZBRA","FOSL","LLY","UPXI","CRDF","ONTX","GLUE","GBCI","PESI","OBLG","HEP","LOCC","GFGD","MIGI","MARPS","PTRA","TBPH","THR","DHX","WST","INUV","SATX","RGR","VIA","VSEC","WAVD","LCFY","SWX","SGU","EGGF","GATO","MNOV","MTAL","OVLY","TMHC","EIG","EWBC","ST","SFST","SCS","REZI","NUWE","RBCAA","NEWT","META","LAES","L","CTVA","PALT","TRMD","KARO","MED","NEPH","MUSA","NTR","EE","VMCA","OCN","NEM","PAYS","WRB","NTAP","ULBI","EPIX","MNRO","DECK","LINC","SOND","FEIM","KSS","KW","SNOW","PEBO","SAFE","PG","NAII","GERN","GOEV","SMG","URI","HRTG","UFAB","RCM","DFS","WLK","SXTP","NLTX","NTST","JFBR","TSVT","CUBI","RDI","SEMR","LXP","GOOG","FDBC","TCBC","CVII","DNN","ERIE","VCXA","IPA","SHFS","HLI","KEQU","XP","TLIS","MANU","EDTK","SPOT","LCAA","ESTC","CUE","LUNG","CTRA","NICK","HCAT","TAC","VERA","VSAC","WGS","WNNR","JOB","MIMO","NSIT","NXTC","QRHC","FMBH","MHO","SFBS","IRIX","VCIG","SNGX","GCI","MRAI","ROCK","CJJD","ECVT","EME","GHSI","PRPL","CPIX","CNVS","EEIQ","NEN","NHTC","FET","SGC","CRAI","SKGR","MSI","SLS","SEER","UTMD","GNSS","VRE","PMT","FTCH","VVI","IMVT","HLP","UI","XENE","ICHR","MTCH","NVVE","RCMT","SPRO","STLA","POOL","LMB","MKFG","FRMEP","SCHW","SEAC","HHS","SPB","CNEY","FOCS","INBX","MTN","NNI","SYBX","DSX","RHP","SOTK","SQ","SOLO","USAU","WRBY","HAYN","SDGR","ELYM","TPVG","VRRM","CTOS","DRI","HLNE","KAI","NPAB","ETN","CRMD","CMPX","CRBU","LILM","SKE","ZTS","NSTC","TCON","KTB","HWKN","WCC","FIGS","GNLN","METCB","RHE","EVTV","SFR","MHUA","J","ECL","COSM","GIPR","EXPE","CMBM","OCX","FREQ","CLH","GENI","IVCA","RDCM","OVV","SYRS","DEN","LEN.B","SBH","VOXR","VFC","ETON","ZIM","PGTI","NR","ELTX","ILMN","PAVS","ELMD","EU","SLND","CHRD","SITE","TRVI","KRNL","PVBC","FLUX","IONS","QRVO","FSR","OWL","UPST","SHOO","SLVM","TBBK","MYRG","VST","GREE","MEIP","PSX","SBUX","DV","UAN","SLP","FFIC","PFIS","CSLR","STC","ECPG","IVCB","FGF","EXC","MDXG","PGSS","LVRO","MBLY","SHUA","MATV","GOVX","LLAP","OVID","GTX","ECBK","SMAP","WRLD","NI","CTRM","FF","EGBN","OPBK","ORGO","GSMG","HMST","RVMD","HTZ","FCBC","FARM","LNSR","WLKP","ZYNE","SKIN","DY","QTRX","MPC","INSE","CHDN","EDBL","HLX","SVFD","NMRK","REE","RGNX","STT","KPTI","TARO","SGML","GYRO","HST","MDC","TNL","WTS","FLNT","DOGZ","SHAK","KSCP","TALK","HGEN","SBSI","TVTX","MYO","ROST","MET","CPSH","OCAX","LFT","HNI","VTSI","CODX","CPB","URG","PGRE","MTZ","GM","ETSY","SRCE","FI","WES","CVEO","FVCB","LIN","NBTB","OII","OSCR","CSWC","MMP","PHM","TSN","UA","ULTA","W","HNVR","XELA","MEGL","HWEL","HTLD","CSWI","DSS","CONX","MPRA","FMC","HLIO","LYV","PHVS","CHAA","GLMD","HFWA","CSQ","NWN","ELVA","HPLT","LGF.B","TGT","EOG","MNK","FBMS","LUMO","DK","CRBP","DSWL","ENSV","FCUV","JYNT","RGTI","GIC","CPT","CPE","CNFRL","TIGO","DKS","TASK","CLF","RUSHA","GAMC","NRIX","CYRX","SMCI","TEAM","VIR","GHM","OSW","USEA","DORM","WMT","SWIM","UBX","SVM","NEO","GABC","ITRI","NC","NPWR","TYL","HOUR","HOG","VRAR","CVGI","EW","CETX","ORGS","GFX","PGEN","CIGI","MTRY","THC","OCSL","LIVN","PK","STCN","RCKY","CHGG","STRR","TENK","EQ","VRAY","NERV","INN","GLT","GS","SFWL","CGC","CWK","DE","SLDB","VTEX","FLIC","ONB","UTZ","DMAQ","ROVR","SWVL","PB","DRTT","GROM","ITIC","VAL","FGH","MSGM","EXEL","KRP","FORR","MBINN","MRAM","HIVE","SLQT","RFIL","CHEA","MODG","PFE","VUZI","JBLU","RRGB","MDGL","HIMS","IDYA","INGN","NVFY","PLTK","TCBX","V","WVVI","ZEV","GTBP","GCO","ORGN","TAP.A","GPAC","PSTV","KFFB","STKS","NX","COIN","FORL","PRTH","HEAR","CMG","EVGO","UNVR","JOBY","INFI","SEDA","THTX","LAB","CLDT","GIGM","JCI","FGMC","ETR","MNSB","PBHC","SWAG","OLIT","GTLB","SEPA","TBMC","SENEB","PDCE","PETS","QUOT","RLJ","TMKR","FMAO","IPG","HE","JAGX","CWBC","HMA","GFAI","FIVE","GIS","PMN","OLB","RKLB","UMBF","ENVX","GDST","IPGP","XOMAO","HCVI","TALO","HUT","ZYXI","JOAN","RPRX","OCUP","IOT","IOSP","DAR","ESMT","CIVB","NVIV","OPAL","NUZE","RVLV","COCO","CLVT","SHOP","GLDD","GNTY","URGN","PPTA","ESOA","SAIA","SAI","FNGR","LEVI","MSB","NUS","MRK","ENTX","KIND","FRG","CPF","PNT","GSHD","KOPN","RMBI","CIO","ZIP","LTC","INGR","LNN","IBTX","SSYS","TARA","EBS","CGBD","REBN","PETV","SPWH","MTD","TRTL","PWUP","SLB","JEWL","GMBL","HMN","POST","RCAT","IVCP","EVLV","RAND","MBSC","CHNR","SGLY","TCI","CMCA","DNMR","FICO","OTMO","DGICA","MBINM","SEIC","INTG","SOHU","SWAV","FATP","FUV","HTH","CZFS","SGA","ENTA","INBK","GDEV","KN","ENPH","SKY","UGRO","CHI","CPHC","CSTA","CRBG","PACI","LCII","IPVF","PJT","RIVN","TRIN","TPR","IVAC","MAA","HMNF","FNV","LIPO","ERF","MBRX","REX","FFNW","SONX","LDI","NAUT","SUPN","ESTE","CHE","FFIE","GDRX","VEEV","DEA","CVR","CVV","PFSW","PPBI","USAS","GBIO","VTLE","HIG","FAMI","SST","LZB","CWEN","KPLT","FANG","MMSI","RMR","MPLN","SPH","RXT","WTTR","IXAQ","LEG","LOCO","GNS","PEN","IMNM","FIX","DPRO","TNK","ED","ICL","ZDGE","TMPO","FONR","CLX","NTLA","NVRO","PFTA","SAMG","WDAY","ZGN","CNXC","KVSA","PMGM","KDNY","LCNB","CIR","FSCO","OMH","MCFT","USNA","IMXI","UG","DOCS","FATE","HAIN","THRD","PLRX","EDR","NFLX","ENTF","FMNB","VBTX","THS","HCDI","VOYA","ZURA","ENZ","III","NYCB","SEE","WETG","FRBK","PASG","USAP","ZNTL","CWH","SPSC","CTV","SCU","EVBN","SURG","XOS","MO","WKHS","GENC","MTRN","EVI","GLRE","SRL","TOVX","WRK","FEMY","PRG","JLL","TMCI","PEGY","UE","FUND","MRSN","INTC","YUMC","RETA","FCPT","ITI","RRR","SMR","RCL","GODN","SMTI","SEEL","PSN","VEEE","JACK","RHI","CLGN","VOC","OZK","CHPT","CSGS","DRTS","GBTG","KULR","KMT","NRBO","SELB","WMB","OPTN","RF","SCTL","TWLV","UNFI","NNOX","RGLD","SPT","VQS","CYAN","RPAY","SRRK","VSTA","MTG","WEX","KRT","TNDM","ENVB","FSM","FAST","DAC","GOSS","HHRS","RDW","SAFT","SWSS","SLNG","KEN","EVGR","GWRS","TBIO","TNYA","IPDN","PCG","DD","MAYS","CM","GOGL","DDS","MLM","CURO","MRTN","FOXA","SAR","ULCC","STVN","FPH","PFGC","HEPA","GXO","FLS","HBNC","FNVT","HLVX","IRT","PPC","TPC","UNCY","HCA","LIQT","CERT","INDP","DRIO","SELF","CLCO","NB","GNLX","SBAC","ENB","PARAA","VRME","UONEK","RBT","YEXT","SOVO","HAYW","NSTG","TPH","STBA","CTSO","ON","EBC","TAYD","MCAF","NAOV","UFI","DOOO","VCEL","TCPC","HYZN","DOLE","KRNY","KKR","KIM","SQL","CGNT","ENS","GPMT","PW","LSF","SPGI","UFPT","GVA","FCNCA","NBN","VGZ","NVMI","FRAF","PDCO","VTYX","UWMC","FEAM","NETC","PAGS","GTAC","SCPL","SIGI","GDEN","GEO","IDEX","CPZ","CRD.A","STBX","FXCO","HSTO","THRN","SRTS","LIDR","UONE","XPAX","SACH","FRZA","FUBO","WLGS","PET","NSTD","MBIN","ORLA","SQFT","WKC","CREG","PHYT","FLME","OXLC","GAIN","GTE","LGF.A","GEGGL","IMMX","INSG","ELTK","MMI","RELI","SILK","TDG","ETNB","HD","SILC","TG","EDIT","LESL","PLYA","SLNA","CNFR","FLEX","DCOM","MXCT","FXNC","STRL","TFX","TSAT","PSNY","LASR","TSRI","EML","CHMG","DSGX","LBTYA","OBIO","PBFS","UNM","GOCO","UEC","ONON","XOM","WMC","CLSK","GNPX","LMT","RES","NMFC","FURY","TSBX","TGI","ICUI","SYM","RUN","KORE","FC","STM","MAIA","SCVL","TENB","YOU","MD","FSP","PAHC","SNDR","THG","CWEN.A","MS","UUU","CMT","ZS","DSP","HMAC","METC","FBK","EXPR","PI","KBNT","TRT","UNTY","CPRI","GBNH","MARX","YOSH","MSGS","IAS","PFSI","KOSS","LMDX","TGNA","HIW","SAH","PEB","CVKD","GRC","MAR","MKTX","PAYO","PRCT","SYNA","CRGE","IKT","PTWO","MCAG","OC","FSI","OSG","VIEW","PFBC","MURF","RKDA","SCSC","MIDD","NURO","SKYH","CRT","SYPR","LPTV","MLEC","IMNN","CNDT","MGIC","HLF","PLTN","NU","LMAT","PHX","SILO","RNAZ","SNT","MVBF","KRO","CPNG","ENFN","UGI","RLAY","ONDS","RTLPO","DMLP","KWR","TMQ","WBD","CLPS","CWCO","NKE","VSH","PLUG","ECX","DEI","EQT","CYBR","MTSI","FFIV","REGN","INST","TSP","NWLI","WOR","HIFS","KRON","MACA","TTI","MEOH","HEI","DGLY","OVBC","GT","EHTH","MYGN","NSSC","STWD","SVC","TLSA","FUL","IMUX","LPCN","CRDL","MESA","MMLP","NPCE","PBPB","QLGN","DGICB","CITE","SGE","TLF","TRUP","GSIT","GIL","RDNT","CHW","SBRA","UNP","RWT","VTRU","DRUG","ZI","GLOB","MMV","PWM","PPYA","SILV","TETE","SHIP","IESC","RAVE","LFCR","COO","GRRR","LIND","PCAR","KLR","RNGR","GLW","FSS","RCRT","MC","RGCO","DOUG","SATS","HXL","STRA","MBIO","DPCS","WMK","KRC","FORD","SSTI","SIEB","HNRA","GOLF","INCR","FGBI","IDR","LVO","WM","DFH","IPAR","LUXH","PULM","FTS","TCX","HUBC","INTE","LSDI","CHEK","FWBI","REYN","DHIL","TGAA","GLSI","QRTEB","IBP","DHAC","FRXB","DGII","PBLA","CRKN","VRNT","RWAYL","SBXC","OPGN","GEOS","OMCL","PCYO","SOI","EPSN","MRIN","FORA","LATG","FDX","OGEN","PDLB","UNB","DH","TCJH","VMAR","TELL","NNN","PLAB","MX","IKNA","HON","CVLT","MOND","SMID","WW","MDJH","PTRS","CSSEN","GMS","CRSR","ENSG","FPI","VSAT","ZEUS","KMI","FDUS","IZEA","PUMP","IOAC","KTCC","NSA","CRWS","RMED","NKLA","UPS","VFF","TSQ","EAF","MVIS","SPXC","PCB","TALS","QMCO","MFIC","VCTR","SEAS","CLPT","COFS","GNL","TOMZ","SNAP","EXPI","CLS","CONN","KNSW","ITRM","KIQ","ONFO","TBCP","LANV","TCRT","IDCC","HCP","SPIR","TREX","VYGR","GMGI","DOCU","UP","DECA","F","PAG","SKT","TRTN","XFIN","GWAV","LFMD","EURN","NEXT","MTEX","GPI","VWE","JWSM","MXL","TOST","HOWL","RCON","IFBD","KNF","NOGN","CLDX","VISL","MNKD","CTAS","SU","WAVC","WRAP","XPER","UIHC","SUI","HILS","Z","MDWT","RH","EBMT","MLP","EBAY","TAP","NMM","CFRX","RILYZ","OOMA","FLT","IDT","VNO","SPLK","OIS","RPTX","TTEC","MATW","STX","UUUU","VVOS","HCMA","OTLK","RILYL","FNCB","FTCI","RVYL","ITP","UPLD","VMI","DRMA","ELV","FDMT","GHLD","SDIG","WSFS","DG","UBCP","VZIO","DIN","GTES","VATE","PROV","FSRX","ERNA","CLNE","ZETA","SGHC","SQSP","FLYW","SCPH","SKWD","ENG","OMGA","TDW","VMD","TDUP","CNDB","MDRR","QLI","MGNI","KHC","NFGC","STIX","WAB","LZM","SBT","SNAX","ICNC","HONE","MIRO","MTEM","MICS","EQBK","HARP","SRC","CRON","MTX","SLGG","CNA","TDY","VVPR","CGEN","PNM","UNF","CPTK","NNVC","RPID","UNH","EJH","UPTD","EBET","SBCF","PIAI","SKYW","UCTT","OHI","MDRX","GNE","NGM","NEU","OCGN","SPLP","DXC","PFLT","CTRN","STGW","CRVL","STSS","FR","GOOS","RBOT","DLR","QGEN","SONM","CMTG","ERAS","FSBW","INVO","SNOA","NOV","USIO","DCBO","HSON","DOMA","NMTC","RENT","TRMB","NTWK","CRI","KLAC","SINT","WPM","SON","ROIV","SXTC","CFFS","MKC.V","CNDA","DOMO","PLAG","UMH","SNDX","QDRO","FAZE","GRAB","IFF","PR","NRIM","LSXMA","NAVI","HESM","RNG","TWCB","VVV","NTRS","INVH","ISPO","IRON","FREY","UCAR","SRPT","FOX","PTPI","TUP","KRYS","UTHR","CROX","ROSS","EGIO","EYEN","LCA","CZR","PAX","YGMZ","SNTG","SGII","CISO","SSBI","VECO","CWT","GRNQ","MHH","EQS","DERM","JEF","PLSE","CNTX","CTBI","LGVN","HUBS","MBUU","CLSD","WRN","VHAQ","ZCMD","NEON","PFC","CENX","PWSC","FLNC","GMDA","GSM","IPSC","CIFR","LNG","GDNR","SFT","SVT","TH","SGTX","ELEV","LYT","RELY","FLAG","CPHI","CUBA","IMCC","ORN","ESS","IRTC","MEDS","TAIT","JGGC","MUR","TCBS","HPK","TRU","SJW","MORN","OCUL","CMCT","SNAL","LWAY","MIR","CPSS","DOC","EXTR","FN","PHIN","RAIN","RVNC","CLIN","DMRC","SPNS","SLM","NVCR","PEG","RAD","VTRS","VYNE","DAIO","MCB","SNES","SSD","NRG","EVGN","LSCC","PFS","FLGT","SEB","SDRL","VHI","MOTS","EXLS","DXR","ENR","INPX","LYB","INAQ","PLD","SCX","TSCO","VTS","WPRT","CRMT","PBBK","CLFD","JAKK","PRAA","SBIG","MLSS","TEL","DGX","OPINL","NYC","GWW","GLP","HUN","GDHG","FNB","HDSN","IZM","MRCC","ELYS","SNDL","GLBZ","OSS","PCH","CINT","USGO","REVG","CLW","PAGP","MPX","KRUS","TLGA","GVP","VHC","QBTS","FIVN","TDS","TRDA","OUT","EVTL","RANI","INSW","CIX","PACK","ESRT","CTSH","MCVT","NSC","INDI","REVB","SLGL","NTGR"]
    # tickers = ['AMC']
    # def process_list_concurrently(data, process_function, batch_size):
    process_list_concurrently(tickers, compare_tickers_lines_to_market, int(len(tickers)/12)+1)
    combine_db_update_files(module_config)
    execute_bulk_update_file(connection, module_config)

    # compare_tickers_lines_to_market(tickers)

    # find_ticker_profitable_lines(tickers[0], load_ticker_history_cached(tickers[0], module_config), module_config)
    # compare_profitable_ticker_lines_to_market(connection, tickers[0], load_ticker_history_cached(tickers[0], module_config, ),module_config, read_only=False)
    # load_profitable_line_matrix(connection, module_config)
    connection.close()

    print(f"\nCompleted Profitable Line test of {len(tickers)} tickers in {int((int(time.time()) - start_time) / 60)} minutes and {int((int(time.time()) - start_time) % 60)} seconds")