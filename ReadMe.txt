This project uses an alphavantage api client. If you want to use it, get your key at https://www.alphavantage.co/support/#api-key and put it into a config.py file in the alpha_client folder. config.py should look like 
apikey = "my API key"
symbols = ["symbol"]

I am hoping to assess the validity of a series of investment intuitions I have and determine the best ways to exploit them:

1. Technical price analysis can significantly improve investment returns
2. Trends exist
3. Funds have personalities
4. Historical returns are the best unbiased indicator of future performance

Information about technical indicators can be found using links in the https://www.alphavantage.co docs page

Call API, write to files:
(pyenv) ~/Alpha_client/alpha_client 
$ python -c 'from client import work_with_files; work_with_files()'

/Analyze API data & calculate returns, save to a cumulative file:
/(pyenv) ~/Alpha_client/alpha_client 
/$ python -c 'from analysis import work_with_files; work_with_files()'  
/			File "C:\Users\Owner\Documents\prog\PY\Alpha_client\alpha_client\analysis.py", line 381, in build_returns
/			    mhdaily, mhaverage, rsi_days_held = calc_return_based_on_daily_macd_hist(data)
/			ValueError: too many values to unpack (expected 3)

Compare macd hist based investment vs buy-and-hold strategy, 
call api, no first buy/sell delay, print to stdout
(pyenv) ~/Alpha_client/alpha_client 
$ python -c 'from price_and_macd import main; main()'
			  File "C:\Users\Owner\Documents\prog\PY\Alpha_client\alpha_client\price_and_macd.py", line 31, in price_and_macd_data
			    calc_return_based_on_daily_macd_hist(prices))
			ValueError: too many values to unpack (expected 3)

Compare macd hist based investment vs buy-and-hold strategy, 
trade at the opening value after deciding overnight to buy or sell
read from and save to files:
(pyenv) ~/Alpha_client/alpha_client 
$ python -c 'from price_and_macd import work_with_files; work_with_files()'

Plot  macd hist, macd hist based investment value and price from returns file; save plot
(pyenv) ~/Alpha_client/alpha_client 
$ python -c 'from plot import work_with_files; work_with_files()'

Compare RSI hist based investment vs buy-and-hold strategy, 
trade at the opening value after deciding overnight to buy or sell
read from and save to files:
(pyenv) ~/Alpha_client/alpha_client 
$ python -c 'from rsi_and_price import work_with_files; work_with_files()'
			  File "<string>", line 1, in <module>
			  File "C:\Users\Owner\Documents\prog\PY\Alpha_client\alpha_client\rsi_and_price.py", line 6, in <module>
			    from analysis import calc_return_based_on_daily_macd_hist, simple_return, calc_rsi_returns, calc_returns
			ImportError: cannot import name 'calc_rsi_returns'
Fetch,build and plot mdh, md value and price data for each fund in config
(pyenv) ~/Alpha_client/alpha_client 
$ python main.py