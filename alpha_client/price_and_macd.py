# Average return on day-after macd signal hold compared to average return timespan
from api import priceset, macds
from client import build_data_object, call_api
from config import symbols
import json
from analysis import calc_return_based_on_daily_macd_hist, simple_return


# compares macd hist bsed investment vs buy-and-hold strategy
# input: fund symbol, date range
# call api for price and macd data
# call analysis methods for calculated values
# output to stdout and return to caller
def price_and_macd_data(symbol, start=0, **kwargs):  # end expected in kwargs
    prices = priceset(symbol)
    macd = macds(symbol)
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


# compares macd hist based investment vs buy-and-hold strategy
# input: fund data, date range
# call analysis methods for calculated values
# output to stdout and return to caller
def price_v_macd(symbol, fund_data, start='0', **kwargs):  # end expected in kwargs
    dates = []
    fundata = {}
    for date in fund_data.keys():
        if int(date.replace("-", "")) >= int(start.replace("-", "")):
            if not ("end" in kwargs):
                kwargs['end'] = list(fund_data.keys())[0]  # leave off the last date
            if (int(date.replace("-", "")) < int(kwargs['end'].replace("-", ""))):
                dates.append(date)
                fundata[date] = fund_data[date]
    dates = list(sorted(dates))
    (macd_hist_returns, summary, macd_days_held) = (
        calc_return_based_on_daily_macd_hist(fundata))
    buy_and_hold, average_simple_return = simple_return(fundata)
    for date in dates:
        if date in macd_hist_returns.keys():
            fundata[date]["mhreturn"] = macd_hist_returns[date]["mhreturn"]
            fundata[date]["mhvalue"] = macd_hist_returns[date]["mhvalue"]
            fundata[date]["buy and hold value"] = buy_and_hold[date]["value"]
            fundata[date]["return"] = buy_and_hold[date]["return"]
    print(symbol, dates[0], dates[-1])
    print(symbol, "Average rate of return using MACD_Hist:", summary)
    per_day = 365 * (macd_hist_returns[dates[-2]]["mhvalue"] - 1) / (macd_days_held - 1)
    print(symbol, "Average per-day-held return using MACD_Hist:", per_day)
    print(symbol, "Average_simple_return:", average_simple_return)
    return(summary, per_day, average_simple_return, macd_hist_returns, fundata)


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
def work_with_files():  # (start=null, end=null)
    start = None
    end = None
    # start = '2015-01-01'
    # end = '2016-01-01'
    n, amr, day, asr = 0, 0, 0, 0
    price_and_macd = {}
    for symbol in symbols:
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

        if start and end:
            (summary, per_day, average_simple_return, macd_hist_returns, fundata) = (
                price_v_macd(symbol, fundata, start, end=end))
        else:
            (summary, per_day, average_simple_return, macd_hist_returns, fundata) = (
                price_v_macd(symbol, fundata))
        fundata["symbol"] = symbol
        fundata["summary"] = summary
        fundata["per_day"] = per_day
        fundata["average_simple_return"] = average_simple_return
        fundata["macd_hist_returns"] = macd_hist_returns
        amr += summary
        day += per_day
        asr += average_simple_return
        n += 1
        price_and_macd[symbol] = fundata
    print("Average rate of return using MACD_Hist:", amr / n)
    print("Average per-day-held return using MACD_Hist:", day / n)
    print("Average_simple_return:", asr / n)
    price_and_macd["Average rate of return using MACD_Hist:"] = amr / n
    price_and_macd["Average per-day-held return using MACD_Hist:"] = day / n
    price_and_macd["Average_simple_return:"] = asr / n
    if start and end:
        filename = "./json/processed/pm" + start + " - " + end + ".json"
    else:
        filename = "./json/processed/pm.json"
    with open(filename, "w") as writeJSON:
        json.dump(price_and_macd, writeJSON)

# python -c 'from price_and_macd import work_with_files; work_with_files()'
# python -c 'from price_and_macd import main; main()'
# struct [date]["MACD_Hist"],["mhreturn"],["mhvalue"]
