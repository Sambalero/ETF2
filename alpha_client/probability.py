from config import fidelity, symbols, etfs_to_process, periods
from client import get_prices
from analysis import dates_from_keys, too_old
from build_summary import get_fundata
from jsontocsv import *
import json
import arrow
import itertools
import config


''' What is the probability of the next two weeks having a positive return? '''
''' What is it if the preceding period had a positive return? '''
''' What is it if the preceding period had a negative return? ''' 
''' Long and short preceding periods?  '''     

''' probability of positive 2wk = count positive 2wk / datapoints
probability of positive 2wk given positive period = count if positive period and positive / count if positive period''' 

'''read if it exists'''
def read_json(filename):
    try:
        with open(filename, 'r') as f:
            fundprices = json.load(f)
        return fundprices
    except:
        print("filename not found - in probabiliy.py line 26")
        pass

def write_fundprices(fundprices, etf):
    pricefile = "./json/prices/" + etf + ".json" 
    with open(pricefile, "w") as writeJSON:
        json.dump(fundprices, writeJSON)

def build_fundprices(symbol, fundata, fundprices={}):
    count = 0
    if not fundata:
        print ("not fundata, ", symbol, count)
        return fundprices
    else: 
        count += 1
        
    for date in list(sorted(fundata.keys())):
        if date == "meta":
            fundprices[date] = fundata[date]
        else:
            fundprices[date] = {}
            fundprices[date]["1. open"] = fundata[date]["1. open"]
            fundprices[date]["2. high"] = fundata[date]["2. high"]
            fundprices[date]["3. low"] = fundata[date]["3. low"]
            fundprices[date]["4. close"] = fundata[date]["4. close"]
            fundprices[date]["5. volume"] = fundata[date]["5. volume"]
    write_fundprices(fundprices, symbol)
    return fundprices

''' analysis.do_fundata update
read from file 
update, build & write as apropo
return '''
def get_fund_price_data(etf): 
    pricefile = "./json/prices/" + etf + ".json" 
    fundprices = read_json(pricefile)
    if fundprices:       
        if too_old(dates_from_keys(fundprices.keys())[-1]):
            print("old 62")
            fundata = get_fundata(etf)
            fundprices = build_fundprices(etf, fundata, fundprices)
    else:
        import pdb; pdb.set_trace()
        fundata = get_fundata(etf)
        fundprices = build_fundprices(etf, fundata)
    return fundprices

def calc_period_return(fundprices, start, finish):
    period_return = (float(fundprices[finish]["4. close"]) - float(fundprices[start]["4. close"]))/float(fundprices[start]["4. close"])
    return period_return

'''funreturn = <symbol>{date: 2wkreturn} ... '''
def two_week_fund_return(etf, fundprices):
    funreturns = {}
    for date in list(fundprices.keys()):
        if date == 'meta' or date == 'note':
            pass
        else:
            funreturns[date] = {}
            two_weeks_from_date = (arrow.get(date, 'YYYY-MM-DD').shift(days=+14)).format('YYYY-MM-DD')
            if two_weeks_from_date in list(fundprices.keys()):
                funreturns[date]["2 week return"] = calc_period_return(fundprices, date, two_weeks_from_date) 
    return funreturns 

'''funreturn = <symbol>{date: periodreturn}, ... '''
def build_funreturn(etf, period, fundprices):  # only need etf for debugging
    funreturns = {}
    periodkey = "previous " + str(period) + " day return"
    dates = list(fundprices.keys())
    if "meta" in dates:
        dates.remove("meta")
    if "note" in dates:
        dates.remove("note")
    dates = list(reversed(dates))  # descending
    for index, date in enumerate(dates):
        if (index + period) < len(dates):
            period_days_ago = dates[index + period]
            if period_days_ago == "meta" or period_days_ago == "note":
                break
            funreturns[date] = {}                
            funreturns[date][periodkey] = calc_period_return(fundprices, period_days_ago, date)
    return funreturns

#  this is the point where I should be using a database... periodkey and 2wk return are column headers            
''' build periodreturns object for calcs
 period_returns = {period: {symbol: {date: { periodkey: periodreturn}, {2wkreturn: 2wkreturn}}, { ...'''
def build_2_week_period_returns():
    returns = {}    # what happens if the etf isn't processable?
    for period in periods:
        returns[period] = {}
        for etf in etfs_to_process: 
            returns[period][etf] = {}
    for etf in etfs_to_process: 
        #  update fund price data
        fundprices = get_fund_price_data(etf)  
        two_week_funreturns = two_week_fund_return(etf, fundprices)
        for period in periods:
            periodkey = "previous " + str(period) + " day return"   
            funreturns = build_funreturn(etf, period, fundprices)
            for date in list(funreturns.keys()):
                if date in list(two_week_funreturns.keys()) and len(two_week_funreturns[date]) > 0 and len(funreturns[date]) > 0:
                    returns[period][etf][date] = {}
                    returns[period][etf][date][periodkey] = funreturns[date][periodkey]
                    returns[period][etf][date]["2 week return"] = two_week_funreturns[date]["2 week return"]
            print("dates in funreturns: ", etf, len(list(funreturns.keys())))
            print("dates in returns[period]: ", period, len(list(returns[period].keys())))
    return returns

''' build averages file 
return averages (running total){period; {tally of periodreturn,tally of 2wkreturn, count of datapoints, count of positive periodreturn, count of positive 2wkreturn }
'''
def two_week_return_by_performance_period():
    tallies = {}
    returns = build_2_week_period_returns()
    for period in periods:
        periodkey = "previous " + str(period) + " day return"        
        tallies[periodkey] = {}
        listlength = 0  # debug value
        for etf in list(returns[period].keys()):
            for date in list(returns[period][etf].keys()):
                two_week_return = returns[period][etf][date]["2 week return"] 
                period_return = returns[period][etf][date][periodkey]
                tallies[periodkey].setdefault("datapoints", 0)
                tallies[periodkey]["datapoints"] += 1
                tallies[periodkey].setdefault("tally 2 week return", 0)
                tallies[periodkey]["tally 2 week return"] += two_week_return
                if two_week_return > 0:
                    tallies[periodkey].setdefault("count positive return", 0)
                    tallies[periodkey]["count positive return"] += 1
                    tallies[periodkey].setdefault("tally positive 2 week return", 0)
                    tallies[periodkey]["tally positive 2 week return"] += two_week_return
                    if period_return > 0:  
                        tallies[periodkey].setdefault("count positive period and return", 0)
                        tallies[periodkey]["count positive period and return"] += 1
                    else:
                        tallies[periodkey].setdefault("count neg period and pos return", 0)
                        tallies[periodkey]["count neg period and pos return"] += 1
                if period_return > 0:
                    tallies[periodkey].setdefault("count positive period", 0)
                    tallies[periodkey]["count positive period"] += 1
                tallies[periodkey].setdefault("max positive period", 0)
                if period_return > tallies[periodkey]["max positive period"]:
                    tallies[periodkey]["max positive period"] = period_return
            listlength += len(list(returns[period][etf].keys())) # debug value
        print("num etfs:", len(list(returns[period].keys())))
        print("list lenght - datapoints: ", listlength - tallies[periodkey]["datapoints"])
        print("datapoints: ", tallies[periodkey]["datapoints"])

        if "count positive return" and "datapoints" in list(tallies[periodkey].keys()): 

            tallies[periodkey]["probability of positive 2 week return"] = tallies[periodkey]["count positive return"] / tallies[periodkey]["datapoints"]
        if "count positive period and return" in list(tallies[periodkey].keys()) and "count positive period" in list(tallies[periodkey].keys()):       
            tallies[periodkey]["probability of positive 2 week return given positive period"] = tallies[periodkey]["count positive period and return"] / tallies[periodkey]["count positive period"]

    with open("./json/processed/returns.json", "w") as writeJSON:
        json.dump(tallies, writeJSON)

    with open("./json/processed/base.json", "w") as writeJSON:
        json.dump(returns, writeJSON)
        


# $ python -c 'from probability import two_week_return_by_performance_period; two_week_return_by_performance_period()' python -m pdb -c continue 'from probability import two_week_return_by_performance_period; two_week_return_by_performance_period()'

# $ python -m pdb -c continue ascript.py 999
