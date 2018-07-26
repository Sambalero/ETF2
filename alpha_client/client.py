import json
from api import *
from config import etfs_to_process

''' call api functions and format data '''

def get_prices(symbol):
    print("getting prices for", symbol)
    prices = priceset(symbol).json()
    # import pdb; pdb.set_trace()
    return prices

def call_api(symbol):
    print("calling api for prices", symbol)
    prices = Api.priceset(symbol)
    print("calling api for macds", symbol)
    macd = Api.macds(symbol)
    print("calling api for stoich", symbol)
    stoch = Api.stoich(symbol)
    print("calling api for rsis", symbol)
    rsi = Api.rsis(symbol)
    print("calling api for adxs", symbol)
    adx = Api.adxs(symbol)
    print("calling api for ccis", symbol)
    cci = Api.ccis(symbol)
    print("calling api for aroons", symbol)
    aroon = Api.aroons(symbol)
    print("calling api for bbandses", symbol)
    bbands = Api.bbandses(symbol)
    print("calling api for ads", symbol)
    ad = Api.ads(symbol)
    print("calling api for obvs", symbol)
    obv = Api.obvs(symbol)
    print("calling api for smas", symbol)
    sma = Api.smas(symbol)
    print("calling api for emas", symbol)
    ema = Api.emas(symbol)
    return (prices, macd, stoch, rsi, adx, cci, aroon, bbands, ad, obv, sma, ema)


# one-time method. delete after use
def add_ma(symbol, ma):
    # import pdb; pdb.set_trace()
    pa = ma + "s"
    print("calling api for " + pa, symbol)
    ma = getattr(Api, pa)(symbol)
    return (ma)

def build_data_object(symbol, api_data):
    (prices, macd, stoch, rsi, adx, cci, aroon, bbands, ad, obv, sma, ema) = api_data
    fundata = prices
    dates = list(sorted(fundata.keys())) 
    for date in dates:
        if (not (macd is None)) and date in macd.keys():
            fundata[date]["MACD"] = macd[date]["MACD"]
            fundata[date]["MACD_Hist"] = macd[date]["MACD_Hist"]
            fundata[date]["MACD_Signal"] = macd[date]["MACD_Signal"]
        if not (stoch is None) and date in stoch.keys():
            fundata[date]["SlowD"] = stoch[date]["SlowD"]
            fundata[date]["SlowK"] = stoch[date]["SlowK"]
        if date in rsi.keys():
            fundata[date]["RSI"] = rsi[date]["RSI"]
        if not (adx is None) and date in adx.keys():
            fundata[date]["ADX"] = adx[date]["ADX"]
        if date in cci.keys():
            fundata[date]["CCI"] = cci[date]["CCI"]
        if date in aroon.keys():
            fundata[date]["Aroon Down"] = aroon[date]["Aroon Down"]
            fundata[date]["Aroon Up"] = aroon[date]["Aroon Up"]
        if date in ad.keys():
            fundata[date]["Chaikin A/D"] = ad[date]["Chaikin A/D"]
        if date in bbands.keys():
            fundata[date]["Real Lower Band"] = bbands[date]["Real Lower Band"]
            fundata[date]["Real Upper Band"] = bbands[date]["Real Upper Band"]
            fundata[date]["Real Middle Band"] = bbands[date]["Real Middle Band"]
        if date in obv.keys():
            fundata[date]["OBV"] = obv[date]["OBV"]
        if date in sma.keys():
            fundata[date]["SMA"] = sma[date]["SMA"]
        if date in ema.keys():
            fundata[date]["EMA"] = ema[date]["EMA"]
    return fundata


def week_by_date(symbol, this_week, api_data):
    (prices, macd, stoch, rsi, adx, cci, aroon, bbands, ad, obv) = api_data
    dates = list(sorted(prices.keys()))
    for date in dates[-8: -1]:
        if not(date in this_week.keys()):
            this_week[date] = {}
        if not(symbol in this_week[date].keys()):
            this_week[date][symbol] = {}
        if date in macd.keys():
            this_week[date][symbol]["MACD"] = macd[date]["MACD"]
            this_week[date][symbol]["MACD_Hist"] = macd[date]["MACD_Hist"]
            this_week[date][symbol]["MACD_Signal"] = macd[date]["MACD_Signal"]
        if date in stoch.keys():
            this_week[date][symbol]["SlowD"] = stoch[date]["SlowD"]
            this_week[date][symbol]["SlowK"] = stoch[date]["SlowK"]
        if date in rsi.keys():
            this_week[date][symbol]["RSI"] = rsi[date]["RSI"]
        if not (adx is None) and date in adx.keys():
            this_week[date][symbol]["ADX"] = adx[date]["ADX"]
        if date in cci.keys():
            this_week[date][symbol]["CCI"] = cci[date]["CCI"]
        if date in aroon.keys():
            this_week[date][symbol]["Aroon Down"] = aroon[date]["Aroon Down"]
            this_week[date][symbol]["Aroon Up"] = aroon[date]["Aroon Up"]
        if date in ad.keys():
            this_week[date][symbol]["Chaikin A/D"] = ad[date]["Chaikin A/D"]
        if date in bbands.keys():
            this_week[date][symbol]["Real Lower Band"] = bbands[date]["Real Lower Band"]
            this_week[date][symbol]["Real Upper Band"] = bbands[date]["Real Upper Band"]
            this_week[date][symbol]["Real Middle Band"] = bbands[date]["Real Middle Band"]
        if date in obv.keys():
            this_week[date][symbol]["OBV"] = obv[date]["OBV"]
    return this_week


def work_with_files(etfs_to_process=etfs_to_process):
    print("working with files in client.py")
    this_week = {}
    for symbol in etfs_to_process:
        api_data = call_api(symbol)
        filename = "./json/raw/" + symbol + ".json"
        fundata = build_data_object(symbol, api_data)
        # this_week = week_by_date(symbol, this_week, api_data)

        with open(filename, "w") as writeJSON:
            json.dump(fundata, writeJSON)

    with open("./json/this_week.json", "w") as writeJSON:
        json.dump(this_week, writeJSON)


def update_data_object(fundata, symbol, api_data):
    # (prices, macd, stoch, rsi, adx, cci, aroon, bbands, ad, obv, sma, ema) = api_data
    dates = list(sorted(fundata.keys())) 
    for date in dates:
        if date in api_data.keys():
            # import pdb; pdb.set_trace()
            fundata[date][list(api_data[date].keys())[0]] = list(api_data[date].values())[0]
    return fundata
# python -c 'from client import work_with_files; work_with_files()'
# work_with_files()
