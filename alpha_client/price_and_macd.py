# Average return on day-after macd signal hold compared to average return timespan
from api import priceset, macds
from client import build_data_object, call_api
from config import symbols, daterange
import json
from analysis import simple_return, calc_returns
from rsi_and_price import indicator_v_price
# from analysis import calc_return_based_on_daily_macd_hist,


# compares macd hist bsed investment vs buy-and-hold strategy
# input: fund symbol, date range
# call api for price and macd data
# call analysis methods for calculated values
# output to stdout and return to caller
# def price_and_macd_data(symbol, start=0, **kwargs):  # end expected in kwargs
#     prices = priceset(symbol)
#     macd = macds(symbol)
#     dates = []
#     for date in prices.keys():
#         if int(date.replace("-", "")) >= start:
#             if "end" in kwargs and int(date.replace("-", "")) > kwargs['end']:
#                 dates.append(date)
#             else:
#                 dates.append(date)
#     dates = list(sorted(dates))
#     for date in dates:
#         if (not (macd is None)) and date in macd.keys():
#             prices[date]["MACD"] = macd[date]["MACD"]
#             prices[date]["MACD_Hist"] = macd[date]["MACD_Hist"]
#             prices[date]["MACD_Signal"] = macd[date]["MACD_Signal"]
#     (macd_hist_returns, summary, macd_days_held) = (
#         calc_return_based_on_daily_macd_hist(prices))
#     print(symbol, dates[0], dates[-1])  # ********HERE IS THE NO DATE DATE RANGE^^^^^^^^^^^^^^^^^^^^^^^^^^
#     print(symbol, "Average rate of return using MACD_Hist:", summary)
#     per_day = 365 * (macd_hist_returns[dates[-2]]["mhvalue"] - 1) / (macd_days_held - 1)
#     print(symbol, "Average per-day-held return using MACD_Hist:", per_day)
#     buy_and_hold, average_simple_return = simple_return(prices)
#     print(symbol, "Average_simple_return:", average_simple_return)
#     return(summary, per_day, average_simple_return)


# from plot 140
# build pm data for missing fund for plot
# ???? add to cumulative calcs ????
def add_to_pm_funds_data(symbol):
    start = daterange[0]
    end = daterange[1]
    fundata = get_fundata(symbol)
    if start and end:
        fundata = (price_v_macd(symbol, fundata, start, end=end))
    else:
        fundata = (price_v_macd(symbol, fundata))
    return fundata


# compares macd hist based investment vs buy-and-hold strategy
# input: fund data, date range
# call analysis methods for calculated values
# append daily return values to fundata object
# output final values to stdout and return everything
def price_v_macd(symbol, fund_data, start='0', **kwargs):  # end expected in kwargs
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

    (macd_hist_returns, summary, macd_days_held, number_of_days, next_day_right_rate) = (
        calc_return_based_on_daily_macd_hist(fundata))
    buy_and_hold, average_simple_return = simple_return(fundata)
    initial_price = float(fundata[dates[0]]["4. close"])
    for date in dates:
        if date in macd_hist_returns.keys():
            fundata[date]["mhreturn"] = macd_hist_returns[date]["mhreturn"]
            fundata[date]["mhvalue"] = macd_hist_returns[date]["mhvalue"]
            fundata[date]["buy and hold value"] = buy_and_hold[date]["value"]
            fundata[date]["return"] = buy_and_hold[date]["return"]
            fundata[date]["price"] = float(fundata[date]["4. close"]) / initial_price
    print(symbol, dates[0], dates[-1])
    print(symbol, "Average rate of return using MACD_Hist:", summary)
    per_day = 365 * (macd_hist_returns[dates[-2]]["mhvalue"] - 1) / (macd_days_held - 1)
    print(symbol, "Average per-day-held return using MACD_Hist:", per_day)
    print(symbol, "Average_simple_return:", average_simple_return)
    fundata["meta"] = {}
    fundata["meta"]["Average rate of return using MACD_Hist"] = summary
    fundata["meta"]["Average per-day-held return using MACD_Hist"] = per_day
    fundata["meta"]["MACD days held"] = macd_days_held
    fundata["meta"]["Average_simple_return"] = average_simple_return
    fundata["meta"]["Length of time averaged"] = number_of_days
    fundata["meta"]["Next day right rate"] = next_day_right_rate
    fundata["meta"]["symbol"] = symbol
    fundata["meta"]["date range"] = (dates[0], dates[-1])
    return(fundata)


def get_fundata(symbol):
    filename = "./json/raw/" + symbol + ".json"
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
        (summary, per_day, average_simple_return) = price_and_macd_data(symbol)
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
    price_and_macd = {}
    for symbol in symbols:
        fundata = get_fundata(symbol)
        if start and end:
            fundata = (price_v_macd(symbol, fundata, start, end=end))
        else:
            fundata = (price_v_macd(symbol, fundata))
        amr += fundata["meta"]["Average rate of return using MACD_Hist"]
        day += fundata["meta"]["Average per-day-held return using MACD_Hist"]
        asr += fundata["meta"]["Average_simple_return"]
        n += 1
        price_and_macd[symbol] = fundata
# These average values are highly imprecise but that's fixable.
    print("Average rate of return using MACD_Hist:", amr / n)
    print("Average per-day-held return using MACD_Hist:", day / n)
    print("Average_simple_return:", asr / n)
    price_and_macd["Average rate of return using MACD_Hist:"] = amr / n
    price_and_macd["Average per-day-held return using MACD_Hist:"] = day / n
    price_and_macd["Average_simple_return:"] = asr / n
    if start and end:  #     fundata["meta"]["date range"] = (dates[0], dates[-1])
        filename = "./json/processed/pm " + start + " - " + end + ".json"
    else:
        filename = "./json/processed/pm.json"
    with open(filename, "w") as writeJSON:
        json.dump(price_and_macd, writeJSON)

# python -c 'from price_and_macd import work_with_files; work_with_files()'
# python -c 'from price_and_macd import main; main()'
# struct [date]["MACD_Hist"],["mhreturn"],["mhvalue"]
