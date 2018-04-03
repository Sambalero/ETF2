from client import build_data_object, call_api
from config import symbols, daterange, strategems, all_the_keys
import json
from analysis import calc_returns
from dateutil import parser


def dates_from_keys(dates):
    dates = list(sorted(dates))
    if "meta" in dates:
        dates.remove("meta")
    return dates


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


def include_meta_data(fundata):
    dates = dates_from_keys(fundata.keys())
    fundata["meta"] = {}
    fundata["meta"]["date_range"] = (dates[0], dates[-1])
    fundata["meta"]["number_of_days"] = (
        parser.parse(dates[-1]) - parser.parse(dates[0])).days
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
        return_x_days_held = 0
        next_days_right_x_days_held = 0
        return_x_number_of_days = 0
        sum_of_days_held = 0
        sum_of_number_of_days = 0

        for symbol in symbols:
            r = fundsdata[symbol]['meta'][indicator][indicator + "_value"] - 1
            return_x_days_held += (
                r * fundsdata[symbol]['meta'][indicator]["days_held"])
            return_x_number_of_days += r * fundsdata[symbol]['meta']["number_of_days"]
            next_days_right_x_days_held += (
                fundsdata[symbol]['meta'][indicator]["days_held"] *
                fundsdata[symbol]['meta'][indicator]["days_right"])
            sum_of_days_held += fundsdata[symbol]['meta'][indicator]["days_held"]
            sum_of_number_of_days += fundsdata[symbol]['meta']["number_of_days"]

        fundsdata[indicator]['meta']["average_return_rate"] = (
            return_x_number_of_days / sum_of_number_of_days)
        fundsdata[indicator]['meta']["next_days_right_rate"] = (
            next_days_right_x_days_held / sum_of_days_held)
        fundsdata[indicator]['meta']["per_day_return_rate"] = (
            return_x_days_held / sum_of_days_held)

    return fundsdata


def build_funds_meta_data(fundsdata):
    funds_meta_data = {}
    for indicator in strategems:
        funds_meta_data[indicator] = fundsdata[indicator]['meta']

    for symbol in symbols:
        funds_meta_data[symbol] = fundsdata[symbol]['meta']

    return funds_meta_data


def build_processed_data():
    fundsdata = {}

    for symbol in symbols:
        fundsdata[symbol] = get_fundata(symbol)

    for indicator in strategems:
        for symbol in symbols:
            fundsdata[symbol] = merge_fund_indicator_returns(
                symbol, indicator, fundsdata[symbol])

    for indicator in strategems:
        fundsdata = append_summary(fundsdata, indicator)

    funds_meta_data = build_funds_meta_data(fundsdata)

    start = daterange[0]
    if not start:
        start = ""
    end = daterange[1]
    if not end:
        end = ""

    if start and end:
        funds_filename = "./json/processed/fundsdata " + start + " - " + " .json"
        with open(funds_filename, "w") as writeJSON:
            json.dump(fundsdata, writeJSON)

    filename = "./json/processed/funds_meta_data " + start + " - " + " .json"
    with open(filename, "w") as writeJSON:
        json.dump(funds_meta_data, writeJSON)
