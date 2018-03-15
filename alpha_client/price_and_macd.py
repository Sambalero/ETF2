# Average return on day-after macd signal hold compared to average return timespan
from api import priceset, macds
from config import symbols
import json
from analysis import calc_return_based_on_daily_macd_hist, simple_return


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


def work_with_files():
    for symbol in symbols:
        prices = priceset(symbol)
        macd = macds(symbol)
        (macd_hist_returns, summary, macd_days_held) = (
            calc_return_based_on_daily_macd_hist(prices))
        dates = list(sorted(prices.keys()))
        for date in dates:
            if (not (macd is None)) and date in macd.keys():
                prices[date]["MACD"] = macd[date]["MACD"]
                prices[date]["MACD_Hist"] = macd[date]["MACD_Hist"]
                prices[date]["MACD_Signal"] = macd[date]["MACD_Signal"]

        filename = symbol + "pm.json"
        prices["mh"] = (summary, macd_days_held)
        with open(filename, "w") as writeJSON:
            json.dump(prices, writeJSON)

# python -c 'from price_and_macd_data import work_with_files; work_with_files()'
# python -c 'from price_and_macd import main; main()'
 struct [date]["MACD_Hist"],["mhreturn"],["mhvalue"]