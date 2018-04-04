from client import build_data_object, call_api
from config import symbols, daterange, strategems, all_the_keys
import json
from analysis import calc_returns, dates_from_keys, calc_rate_of_return
from dateutil import parser


# get return values by given fund and indicator
# merge that with api data in fund object
def merge_fund_indicator_returns(symbol, indicator, fund_data):
    # if not(fund_data):
    #     print(symbol, indicator)
    dates = dates_from_keys(fund_data.keys())
    # merge returns with api data
    # calc returns will have value and hold info by date plus
    # summarized values by symbol ("meta")
    fireturns = calc_returns(fund_data, indicator)
    fundata = {}
    if "meta" in fund_data.keys():
        fundata["meta"] = {**fireturns["meta"], **fund_data["meta"]}
    else:
        fundata["meta"] = fireturns["meta"]
    for date in dates:
        if date in fireturns.keys():
            fundata[date] = {**fireturns[date], **fund_data[date]}
    else:
        fundata[date] = fund_data[date]

    return fundata


def all_indicators_only(fun_data):
    dates = dates_from_keys(fun_data.keys())
    for date in sorted(list(fun_data.keys())):
        for indicator in all_the_keys:
            if not(indicator in fun_data[date].keys()):
                if date in dates:
                    dates.remove(date)
    fundata = {}
    for date in dates:
        fundata[date] = fun_data[date]
    return fundata


def fund_data_in_range(fun_data):

    start = daterange[0]
    if start:
        start = int(start.replace("-", ""))
    else:
        start = 0
    end = daterange[1]
    fundata = {}  # a new object that only covers the given range
    funkeys = list(fun_data.keys())
    for date in funkeys:
        if int(date.replace("-", "")) >= start:
            if not (end):
                end = list(fun_data.keys())[-1]
            if (int(date.replace("-", "")) <= int(end.replace("-", ""))):
                fundata[date] = fun_data[date]
    return fundata


def calc_return(start, end):
    if start > end:
        return ((end - start) / start)
    else:
        return (((end - start) / start) - 1)


def include_meta_data(fundata):
    dates = dates_from_keys(fundata.keys())
    fundata["meta"] = {}
    fundata["meta"]["start"] = dates[0]
    fundata["meta"]["starting price"] = fundata[dates[0]]["4. close"]
    fundata["meta"]["end"] = dates[-1]
    fundata["meta"]["ending price"] = fundata[dates[-1]]["4. close"]
    fundata["meta"]["number_of_days"] = (
        parser.parse(dates[-1]) - parser.parse(dates[0])).days
    fundata["meta"]["market_days"] = len(dates)
    fundata["meta"]["total return"] = round(calc_return(
        float(fundata["meta"]["starting price"]),
        float(fundata["meta"]["ending price"])), 3)
    fundata["meta"]["daily rate"] = round(calc_rate_of_return(
        float(fundata["meta"]["starting price"]),
        float(fundata["meta"]["ending price"]),
        fundata["meta"]["number_of_days"]), 10)
    return fundata


def limit_fundata(fundata):
    fundata = all_indicators_only(fundata)

    fundata = fund_data_in_range(fundata)

    fundata = include_meta_data(fundata)
    return fundata


def get_fundata(symbol):
    filename = "./json/raw/" + symbol + ".json"  # if old data get update?
    try:
        f = open(filename)
        fundata = json.load(f)
        f.close()
    except IOError:
        api_data = call_api(symbol)
        fundata = build_data_object(symbol, api_data)
        with open(filename, "w") as writeJSON:
            json.dump(fundata, writeJSON)
    fundata = limit_fundata(fundata)
    fundata["meta"]["symbol"] = symbol
    return fundata


def append_summary(fundsdata, indicator):
    for indicator in strategems:
        fundsdata[indicator] = {}
        fundsdata[indicator]['meta'] = {}
        sum_of_days_held = 0
        sum_of_number_of_days = 0
        sum_of_returns = 0
        sum_of_next_days_right = 0
        sum_of_rightable_days = 0
        sum_of_cagr_x_days = 0

        for symbol in symbols:
            r = fundsdata[symbol]['meta'][indicator][indicator + "_value"] - 1
            sum_of_returns += r
            sum_of_days_held += fundsdata[symbol]['meta'][indicator]["days_held"]
            sum_of_number_of_days += fundsdata[symbol]['meta']["number_of_days"]
            sum_of_next_days_right += fundsdata[symbol]['meta'][indicator]["days_right"]
            sum_of_rightable_days += (
                fundsdata[symbol]['meta']["market_days"] - 1)
            sum_of_cagr_x_days += (
                fundsdata[symbol]['meta'][indicator]["daily_return_rate"] *
                fundsdata[symbol]['meta']["number_of_days"])

        if sum_of_number_of_days != 0:
            fundsdata[indicator]['meta']["average_return_rate"] = round(
                (36500 * r / sum_of_number_of_days), 5)
        else:
            fundsdata[indicator]['meta']["average_return_rate"] = 0

        if sum_of_rightable_days != 0:
            fundsdata[indicator]['meta']["next_days_right_rate"] = round(
                (sum_of_next_days_right / sum_of_rightable_days), 3)
        else:
            fundsdata[indicator]['meta']["next_days_right_rate"] = 0

        if sum_of_days_held != 0:
            fundsdata[indicator]['meta']["annualized_per_day_return"] = round(
                (36500 * r / sum_of_days_held), 5)
        else:
            fundsdata[indicator]['meta']["annualized_per_day_return"] = 0

        if sum_of_number_of_days != 0:
            fundsdata[indicator]['meta']["averaged CAGR"] = round(
                (sum_of_cagr_x_days / sum_of_number_of_days), 5)
        else:
            fundsdata[indicator]['meta']["averaged CAGR"] = 0

    return fundsdata


def build_funds_meta_data(fundsdata, funds_meta_data):
    for indicator in strategems:
        funds_meta_data[indicator] = fundsdata[indicator]['meta']

    for symbol in symbols:
        funds_meta_data[symbol] = fundsdata[symbol]['meta']

    return funds_meta_data


def add_data_descriptors():
    funds_meta_data = {}
    funds_meta_data["meta"] = {}
    funds_meta_data["meta"]["average_return_rate"] = (
        "average annualized percent profit or loss on $1 per stratem")
    funds_meta_data["meta"]["next_days_right_rate"] = "daily predictive probability"
    funds_meta_data["meta"]["per_day_return_rate"] = (
        "average annualized percent daily return on $1 when invested")
    funds_meta_data["meta"]["days_held"] = "number of days invested during period"
    funds_meta_data["meta"]["days_right"] = (
        "number of days predicted correctly during period")
    funds_meta_data["meta"]["market days"] = "investment days available during period"
    funds_meta_data["meta"]["days_right_rate"] = "same as next_days_right_rate"
    funds_meta_data["meta"]["<indicator>_value"] = (
        "value of $1 invested per strategem at end of period")
    funds_meta_data["meta"]["average per day return"] = "same as per_day_return_rate"
    funds_meta_data["meta"]["average_return_rate"] = (
        "average annualized percent profit or loss on $1 per stratem")
    funds_meta_data["meta"]["number_of_days"] = "number of days in period"

    return funds_meta_data


def build_processed_data():
    fundsdata = {}
# mashall api data
    for symbol in symbols:
        fundsdata[symbol] = get_fundata(symbol)
# get and merge data from strategems
    for indicator in strategems:
        for symbol in symbols:
            fundsdata[symbol] = merge_fund_indicator_returns(
                symbol, indicator, fundsdata[symbol])
# build and append per-fund and per-strategem summary values (averages)
    for indicator in strategems:
        fundsdata = append_summary(fundsdata, indicator)
# create readable JSON summary to save as smaller file
# with explanatory notes for clarity
    funds_meta_data = add_data_descriptors()
    funds_meta_data = build_funds_meta_data(fundsdata, funds_meta_data)
# build file names
    start = daterange[0]
    if not start:
        start = ""
    end = daterange[1]
    if not end:
        end = ""
    funds_filename = "./json/processed/fundsdata " + start + " - " + end + ".json"
    filename = "./json/processed/funds_meta_data " + start + " - " + end + ".json"
# save
    with open(funds_filename, "w") as writeJSON:
        json.dump(fundsdata, writeJSON)
    with open(filename, "w") as writeJSON:
        json.dump(funds_meta_data, writeJSON)
