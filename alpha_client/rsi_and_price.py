from client import build_data_object, call_api
from config import symbols, daterange, indicators
import json
from analysis import simple_return, calc_returns


# limit dates to range from config.py
# get return values by given fund and indicator
# merge that with api data in fund object
def merge_fund_indicator_returns(symbol, indicator, fund_data):
    start = daterange[0]
    if start:
        start = int(start.replace("-", ""))
    else:
        start = 0
    end = daterange[1]
    dates = []
    fundata = {}  # a new object that only covers the given range
    funkeys = list(fund_data.keys())
    if "meta" in funkeys:
        funkeys.remove("meta")
    for date in funkeys:
        if int(date.replace("-", "")) >= start:
            if not (end):
                end = list(fund_data.keys())[0]  # leave off the last date
            if (int(date.replace("-", "")) < int(end.replace("-", ""))):
                dates.append(date)
                fundata[date] = fund_data[date]
    dates = list(sorted(dates))

    # merge returns with api data
    # calc returns will have value and hold info by date plus
    # summarized values by symbol ("meta")
    fireturns = calc_returns(fundata, indicator)
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


# *****DEPRECATED***
# compares macd hist based investment vs buy-and-hold strategy
# input: fund data, date range
# call analysis methods for calculated values
# append daily return values to fundata object
# output final values to stdout and return everything

def indicator_v_price(symbol, indicator, fund_data, start='0', **kwargs):
    dates = []
    # indicator = "RSI"
    fundata = {}  # a new object that only covers the given range
    # print( indicator + " : " +)
    for date in fund_data.keys():
        if date == "RSI":
            print("Here is the errror")
            print(symbol, indicator)
        if int(date.replace("-", "")) >= int(start.replace("-", "")):
            if not ("end" in kwargs):
                kwargs['end'] = list(fund_data.keys())[0]  # leave off the last date
            if (int(date.replace("-", "")) < int(kwargs['end'].replace("-", ""))):
                dates.append(date)
                fundata[date] = fund_data[date]
    dates = list(sorted(dates))
    # returns = calc_rsi_returns(fundata)
    returns = calc_returns(fundata, indicator)
    buy_and_hold, average_simple_return = simple_return(fundata)  # move elsewhere
    initial_price = float(fundata[dates[0]]["4. close"])
    meta = indicator + "meta"
    print(returns[meta].keys())
    i = 0
    for date in dates:
        if date in returns.keys():
            if i == 0:
                print(returns[date].keys())
            i += 1
            fundata[date][indicator + " return"] = returns[date][indicator + " return"]
            fundata[date][indicator + " value"] = returns[date][indicator + " value"]
            fundata[date]["buy and hold value"] = buy_and_hold[date]["buy and hold value"]
            fundata[date]["return"] = buy_and_hold[date]["return"]
            fundata[date]["price"] = float(fundata[date]["4. close"]) / initial_price
    print(symbol, dates[0], dates[-1])
    print(symbol, "Average rate of return using " + indicator + ": ",
          returns[meta][indicator + " average_return_rate"])
    per_day = 365 * (returns[dates[-2]][indicator + " value"] - 1) / (
        returns[meta][indicator + " days_held"] - 1)
    print(symbol, "Average per-day-held return using " + indicator + ": ",
          returns[meta][indicator + " average_return_rate"])
    print(symbol, "Average_simple_return using " + indicator + ": ",
          average_simple_return)
    print(symbol, "RSI days_right_rate:", returns[meta][indicator + " days_right_rate"])

    fundata["meta"] = {}
    fundata["meta"]["Average rate of return using " + indicator] = (
        returns[meta][indicator + " average_return_rate"])
    fundata["meta"]["Average per-day-held return using " + indicator] = per_day
    fundata["meta"]["Number of days held"] = returns[meta][indicator + " days_held"]
    fundata["meta"]["Average_simple_return"] = average_simple_return
    fundata["meta"]["Length of time averaged"] = (
        returns[meta][indicator + " number_of_days"])
    fundata["meta"]["Next day right rate"] = returns[meta][indicator + " days_right_rate"]
    fundata["meta"]["symbol"] = symbol
    fundata["meta"]["date range"] = (dates[0], dates[-1])
    return(fundata)


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
    return fundata


# Build processed data object from saved api responses
# But call the api if you have to
# write to files, too.
def work_with_files():  # DEPRECATED
    returns = {}
    fundsdata = {}
    for symbol in symbols:
        fundsdata[symbol] = get_fundata(symbol)

    for indicator in indicators:
        start = daterange[0]
        end = daterange[1]
        n, amr, day, asr = 0, 0, 0, 0
        returns[indicator] = {}

        for symbol in symbols:
            if start and end:
                fundata = (indicator_v_price(symbol, indicator, fundsdata[symbol],
                           start, end=end))
            else:
                fundata = (indicator_v_price(symbol, indicator, fundsdata[symbol]))
            amr += fundata["meta"]["Average rate of return using " + indicator]
            day += fundata["meta"]["Average per-day-held return using " + indicator]
            asr += fundata["meta"]["Average_simple_return"]
            n += 1
            if not(symbol in returns.keys()):
                returns[symbol] = {}
            returns[symbol][indicator] = fundata
    # These average values are highly imprecise but that's fixable.
        print("Average rate of return using " + indicator + " :", amr / n)
        print("Average per-day-held return using " + indicator + " :", day / n)
        print("Average_simple_return:", asr / n)
        returns[indicator]["Average rate of return using " + indicator + " :"] = amr / n
        returns[indicator]["Average per-day-held return using " + indicator + " :"] = (
            day / n)
        returns[indicator]["Average_simple_return:"] = asr / n

    filename = "./json/processed/returns.json"
    with open(filename, "w") as writeJSON:
        json.dump(returns, writeJSON)


def build_processed_data():
    fundsdata = {}
    fundsdata['meta'] = {}

    for symbol in symbols:
        fundsdata[symbol] = get_fundata(symbol)

    for indicator in indicators:
        for symbol in symbols:
            fundsdata[symbol] = merge_fund_indicator_returns(
                symbol, indicator, fundsdata[symbol])

    subtotal_of_return = 0
    subtotal_of_days_in_period = 0
    subtotal_of_days_held = 0
    subtotal_of_next_days_right = 0
    subtotal_of_market_days = 0

    for indicator in indicators:
        fundsdata[indicator] = {}
        fundsdata[indicator]['meta'] = {}

        for symbol in symbols:
            subtotal_of_return += fundsdata[symbol]['meta'][indicator]["value"]
            subtotal_of_days_in_period += (
                fundsdata[symbol]['meta'][indicator]["number_of_days"])
            subtotal_of_days_held += fundsdata[symbol]['meta'][indicator]["days_held"]
            subtotal_of_next_days_right += (
                fundsdata[symbol]['meta'][indicator]["days_right"])
            subtotal_of_market_days += fundsdata[symbol]['meta'][indicator]["market days"]

        fundsdata[indicator]['meta']["average_return_rate"] = (
            subtotal_of_return / subtotal_of_days_in_period)
        fundsdata[indicator]['meta']["next_days_right_rate"] = (
            subtotal_of_next_days_right / subtotal_of_market_days)
        fundsdata[indicator]['meta']["per_day_return_rate"] = (
            subtotal_of_return / subtotal_of_days_held)

    funds_meta_data = {}
    for indicator in indicators:
        funds_meta_data[indicator] = fundsdata[indicator]['meta']
    for symbol in symbols:
        funds_meta_data[symbol] = fundsdata[symbol]['meta']

    filename = "./json/processed/funds_meta_data.json"
    with open(filename, "w") as writeJSON:
        json.dump(funds_meta_data, writeJSON)
