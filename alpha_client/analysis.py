

def calc_rate_of_return(start, end, days):
    return(end / start) ** (1 / days)


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
    if "note" in dates:
        dates.remove("note")
    return dates


def ownership_condition(indicator, value):
    if indicator == "MACD_Hist":
        if value > 0:
            condition = "buy"
        if value == 0:
            condition = "stay"
        if value < 0:
            condition = "sell"
    if indicator == "RSI":
        if value > 50:
            condition = "buy"
        if value == 50:
            condition = "stay"
        if value < 50:
            condition = "sell"
    return condition


def include_ownership(fundata, indicator, dates):
    if "meta" in fundata.keys():
        for i, date in enumerate(dates):
            if i == 0:
                fundata[date]["held_per_" + indicator] = False
            else:
                if (ownership_condition(indicator, float(fundata[dates[i - 1]][indicator])) ==
                        "buy"):
                    fundata[date]["held_per_" + indicator] = True
                if (ownership_condition(indicator, float(fundata[dates[i - 1]][indicator])) ==
                        "stay"):
                    fundata[date]["held_per_" + indicator] = (
                        fundata[dates[i - 1]]["held_per_" + indicator])
                if (ownership_condition(indicator, float(fundata[dates[i - 1]][indicator])) ==
                        "sell"):
                    fundata[date]["held_per_" + indicator] = False
    return fundata


def next_days_right(fundata, indicator, dates):
    next_days_right = 0
# for Buy-and-Hold, whenever the price goes up it's right day
    if indicator == "Buy_and_Hold":
        for i, date in enumerate(dates):
            if i > 0:
                if fundata[date]["4. close"] > fundata[dates[i - 1]]["4. close"]:
                    next_days_right += 1
# any day after day 1 that we don't lose is a right next day
    else:
        for i, date in enumerate(dates):
            if i > 0:
                if fundata[date]["held_per_" + indicator]:
                    if fundata[date][indicator + "_return_today"] >= 0:
                        next_days_right += 1
                elif fundata[dates[i - 1]]["4. close"] >= fundata[date]["4. close"]:
                    next_days_right += 1
    return next_days_right


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


def calc_daily_bnh_returns(fundata, indicator, dates):
    for i, date in enumerate(dates):
        if i == 0:
            fundata[date][indicator + "_value"] = 1
            fundata[date][indicator + "_return_today"] = 0
        else:
            fundata = add_today_s_change(fundata, indicator, date, dates[i - 1])
    return fundata


def append_indicator_summary(fundata, indicator, dates):
    if "meta" in fundata.keys():
        fundata["meta"][indicator]["days_right"] = next_days_right(fundata, indicator, dates)

        try:
            fundata["meta"][indicator][indicator + "_value"] = (
                round(fundata[dates[-1]][indicator + "_value"], 3))
        except:
            import pdb; pdb.set_trace()

        if indicator == "Buy_and_Hold":
            fundata["meta"][indicator]["days_held"] = len(dates) - 1
        else:
            fundata["meta"][indicator]["days_held"] = days_held(fundata, indicator, dates)

        if fundata["meta"]["market_days"] != 0:
            fundata["meta"][indicator]["days_right_rate"] = (
                round(fundata["meta"][indicator]["days_right"] /
                      (fundata["meta"]["market_days"] - 1), 3))
        else:
            fundata["meta"][indicator]["days_right_rate"] = 0

        fundata["meta"][indicator]["averaged_annualized_CAGR"] = round(36500 * (
            calc_rate_of_return(1, fundata[dates[-1]][indicator + "_value"],
                                len(dates) - 1) - 1), 4)

    return fundata


# Assumes that we trade at the opening value after deciding ovrnight to buy or sell
def calc_returns(fundata, indicator):
    # struct [date][indicator],[net_return],[value];
    # r["average_return"],["days_held"],["days_right_rate"],["number_of_days"]
    dates = dates_from_keys(fundata.keys())

    if indicator == "Buy_and_Hold":
        fundata = calc_daily_bnh_returns(fundata, indicator, dates)
    else:
        fundata = include_ownership(fundata, indicator, dates)
        fundata = calc_daily_return(fundata, indicator, dates)


    if ("meta" in fundata.keys()):

        if not(indicator in fundata["meta"].keys()):
            fundata["meta"][indicator] = {}
        fundata = append_indicator_summary(fundata, indicator, dates)

    return(fundata)
