'''deprecated
replaced with probability/py
'''


from config import fidelity, symbols, old, etfs_to_process
from client import get_prices
from analysis import dates_from_keys, too_old
from jsontocsv import *
import json
import arrow
# what range of past values best predicts the value 2 weeks from now?
# how does it vary across funds?
# fund: age, posright freq, negright freq, optimum

def pricefile(symbol):
    return "./json/prices/" + symbol + ".json"


def write_prices(fundata, symbol):
    filename = pricefile(symbol)
    with open(filename, "w") as writeJSON:
        json.dump(fundata, writeJSON)


def read_json(filename):
    try:
        f = open(filename)
        fundata = json.load(f)
        f.close()
    except (IOError, ValueError):
        fundata = {}
    return fundata


def get_fund_price_data(symbol):
    filename = pricefile(symbol)
    fundata = read_json(filename)
    if fundata:
        if too_old(dates_from_keys(fundata.keys())[-1]):
            fundata = get_prices(symbol, "compact")  # get data
            write_prices(fundata, symbol)
    else:
        fundata = get_prices(symbol) # get data
        write_prices(fundata, symbol)
    return fundata


# The probability of increase in the next two weeks
# if there was an increase over the last n days (period)
# number of possible increase(0) = datarange in business days - 2 weeks - period
#                             (n) = number of days with increase over predictive period in datarange - 2 weeks 
# number of increases    = number of possible increases    :: that increased
# The winner (fidelity set) is something around 4603 with .8 probability. at 10 yrs it's only .62; 0 is .572
# The winner (original set) is something around 4605 with .82 probability. at 10 yrs it's only .625; 0 is .586


def predict_two_weeks_from_now():
    results = {}
    summary = {}
    for etf in fidelity + list(set(symbols) - set(fidelity)):  
        fundata = get_fund_price_data(etf)
        # why do this separately from rank, etc?
        dates = dates_from_keys(fundata.keys())    
        results[etf] = {}
        period_range = range(len(fundata) - 10)
        for period in period_range:  # each performance period
        # over the data range
            deltas = []
            poscount, negcount, possible = 0, 0, 0
            last_index_value = len(fundata) - 10 - period

            if not period in summary.keys():
                summary[period] = {"poscount": 0,  "possible": 0, "N": 0, "points": 0}
            if not period in results[etf].keys():
                results[etf][period] = {"poscount": 0,  "possible": 0, "points": 0}
            summary[period]["N"] += 1

            for i in range(last_index_value): 
                return_over_preceding_period = float(fundata[dates[i+period]]["4. close"]) - float(fundata[dates[i]]["4. close"])

                return_in_two_weeks = float(fundata[dates[i+period+10]]["4. close"]) - float(fundata[dates[i+period]]["4. close"] )

                deltas.append({"i" : i, "dates" : ([dates[i]], [dates[i+period]]), "deltas": (return_over_preceding_period, return_in_two_weeks)})
                if return_over_preceding_period >= 0:
                    possible += 1
                    if return_in_two_weeks > 0: 
                        poscount += 1
                if return_over_preceding_period < 0 and return_in_two_weeks < 0: 
                    negcount += 1

            results[etf][period]["poscount"] += poscount
            results[etf][period]["possible"] += possible
            results[etf][period]["points"] += last_index_value

            summary[period]["poscount"] += results[etf][period]["poscount"]
            summary[period]["possible"] += results[etf][period]["possible"]
            summary[period]["points"] += results[etf][period]["points"]

    for period in summary:
        summary[period]["probability"]  = round(summary[period]['poscount']/summary[period]['possible'], 4)

    convert(inputfile=None, inputobject=summary, outputfile='results.csv', linekey="period")


def append_delta1825_and_delta14_to_files():
    for etf in fidelity + list(set(symbols) - set(fidelity)):
        fundata = get_fund_price_data(etf)
        dates = dates_from_keys(fundata.keys())
        if len(dates) > 1839:
            for i in range(1825, len(dates)): 
                delta1825 = (float(fundata[dates[i]]["4. close"]) - float(fundata[dates[i-1825]]["4. close"])) / float(fundata[dates[i-1825]]["4. close"])
                fundata[dates[i]]["delta1825"] = delta1825
            for i in range(len(dates) - 10):
                delta14 = (float(fundata[dates[i+10]]["4. close"]) - float(fundata[dates[i]]["4. close"])) / float(fundata[dates[i]]["4. close"])
                fundata[dates[i]]["delta14"] = delta14
        write_prices(fundata, etf)

def append_2_wk_change_to_files():
    for etf in fidelity + list(set(symbols) - set(fidelity)):
        fundata = get_fund_price_data(etf)
        dates = dates_from_keys(fundata.keys())
        if len(dates) > 15:
            for i in range(15, len(dates)): 
                delta10 = (float(fundata[dates[i]]["4. close"]) - float(fundata[dates[i-10]]["4. close"])) / float(fundata[dates[i-10]]["4. close"])
                fundata[dates[i]]["delta10"] = delta10
        write_prices(fundata, etf)

def rank_and_value():
    # append_delta1825_and_delta14_to_files()
    # import sys; sys.stdout = open('file.txt', 'w')
    daily_rankings = {}
    summary = {}
    for etf in fidelity + list(set(symbols) - set(fidelity)):  #  ['PTH', "QQQ", "FPX", "ONEQ"]:    
        # print (etf)
        fundata = get_fund_price_data(etf)
        dates = dates_from_keys(fundata.keys())
        for date in dates:
            if ("delta1825" in fundata[date].keys() and "delta14" in fundata[date].keys()):
                obj = {"etf": etf, "delta1825": fundata[date]["delta1825"], "delta14": fundata[date]["delta14"]}
                # print(date, obj)
                # if date == '2014-07-14':
                #     import pdb; pdb.set_trace()
                if not date in daily_rankings.keys():
                    daily_rankings[date] = [obj]
                if daily_rankings[date] == None:
                    daily_rankings[date] = [obj]    
                if not obj in daily_rankings[date]:
                    daily_rankings[date].append(obj)
                # print(daily_rankings[date])
    # import pdb; pdb.set_trace()
    for date in daily_rankings:
        lst = daily_rankings[date]
        # sorted(list_of_dict, key=lambda d: d['c'], reverse=True)
        daily_rankings[date] = list(reversed(sorted(daily_rankings[date], key=lambda x: x["delta1825"])))
# print(daily_rankings[dates[-1][1]])

    with open("rank.json", "w") as writeJSON:
        json.dump(daily_rankings, writeJSON, sort_keys = True)

def rank_and_prob():
    rank = read_json("rank.json")
    rank_n_prob = {}
    for date in rank:
        for i in range(len(rank[date])):
            if not i in rank_n_prob.keys():
                rank_n_prob[i] = {"delta1825": 0, "delta14": 0, "n": 0}
            rank_n_prob[i]["n"] += 1
            rank_n_prob[i]["delta1825"] = rank_n_prob[i]["delta1825"] + (rank[date][i]["delta1825"] - rank_n_prob[i]["delta1825"]) / rank_n_prob[i]["n"]
            rank_n_prob[i]["delta14"] = rank_n_prob[i]["delta14"] + (rank[date][i]["delta14"] - rank_n_prob[i]["delta14"])/ rank_n_prob[i]["n"]
    print (rank_n_prob)

    with open("rnp.json", "w") as writeJSON:
        json.dump(rank_n_prob, writeJSON)

# change this to reflect the reletive value of being in the top returns list

def top_100():
    deltas = []
    for etf in fidelity + list(set(symbols) - set(fidelity)):  
        fundata = get_fund_price_data(etf)
        dates = dates_from_keys(fundata.keys())    
        period = 5*365  # from runs of predict_two_weeks_from_now(); we learned that the jum at 11 years was due to narrowing the field
        if len(dates) > period:
            delta = (float(fundata[dates[period]]["4. close"]) - float(fundata[dates[0]]["4. close"])) / float(fundata[dates[period]]["4. close"])
            deltas.append({"etf": etf, "delta": delta})
    deltas = sorted(deltas, key=lambda x: x["delta"]).reverse()
    convert_list(inputfile=None, inputobject=deltas, outputfile='top_100.csv', linekey=None) 

# def get_6_year_return(fundata, dates, period, index=0):

def set_6_year_return(fundata, symbol): 
    dates = dates_from_keys(fundata.keys())  # ascending order, old to new
    period = 6*261 
    for index in range(len(dates) - 1, -1, -1):  # descending order, new to old
        # import pdb; pdb.set_trace()  
        '''fundata['2018-07-16'] = 0.0! 
        fundata['2010-07-21'] = dne '''
        if "6_year_return" in fundata[dates[index]].keys():
            return fundata 
        if index >= period:
            fundata[dates[index]]["6_year_return"] = (
                (float(fundata[dates[index]]["4. close"]) 
                - float(fundata[dates[index - period]]["4. close"])) 
                / float(fundata[dates[index - period]]["4. close"]))
            # now - then / then
        else: # now - oldest / oldest
            fundata[dates[index]]["6_year_return"] = (
                (float(fundata[dates[index]]["4. close"]) 
                - float(fundata[dates[0]]["4. close"])) 
                / float(fundata[dates[0]]["4. close"]))
    write_prices(fundata, symbol)
    return fundata


def build_6_year_returns(fundata, etf, six_year_returns):
    dates = list(reversed(dates_from_keys(fundata.keys()))) # descending order, new to old
    for date in dates:
        if not (date in six_year_returns.keys()):
            six_year_returns[date] = {}
        six_year_returns[date][etf] = {"return": fundata[date]["6_year_return"]}
    return six_year_returns

def append_rank_to_6_year_returns(six_year_returns):
    # import pdb; pdb.set_trace()
    for date in list(reversed(sorted(six_year_returns.keys()))):
        ranked = list(reversed(sorted(six_year_returns[date].items(), key=lambda k_v: k_v[1]['return'])))
        for index, obj in enumerate(ranked):
            six_year_returns[date][obj[0]]["rank"] = index + 1
    return six_year_returns


def set_6_year_rank(fundata, etf, six_year_returns):
    dates = dates_from_keys(fundata.keys())  # ascending order, old to new
    for index in range(len(dates) - 1, 0, -1):  # descending order, new to old
        fundata[dates[index]]["rank"] = six_year_returns[dates[index]][etf]["rank"]
    return fundata   

def create_csv_price_files():
    ''' these files get moved to backtrader. maybe link?'''
    # for etf in fidelity + list(set(symbols) - set(fidelity)): #  ["AADR"]: #
    for etf in etfs_to_process:
        #  update fundata files
        fundata = get_fund_price_data(etf)
        #  this ordering may not be necessary
        import collections
        rfundata = collections.OrderedDict(fundata)
        
        dates = dates_from_keys(fundata.keys()) #  ascending
        for date in dates:
            # print(date)
            rfundata[date] = fundata[date] 
        pricefile = "./csv/prices/" + etf + ".txt"
        btconvert(inputfile=None, inputobject=rfundata, outputfile=pricefile, linekey=None)

''' append a rank value based on period performance to the price files '''
def rank_etfs():
    funds_to_process = fidelity + list(set(symbols) - set(fidelity))  # ["AADR", "QQQ", "FPX", "ONEQ"] #  ['AADR'] #    
    six_year_returns = {}
    for etf in funds_to_process:
        fundata = get_fund_price_data(etf)
        fundata = set_6_year_return(fundata, etf)  # include return in etf pricefile & json
        # collect returns in an object so they can be ranked
        six_year_returns = build_6_year_returns(fundata, etf, six_year_returns)  
    six_year_returns = append_rank_to_6_year_returns(six_year_returns)  # include the returns rank in the etf pricefile
    print(six_year_returns["2018-01-30"])
    for etf in funds_to_process:
        fundata = get_fund_price_data(etf)
        fundata = set_6_year_rank(fundata, etf, six_year_returns)
        # write_prices(fundata, etf)
        ranked_price_file = "./../../trdr/backtrader/datas/ranked/" + etf + ".txt"
        btconvert_with_rank(inputfile=None, inputobject=fundata, outputfile=ranked_price_file, linekey=None)



# reversed_od = OrderedDict(reversed(od.items()))
# OrderedDict(sorted(my_dict.items(), key=lambda t: t[0], reverse=True))
# $ python -c 'from etf_selection_period import predict_two_weeks_from_now; predict_two_weeks_from_now()'
# $ python -c 'from etf_selection_period import top_100; top_100()'
# $ python -c 'from etf_selection_period import append_delta1825_and_delta14_to_files; append_delta1825_and_delta14_to_files()'
# $ python -c 'from etf_selection_period import rank_and_value; rank_and_value()'
# $ python -c 'from etf_selection_period import rank_and_prob; rank_and_prob()'
# $ python -c 'from etf_selection_period import append_2_wk_change_to_files; append_2_wk_change_to_files()'
# $ python -c 'from etf_selection_period import create_csv_price_files; create_csv_price_files()'
# $ python -c 'from etf_selection_period import rank_etfs; rank_etfs()'