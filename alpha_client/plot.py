import json
from matplotlib import pyplot as plt
from config import symbols, daterange, strategies, indicators
from build_summary import build_file_names


def plot_sets(fundata, indicator, strategy):
    plottable = {}
    dates = list(sorted(fundata.keys()))
    plottable["dates"] = dates
    plottable["indicator"] = []
    plottable["price"] = []
    plottable["value"] = []
    for date in dates:
        if strategy == "RSI2" or strategy == "RSI70":
            plottable["indicator"].append(float(fundata[date]["RSI"]) / 50 - 1)
        elif strategy == "SlowK":
            plottable["indicator"].append(float(fundata[date]["SlowK"]) / 50)
        else:
            plottable["indicator"].append(float(fundata[date][indicator]))
        plottable["price"].append(float(fundata[date]["Buy_and_Hold_value"]))
        plottable["value"].append(float(fundata[date][strategy + "_value"]))
    return plottable


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


def open_fundsdata():
    (filename, funds_filename) = build_file_names()
    try:
        f = open(funds_filename)
        fundsdata = json.load(f)
        f.close()
    except Exception as e:
        print("if the file is missing, we could generate one here if we have to")
        print(e)
    return fundsdata


def get_fund_and_strategy():
    print("Funds:")
    for i, fund in enumerate(symbols):
        print(" " + repr(i) + ": " + fund)
    symbol = symbols[int(input("Enter the fund number: "))]

    print("Strategies:")
    for i, strategy in enumerate(strategies):
        print(" " + repr(i) + ": " + strategy)
    strategy = strategies[int(input("Enter the Strategy number: "))]

    indicator = indicators[strategy]
    return(symbol, indicator, strategy)


def plot_fundsdata():
    fundsdata = open_fundsdata()
    # import pdb; pdb.set_trace()
    (symbol, indicator, strategy) = get_fund_and_strategy()
    fundata = fundsdata[symbol]
    if "meta" in fundata.keys():
        del fundata["meta"]
    start = daterange[0]
    end = daterange[1]
    title = symbol + " " + strategy + " and Price, " + start + " - " + end
    fundata = plot_sets(fundata, indicator, strategy)
    labels = (symbol, strategy, strategy + " value", "price", title, "file")
    days = [str(int(day.replace('-', '')) - 20000000) for day in (fundata["dates"])]
    op = fundata["indicator"]
    ch = fundata["value"]
    re = fundata["price"]
    exes, days = zip(*[day for day in enumerate(days)])
    data_set = tuple(zip(exes, days, op, ch, re))
    plot_3_y_values(data_set, labels)

# python -c 'from plot import plot_fundsdata; plot_fundsdata()'
