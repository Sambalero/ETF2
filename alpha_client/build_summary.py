import json
from client import build_data_object, call_api
from config import daterange, strategies, all_the_keys, etfs_to_process
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


def add_selector_info():
    summary = {}
    summary["options"] = {}
    summary["options"]["strategies"] = strategies
    summary["options"]["funds"] = etfs_to_process
    summary["options"]["assume overnight delay"] = not(precalc)

    return summary


def append_summary(fundsdata, indicator):
    for indicator in strategies:
        fundsdata[indicator] = {}
        fundsdata[indicator]['meta'] = {}
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
                r = fundsdata[symbol]['meta'][indicator][indicator + "_value"] - 1
                sum_of_returns += r
                sum_of_days_held += fundsdata[symbol]['meta'][indicator]["days_held"]
                sum_of_number_of_days += fundsdata[symbol]['meta']["number_of_days"]
                sum_of_next_days_right += (
                    fundsdata[symbol]['meta'][indicator]["days_right"])
                sum_of_days_held_right += (
                    fundsdata[symbol]['meta'][indicator]["profitable_days"])
                sum_of_rightable_days += (
                    fundsdata[symbol]['meta']["market_days"] - 1)
                sum_of_cagr_x_days += (
                    fundsdata[symbol]['meta'][indicator]["averaged_annualized_CAGR"] *
                    fundsdata[symbol]['meta']["number_of_days"])

# calculate the interesting values
        if sum_of_rightable_days != 0:
            fundsdata[indicator]['meta']["next_days_right_rate"] = round(
                (sum_of_next_days_right / sum_of_rightable_days), 3)
        else:
            fundsdata[indicator]['meta']["next_days_right_rate"] = 0

        if sum_of_days_held_right != 0:
            fundsdata[indicator]['meta']["profitable_days_rate"] = round(
                (sum_of_days_held_right / sum_of_days_held), 3)
        else:
            fundsdata[indicator]['meta']["next_days_right_rate"] = 0

        if sum_of_number_of_days != 0:
            fundsdata[indicator]['meta']["averaged_annualized_CAGR"] = round(
                (sum_of_cagr_x_days / sum_of_number_of_days), 5)
        else:
            fundsdata[indicator]['meta']["averaged_annualized_CAGR"] = 0

    return fundsdata


def merge_fund_indicator_returns(symbol, strategy, fund_data):
    fundata = {}
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
    dates = dates_from_keys(fundata.keys())
    if len(dates):
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
        fundata["note"] = "No data in range for "
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
    funkeys = list(fun_data.keys())
    for date in funkeys:
        if int(date.replace("-", "")) >= start:
            if not (end):
                end = list(fun_data.keys())[-1]
            if (int(date.replace("-", "")) <= int(end.replace("-", ""))):
                fundata[date] = fun_data[date]

    return fundata


def all_indicators_only(fun_data):
    dates = dates_from_keys(fun_data.keys())
# remove all the dates that have incomplete data
    for date in sorted(list(fun_data.keys())):
        for indicator in all_the_keys:
            if not(indicator in fun_data[date].keys()):
                if date in dates:
                    dates.remove(date)

# copy values to a new object using keys that remain
    fundata = {}
    for date in dates:
        fundata[date] = fun_data[date]
    return fundata


# call methods that toss out extra data
def limit_fundata(fundata):
    fundata = all_indicators_only(fundata)
    fundata = fund_data_in_range(fundata)
    return fundata


def get_fundata(symbol): 
    filename = "./json/raw/" + symbol + ".json"  # if old data get update?
# read from file if there is one; call api if there isn't
    try:
        f = open(filename)
        fundata = json.load(f)
        f.close()
    except Exception as e:
        print(e)
        api_data = call_api(symbol)  # a response object set
        fundata = build_data_object(symbol, api_data)
        with open(filename, "w") as writeJSON:
            json.dump(fundata, writeJSON)
    if too_old(dates_from_keys(fundata.keys())[-1], 2):
        # import pdb; pdb.set_trace()
        api_data = call_api(symbol)
        fundata = build_data_object(symbol, api_data)
        with open(filename, "w") as writeJSON:
            json.dump(fundata, writeJSON)
# toss unwanted date
    fundata = limit_fundata(fundata)
# incllude the symbol name for human readability
    if "meta" in fundata.keys():
        fundata["meta"]["symbol"] = symbol
    else:
        if "note" in fundata.keys():
            fundata["note"] = fundata["note"] + symbol
        else:
            fundata["note"] = symbol
    return fundata


def build_file_names():
    start = daterange[0]
    if not start:
        start = ""
    end = daterange[1]
    if not end:
        end = ""
    funds_filename = "./json/processed/fundsdata " + start + " - " + end + ".json"
    filename = "./json/processed/summary " + start + " - " + end + ".json"
    return(filename, funds_filename)


def build_processed_data():
    # import pdb; pdb.set_trace()
    fundsdata = {}
# marshall api data
    for symbol in etfs_to_process:
        fundsdata[symbol] = get_fundata(symbol)
# add helpful fund specific information
        fundsdata[symbol] = include_fund_specific_meta_data(fundsdata[symbol])
# get and merge data from investment return calculations
    for strategy in strategies:
        for symbol in etfs_to_process:
            fundsdata[symbol] = merge_fund_indicator_returns(
                symbol, strategy, fundsdata[symbol])
# build and append per-fund and per-strategem summary values (averages)
    for strategy in strategies:
        fundsdata = append_summary(fundsdata, strategy)
# create readable JSON summary to save as smaller file
# list selected options
    summary = add_selector_info()
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
# python -c 'from build_summary import build_processed_data; build_processed_data()'