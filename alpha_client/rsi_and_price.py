# Average return on day-after macd signal hold compared to average return timespan
from api import priceset, macds, rsis
from client import build_data_object, call_api
from config import symbols, daterange
import json
from analysis import calc_return_based_on_daily_macd_hist, simple_return, calc_rsi_returns


# compares macd hist bsed investment vs buy-and-hold strategy
# input: fund symbol, date range
# call api for price and macd data
# call analysis methods for calculated values
# output to stdout and return to caller
def rsi_and_price_data(symbol, start=0, **kwargs):  # end expected in kwargs
    prices = priceset(symbol)
    rsi = rsis(symbol)
    dates = []
    for date in prices.keys():
        if int(date.replace("-", "")) >= start:
            if "end" in kwargs and int(date.replace("-", "")) > kwargs['end']:
                dates.append(date)
            else:
                dates.append(date)
    dates = list(sorted(dates))
    for date in dates:
        if (not (macd is None)) and date in macd.keys():
            prices[date]["MACD"] = macd[date]["MACD"]
            prices[date]["MACD_Hist"] = macd[date]["MACD_Hist"]
            prices[date]["MACD_Signal"] = macd[date]["MACD_Signal"]
    (macd_hist_returns, summary, macd_days_held) = (
        calc_return_based_on_daily_macd_hist(prices))
    print(symbol, dates[0], dates[-1])
    print(symbol, "Average rate of return using MACD_Hist:", summary)
    per_day = 365 * (macd_hist_returns[dates[-2]]["mhvalue"] - 1) / (macd_days_held - 1)
    print(symbol, "Average per-day-held return using MACD_Hist:", per_day)
    buy_and_hold, average_simple_return = simple_return(prices)
    print(symbol, "Average_simple_return:", average_simple_return)
    return(summary, per_day, average_simple_return)


# from plot 140
# build pm data for missing fund for plot
# ???? add to cumulative calcs ????
def add_to_pm_funds_data(symbol):
    start = daterange[0]
    end = daterange[1]
    fundata = get_fundata(symbol)
    if start and end:
        fundata = (rsi_v_price(symbol, fundata, start, end=end))
    else:
        fundata = (rsi_v_price(symbol, fundata))
    return fundata


# compares macd hist based investment vs buy-and-hold strategy
# input: fund data, date range
# call analysis methods for calculated values
# append daily return values to fundata object
# output final values to stdout and return everything
def rsi_v_price(symbol, fund_data, start='0', **kwargs):  # end expected in kwargs
    dates = []
    fundata = {}  # a new object that only covers the given range
    for date in fund_data.keys():
        if int(date.replace("-", "")) >= int(start.replace("-", "")):
            if not ("end" in kwargs):
                kwargs['end'] = list(fund_data.keys())[0]  # leave off the last date
            if (int(date.replace("-", "")) < int(kwargs['end'].replace("-", ""))):
                dates.append(date)
                fundata[date] = fund_data[date]
    dates = list(sorted(dates))
    rsi_returns = calc_rsi_returns(fundata)
    buy_and_hold, average_simple_return = simple_return(fundata)
    initial_price = float(fundata[dates[0]]["4. close"])
    for date in dates:
        if date in rsi_returns.keys():
            fundata[date]["rsi_return"] = rsi_returns[date]["rsi_return"]
            fundata[date]["rsi_value"] = rsi_returns[date]["rsi_value"]
            fundata[date]["buy and hold value"] = buy_and_hold[date]["value"]
            fundata[date]["return"] = buy_and_hold[date]["return"]
            fundata[date]["price"] = float(fundata[date]["4. close"]) / initial_price
    print(symbol, dates[0], dates[-1])
    print(symbol, "Average rate of return using RSI:", rsi_returns["rsi meta"]["rsi_average_return_rate"])
    per_day = 365 * (rsi_returns[dates[-2]]["rsi_value"] - 1) / (rsi_returns["rsi meta"]["rsi_days_held"] - 1)
    print(symbol, "Average per-day-held return using RSI:", rsi_returns["rsi meta"]["rsi_average_return_rate"])
    print(symbol, "Average_simple_return:", average_simple_return)
    fundata["meta"] = {}
    fundata["meta"]["Average rate of return using RSI"] = rsi_returns["rsi meta"]["rsi_average_return_rate"]
    fundata["meta"]["Average per-day-held return using RSI"] = per_day
    fundata["meta"]["RSI days held"] = rsi_returns["rsi meta"]["rsi_days_held"]
    fundata["meta"]["Average_simple_return"] = average_simple_return
    fundata["meta"]["Length of time averaged"] = rsi_returns["rsi meta"]["number_of_days"]
    fundata["meta"]["Next day right rate"] = rsi_returns["rsi meta"]["days_right_rate"]
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


def main():
    n, amr, day, asr = 0, 0, 0, 0
    for symbol in symbols:
        (summary, per_day, average_simple_return) = rsi_and_price_data(symbol)
        amr += summary
        day += per_day
        asr += average_simple_return
        n += 1
    print("Average rate of return using MACD_Hist:", amr / n)
    print("Average per-day-held return using MACD_Hist:", day / n)
    print("Average_simple_return:", asr / n)


# Use data from files rather than call the api.
# But call the api if you have to
# write to files, too.
def work_with_files():
    start = daterange[0]
    end = daterange[1]
    n, amr, day, asr = 0, 0, 0, 0
    rsi_and_price = {}
    for symbol in symbols:
        fundata = get_fundata(symbol)
        if start and end:
            fundata = (rsi_v_price(symbol, fundata, start, end=end))   # *******LEFT method HERE^^^^^^^^^^^^^^^^^^^^^^^^^^
        else:
            fundata = (rsi_v_price(symbol, fundata))
        amr += fundata["meta"]["Average rate of return using RSI"]
        day += fundata["meta"]["Average per-day-held return using RSI"]
        asr += fundata["meta"]["Average_simple_return"]
        n += 1
        rsi_and_price[symbol] = fundata
# These average values are highly imprecise but that's fixable.
    print("Average rate of return using RSI:", amr / n)
    print("Average per-day-held return using RSI:", day / n)
    print("Average_simple_return:", asr / n)
    rsi_and_price["Average rate of return using RSI:"] = amr / n
    rsi_and_price["Average per-day-held return using MACD_Hist:"] = day / n
    rsi_and_price["Average_simple_return:"] = asr / n
    if not(start and end): 
        (start, end) = fundata["meta"]["date range"]
    filename = "./json/processed/pr " + start + " - " + end + ".json"
    with open(filename, "w") as writeJSON:
        json.dump(rsi_and_price, writeJSON)

# python -c 'from rsi_and_price import work_with_files; work_with_files()'
# python -c 'from rsi_and_price import main; main()'
# struct [date]["MACD_Hist"],["mhreturn"],["mhvalue"]
