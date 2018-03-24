import json
from matplotlib import pyplot as plt
from config import symbols, daterange


# Massage fundata into parallel lists for plotting
def plottable(fundata):
    plottable = {}
    dates = list(sorted(fundata.keys()))
    plottable["dates"] = dates
    # [dates[50] will include all the indicators
    keys = list(fundata[dates[50]].keys())
    # print(keys)
    for key in keys:
        plottable[key] = []
        for date in dates:
            plottable[key].append(float(fundata[date][key]))
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
        plot_name = "./plots/" + labels[0] + " " + labels[4] + de[-1] + ".png"
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


# plots mdh, md value and price from returns file
def work_with_files():
    try:
        f = open("./json/processed/" + "returns.json")
        fundata = json.load(f)
        f.close()
    except Exception as e:
        print(e)

    for symbol in symbols:
        data = plottable(fundata[symbol])
        labels = (symbol, "MACD_Hist", "mhvalue", "price", "macd and price", "file")
        days = [str(int(day.replace('-', '')) - 20000000) for day in (data["dates"])]
        op = data["MACD_Hist"]
        ch = data["mhvalue"]
        re = data["price"]
        exes, days = zip(*[day for day in enumerate(days)])
        data_set = tuple(zip(exes, days, op, ch, re))
        plot_3_y_values(data_set, labels)


def work_with_pm_files():
    start = daterange[0]
    end = daterange[1]
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
        fundata = fundsdata[symbol]
        del fundata["meta"]
        data = plottable(fundata)
        title = symbol + ": MACD and price, " + start + " - " + end
        labels = (symbol, "MACD_Hist", "mhvalue", "price", title, "file")
        days = [str(int(day.replace('-', '')) - 20000000) for day in (data["dates"])]
        op = data["MACD_Hist"]
        ch = data["mhvalue"]
        re = data["price"]
        exes, days = zip(*[day for day in enumerate(days)])
        data_set = tuple(zip(exes, days, op, ch, re))
        plot_3_y_values(data_set, labels)

# python -c 'from plot import work_with_files; work_with_files()'
# python -c 'from plot import work_with_pm_files; work_with_pm_files()'
