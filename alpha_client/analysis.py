from dateutil import parser


def add_today_s_change(fundata, indicator, date, yesterday):
    today_s_change = (
        (float(fundata[date]["4. close"]) -
         float(fundata[yesterday]["4. close"])) /
        float(fundata[yesterday]["4. close"]))
    fundata[date][indicator + "_return_today"] = today_s_change
    fundata[date][indicator + "_value"] = (
        (today_s_change + 1) * fundata[yesterday][indicator + "_value"])
    return fundata


def add_first_day_s_change(fundata, indicator, date, yesterday):  # helpers
    first_change = (
        (float(fundata[date]["4. close"]) -
         float(fundata[date]["1. open"])) /
        float(fundata[yesterday]["4. close"]))
    fundata[date][indicator + "_return_today"] = first_change
    fundata[date][indicator + "_value"] = (
        (first_change + 1) * fundata[yesterday][indicator + "_value"])
    return fundata


def add_overnight_change(fundata, indicator, date, yesterday):  # helpers
    overnight_change = (
        (float(fundata[date]["1. open"]) -
         float(fundata[yesterday]["4. close"])) /
        float(fundata[yesterday]["4. close"]))
    fundata[date][indicator + "_return_today"] = overnight_change
    fundata[date][indicator + "_value"] = (
        (overnight_change + 1) * fundata[yesterday][indicator + "_value"])
    return fundata


def dates_from_keys(dates):
    dates = list(sorted(dates))
    if "meta" in dates:
        dates.remove("meta")
    return dates


def include_ownership(fundata, indicator, dates):
    for i, date in enumerate(dates):
        if i == 0:
            fundata[date]["held_per_" + indicator] = False
        else:
            if float(fundata[dates[i - 1]][indicator]) > 0:
                fundata[date]["held_per_" + indicator] = True
            if float(fundata[dates[i - 1]][indicator]) == 0:
                fundata[date]["held_per_" + indicator] = (
                    fundata[dates[i - 1]]["held_per_" + indicator])
            if float(fundata[dates[i - 1]][indicator]) < 0:
                fundata[date]["held_per_" + indicator] = False
    return fundata


def add_market_day_count(fundata, dates):
    for i, date in enumerate(dates):
        fundata[date]["market_days"] = i
    return fundata


def next_days_right(fundata, indicator, dates):
    next_days_right = 0
    for i, date in enumerate(dates):
        if fundata[date]["held_per_" + indicator]:
            if ((i + 1) < len(dates) and
                    fundata[dates[i + 1]][indicator + "_return_today"] >= 0):
                next_days_right += 1
    return next_days_right


def days_held(fundata, indicator, dates):
    days_held = 0
    for date in dates:
        if fundata[date]["held_per_" + indicator]:
            days_held += 1
    return days_held


def calc_daily_return(fundata, indicator, dates):
    for i, date in enumerate(dates):
        if i == 0:
            fundata[date][indicator + "_value"] = 1
            fundata[date][indicator + "_return_today"] = 0
        else:
            if fundata[date]["held_per_" + indicator]:  # I own it
                if fundata[dates[i - 1]]["held_per_" + indicator]:  # I owned it yesterday
                    fundata = add_today_s_change(fundata, indicator, date, dates[i - 1])
                else:  # I bought it this morning
                    fundata = add_first_day_s_change(
                        fundata, indicator, date, dates[i - 1])
            else:  # I don't own it
                if fundata[dates[i - 1]]["held_per_" + indicator]:  # I sold it this a.m.
                    fundata = add_overnight_change(fundata, indicator, date, dates[i - 1])
                else:  # I still don't own it
                    fundata[date][indicator + "_value"] = (
                        fundata[dates[i - 1]][indicator + "_value"])
                    fundata[date][indicator + "_return_today"] = 0
    return fundata


def append_indicator_summary(fundata, indicator, dates):

    fundata["meta"][indicator]["days_held"] = days_held(fundata, indicator, dates)
    fundata["meta"][indicator]["days_right"] = next_days_right(fundata, indicator, dates)
    fundata["meta"][indicator]["market days"] = fundata[dates[-1]]["market_days"]

    fundata["meta"][indicator]["days_right_rate"] = (
        round(fundata["meta"][indicator]["days_right"] /
              fundata[dates[-1]]["market_days"], 3))

    fundata["meta"][indicator][indicator + "_value"] = (
        round(fundata[dates[-1]][indicator + "_value"], 3))

    fundata["meta"][indicator]["average per day return"] = round((
        fundata["meta"][indicator][indicator + "_value"] - 1) /
        fundata["meta"][indicator]["days_held"], 5)

    if fundata["meta"]["number_of_days"] > 0:
        fundata["meta"][indicator]["average_return_rate"] = round(365 * (
            fundata[dates[-1]][indicator + "_value"] - 1) /
            fundata["meta"]["number_of_days"], 5)
    else:
        fundata["meta"][indicator]["average_return_rate"] = 0

    return fundata


# Assumes that we trade at the opening value after deciding ovrnight to buy or sell
def calc_returns(fundata, indicator):
    # struct [date][indicator],[net_return],[value];
    # r["average_return_rate"],["days_held"],["days_right_rate"],["number_of_days"]

    dates = dates_from_keys(fundata.keys())
    fundata = include_ownership(fundata, indicator, dates)
    fundata = calc_daily_return(fundata, indicator, dates)
# is this the same as len(dates) and is it needed as an intermediate value?
    fundata = add_market_day_count(fundata, dates)

    if not("meta" in fundata.keys()):
        fundata["meta"] = {}

    if not(indicator in fundata["meta"].keys()):
        fundata["meta"][indicator] = {}

    fundata = append_indicator_summary(fundata, indicator, dates)

    return(fundata)


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
