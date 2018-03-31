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


# indicator_v_price should merge indicator returns values with fundata, 
# and create/build  meta key
def merge_fund_indicator_returns(symbol, indicator, fund_data):
    start = daterange[0]
    if start: 
        start = int(start.replace("-", "")) 
    else: 
        start = 0
    end = daterange[1]
    dates = []
    fundata = {}  # a new object that only covers the given range
    funkeys = list(fund_data.keys())  # we may have added a "meta" key to our oject
    if "meta" in funkeys:
        funkeys.remove("meta")
    # import pdb; pdb.set_trace()
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
    # summarized values by symbol-indicator ("meta")
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




# compares macd hist based investment vs buy-and-hold strategy
# input: fund data, date range
# call analysis methods for calculated values
# append daily return values to fundata object
# output final values to stdout and return everything

def indicator_v_price(symbol, indicator, fund_data, start='0', **kwargs):  # end expected in kwargs
    dates = []
    # indicator = "RSI"
    fundata = {}  # a new object that only covers the given range
    # print( indicator + " : " +)
    for date in fund_data.keys():
        if date == "RSI":
            print ("Here is the errror")
            print (symbol, indicator)
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
    print(returns[meta].keys())  # -----------------------------------------------------
    i = 0
    for date in dates:
        if date in returns.keys():
            if i == 0:
                print(returns[date].keys())
            # [indicator] is included in return. Is there a reason??
            i += 1
            fundata[date][indicator + " return"] = returns[date][indicator + " return"]
            fundata[date][indicator + " value"] = returns[date][indicator + " value"]
            fundata[date]["buy and hold value"] = buy_and_hold[date]["buy and hold value"]
            fundata[date]["return"] = buy_and_hold[date]["return"]
            fundata[date]["price"] = float(fundata[date]["4. close"]) / initial_price
    print(symbol, dates[0], dates[-1])
    print(symbol, "Average rate of return using " + indicator + ": ", returns[meta][indicator + " average_return_rate"])
    per_day = 365 * (returns[dates[-2]][indicator + " value"] - 1) / (returns[meta][indicator + " days_held"] - 1)
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
    fundsdata = {}
    for symbol in symbols:
        fundsdata[symbol] = get_fundata(symbol)

    for indicator in indicators:
        start = daterange[0]
        end = daterange[1]
        n, amr, day, asr = 0, 0, 0, 0
        returns[indicator] = {}

        for symbol in symbols:
# indicator_v_price should merge indicator returns values with fundata, 
# and create/build  indicator-meta key

            if start and end:
                fundata = (indicator_v_price(symbol, indicator, fundsdata[symbol], start, end=end))  # (get start and end from config at indkcator v price)
            else:
                fundata = (indicator_v_price(symbol, indicator, fundsdata[symbol]))   # when indicator is MACD, rundata includes RSI
            amr += fundata["meta"]["Average rate of return using " + indicator]
            day += fundata["meta"]["Average per-day-held return using " + indicator]
            asr += fundata["meta"]["Average_simple_return"]  # ,,,,,,,,,,,,,,,,pull this out
            n += 1
            if not(symbol in returns.keys()):
                returns[symbol] = {}
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

def build_processed_data():
    returns = {}
    fundsdata = {}
    for symbol in symbols:
        fundsdata[symbol] = get_fundata(symbol)

    for indicator in indicators:
        # n, amr, day, asr = 0, 0, 0, 0
# build suer meta

        for symbol in symbols:
            fundsdata[symbol] = merge_fund_indicator_returns(symbol, indicator, fundsdata[symbol])

    for key in fundsdata['QQQ']['meta']['MACD'].keys():
        print (key, fundsdata['QQQ']['meta']['MACD'][key])
        
    import pdb; pdb.set_trace()

# (Pdb) fundsdata['QQQ']['meta']['RSI'].keys()
# dict_keys(['RSI number_of_days', 'RSI average_return_rate', 'days_held', 'days_right_rate'])
# (Pdb) fundsdata['QQQ']['meta']['MACD'].keys()
# dict_keys(['MACD number_of_days', 'MACD average_return_rate', 'days_held', 'days_right_rate'])
# (Pdb)
# (['MACD number_of_days', 'MACD average_return_rate', 'days_held', 'days_right_rate'])