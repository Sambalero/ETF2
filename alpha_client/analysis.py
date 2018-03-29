import json
from dateutil import parser
from config import symbols


def today_s_first_change(data, date, yesterday_s_close):  # helpers
    return (float(data[date]["4. close"]) -
            float(data[date]["1. open"])) / yesterday_s_close


def overnight_change(data, date, yesterday_s_close):  # helpers
    return (float(data[date]["1. open"]) - yesterday_s_close
            ) / yesterday_s_close


# Assumes that we trade at the opening value after deciding ovrnight to buy or sell
def calc_returns(fundata, indicator):
    # print(fundata)
    returns = {}  # struct [date][indicator],[net_return],[value];
    meta = indicator + "meta"
    returns[meta] = {}  # helper???
    # ["rsi_average_return_rate"],["days_held"],["days_right_rate"],["number_of_days"]
    dates = []
    for date in fundata.keys():
        if indicator in fundata[date].keys():
            dates.append(date)
            returns[date] = {}
            returns[date][indicator] = fundata[date][indicator]
    yesterday_s_close = 1
    yesterday_s_value = 1
    value = 1
    days_held = 0
    next_days_right = 0
    rightable_days = 0   # maarket days?
# skip dates when the mdh value is not available
    for date in fundata.keys():  # helpers fundates
        if indicator in fundata[date].keys():
            dates.append(date)
            returns[date] = {}
            returns[date][indicator] = fundata[date][indicator]

    dates = list(sorted(dates))
    value = indicator + "value"
    net_return = indicator + "return"
    for index, date in enumerate(dates):
        today_s_change = (float(fundata[date]["4. close"]) -
                          yesterday_s_close) / yesterday_s_close
#  nothing to work with for the first entry
        if index == 0:
            returns[date][value] = yesterday_s_value
            returns[date][net_return] = 0
#  if yesterday's hist > 0 get net_return
        elif float(returns[dates[index - 1]][indicator]) >= 0:
            days_held += 1
            rightable_days += 1
            if today_s_change >= 0:
                next_days_right += 1
            if index > 1:
                # buy in at opening value
                if not(float(returns[dates[index - 2]]
                       [indicator]) > 0):
                    returns[date][net_return] = today_s_first_change(
                        fundata, date, yesterday_s_close)
                    returns[date][value] = yesterday_s_value * (
                        1 + today_s_first_change(fundata, date, yesterday_s_close))
                else:  # keep returns close to close
                    returns[date][net_return] = today_s_change
                    returns[date][
                        value] = yesterday_s_value * (1 + today_s_change)
            else:  # index == 1: buy in
                returns[date][net_return] = today_s_first_change(
                    fundata, date, yesterday_s_close)
                returns[date][value] = yesterday_s_value * \
                    (1 + today_s_first_change(fundata, date, yesterday_s_close))
        else:  # yesterday_s_macd_hist < 0 - sell or don't buy
            if index > 1:
                rightable_days += 1
                if today_s_change < 0:
                    next_days_right += 1
                # sell takes the overnight change
                if (float(returns[dates[index - 2]]
                          [indicator]) > 0):
                    returns[date][value] = yesterday_s_value * (
                        1 + overnight_change(fundata, date, yesterday_s_close))
                    returns[date][net_return] = overnight_change(
                        fundata, date, yesterday_s_close)
                else:  # nothing
                    returns[date][value] = yesterday_s_value
                    returns[date][net_return] = 0
            else:  # index == 1: nothing
                returns[date][value] = yesterday_s_value
                returns[date][net_return] = 0

#  save yesterday's close, yesterday's accrued value
        yesterday_s_close = float(fundata[date]["4. close"])
        yesterday_s_value = returns[date][value]
    average_return_rate = indicator + " average_return_rate"
    number_of_days = indicator + " number_of_days"
    returns[meta][number_of_days] = (
        parser.parse(dates[-1]) - parser.parse(dates[0])).days
    if returns[meta][number_of_days] > 0:
        returns[meta][average_return_rate] = 365 * (
            yesterday_s_value - 1) / returns[meta][number_of_days]
    else:
        returns[meta][average_return_rate] = 0
    returns[meta][indicator + " days_held"] = days_held
    returns[meta][indicator + " days_right_rate"] = next_days_right / rightable_days
    return(returns)


# # Assumes that we trade at the opening value after deciding ovrnight to buy or sell
# def calc_return_based_on_daily_macd_hist(data):
#     # print(data)
#     macd_hist_returns = {}  # struct [date]["MACD_Hist"],["mhreturn"],["mhvalue"]
#     dates = []
#     yesterday_s_close = 1
#     yesterday_s_mhvalue = 1
#     rsi_days_held = 0
#     next_days_right = 0
#     rsi_rightable_days = 0
# # skip dates when the mdh value is not available
#     for date in data.keys():
#         if "MACD_Hist" in data[date].keys():
#             dates.append(date)
#             macd_hist_returns[date] = {}
#             macd_hist_returns[date]["MACD_Hist"] = data[date]["MACD_Hist"]

#     dates = list(sorted(dates))
#     for index, date in enumerate(dates):
#         today_s_change = (float(data[date]["4. close"]) -
#                           yesterday_s_close) / yesterday_s_close
# #  nothing to work with for the first entry
#         if index == 0:
#             macd_hist_returns[date]["mhvalue"] = yesterday_s_mhvalue
#             macd_hist_returns[date]["mhreturn"] = 0
# #  if yesterday's hist > 0 get return
#         elif float(macd_hist_returns[dates[index - 1]]["MACD_Hist"]) >= 0:
#             rsi_days_held += 1
#             rsi_rightable_days += 1
#             if today_s_change >= 0:
#                 next_days_right += 1
#             if index > 1:
#                 # buy in at opening value
#                 if not(float(macd_hist_returns[dates[index - 2]]
#                        ["MACD_Hist"]) > 0):
#                     macd_hist_returns[date]["mhreturn"] = today_s_first_change(
#                         data, date, yesterday_s_close)
#                     macd_hist_returns[date]["mhvalue"] = yesterday_s_mhvalue * (
#                         1 + today_s_first_change(data, date, yesterday_s_close))
#                 else:  # keep returns close to close
#                     macd_hist_returns[date]["mhreturn"] = today_s_change
#                     macd_hist_returns[date][
#                         "mhvalue"] = yesterday_s_mhvalue * (1 + today_s_change)
#             else:  # index == 1: buy in
#                 macd_hist_returns[date]["mhreturn"] = today_s_first_change(
#                     data, date, yesterday_s_close)
#                 macd_hist_returns[date]["mhvalue"] = yesterday_s_mhvalue * \
#                     (1 + today_s_first_change(data, date, yesterday_s_close))
#         else:  # yesterday_s_macd_hist < 0 - sell or don't buy
#             if index > 1:
#                 rsi_rightable_days += 1
#                 if today_s_change < 0:
#                     next_days_right += 1
#                 # sell takes the overnight change
#                 if (float(macd_hist_returns[dates[index - 2]]
#                           ["MACD_Hist"]) > 0):
#                     macd_hist_returns[date]["mhvalue"] = yesterday_s_mhvalue * (
#                         1 + overnight_change(data, date, yesterday_s_close))
#                     macd_hist_returns[date]["mhreturn"] = overnight_change(
#                         data, date, yesterday_s_close)
#                 else:  # nothing
#                     macd_hist_returns[date]["mhvalue"] = yesterday_s_mhvalue
#                     macd_hist_returns[date]["mhreturn"] = 0
#             else:  # index == 1: nothing
#                 macd_hist_returns[date]["mhvalue"] = yesterday_s_mhvalue
#                 macd_hist_returns[date]["mhreturn"] = 0

# #  save yesterday's close, yesterday's accrued value
#         yesterday_s_close = float(data[date]["4. close"])
#         yesterday_s_mhvalue = macd_hist_returns[date]["mhvalue"]
#     number_of_days = (parser.parse(dates[-1]) - parser.parse(dates[0])).days

#     if number_of_days > 0:
#         summary = 365 * (yesterday_s_mhvalue - 1) / number_of_days
#     else:
#         summary = 0

#     return(macd_hist_returns, summary, rsi_days_held, number_of_days,
#            next_days_right / rsi_rightable_days)


# def calc_return_based_on_daily_stoch(data):
#     stoch_returns = {}
#     dates = list(sorted(data.keys()))
#     yesterday_s_slow_d = 0
#     yesterday_s_slow_k = 0
#     yesterday_s_close = 1
#     yesterday_s_value = 1
#     for date in dates:
#         stoch_returns[date] = {}
#         stoch_returns[date]["hold"] = (
#             (yesterday_s_slow_d - yesterday_s_slow_k) > 0)

#         today_s_change = (
#             float(data[date]["4. close"]) - yesterday_s_close) / yesterday_s_close

#         if stoch_returns[date]["hold"]:
#             stoch_returns[date]["value"] = yesterday_s_value * \
#                 (1 + today_s_change)
#         else:
#             stoch_returns[date]["value"] = yesterday_s_value

#         yesterday_s_close = float(data[date]["4. close"])

#         if "SlowD" in data[date].keys():
#             yesterday_s_slow_d = float(data[date]["SlowD"])
#         if "SlowK" in data[date].keys():
#             yesterday_s_slow_d = float(data[date]["SlowK"])

#         yesterday_s_value = stoch_returns[date]["value"]

#         number_of_days = (parser.parse(
#             dates[-1]) - parser.parse(dates[0])).days

#     summary = 365 * (yesterday_s_value - 1) / number_of_days

#     return(stoch_returns, summary)


# def calc_return_based_on_daily_stoch_and_macd_hist(
#         data, macd_hist_returns, stoch_returns):
#     snm_returns = {}
#     dates = list(sorted(data.keys()))
#     yesterday_s_close = 1
#     yesterday_s_value = 1
#     for date in dates:
#         snm_returns[date] = {}
#         snm_returns[date]["hold"] = macd_hist_returns[
#             date]["hold"] and stoch_returns[date]["hold"]

#         today_s_change = (
#             float(data[date]["4. close"]) - yesterday_s_close) / yesterday_s_close

#         if snm_returns[date]["hold"]:
#             snm_returns[date]["value"] = yesterday_s_value * \
#                 (1 + today_s_change)
#         else:
#             snm_returns[date]["value"] = yesterday_s_value

#         yesterday_s_close = float(data[date]["4. close"])
#         yesterday_s_value = snm_returns[date]["value"]

#         number_of_days = (parser.parse(
#             dates[-1]) - parser.parse(dates[0])).days

#     summary = 365 * (yesterday_s_value - 1) / number_of_days

#     return(snm_returns, summary)


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
        buy_and_hold[date]["buy and hold value"] = 1 + change
        buy_and_hold[date]["return"] = today_s_change
        yesterday_s_close = float(data[date]["4. close"])

    average_simple_return = 365 * change / number_of_days
    return buy_and_hold, average_simple_return


# def build_returns(symbol, data, returns):
#     print("building", symbol, "returns object")
#     if not(symbol in returns.keys()):  # object setup
#         returns[symbol] = {}
#     if not("summary" in returns.keys()):
#         returns["summary"] = {}

#     mhdaily, mhaverage, rsi_days_held = calc_return_based_on_daily_macd_hist(data)
#     srdaily, sraverage = simple_return(data)

#     dates = list(sorted(data.keys()))
#     for date in dates:
#         if date in mhdaily.keys():
#             if date in returns[symbol].keys():
#                 returns[symbol][date] = {**returns[symbol][date], **mhdaily[date]}
#             else:
#                 returns[symbol][date] = mhdaily[date]  # redundant?
#         if date in srdaily.keys():
#             if date in returns[symbol].keys():
#                 returns[symbol][date] = {**returns[symbol][date], **srdaily[date]}

#     returns["summary"][symbol + " return based on daily macd hist"] = mhaverage
#     return returns


# def work_with_files():
#     try:
#         f = open("./json/processed/returns.json")
#         returns = json.load(f)
#         f.close()
#     except IOError:
#         returns = {}

#     for symbol in symbols:
#         filename = "./json/raw/" + symbol + ".json"
#         f = open(filename)
#         data = json.load(f)
#         f.close()

#         returns = build_returns(symbol, data, returns)

#     with open("./json/processed/returns.json", "w") as writeJSON:
#         json.dump(returns, writeJSON)
# # python -c 'from analysis import work_with_files; work_with_files()'
