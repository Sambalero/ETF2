import requests
import time
from config import apikey


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
