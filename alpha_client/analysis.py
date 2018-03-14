import json
from dateutil import parser
from config import symbols


# Assume that we pay the opening value after deciding ovrnight to buy.
def today_s_first_change(data, date, yesterday_s_close):
    return (float(data[date]["4. close"]) -
            float(data[date]["1. open"])) / yesterday_s_close


def calc_return_based_on_daily_macd_hist(data):
    macd_hist_returns = {}  # struct date:{MACD_Hist: mhreturn, mhvalue}
    dates = list(sorted(data.keys()))
    yesterday_s_close = 1
    yesterday_s_mhvalue = 1

    first_macd_index = 0
    for index, date in enumerate(dates):
        macd_hist_returns[date] = {}
# skip dates when the mdh value is not available
#  ? change to while with counter?
        if not("MACD_Hist" in data[date].keys()):
            # print(data[date].keys())
            first_macd_index = first_macd_index + 1
            macd_hist_returns[date]["MACD_Hist"] = 0
            # change to a woarnning if > x indexing:  1373 34
            # print("indexing: ", index, first_macd_index)
        else:
            macd_hist_returns[date]["MACD_Hist"] = data[date]["MACD_Hist"]

        today_s_change = (float(data[date]["4. close"]) -
                          yesterday_s_close) / yesterday_s_close
#  if yesterday's hist > 0 get return
        if index == 0:
            macd_hist_returns[date]["mhvalue"] = yesterday_s_mhvalue
            macd_hist_returns[date]["mhreturn"] = 0

        elif float(macd_hist_returns[dates[index - 1]]["MACD_Hist"]) > 0:
            if index > 1:
                # first time is different
                if not(float(macd_hist_returns[dates[index - 2]]
                       ["MACD_Hist"]) > 0):
                    macd_hist_returns[date]["mhreturn"] = today_s_first_change(
                        data, date, yesterday_s_close)
                    macd_hist_returns[date]["mhvalue"] = yesterday_s_mhvalue * (
                        1 + today_s_first_change(data, date, yesterday_s_close))
                else:  # not first time
                    macd_hist_returns[date]["mhreturn"] = today_s_change
                    macd_hist_returns[date][
                        "mhvalue"] = yesterday_s_mhvalue * (1 + today_s_change)
            else:  # first time
                macd_hist_returns[date]["mhreturn"] = today_s_first_change(
                    data, date, yesterday_s_close)
                macd_hist_returns[date]["mhvalue"] = yesterday_s_mhvalue * \
                    (1 + today_s_first_change(data, date, yesterday_s_close))
        else:  # yesterday_s_macd_hist < 0 - no change
            macd_hist_returns[date]["mhvalue"] = yesterday_s_mhvalue
            macd_hist_returns[date]["mhreturn"] = 0

#  save yeteredy's close
        yesterday_s_close = float(data[date]["4. close"])


#  save yesterday's accrued value
        yesterday_s_mhvalue = macd_hist_returns[date]["mhvalue"]
        number_of_days = (parser.parse(
            dates[-1]) - parser.parse(dates[first_macd_index])).days

    if number_of_days > 0:
        summary = 365 * (yesterday_s_mhvalue - 1) / number_of_days
    else:
        summary = 0

    return(macd_hist_returns, summary)


def calc_return_based_on_daily_stoch(data):
    stoch_returns = {}
    dates = list(sorted(data.keys()))
    yesterday_s_slow_d = 0
    yesterday_s_slow_k = 0
    yesterday_s_close = 1
    yesterday_s_value = 1
    for date in dates:
        stoch_returns[date] = {}
        stoch_returns[date]["hold"] = (
            (yesterday_s_slow_d - yesterday_s_slow_k) > 0)

        today_s_change = (
            float(data[date]["4. close"]) - yesterday_s_close) / yesterday_s_close

        if stoch_returns[date]["hold"]:
            stoch_returns[date]["value"] = yesterday_s_value * \
                (1 + today_s_change)
        else:
            stoch_returns[date]["value"] = yesterday_s_value

        yesterday_s_close = float(data[date]["4. close"])

        if "SlowD" in data[date].keys():
            yesterday_s_slow_d = float(data[date]["SlowD"])
        if "SlowK" in data[date].keys():
            yesterday_s_slow_d = float(data[date]["SlowK"])

        yesterday_s_value = stoch_returns[date]["value"]

        number_of_days = (parser.parse(
            dates[-1]) - parser.parse(dates[0])).days

    # print("summin the stoich")

    summary = 365 * (yesterday_s_value - 1) / number_of_days

    return(stoch_returns, summary)


def calc_return_based_on_daily_stoch_and_macd_hist(
        data, macd_hist_returns, stoch_returns):
    snm_returns = {}
    dates = list(sorted(data.keys()))
    yesterday_s_close = 1
    yesterday_s_value = 1
    for date in dates:
        snm_returns[date] = {}
        snm_returns[date]["hold"] = macd_hist_returns[
            date]["hold"] and stoch_returns[date]["hold"]

        today_s_change = (
            float(data[date]["4. close"]) - yesterday_s_close) / yesterday_s_close

        if snm_returns[date]["hold"]:
            snm_returns[date]["value"] = yesterday_s_value * \
                (1 + today_s_change)
        else:
            snm_returns[date]["value"] = yesterday_s_value

        yesterday_s_close = float(data[date]["4. close"])
        yesterday_s_value = snm_returns[date]["value"]

        number_of_days = (parser.parse(
            dates[-1]) - parser.parse(dates[0])).days

    summary = 365 * (yesterday_s_value - 1) / number_of_days

    return(snm_returns, summary)


def simple_return(data):
    dates = list(sorted(data.keys()))
    buy_and_hold = {}
    yesterday_s_close = 0.0
    for date in dates:
        buy_and_hold[date] = {}
        buy_and_hold[date]["price"] = float(
            data[date]["4. close"]) / float(data[dates[0]]["4. close"])

        number_of_days = (parser.parse(date) - parser.parse(dates[0])).days
        if number_of_days == 0:
            change = 0
            today_s_change = 0
        else:
            change = (float(data[date]["4. close"]) - float(data[dates[0]]
                      ["4. close"])) / float(data[dates[0]]["4. close"])
            today_s_change = (
                float(data[date]["4. close"]) - yesterday_s_close) / yesterday_s_close

        buy_and_hold[date]["return since" + str(dates[0])] = change
        buy_and_hold[date]["return"] = today_s_change
        yesterday_s_close = float(data[date]["4. close"])

    average_simple_return = 365 * change / number_of_days
    return buy_and_hold, average_simple_return


def build_returns(symbol, data, returns):
    print("building", symbol, "returns object")
    if not(symbol in returns.keys()):  # object setup
        returns[symbol] = {}
    if not("summary" in returns.keys()):
        returns["summary"] = {}

    mhdaily, mhaverage = calc_return_based_on_daily_macd_hist(data)
    srdaily, sraverage = simple_return(data)

    dates = list(sorted(data.keys()))
    for date in dates:
        if date in mhdaily.keys():
            if date in returns[symbol].keys():
                returns[symbol][date] = {**returns[symbol][date], **mhdaily[date]}
            else:
                returns[symbol][date] = mhdaily[date]  # redundant?
        if date in srdaily.keys():
            if date in returns[symbol].keys():
                returns[symbol][date] = {**returns[symbol][date], **srdaily[date]}

    returns["summary"][symbol + " return based on daily macd hist"] = mhaverage
    return returns


def work_with_files():
    try:
        f = open("returns2.json")
        returns = json.load(f)
        f.close()
    except IOError:
        returns = {}

    for symbol in symbols:
        filename = symbol + ".json"
        f = open(filename)
        data = json.load(f)
        f.close()

        returns = build_returns(symbol, data, returns)

    with open("returns2.json", "w") as writeJSON:
        json.dump(returns, writeJSON)
# python -c 'from analysis import work_with_files; work_with_files()'
