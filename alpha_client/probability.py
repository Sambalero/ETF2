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
''' Long and short preceding periods positive?  '''
''' Can we get a function? '''       

''' probability of positive 2wk = count positive 2wk / datapoints
probability of positive 2wk given positive period = count if positive period and positive / count if positive period''' 

'''read if it exists'''
def read_json(filename):
    try:
        with open(filename, 'r') as f:
            fundprices = json.load(f)
        return fundprices
    except:
        print("filename not found in probabiliy.py line 26")
        pass

def write_fundprices(fundprices, etf):
    pricefile = "./json/prices/" + etf + ".json" 
    with open(pricefile, "w") as writeJSON:
        json.dump(fundprices, writeJSON)

def build_fundprices(symbol, fundata, fundprices={}): # eventually called with none
    # import pdb; pdb.set_trace()
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

''' analysis.do_fundata update '''
def get_fund_price_data(etf): 
    pricefile = "./json/prices/" + etf + ".json" 
    fundprices = read_json(pricefile)
    if fundprices:       
        if too_old(dates_from_keys(fundprices.keys())[-1]): # can override value fro config.old here as second arg.
            print("old 62")
            fundata = get_fundata(etf) #<---------------------sometimes losing it here
            # fred = dict(islice(fundata.items(), 0, 2))
            # print("old", fred)
            fundprices = build_fundprices(etf, fundata, fundprices)
    else:
        import pdb; pdb.set_trace()
        fundata = get_fundata(etf)

        # print("else", fundata) prints fundata
        fundprices = build_fundprices(etf, fundata)
    return fundprices

def calc_period_return(fundprices, start, finish):
    period_return = (float(fundprices[finish]["4. close"]) - float(fundprices[start]["4. close"]))/float(fundprices[start]["4. close"])
    return period_return


'''funreturn = {symbol: {date: {{periodreturn:}, {2wkreturn:} '''
def build_funreturn(etf, period, fundprices):
    funreturns = {}
    funreturns[etf] = {}
    for date in list(fundprices.keys()):
        if date == "meta" or date == "note":
            pass
        else:
            funreturns[etf][date] = {}
            # print("DATE ", date)
            period_days_ago = (arrow.get(date, 'YYYY-MM-DD').shift(days=-period)).format('YYYY-MM-DD')
            two_weeks_from_date = (arrow.get(date, 'YYYY-MM-DD').shift(days=+14)).format('YYYY-MM-DD')

            if period_days_ago in list(fundprices.keys()):
                funreturns[etf][date]["period return"] = calc_period_return(fundprices, period_days_ago, date)
            if two_weeks_from_date in list(fundprices.keys()):
                funreturns[etf][date]["2 week return"] = calc_period_return(fundprices, date, two_weeks_from_date)
    print("97 period, etf ", period, etf)
    return funreturns

            
''' build periodreturns object for calcs
 period_returns = <period>{symbol: {date: {{periodreturn:}, {2wkreturn:} ...'''
def performance_period_two_week_returns(period):
    returns = {}
    for etf in etfs_to_process: 
        # if etf == 'ALFA':
        #     import pdb; pdb.set_trace()
        period = [str(period) +" day performance period"]
        fundprices = get_fund_price_data(etf)
        funreturn = build_funreturn(etf, period, fundprices) # funreturn is
        returns[period] = {}
        returns[period] = funreturn
    print("returns 110")
    return returns

''' build averages file 
return averages (running total){period; {tally of periodreturn,tally of 2wkreturn, count of datapoints, count of positive periodreturn, count of positive 2wkreturn }
'''
def two_week_return_by_performance_period():
    # import pdb; pdb.set_trace()
    tallies = {}
    returns = {}
    for period in periods:
        periodkey = str(period) +" day performance period"
        # returns = performance_period_two_week_returns(period)
        # '''<period>{symbol: {date: {{periodreturn:}, {2wkreturn:} ...'''
        # period = str(period) +" day performance period"        
        tallies[periodkey] = {}
        for etf in etfs_to_process: 
            fundprices = get_fund_price_data(etf)
            returns[periodkey] = build_funreturn(etf, period, fundprices)
            # funreturn = build_funreturn(etf, period, fundprices)
            # import pdb; pdb.set_trace() 
            # returns[periodkey] = funreturn   # this seems to take a log time!  <----------------p  
        print("----135---", arrow.now())
        for etf in list(returns[periodkey].keys()):
            print("----137---", arrow.now())
            for date in list(returns[periodkey][etf].keys()):
                print("----139---", arrow.now())
                # import pdb; pdb.set_trace()
                # (Pdb) p etf 'AADR'
                # (Pdb) p date '12 day performance period'               
                # (Pdb) p tallies
                # {'12 ay performance period': {}}
                # (Pdb) p(returns)
                # {'AADR': {'12 day performance period': {'AADR': {'2010-10-13': {'2 week return':
                # None}, '2010-10-14': {'2 week return': No
                todays_keys = list(returns[periodkey][etf][date].keys())
                print(date, " 147")
                if (("2 week return" in todays_keys) and ("period return" in todays_keys)):
                    print(date, " 149")
                    # import pdb; pdb.set_trace() 
                    two_week_return = returns[periodkey][etf][date]["2 week return"] 
                    period_return = returns[periodkey][etf][date]["period return"]
                    tallies[periodkey].setdefault("datapoints", 0)
                    tallies[periodkey]["datapoints"] += 1
                    tallies[periodkey].setdefault("tally 2 week return", 0)
                    tallies[periodkey]["tally 2 week return"] += two_week_return

                    if two_week_return > 0:
                        tallies[periodkey].setdefault("count positive return", 0)
                        tallies[periodkey]["count positive return"] += 1
                        tallies[periodkey].setdefault("tally positive 2 week return", 0)
                        tallies[periodkey]["tally positive 2 week return"] += two_week_return
                        if returns[periodkey][etf][date]["period return"] > 0:
                            tallies[periodkey].setdefault("count positive period and return", 0)
                            tallies[periodkey]["count positive period and return"] += 1
                    if period_return > 0:
                        tallies[periodkey].setdefault("count positive period", 0)
                        tallies[periodkey]["count positive period"] += 1
                    tallies[periodkey].setdefault("max positive period", 0)
                    if period_return > tallies[periodkey]["max positive period"]:
                        tallies[periodkey]["max positive period"] = period_return
        print("----171---")
        if "count positive return" and "datapoints" in list(tallies[periodkey].keys()): 

            tallies[periodkey]["probability of positive 2 week return"] = tallies[periodkey]["count positive return"] / tallies[periodkey]["datapoints"]
        if "count positive period and return" and "count positive period" in list(tallies[periodkey].keys()):       
            tallies[periodkey]["probability of positive 2 week return given positive period"] = tallies[periodkey]["count positive period and return"] / tallies[periodkey]["count positive period"]

    with open("./json/processed/returns.json", "w") as writeJSON:
        json.dump(tallies, writeJSON)
        
    import pdb; pdb.set_trace() 


# $ python -c 'from probability import two_week_return_by_performance_period; two_week_return_by_performance_period()' python -m pdb -c continue 'from probability import two_week_return_by_performance_period; two_week_return_by_performance_period()'