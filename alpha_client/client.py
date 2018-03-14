import requests
import json
import time
from config import apikey, symbols


def get_with_retry(url, funkey, retries=10, backoff_factor=1):
    counter = 0
    t0 = time.time()
    while (counter < retries):
        counter += 1
        try:
            return requests.get(url).json()[funkey]
        except (KeyError, Exception) as e:
            print('GET', url, 'failed :(', e.__class__.__name__, e)
            delay = backoff_factor * counter
            time.sleep(delay)
            continue
    t1 = time.time()
    print(retries, " failures getting ", url, 'Took', t1 - t0, 'seconds')
    return


def priceset(symbol):
    url = ("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" +
           symbol + "&outputsize=full&apikey=" + apikey)
    return get_with_retry(url, "Time Series (Daily)")


def macds(symbol):
    url = ("https://www.alphavantage.co/query?function=MACD&symbol=" + symbol +
           "&interval=daily&series_type=close &apikey=" + apikey)
    return get_with_retry(url, "Technical Analysis: MACD")


def stoich(symbol):
    url = ("https://www.alphavantage.co/query?function=STOCH&symbol=" + symbol +
           "&interval=daily&apikey=" + apikey)
    return get_with_retry(url, "Technical Analysis: STOCH")


def rsis(symbol):
    url = ("https://www.alphavantage.co/query?function=RSI&symbol=" + symbol +
           "&interval=daily&time_period=14&series_type=close &apikey=" + apikey)
    return get_with_retry(url, "Technical Analysis: RSI")


def adxs(symbol):
    url = ("https://www.alphavantage.co/query?function=ADX&symbol=" + symbol +
           "&interval=daily&time_period=14&apikey=" + apikey)
    return get_with_retry(url, "Technical Analysis: ADX")


def ccis(symbol):
    url = ("https://www.alphavantage.co/query?function=CCI&symbol=" + symbol +
           "&interval=daily&time_period=14&apikey=" + apikey)
    return get_with_retry(url, "Technical Analysis: CCI")


def aroons(symbol):
    url = ("https://www.alphavantage.co/query?function=AROON&symbol=" + symbol +
           "&interval=daily&time_period=14&apikey=" + apikey)
    return get_with_retry(url, "Technical Analysis: AROON")


def bbandses(symbol):
    url = ("https://www.alphavantage.co/query?function=BBANDS&symbol=" + symbol +
           "&interval=daily&time_period=5&series_type=\
           close &nbdevup=3&nbdevdn=3&apikey=" + apikey)
    return get_with_retry(url, "Technical Analysis: BBANDS")


def ads(symbol):
    url = ("https://www.alphavantage.co/query?function=AD&symbol=" + symbol +
           "&interval=daily&apikey=" + apikey)
    return get_with_retry(url, "Technical Analysis: Chaikin A/D")


def obvs(symbol):
    url = ("https://www.alphavantage.co/query?function=OBV&symbol=" + symbol +
           "&interval=daily&apikey=" + apikey)
    return get_with_retry(url, "Technical Analysis: OBV")


def call_api(symbol):
    print("calling api for ", symbol)
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


def work_with_files(symbols=symbols):

    this_week = {}
    for symbol in symbols:
        api_data = call_api(symbol)
        filename = symbol + ".json"
        fundata = build_data_object(symbol, api_data)
        this_week = week_by_date(symbol, this_week, api_data)

        with open(filename, "w") as writeJSON:
            json.dump(fundata, writeJSON)

    with open("this week", "w") as writeJSON:
        json.dump(this_week, writeJSON)
# python -c 'from client import work_with_files; work_with_files()'
