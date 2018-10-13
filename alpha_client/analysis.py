import config  #  import precalc, old
import arrow
import json

''' basic api data crunching '''

def pricefile(symbol):
    return "./json/prices/" + symbol + ".json"

# not exact since we really want buisiness days
def too_old(date, age=0):
    if age == 0:
        age = config.old
    if (arrow.now() - arrow.get(date,'YYYY-MM-DD')).days > int(age):  
        return True


def write_prices(fundata, symbol):
    filename = pricefile(symbol)
    with open(filename, "w") as writeJSON:
        json.dump(fundata, writeJSON)


def read_json(filename):
    try:
        f = open(filename)
        fundata = json.load(f)
        f.close()
    except (IOError, ValueError):
        fundata = {}
    return fundata

# '''updated in probability.py'''
# def do_fundata(symbol): 
#     filename = pricefile(symbol)
#     fundata = read_json(filename)
#     if fundata:
#         if too_old(dates_from_keys(fundata.keys())[-1], 2):
#             fundata = get_prices(symbol)["Time Series (Daily)"]  # get data
#             write_prices(fundata, symbol)
#     else:
#         fundata = get_prices(symbol)["Time Series (Daily)"]  # get data
#         write_prices(fundata, symbol)
#     return fundata


def calc_cagr(start, end, days):
    return(((end / start) ** (1 / days)) - 1)


def add_today_s_change(fundata, indicator, date, yesterday):
    today_s_change = (
        (float(fundata[date]["4. close"]) -
         float(fundata[yesterday]["4. close"])) /
        float(fundata[yesterday]["4. close"]))
    fundata[date][indicator + "_return_today"] = today_s_change
    fundata[date][indicator + "_value"] = (
        (today_s_change + 1) * fundata[yesterday][indicator + "_value"])
    return fundata


def add_first_day_s_change(fundata, indicator, date, yesterday):
    first_change = (
        (float(fundata[date]["4. close"]) -
         float(fundata[date]["1. open"])) /
        float(fundata[yesterday]["4. close"]))
    fundata[date][indicator + "_return_today"] = first_change
    fundata[date][indicator + "_value"] = (
        (first_change + 1) * fundata[yesterday][indicator + "_value"])
    return fundata


def add_overnight_change(fundata, indicator, date, yesterday):
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
    if "note" in dates:
        dates.remove("note")
    return dates


def rsi_peak(fundata, indicator, dates, i):
    reset = False
    peak = 0
    indicator_value = float(fundata[dates[0]][indicator])
    if indicator_value > 70:
        peak = indicator_value
    # import pdb; pdb.set_trace()
    for date in (0, i):
        indicator_value = float(fundata[dates[date]][indicator])
        if peak - indicator_value > 5:
            reset = True
        if indicator_value < 55:
            reset = False
        if not reset:
            if indicator_value > peak:
                peak = indicator_value
    return peak

class Strats:
    def MACD_Hist(fundata, strategy, dates, i):
        value = float(fundata[dates[i - 1]][strategy])
        if value > 0:
            condition = "buy"
        if value == 0:
            condition = "stay"
        if value < 0:
            condition = "sell"
        return condition


    def RSI(fundata, strategy, dates, i):
        value = float(fundata[dates[i - 1]]["RSI"])
        if value > 50:
            condition = "buy"
        if value == 50:
            condition = "stay"
        if value < 50:
            condition = "sell"
        return condition


    def SlowD(fundata, strategy, dates, i):
        dvalue = float(fundata[dates[i - 1]]["SlowD"])
        kvalue = float(fundata[dates[i - 1]]["SlowK"])
        if kvalue > dvalue:
            condition = "buy"
        if kvalue == dvalue:
            condition = "stay"
        if kvalue < dvalue:
            condition = "sell"
        return condition


    def SlowK(fundata, strategy, dates, i):
        kvalue = float(fundata[dates[i - 1]]["SlowK"])
        if kvalue < 20:
            condition = "buy"
        elif kvalue > 80:
            condition = "sell"
        else:
            condition = "stay"
        return condition


    # buy above 50 and rising
    def RSI2(fundata, strategy, dates, i):
        value = float(fundata[dates[i - 1]]["RSI"])
        value2 = float(fundata[dates[i - 2]]["RSI"])
        if value > 50 and value >= value2:
            condition = "buy"
        else:
            condition = "sell"
        return condition

    def RSI3(fundata, strategy, dates, i):
        value = float(fundata[dates[i - 1]]["RSI"])
        value2 = float(fundata[dates[i - 2]]["RSI"])
        if value > 50 and value >= value2:
            condition = "buy"
        elif value < 50:
            condition = "sell"
        else:
            condition =  "stay"
        return condition

    def RSI4(fundata, strategy, dates, i):
        priceyesterday = float(fundata[dates[i - 1]]["4. close"])
        rsiyesterday = float(fundata[dates[i - 1]]["RSI"])
        smayesterday = float(fundata[dates[i - 1]]["SMA"])
        heldyesterday = fundata[dates[i - 1]]["held_per_RSI4"]
        if rsiyesterday >= 50 and priceyesterday >= smayesterday and not(heldyesterday):
            condition = "buy"
        elif rsiyesterday < 50 and priceyesterday < smayesterday and heldyesterday:
            condition = "sell"
        else:
            condition =  "stay"
        return condition

    def RSI70(fundata, strategy, dates, i):
        value = float(fundata[dates[i - 1]]["RSI"])
        value2 = float(fundata[dates[i - 2]]["RSI"])
        peak = rsi_peak(fundata, "RSI", dates, i)
        if value > 70 and peak - value > 5:  # value near peak?
            condition = "buy"
        else:
            condition = "sell"
        return condition


    '''not done '''
    def crossover_with_rank(fundata, strategy, dates, i): 
        # make sure rank value is available and up to date for range
        # find fund in rank range
        if rsi > 50 and rsi > rsi2 and price > sma and price2 < sma and rank < 5:
            condition = "buy"
        elif rsi < 50 and price < sma:
            condition = "sell"
        else:
            condition =  "stay"
        return condition

        #  don't need strategy in Strats args
def include_ownership(fundata, strategy, dates):
    if "meta" in fundata.keys():
        for i, date in enumerate(dates):
            # if date == '2018-01-22':
                # import pdb; pdb.set_trace()
            if i == 0:
                fundata[date]["held_per_" + strategy] = False
            else:
                ownership_condition = getattr(Strats, strategy)(fundata, strategy, dates, i)
                if ownership_condition == "buy":
                    fundata[date]["held_per_" + strategy] = True
                if ownership_condition== "stay":
                    fundata[date]["held_per_" + strategy] = (
                        fundata[dates[i - 1]]["held_per_" + strategy])
                if ownership_condition == "sell":
                    fundata[date]["held_per_" + strategy] = False
    return fundata


def good_days(fundata, indicator, dates):
    next_days_right = 0
    profitable_days = 0
# for Buy-and-Hold, whenever the price goes up it's right day
    if indicator == "Buy_and_Hold":
        for i, date in enumerate(dates):
            if i > 0:
                if fundata[date]["4. close"] > fundata[dates[i - 1]]["4. close"]:
                    next_days_right += 1
        profitable_days = next_days_right
# any day after day 1 that we don't lose is a right next day
    else:
        for i, date in enumerate(dates):
            if i > 0:
                if fundata[date]["held_per_" + indicator]:
                    if fundata[date][indicator + "_return_today"] >= 0:
                        next_days_right += 1
                        profitable_days += 1
                elif fundata[dates[i - 1]]["4. close"] >= fundata[date]["4. close"]:
                    next_days_right += 1
    return (next_days_right, profitable_days)


def days_held(fundata, indicator, dates):
    days_held = 0
    for date in dates:
        if fundata[date]["held_per_" + indicator]:
            days_held += 1
    return days_held


def calc_daily_return(fundata, indicator, dates):
    if "meta" in fundata.keys():
        for i, date in enumerate(dates):
            if i == 0:
                fundata[date][indicator + "_value"] = 1
                fundata[date][indicator + "_return_today"] = 0
            else:
                if fundata[date]["held_per_" + indicator]:  # I own it
                    # I owned it yesterday
                    if fundata[dates[i - 1]]["held_per_" + indicator]:
                        fundata = add_today_s_change(
                            fundata, indicator, date, dates[i - 1])
                    else:  # I bought it this morning
                        fundata = add_first_day_s_change(
                            fundata, indicator, date, dates[i - 1])
                else:  # I don't own it
                    # I sold it this a.m.
                    if fundata[dates[i - 1]]["held_per_" + indicator]:
                        fundata = add_overnight_change(
                            fundata, indicator, date, dates[i - 1])
                    else:  # I still don't own it
                        fundata[date][indicator + "_value"] = (
                            fundata[dates[i - 1]][indicator + "_value"])
                        fundata[date][indicator + "_return_today"] = 0
    return fundata


def simple_daily_return(fundata, strategy, dates):
    if "meta" in fundata.keys():
        for i, date in enumerate(dates):
            if i == 0:
                fundata[date][strategy + "_value"] = 1
                fundata[date][strategy + "_return_today"] = 0
            else:
                if fundata[date]["held_per_" + strategy]:  # I own it
                    fundata = add_today_s_change(
                        fundata, strategy, date, dates[i - 1])
                else:  # I don't own it
                    fundata[date][strategy + "_value"] = (
                        fundata[dates[i - 1]][strategy + "_value"])
                    fundata[date][strategy + "_return_today"] = 0
    return fundata


def calc_daily_bnh_returns(fundata, strategy, dates):
    for i, date in enumerate(dates):
        if i == 0:
            fundata[date][strategy + "_value"] = 1
            fundata[date][strategy + "_return_today"] = 0
        else:
            fundata = add_today_s_change(fundata, strategy, date, dates[i - 1])
    return fundata


def append_indicator_summary(fundata, strategy, dates):
    if "meta" in fundata.keys():
        # If there's data for the period in question
        # report the number of days the strategy worked
        (next_days_right, profitable_days) = good_days(fundata, strategy, dates)
        fundata["meta"][strategy]["days_right"] = next_days_right
        fundata["meta"][strategy]["profitable_days"] = profitable_days

# report the end of period investment value
        fundata["meta"][strategy][strategy + "_value"] = (
            round(fundata[dates[-1]][strategy + "_value"], 3))

# report the number of days invested using the strategy
        if strategy == "Buy_and_Hold":
            fundata["meta"][strategy]["days_held"] = len(dates) - 1
        else:
            fundata["meta"][strategy]["days_held"] = days_held(fundata, strategy, dates)

# report the number of days right as a rate
        if fundata["meta"]["market_days"] != 0:
            fundata["meta"][strategy]["days_right_rate"] = (
                round(fundata["meta"][strategy]["days_right"] /
                      (fundata["meta"]["market_days"] - 1), 3))
        else:
            fundata["meta"][strategy]["days_right_rate"] = 0

# same for number of profitable days
        if fundata["meta"][strategy]["days_held"] != 0:
            fundata["meta"][strategy]["profitable_days_rate"] = (
                round(fundata["meta"][strategy]["profitable_days"] /
                      fundata["meta"][strategy]["days_held"], 3))
        else:
            fundata["meta"][strategy]["profitable_days_rate"] = 0

# report the equivalent compounding investment rate
        fundata["meta"][strategy]["averaged_annualized_CAGR"] = round(36500 * (
            calc_cagr(1, fundata[dates[-1]][strategy + "_value"],
                      fundata["meta"]["number_of_days"] - 1)), 4)

    return fundata


# Assumes that we trade at the opening value after deciding ovrnight to buy or sell
def calc_returns(fundata, strategy):
    # struct [date][indicator],[net_return],[value];
    # r["average_return"],["days_held"],["days_right_rate"],["number_of_days"]
    dates = dates_from_keys(fundata.keys())

    if strategy == "Buy_and_Hold":
        fundata = calc_daily_bnh_returns(fundata, strategy, dates)
    else:
        fundata = include_ownership(fundata, strategy, dates)
        if precalc:
            fundata = simple_daily_return(fundata, strategy, dates)
        else:
            fundata = calc_daily_return(fundata, strategy, dates)

    if ("meta" in fundata.keys()):
        if not(strategy in fundata["meta"].keys()):
            fundata["meta"][strategy] = {}
        fundata = append_indicator_summary(fundata, strategy, dates)

    return(fundata)
