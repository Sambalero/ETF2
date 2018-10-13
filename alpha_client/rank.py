from config import fidelity, symbols, etfs_to_process
from analysis import dates_from_keys, pricefile, write_prices, read_json
from build_summary import get_fundata
from jsontocsv import *
import json
import time

# what range of past values best predicts the value 2 weeks from now?
# how does it vary across funds?
# fund: age, posright freq, negright freq, optimum
def save_ranked_returns_object(ranked_returns_object):
    ts = int(time.time())
    filename = "./json/processed/ranked"+ str(ts) +".csv"
    print("filename: ", filename)
    convertranked(inputfile=None, inputobject=ranked_returns_object, outputfile=filename , linekey="ETF")

''' calculate and set {n_return : value} in fundata object. writes that to pricedata file '''
def set_period_return(fundata, symbol, period):
    dates = dates_from_keys(fundata.keys())  # ascending order, old to new
    # import pdb; pdb.set_trace()    
    for index in range(len(dates) - 1, -1, -1):  # descending order, new to old, start with large index
        if str(period) + "_return" in fundata[dates[index]].keys():
            return fundata 
        if index >= period: # newer values: period change / older value
            fundata[dates[index]][str(period) + "_return"] = (
                (float(fundata[dates[index]]["4. close"]) 
                - float(fundata[dates[index - period]]["4. close"])) 
                / float(fundata[dates[index - period]]["4. close"]))
        else: # less than full period of data: change / oldest
            fundata[dates[index]][str(period) + "_return"] = (
                (float(fundata[dates[index]]["4. close"]) 
                - float(fundata[dates[0]]["4. close"])) 
                / float(fundata[dates[0]]["4. close"]))
    write_prices(fundata, symbol)
    return fundata

''' calculate and set {two_period_return : value} in fundata object. writes that to pricedata file.  two_period_return = average of 2*period2 + period1'''
def set_two_period_return(fundata, symbol, period1, period2): 
    dates = dates_from_keys(fundata.keys())  # ascending order, old to new
    for index in range(len(dates) - 1, -1, -1):  # descending order, new to old
        # if "two_period_return" in fundata[dates[index]].keys():
        #     return fundata
        # if index == 1:
        #     import pdb; pdb.set_trace() 
        fundata[dates[index]]["two_period_return"] = (
            (float(fundata[dates[index]][str(period1) + "_return"]) 
            + 2 * float(fundata[dates[index]][str(period2) + "_return"])) / 3)
        # try:
        #     fundata[dates[index]]["two_period_return"] = (
        #         (float(fundata[dates[index]][str(period1) + "_return"]) 
        #         + 2 * float(fundata[dates[index]][str(period2) + "_return"])) / 3)
        # except Exception as e:
        #     print(e)
        #     print("date was: " + str(dates[index])+ ", symbol: " + symbol)
    write_prices(fundata, symbol)
    return fundata

''' create an all-etfs object with only the data we need'''
def build_returns_object_for_ranking(fundata, etf, returns_object_for_ranking):
    dates = list(reversed(dates_from_keys(fundata.keys()))) # descending order, new to old
    for date in dates:
        if not (date in returns_object_for_ranking.keys()):
            returns_object_for_ranking[date] = {}
        try:
            returns_object_for_ranking[date][etf] = {}
            returns_object_for_ranking[date][etf]["two_period_return"] = fundata[date]["two_period_return"]
            returns_object_for_ranking[date][etf]["20_return"] = fundata[date]["20_return"]
            returns_object_for_ranking[date][etf]["130_return"] = fundata[date]["130_return"]
        except Exception as e:
            print(e)
            print("date was: " + date + ", etf: " + etf)          
    return returns_object_for_ranking

''' sort etfs by return '''
def append_rank_to_returns_object_for_ranking(returns_object_for_ranking):
    i=0
    ranked2 = ranked20 = ranked130 = []
    # import pdb; pdb.set_trace()
    for date in list(reversed(sorted(returns_object_for_ranking.keys()))):
        i+=1
        try:
            ranked2 = list(reversed(sorted(returns_object_for_ranking[date].items(), key=lambda k_v: k_v[1]['two_period_return'])))
            ranked20 = list(reversed(sorted(returns_object_for_ranking[date].items(), key=lambda k_v: k_v[1]['20_return'])))
            ranked130 = list(reversed(sorted(returns_object_for_ranking[date].items(), key=lambda k_v: k_v[1]['130_return'])))
        except Exception as e:
            print(e)
            print("date was: " + date )   
        for index, obj in enumerate(ranked2):
            returns_object_for_ranking[date][obj[0]]["rank2"] = index + 1
            # if i<20 and index <20:
                # print (date, index + 1, obj)
        for index, obj in enumerate(ranked20):
            returns_object_for_ranking[date][obj[0]]["rank20"] = index + 1
            # if i<20 and index <20:
                # print (date, index + 1, obj)
        for index, obj in enumerate(ranked130):
            returns_object_for_ranking[date][obj[0]]["rank130"] = index + 1
            # if i<20 and index <20:
                # print (date, index + 1, obj)
    return returns_object_for_ranking

''' add rank to fundata file '''
def set_ranks(fundata, etf, returns_object_for_ranking):
    if fundata:
        dates = dates_from_keys(fundata.keys())  # ascending order, old to new
        for index in range(len(dates) - 1, 0, -1):  # descending order, new to old
            fundata[dates[index]]["rank2"] = returns_object_for_ranking[dates[index]][etf]["rank2"]
            fundata[dates[index]]["rank20"] = returns_object_for_ranking[dates[index]][etf]["rank20"]
            fundata[dates[index]]["rank130"] = returns_object_for_ranking[dates[index]][etf]["rank130"]
    return fundata   

''' append a rank value based on 2 period performance to the price files; check config - daterange must be none '''
def rank_etfs():
    # funds_to_process = fidelity + list(set(symbols) - set(fidelity))  # ["AADR", "QQQ", "FPX", "ONEQ"] #  ['AADR'] #   
    # import pdb; pdb.set_trace() 
    returns_object_for_ranking = {}
    fundsdata = {}
    for etf in etfs_to_process:
        fundata = get_fundata(etf)
        # save to avoid doing get_fundata again
        fundsdata[etf] = fundata
        # include return in etf pricefile json
        if fundata:
            fundata = set_period_return(fundata, etf, 130) 
            fundata = set_period_return(fundata, etf, 20) 
            fundata = set_two_period_return(fundata, etf, 130, 20)
            # collect returns in an object so they can be ranked
            returns_object_for_ranking = build_returns_object_for_ranking(fundata, etf, returns_object_for_ranking)  
    returns_object_for_ranking = append_rank_to_returns_object_for_ranking(returns_object_for_ranking)  # include the returns rank in the etf pricefile
    save_ranked_returns_object(returns_object_for_ranking)
    # print(returns_object_for_ranking["2018-01-30"])
    ''' save fundata file with ranks to backtrader as csv(.txt) '''
    for etf in etfs_to_process:
        fundata = fundsdata[etf]  
        if fundata:
            fundata = set_ranks(fundata, etf, returns_object_for_ranking)
            ranked_price_filename = "./../../trdr/backtrader/datas/ranked/" + etf + ".txt"
            btconvert_with_rank(inputfile=None, inputobject=fundata, outputfile=ranked_price_filename, linekey=None)

def debug_rank_etfs():
    fundata = get_fundata("AIA")
    fundata = set_period_return(fundata, "AIA", 20) 

# $ python -c 'from rank import debug_rank_etfs; debug_rank_etfs()'

# $ python -c 'from rank import rank_etfs; rank_etfs()'