from config import fidelity, symbols
from client import get_prices
from analysis import dates_from_keys, pricefile, too_old, write_prices, read_json, do_fundata
from jsontocsv import *
import json
  
# what range of past values best predicts the value 2 weeks from now?
# how does it vary across funds?
# fund: age, posright freq, negright freq, optimum


def set_period_return(fundata, symbol, period):
    dates = dates_from_keys(fundata.keys())  # ascending order, old to new
    for index in range(len(dates) - 1, -1, -1):  # descending order, new to old
        if str(period) + "_return" in fundata[dates[index]].keys():
            return fundata 
        if index >= period:
            fundata[dates[index]][str(period) + "_return"] = (
                (float(fundata[dates[index]]["4. close"]) 
                - float(fundata[dates[index - period]]["4. close"])) 
                / float(fundata[dates[index - period]]["4. close"]))
            # now - then / then
        else: # now - oldest / oldest
            fundata[dates[index]][str(period) + "_return"] = (
                (float(fundata[dates[index]]["4. close"]) 
                - float(fundata[dates[0]]["4. close"])) 
                / float(fundata[dates[0]]["4. close"]))
    write_prices(fundata, symbol)
    return fundata

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


def build_two_period_returns(fundata, etf, two_period_returns):
    dates = list(reversed(dates_from_keys(fundata.keys()))) # descending order, new to old
    for date in dates:
        if not (date in two_period_returns.keys()):
            two_period_returns[date] = {}
        try:
            two_period_returns[date][etf] = {"two_period_return": fundata[date]["two_period_return"]}
        except Exception as e:
            print(e)
            print("date was: " + date + ", etf: " + etf)          
    return two_period_returns

def append_rank_to_two_period_returns(two_period_returns):
    i=0
    for date in list(reversed(sorted(two_period_returns.keys()))):
        i+=1
        ranked = list(reversed(sorted(two_period_returns[date].items(), key=lambda k_v: k_v[1]['two_period_return'])))
        for index, obj in enumerate(ranked):
            two_period_returns[date][obj[0]]["rank"] = index + 1
            if i<20 and index <20:
                print (date, index + 1, obj)
    return two_period_returns


def set_two_period_rank(fundata, etf, two_period_returns):
    dates = dates_from_keys(fundata.keys())  # ascending order, old to new
    for index in range(len(dates) - 1, 0, -1):  # descending order, new to old
        fundata[dates[index]]["rank"] = two_period_returns[dates[index]][etf]["rank"]
    return fundata   

''' append a rank value based on 2 period performance to the price files '''
def rank_etfs():
    funds_to_process = fidelity + list(set(symbols) - set(fidelity))  # ["AADR", "QQQ", "FPX", "ONEQ"] #  ['AADR'] #    
    two_period_returns = {}
    for etf in funds_to_process:
        fundata = do_fundata(etf)
        # include return in etf pricefile json

        fundata = set_period_return(fundata, etf, 130) 
        fundata = set_period_return(fundata, etf, 20) 
        fundata = set_two_period_return(fundata, etf, 130, 20)
        # collect returns in an object so they can be ranked
        two_period_returns = build_two_period_returns(fundata, etf, two_period_returns)  
    two_period_returns = append_rank_to_two_period_returns(two_period_returns)  # include the returns rank in the etf pricefile
    # print(two_period_returns["2018-01-30"])
    for etf in funds_to_process:
        fundata = do_fundata(etf)
        fundata = set_two_period_rank(fundata, etf, two_period_returns)
        # write_prices(fundata, etf)
        ranked_price_file = "./../../trdr/backtrader/datas/ranked/" + etf + ".txt"
        btconvert_with_rank(inputfile=None, inputobject=fundata, outputfile=ranked_price_file, linekey=None)

# $ python -c 'from rank import rank_etfs; rank_etfs()'