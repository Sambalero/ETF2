import json
from api import *
from config import etfs_to_process

''' call api functions and format data '''

def get_prices(symbol):
    print("getting prices for", symbol)
    prices = priceset(symbol).json()
    # import pdb; pdb.set_trace()
    return prices
#  prices = priceset(symbol).json()["Time Series (Daily)"]
def call_api(symbol):
    print("calling api for", symbol)
    prices = priceset(symbol)
    macd = macds(symbol)
    stoch = stoich(symbol)
    rsi = rsis(symbol)
    adx = adxs(symbol)
    cci = ccis(symbol)
    aroon = aroons(symbol)
    bbands = bbandses(symbol)
    ad = ads(symbol)
    obv = obvs(symbol)
    return (prices, macd, stoch, rsi, adx, cci, aroon, bbands, ad, obv)


def build_data_object(symbol, api_data):
    (prices, macd, stoch, rsi, adx, cci, aroon, bbands, ad, obv) = api_data
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
        this_week = week_by_date(symbol, this_week, api_data)

        with open(filename, "w") as writeJSON:
            json.dump(fundata, writeJSON)

    with open("./json/this_week.json", "w") as writeJSON:
        json.dump(this_week, writeJSON)
# python -c 'from client import work_with_files; work_with_files()'
# work_with_files()
