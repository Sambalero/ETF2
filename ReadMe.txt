This project uses an alphavantage api client. If you want to use it, get your key at https://www.alphavantage.co/support/#api-key and put it into a config.py file in the alpha_client folder. config.py should look like 
apikey = "my API key"
symbols = ["symbol"]
daterange = (None, None) # None will return the entire available range
# daterange = ('2018-03-25', '2018-04-05')
strategies = ["RSI", "MACD_Hist", "Buy_and_Hold"]  # Additional keys will evaluate vs. 0
all_the_keys = ['1. open', '2. high', '3. low', '4. close', '5. volume', 'MACD',
                'MACD_Hist', 'MACD_Signal', 'SlowD', 'SlowK', 'RSI', 'ADX', 'CCI',
                'Aroon Down', 'Aroon Up', 'Chaikin A/D', 'Real Lower Band',
                'Real Upper Band', 'Real Middle Band', 'OBV']

I am hoping to assess the validity of a series of investment intuitions I have and determine the best ways to exploit them:

1. Technical price analysis can significantly improve investment returns
2. Trends exist
3. Funds have personalities
4. Historical returns are the best unbiased indicator of future performance

Information about technical strategies can be found using links in the https://www.alphavantage.co docs page

Call API, write to files:
(pyenv) ~/Alpha_client/alpha_client 
$ python -c 'from client import work_with_files; work_with_files()'

Build a performance summary based on various technical strategies and save to file:
(pyenv) ~/Alpha_client/alpha_client 
$ python -c 'from build_summary import build_processed_data; build_processed_data()'

Plot has not been rewritten to work with new methods. It is currently broken.
(pyenv) ~/Alpha_client/alpha_client 
$ python -c 'from plot import work_with_files; work_with_files()'

