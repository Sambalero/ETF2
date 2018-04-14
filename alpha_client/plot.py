import json
from matplotlib import pyplot as plt
from config import symbols, daterange
from price_and_macd import add_to_pm_funds_data


# Massage fundata into parallel lists for plotting
def plottable(fundata):
    plottable = {}
    dates = list(sorted(fundata.keys()))
    plottable["dates"] = dates
    # [dates[50] will include all the indicators
    keys = list(fundata[dates[50]].keys())
    for key in keys:
        plottable[key] = []
        for date in dates:
            plottable[key].append(float(fundata[date][key]))
    return plottable


def full_pm(fun_data):  # I don't think this is needed anymore. now done previously?
    fundata = {}
    all_the_keys = ['1. open', '2. high', '3. low', '4. close', '5. volume', 'MACD',
                    'MACD_Hist', 'MACD_Signal', 'SlowD', 'SlowK', 'RSI', 'ADX', 'CCI',
                    'Aroon Down', 'Aroon Up', 'Chaikin A/D', 'Real Lower Band',
                    'Real Upper Band', 'Real Middle Band', 'OBV', 'mhreturn',
                    'mhvalue', 'buy and hold value', 'return', 'price']
    for date in fun_data.keys():
        keys = fun_data[date].keys()
        if set(all_the_keys) <= set(keys):
            fundata[date] = fun_data[date]
    return fundata


def plot_3_y_values(data_set, labels):

    fig, ax = plt.subplots()  # create subplots to work with
    (x, d, y, c, r) = zip(*data_set)  # unzip the data set

    ax.plot(x, c, label=labels[2])  # plot c against x
    ax.plot(x, r, label=labels[3])  # plot r against x
    pairs = list(zip(x, y))  # ??????? xip x & y
    while pairs[0][1] == 0:   # ???????
        del pairs[0]  # ???????
    (x, y) = zip(*tuple(pairs))  # ??????? unzip x & y
    ax.plot(x, y, label=labels[1])  # plot y against x
    # oz = [0]*len(x)
    ax.plot(x, [0] * len(x))  # plot y=0 for reference

    h = max(y)  # get the height of the plot - need other series, too, actually

    # these data point text labels are actually completely independent of the points
    # label every ith point
    i = (int(len(data_set) / 5))
    text_set = data_set[0: 1 - i: i]  # label 5 points
    if text_set[-1] != data_set[-1]:  # label last point
        text_set = list(text_set)
        text_set.append(data_set[-1])

    for i in range(len(text_set)):
        (x, d, y, c, r) = text_set[i]
        (dd, dl, tr, dr, dp) = (0, 10, 0, 90, 10)
        i = 0
        for v in [y, c, r]:
            if v < (h / 2):
                dd = 1
            if i == 1:
                dl = 0
            if i == 2:
                dl = 20
            i += 1
            #  don't print 0's
            if v != 0:
                ax.text(x, v, str(round(v, 2)), withdash=True,
                        dashdirection=dd,
                        dashlength=dl,
                        rotation=tr,
                        dashrotation=dr,
                        dashpush=dp,
                        )

    # override the default x axis labels
    (ex, de, wy, ch, re) = zip(*text_set)
    plt.xticks(ex, de)
    plt.subplots_adjust(bottom=0.15, top=0.85)  # default top is 0.9
    for label in ax.get_xticklabels():
        label.set_rotation(270)

    # add header box
    box_text = labels[4]
    fc = 'xkcd:sky blue'
    plt.text(0.5, 1.15, box_text,
             horizontalalignment='center',
             verticalalignment='center',
             style='italic',
             transform=ax.transAxes,
             bbox={'facecolor': fc, 'alpha': .5, 'pad': 3})

    plt.legend()
    plt.title(labels[0])
    if labels[5] == "file":
        plot_name = "./plots/" + labels[4] + ".png"
        print(plot_name)
        plt.savefig(plot_name)
    plt.show()


# There will be a different version of this for each graph
def call_plot_3_y_values(symbols, fundata):
    for symbol in symbols:
        data = plottable(fundata[symbol])
        labels = (symbol, "MACD_Hist", "mhvalue", "price", "macd and price", "show")
        days = [str(int(day.replace('-', '')) - 20000000) for day in (data["dates"])]
        op = data["MACD_Hist"]
        ch = data["mhvalue"]
        re = data["price"]
        exes, days = zip(*[day for day in enumerate(days)])
        data_set = tuple(zip(exes, days, op, ch, re))
        plot_3_y_values(data_set, labels)


# plots mdh, md value and price from pm files
def work_with_files():
    start = daterange[0]
    end = daterange[1]
    fundsdata = {}
    if start and end:
        filename = "./json/processed/pm" + start + " - " + end + ".json"
    else:
        filename = "./json/processed/pm.json"

    try:
        f = open(filename)
        fundsdata = json.load(f)
        f.close()
    except Exception as e:
        print("if the file is missing, we could generate one here if we have to")
        print(e)

    for symbol in symbols:
        if not(symbol in fundsdata.keys()):
            fundata = add_to_pm_funds_data(symbol)
        else:
            fundata = fundsdata[symbol]
        del fundata["meta"]
        if not(start and end):
            fundata = full_pm(fundata)
            title = symbol + " MACD and Price"
        else:
            title = symbol + " MACD and Price, " + start + " - " + end
        fundata = plottable(fundata)
        labels = (symbol, "MACD_Hist", "mhvalue", "price", title, "file")
        print(labels)
        days = [str(int(day.replace('-', '')) - 20000000) for day in (fundata["dates"])]
        op = fundata["MACD_Hist"]
        ch = fundata["mhvalue"]
        re = fundata["price"]
        exes, days = zip(*[day for day in enumerate(days)])
        data_set = tuple(zip(exes, days, op, ch, re))
        plot_3_y_values(data_set, labels)

# python -c 'from plot import work_with_files; work_with_files()'
