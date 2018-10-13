import json
from api import *
from config import etfs_to_process

''' call api functions and format data '''

def get_prices(symbol, outputsize='full'):
    print("getting prices for", symbol)
    prices = Api.priceset(symbol, outputsize)
    # import pdb; pdb.set_trace()
    return prices

def call_api(symbol, outputsize='full'):
    print("calling api for prices", symbol)
    prices = Api.priceset(symbol, outputsize)
    print("calling api for macds", symbol)
    macd = Api.macds(symbol, outputsize)
    print("calling api for stoich", symbol)
    stoch = Api.stoich(symbol, outputsize)
    print("calling api for rsis", symbol)
    rsi = Api.rsis(symbol, outputsize)
    print("calling api for adxs", symbol)
    adx = Api.adxs(symbol, outputsize)
    print("calling api for ccis", symbol)
    cci = Api.ccis(symbol, outputsize)
    print("calling api for aroons", symbol)
    aroon = Api.aroons(symbol, outputsize)
    print("calling api for bbandses", symbol)
    bbands = Api.bbandses(symbol, outputsize)
    print("calling api for ads", symbol)
    ad = Api.ads(symbol, outputsize)
    print("calling api for obvs", symbol)
    obv = Api.obvs(symbol, outputsize)
    print("calling api for smas", symbol)
    sma = Api.smas(symbol, outputsize)
    print("calling api for emas", symbol)
    ema = Api.emas(symbol, outputsize)
    return (prices, macd, stoch, rsi, adx, cci, aroon, bbands, ad, obv, sma, ema)


def build_data_object(symbol, api_data):
    (prices, macd, stoch, rsi, adx, cci, aroon, bbands, ad, obv, sma, ema) = api_data
    fundata = prices
    if fundata:
        dates = list(sorted(fundata.keys())) 
        for date in dates:
            if (not (macd is None)) and date in macd.keys():
                fundata[date]["MACD"] = macd[date]["MACD"]
                fundata[date]["MACD_Hist"] = macd[date]["MACD_Hist"]
                fundata[date]["MACD_Signal"] = macd[date]["MACD_Signal"]
            if not (stoch is None) and date in stoch.keys():
                fundata[date]["SlowD"] = stoch[date]["SlowD"]
                fundata[date]["SlowK"] = stoch[date]["SlowK"]
            if not (rsi is None) and date in rsi.keys():
                fundata[date]["RSI"] = rsi[date]["RSI"]
            if not (adx is None) and date in adx.keys():
                fundata[date]["ADX"] = adx[date]["ADX"]
            if not (cci is None) and date in cci.keys():
                fundata[date]["CCI"] = cci[date]["CCI"]
            if not (aroon is None) and date in aroon.keys():
                fundata[date]["Aroon Down"] = aroon[date]["Aroon Down"]
                fundata[date]["Aroon Up"] = aroon[date]["Aroon Up"]
            if not (ad is None) and date in ad.keys():
                fundata[date]["Chaikin A/D"] = ad[date]["Chaikin A/D"]
            if not (bbands is None) and date in bbands.keys():
                fundata[date]["Real Lower Band"] = bbands[date]["Real Lower Band"]
                fundata[date]["Real Upper Band"] = bbands[date]["Real Upper Band"]
                fundata[date]["Real Middle Band"] = bbands[date]["Real Middle Band"]
            if not (obv is None) and date in obv.keys():
                fundata[date]["OBV"] = obv[date]["OBV"]
            if not (sma is None) and date in sma.keys():
                fundata[date]["SMA"] = sma[date]["SMA"]
            if not (ema is None) and date in ema.keys():
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

' no longer neeeded'
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
