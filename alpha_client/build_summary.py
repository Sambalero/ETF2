import json
from client import build_data_object, call_api, update_data_object
from config import daterange, strategies, all_the_keys, etfs_to_process, old
from config import save_fundsdata_file, precalc
from analysis import Strats, calc_returns, dates_from_keys, calc_cagr, too_old
from dateutil import parser


def build_summary(fundsdata, summary):
    for indicator in strategies:
        summary[indicator] = fundsdata[indicator]['meta']

    for symbol in etfs_to_process:
        if "meta" in fundsdata[symbol].keys():
            summary[symbol] = fundsdata[symbol]['meta']

    return summary

def build_strat_summary(fundsdata, summary, strategy):

    summary[strategy] = fundsdata[strategy]['meta']

    for symbol in etfs_to_process:
        if "meta" in fundsdata[symbol].keys():
            summary[symbol] = fundsdata[symbol]['meta']
    return summary


def add_data_descriptors(summary):
    summary["keys"] = {}
    summary["keys"]["CAGR"] = (
        "equivalent compounding daily rate = (x/x0)^1/t - 1")
    summary["keys"]["averaged_annualized_CAGR"] = (
        "equivalent compounding annual percentage rate = 36500 x CAGR")
    summary["keys"]["<strategy>_value"] = (
        "value of $1 invested per strategy at end of period")
    summary["keys"]["next_days_right_rate"] = "daily predictive probability"
    summary["keys"]["days_held"] = "number of days invested during period"
    summary["keys"]["days_right"] = (
        "number of days predicted correctly during period")
    summary["keys"]["market days"] = "investment days available during period"
    summary["keys"]["number_of_days"] = "number of days in period"

    return summary


def add_selector_info(summary, strat=strategies):
    summary["options"] = {}
    summary["options"]["strategies"] = strat
    summary["options"]["funds"] = etfs_to_process
    summary["options"]["assume overnight delay"] = not(precalc)

    return summary


def append_summary(fundsdata, strategy):
    # for strategy in strategies:
    fundsdata[strategy] = {}
    fundsdata[strategy]['meta'] = {}
    sum_of_days_held = 0
    sum_of_number_of_days = 0
    sum_of_returns = 0
    sum_of_next_days_right = 0
    sum_of_days_held_right = 0
    sum_of_rightable_days = 0
    sum_of_cagr_x_days = 0

# if there's data, build subtotals for aggregate calcs
    for symbol in etfs_to_process:
        if "meta" in fundsdata[symbol].keys():
            r = fundsdata[symbol]['meta'][strategy][strategy + "_value"] - 1
            sum_of_returns += r
            sum_of_days_held += fundsdata[symbol]['meta'][strategy]["days_held"]
            sum_of_number_of_days += fundsdata[symbol]['meta']["number_of_days"]
            sum_of_next_days_right += (
                fundsdata[symbol]['meta'][strategy]["days_right"])
            sum_of_days_held_right += (
                fundsdata[symbol]['meta'][strategy]["profitable_days"])
            sum_of_rightable_days += (
                fundsdata[symbol]['meta']["market_days"] - 1)
            sum_of_cagr_x_days += (
                fundsdata[symbol]['meta'][strategy]["averaged_annualized_CAGR"] *
                fundsdata[symbol]['meta']["number_of_days"])

# calculate the interesting values
    if sum_of_rightable_days != 0:
        fundsdata[strategy]['meta']["next_days_right_rate"] = round(
            (sum_of_next_days_right / sum_of_rightable_days), 3)
    else:
        fundsdata[strategy]['meta']["next_days_right_rate"] = 0

    if sum_of_days_held_right != 0:
        fundsdata[strategy]['meta']["profitable_days_rate"] = round(
            (sum_of_days_held_right / sum_of_days_held), 3)
    else:
        fundsdata[strategy]['meta']["next_days_right_rate"] = 0

    if sum_of_number_of_days != 0:
        fundsdata[strategy]['meta']["averaged_annualized_CAGR"] = round(
            (sum_of_cagr_x_days / sum_of_number_of_days), 5)
    else:
        fundsdata[strategy]['meta']["averaged_annualized_CAGR"] = 0

    return fundsdata

def get_latest_summary():

    import glob
    import os
    # import pdb; pdb.set_trace()
    list_of_files = glob.glob("./json/processed/summary*.json") 
    latest_file = max(list_of_files, key=os.path.getctime)
    print ("Opening: ", latest_file)
    # latest_summary = json.load(latest_file)
    with open(latest_file, 'r') as json_file:
        latest_summary = json.load(json_file)
    return latest_summary

def merge_strat_into_summary(stratfundsdata, summary, strategy):
    summary = get_latest_summary()
    summary = add_selector_info(summary, [strategy])
# include explanatory notes for clarity
    summary = add_data_descriptors(summary)
# report averaged values by fund and strategy
    summary = build_strat_summary(stratfundsdata, summary, strategy)


def merge_fund_indicator_returns(symbol, strategy, fund_data):
    fundata = {}
    if fund_data:
        dates = dates_from_keys(fund_data.keys())
    # calculate return values by fund using given strategy
        fireturns = calc_returns(fund_data, strategy)
    # merge with api data
        if "meta" in fund_data.keys():
            fundata["meta"] = {**fireturns["meta"], **fund_data["meta"]}
        for date in dates:
            if date in fireturns.keys():
                fundata[date] = {**fireturns[date], **fund_data[date]}
            else:
                fundata[date] = fund_data[date]

    return fundata


def include_fund_specific_meta_data(fundata):
    if fundata:
        dates = dates_from_keys(fundata.keys())
        if len(dates):
            if too_old(dates[-1]) or not("meta" in fundata.keys()):
                fundata["meta"] = {}
                fundata["meta"]["start"] = dates[0]
                fundata["meta"]["starting price"] = fundata[dates[0]]["4. close"]
                fundata["meta"]["end"] = dates[-1]
                fundata["meta"]["ending price"] = fundata[dates[-1]]["4. close"]
                fundata["meta"]["number_of_days"] = (
                    parser.parse(dates[-1]) - parser.parse(dates[0])).days
                fundata["meta"]["market_days"] = len(dates)
                fundata["meta"]["return"] = round(
                    (float(fundata["meta"]["ending price"]) -
                     float(fundata["meta"]["starting price"])) /
                    float(fundata["meta"]["starting price"]), 3)
                fundata["meta"]["averaged_annualized_CAGR"] = round(36500 * (calc_cagr(
                    float(fundata["meta"]["starting price"]),
                    float(fundata["meta"]["ending price"]),
                    fundata["meta"]["number_of_days"])), 4)
        else:
            fundata["meta"] = {}
            fundata["meta"]["note"] = "No data in range for "
        return fundata


def fund_data_in_range(fun_data):
    start = daterange[0]
    if start:
        start = int(start.replace("-", ""))
    else:
        start = 0
    end = daterange[1]
# check if each date is in the desired range,
# copy to a new object if it is
    fundata = {}
    if fun_data:
        funkeys = list(fun_data.keys())
        for date in funkeys:
            if int(date.replace("-", "")) >= start:
                if not (end):
                    end = list(fun_data.keys())[-1]
                if (int(date.replace("-", "")) <= int(end.replace("-", ""))):
                    fundata[date] = fun_data[date]
        return fundata


def all_indicators_only(fun_data):
    if fun_data:
        dates = dates_from_keys(fun_data.keys())
# remove all the dates that have incomplete data
    
        for date in sorted(list(fun_data.keys())):
            for indicator in all_the_keys:
                if not(indicator in fun_data[date].keys()):
                    if date in dates:
                        # print (date)
                        # print (indicator)
                        dates.remove(date)

# copy values to a new object using keys that remain
        fundata = {}
        for date in dates:
            fundata[date] = fun_data[date]
        return fundata


# call methods that toss out extra data 
''' I think after 8/27 this is no longer used '''
def limit_fundata(fundata):
    fundata = all_indicators_only(fundata)
    fundata = fund_data_in_range(fundata)
    return fundata

def no_file(symbol, filename):
        api_data = call_api(symbol)  
        fundata = build_data_object(symbol, api_data)
        with open(filename, "w") as writeJSON:
            json.dump(fundata, writeJSON)   


def get_fundata(symbol, indicators = [], start = None, end = None): 
    filename = "./json/raw/" + symbol + ".json"  
# read from file if there is one; call api if there isn't
    # if symbol == 'ALFA':
    #     import pdb; pdb.set_trace()
    try:
        f = open(filename)
        fundata = json.load(f)
        f.close()
    except Exception as e:
        print(e)
        fundata = no_file(symbol, filename)
    if not fundata:
        fundata = no_file(symbol, filename)
#update if "too old"
    if fundata and too_old(dates_from_keys(fundata.keys())[-1]):
        api_data = call_api(symbol, 'compact')

        # import pdb; pdb.set_trace()
        fundata = build_data_object(symbol, api_data)
        with open(filename, "w") as writeJSON:
            json.dump(fundata, writeJSON)
# toss unwanted dates 
    ''' 8/27 I'm pulling out fund_data_in_range  because too often I'm seeing it result 
    in empty files. It will need to be replaced where needed. (after processing)
    and all_indicators_only(fundata) 9/24
    fundata = limit_fundata(fundata)  
    fundata = all_indicators_only(fundata) '''
# include the symbol name for human readability    
    if fundata:
        if "meta" in fundata.keys():
            fundata["meta"]["symbol"] = symbol
    # note says "No data in range for ". should probably be moved into meta?
        else:
            if "note" in fundata.keys():
                fundata["meta"]["note"] = fundata["note"] + symbol
                del(fundata["note"])
        with open(filename, "w") as writeJSON:
            json.dump(fundata, writeJSON)
        return fundata


def build_file_names(strategy=""):
    start = daterange[0]
    if not start:
        start = ""
    end = daterange[1]
    if not end:
        end = ""
    funds_filename = "./json/processed/" + strategy + "fundsdata " + start + " - " + end + ".json"
    filename = "./json/processed/" + strategy + "summary " + start + " - " + end + ".json"
    return(filename, funds_filename)

def add_more_indicators():
    # import pdb; pdb.set_trace()
# marshall api data
    for symbol in etfs_to_process:
        filename = "./json/raw/" + symbol + ".json"  
    # read from file if there is one; call api if there isn't
        try:
            f = open(filename)
            fundata = json.load(f)
            f.close()
        except Exception as e:
            print(e)
            api_data = call_api(symbol)  
            fundata = build_data_object(symbol, api_data)
            with open(filename, "w") as writeJSON:
                json.dump(fundata, writeJSON)
        dates = dates_from_keys(fundata.keys())
        for ma in ["sma", "ema"]:  #  change ma to new_indicator
            if not (ma.upper() in  fundata[dates[-1]]):
                api_data = add_ma(symbol, ma)  # a response object set
                fundata = update_data_object(fundata, symbol, api_data)
        with open(filename, "w") as writeJSON:
            json.dump(fundata, writeJSON) 

''' deprecated build stratfundsdata. old fundsdata was getting too big. '''
def run_strategy(strategy):
    import pdb; pdb.set_trace() 
    stratfundsdata = {}
# marshall api data
    for symbol in etfs_to_process:
        stratfundsdata[symbol] = get_fundata(symbol)
# add helpful fund specific information 
        ''' start date should be chaned to first date, not date range value '''
        stratfundsdata[symbol] = include_fund_specific_meta_data(stratfundsdata[symbol])
# get (calc) and merge data from investment return calculations
    for symbol in etfs_to_process:
        stratfundsdata[symbol] = merge_fund_indicator_returns(
            symbol, strategy, stratfundsdata[symbol])
        stratfundsdata[symbol] = merge_fund_indicator_returns(
            symbol, "Buy_and_Hold", stratfundsdata[symbol])
    ''' summary should merge new calcs into existing summary file

     '''
# build and append per-fund and per-strategem summary values (averages)
    # import pdb; pdb.set_trace()
    stratfundsdata = append_summary(stratfundsdata, strategy)
# update summary file
    ''' merge_strat_into_summary '''
    summary = {}
    merge_strat_into_summary(stratfundsdata, summary, strategy)
# build file names
    (filename, funds_filename) = build_file_names(strategy)
# save

    with open(funds_filename, "w") as writeJSON:
        json.dump(stratfundsdata, writeJSON)
    with open(filename, "w") as writeJSON:
        json.dump(summary, writeJSON)

''' a temporary script to change from megafile to processed fund files '''
def write_fundata():
    for symbol in etfs_to_process:
        filename = "./json/fundata/" + symbol + "_p.json" 
        fundata = get_fundata(symbol)
        with open(filename, "w") as writeJSON:
            json.dump(fundata, writeJSON)



def build_processed_data_old():
    # import pdb; pdb.set_trace()
    fundsdata = {}
# marshall api data
    for symbol in etfs_to_process:
        # import pdb; pdb.set_trace()
        fundsdata[symbol] = get_fundata(symbol)
# add helpful fund specific information
        fundsdata[symbol] = include_fund_specific_meta_data(fundsdata[symbol])
# get and merge data from investment return calculations
    for strategy in strategies:
        for symbol in etfs_to_process:
            fundsdata[symbol] = merge_fund_indicator_returns(
                symbol, strategy, fundsdata[symbol])
# build and append per-fund and per-strategem summary values (averages)
    import pdb; pdb.set_trace()
    for strategy in strategies:
        fundsdata = append_summary(fundsdata, strategy)
# create readable JSON summary to save as smaller file
    summary = {}
# list selected options
    summary = add_selector_info(summary)
# include explanatory notes for clarity
    summary = add_data_descriptors(summary)
# report averaged values by fund and strategy
    summary = build_summary(fundsdata, summary)
# build file names
    (filename, funds_filename) = build_file_names()
# save
    if save_fundsdata_file:
        with open(funds_filename, "w") as writeJSON:
            json.dump(fundsdata, writeJSON)
    with open(filename, "w") as writeJSON:
        json.dump(summary, writeJSON)


''' therre will be a build_summary method, too ''' 
def build_processed_fundata():
# marshall api data
# read from raw file, update if needed from api, dump to p file
    for symbol in etfs_to_process:
        filename = "./json/fundata/" + symbol + "_p.json" 
        fundata = get_fundata(symbol)
        with open(filename, "w") as writeJSON:
            json.dump(fundata, writeJSON)

    fundsdata = {}

    for symbol in etfs_to_process:
# build fundsdata from raw file
        fundsdata[symbol] = get_fundata(symbol)
# add helpful fund specific information
        fundsdata[symbol] = include_fund_specific_meta_data(fundsdata[symbol])
# get and merge data from investment return calculations
    for strategy in strategies:
        for symbol in etfs_to_process:
            fundsdata[symbol] = merge_fund_indicator_returns(
                symbol, strategy, fundsdata[symbol])
# build and append per-fund and per-strategem summary values (averages)
# ''' I'm pretty sure this is not working quite right at some point downstream '''
#     import pdb; pdb.set_trace()
    for strategy in strategies:
        #  build summary of strategy data for each etf and append it.
        fundsdata = append_summary(fundsdata, strategy)
# create readable JSON summary to save as smaller file
    summary = {}
# list selected options
    summary = add_selector_info(summary)
# include explanatory notes for clarity
    summary = add_data_descriptors(summary)
# report averaged values by fund and strategy
    summary = build_summary(fundsdata, summary)
# build file names
    (filename, funds_filename) = build_file_names()
# save
    if save_fundsdata_file:
        with open(funds_filename, "w") as writeJSON:
            json.dump(fundsdata, writeJSON)
    with open(filename, "w") as writeJSON:
        json.dump(summary, writeJSON)

'''save this line for debug'''
'''json.dump(fundata, open("./json/fundata/111.json", "w"))'''

''' see notes.txt for status '''
# get and merge data from investment return calculations

# python -c 'from build_summary import get_fundata; get_fundata('AIA')'
# python -c 'from build_summary import build_processed_data; build_processed_data()'
# python -c 'from build_summary import add_more_indicators; add_more_indicators()'
# python -c 'from build_summary import run_strategy; run_strategy("RSI4")'
# python -c 'from build_summary import write_fundata; write_fundata()'
# python -c 'from build_summary import build_processed_fundata; build_processed_fundata()'
