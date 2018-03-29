# Average return on day-after macd signal hold compared to average return timespan
from api import priceset, macds, rsis
from client import build_data_object, call_api
from config import symbols, daterange, indicators
import json
from analysis import simple_return, calc_returns
# from analysis import calc_return_based_on_daily_macd_hist, , calc_rsi_returns


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


# compares macd hist based investment vs buy-and-hold strategy
# input: fund data, date range
# call analysis methods for calculated values
# append daily return values to fundata object
# output final values to stdout and return everything
def indicator_v_price(symbol, indicator, fund_data, start='0', **kwargs):  # end expected in kwargs
    dates = []
    # indicator = "RSI"
    fundata = {}  # a new object that only covers the given range
    for date in fund_data.keys():
        if int(date.replace("-", "")) >= int(start.replace("-", "")):
            if not ("end" in kwargs):
                kwargs['end'] = list(fund_data.keys())[0]  # leave off the last date
            if (int(date.replace("-", "")) < int(kwargs['end'].replace("-", ""))):
                dates.append(date)
                fundata[date] = fund_data[date]
    dates = list(sorted(dates))
    # returns = calc_rsi_returns(fundata)
    returns = calc_returns(fundata, indicator)
    buy_and_hold, average_simple_return = simple_return(fundata)
    initial_price = float(fundata[dates[0]]["4. close"])
    meta = indicator + "meta"
    print(returns[meta].keys())
    for date in dates:
        if date in returns.keys():
            fundata[date][indicator + "return"] = returns[date][indicator + "return"]
            fundata[date][indicator + "value"] = returns[date][indicator + "value"]
            fundata[date]["buy and hold value"] = buy_and_hold[date]["buy and hold value"]
            fundata[date]["return"] = buy_and_hold[date]["return"]
            fundata[date]["price"] = float(fundata[date]["4. close"]) / initial_price
    print(symbol, dates[0], dates[-1])
    print(symbol, "Average rate of return using " + indicator + ": ", returns[meta][indicator + " average_return_rate"])
    per_day = 365 * (returns[dates[-2]][indicator + "value"] - 1) / (returns[meta][indicator + " days_held"] - 1)
    print(symbol, "Average per-day-held return using " + indicator + ": ", returns[meta][indicator + " average_return_rate"])
    print(symbol, "Average_simple_return using " + indicator + ": ", average_simple_return)
    print(symbol, "RSI days_right_rate:", returns[meta][indicator + " days_right_rate"])

    fundata["meta"] = {}
    fundata["meta"]["Average rate of return using " + indicator] = returns[meta][indicator + " average_return_rate"]
    fundata["meta"]["Average per-day-held return using " + indicator] = per_day
    fundata["meta"]["Number of days held"] = returns[meta][indicator + " days_held"]
    fundata["meta"]["Average_simple_return"] = average_simple_return
    fundata["meta"]["Length of time averaged"] = returns[meta][indicator + " number_of_days"]
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
def work_with_files():
    returns = {}
    for indicator in indicators:
        start = daterange[0]
        end = daterange[1]
        n, amr, day, asr = 0, 0, 0, 0
        returns[indicator] = {}
        for symbol in symbols:
            returns[symbol] = {}
            fundata = get_fundata(symbol)
            if start and end:
                fundata = (indicator_v_price(symbol, indicator, fundata, start, end=end))  
            else:
                fundata = (indicator_v_price(symbol, indicator, fundata))
            amr += fundata["meta"]["Average rate of return using " + indicator]
            day += fundata["meta"]["Average per-day-held return using " + indicator]
            asr += fundata["meta"]["Average_simple_return"]  # ,,,,,,,,,,,,,,,,pull this out
            n += 1
            returns[symbol][indicator] = fundata
    # These average values are highly imprecise but that's fixable.
        print("Average rate of return using " + indicator + " :", amr / n)
        print("Average per-day-held return using " + indicator + " :", day / n)
        print("Average_simple_return:", asr / n)
        returns[indicator]["Average rate of return using " + indicator + " :"] = amr / n
        returns[indicator]["Average per-day-held return using " + indicator + " :"] = day / n
        returns[indicator]["Average_simple_return:"] = asr / n
        # if not(start and end):
        #     (start, end) = fundata["meta"]["date range"]
        # filename = "./json/processed/returns " + start + " - " + end + ".json"
    # import pdb; pdb.set_trace()
    filename = "./json/processed/returns.json"
    with open(filename, "w") as writeJSON:
        json.dump(returns, writeJSON)

# python -c 'from rsi_and_price import work_with_files; work_with_files()'
# python -c 'from rsi_and_price import main; main()'
# struct [date]["MACD_Hist"],["mhreturn"],["mhvalue"]
