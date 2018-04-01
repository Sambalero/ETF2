from dateutil import parser


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
    # r["average_return_rate"],["days_held"],["days_right_rate"],["number_of_days"]
    yesterday_s_close = 1
    yesterday_s_value = 1
    days_held = 0
    next_days_right = 0
    rightable_days = 0   # market days?
    dates = list(sorted(fundata.keys()))
    if not("meta" in fundata.keys()):
        returns["meta"] = {}
    else:
        returns["meta"] = fundata["meta"]
        dates.remove("meta")
# calc daily return and accumulated value
    # import pdb; pdb.set_trace()
    for index, date in enumerate(dates):
        returns[date] = {}
        returns[date][indicator] = {}
        # if not("4. close" in fundata[date].keys()):
        #     import pdb; pdb.set_trace()
        today_s_change = (float(fundata[date]["4. close"]) -
                          yesterday_s_close) / yesterday_s_close
#  nothing to work with for the first entry
        if index == 0:
            returns[date][indicator]["value"] = yesterday_s_value
            returns[date][indicator]["net_return"] = 0
#  if yesterday's hist > 0 get net_return
        elif float(fundata[dates[index - 1]][indicator]) >= 0:
            days_held += 1
            rightable_days += 1
            if today_s_change >= 0:
                next_days_right += 1
            if index > 1:
                # buy in at opening value
                if not(float(fundata[dates[index - 2]][indicator]) > 0):
                    returns[date][indicator]["net_return"] = today_s_first_change(
                        fundata, date, yesterday_s_close)
                    returns[date][indicator]["value"] = yesterday_s_value * (
                        1 + today_s_first_change(fundata, date, yesterday_s_close))
                else:  # keep returns close to close
                    returns[date][indicator]["net_return"] = today_s_change
                    returns[date][indicator]["value"] = yesterday_s_value * (
                        1 + today_s_change)
            else:  # index == 1: buy in
                returns[date][indicator]["net_return"] = today_s_first_change(
                    fundata, date, yesterday_s_close)
                returns[date][indicator]["value"] = yesterday_s_value * \
                    (1 + today_s_first_change(fundata, date, yesterday_s_close))
        else:  # yesterday_s_mindicaator < 0 - sell or don't buy
            if index > 1:
                rightable_days += 1
                if today_s_change < 0:
                    next_days_right += 1
                # sell takes the overnight change
                if (float(fundata[dates[index - 2]]
                          [indicator]) > 0):
                    returns[date][indicator]["value"] = yesterday_s_value * (
                        1 + overnight_change(fundata, date, yesterday_s_close))
                    returns[date][indicator]["net_return"] = overnight_change(
                        fundata, date, yesterday_s_close)
                else:  # nothing
                    returns[date][indicator]["value"] = yesterday_s_value
                    returns[date][indicator]["net_return"] = 0
            else:  # index == 1: nothing
                returns[date][indicator]["value"] = yesterday_s_value
                returns[date][indicator]["net_return"] = 0

#  save yesterday's close, yesterday's accrued value
        yesterday_s_close = float(fundata[date]["4. close"])
        yesterday_s_value = returns[date][indicator]["value"]
    returns["meta"][indicator] = {}
    returns["meta"][indicator]["date_range"] = (dates[0], dates[-1], indicator)
    returns["meta"][indicator]["number_of_days"] = (
        parser.parse(dates[-1]) - parser.parse(dates[0])).days

    if returns["meta"][indicator]["number_of_days"] > 0:
        returns["meta"][indicator]["average_return_rate"] = round(365 * (
            yesterday_s_value - 1) / returns["meta"][indicator]["number_of_days"], 5)
    else:
        returns["meta"][indicator]["average_return_rate"] = 0

    returns["meta"][indicator]["days_held"] = days_held
    returns["meta"][indicator]["days_right"] = next_days_right
    returns["meta"][indicator]["days_right_rate"] = (
        round(next_days_right / rightable_days, 3))
    returns["meta"][indicator]["market days"] = rightable_days
    returns["meta"][indicator]["per day return"] = round(365 * (
        yesterday_s_value - 1) / days_held, 5)
    returns["meta"][indicator]["value"] = round(yesterday_s_value, 3)
    return(returns)


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
