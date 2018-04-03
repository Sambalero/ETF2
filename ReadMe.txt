This project uses an alphavantage api client. If you want to use it, get your key at https://www.alphavantage.co/support/#api-key and put it into a config.py file in the alpha_client folder. config.py should look like 
apikey = "my API key"
symbols = ["symbol"]

I am hoping to assess the validity of a series of investment intuitions I have and determine the best ways to exploit them:

1. Technical price analysis can significantly improve investment returns
2. Trends exist
3. Funds have personalities
4. Historical returns are the best unbiased indicator of future performance

Information about technical strategems can be found using links in the https://www.alphavantage.co docs page

Call API, write to files:
(pyenv) ~/Alpha_client/alpha_client 
$ python -c 'from client import work_with_files; work_with_files()'

Build a performance summary of various strategies based on technical strategems and save to file:
(pyenv) ~/Alpha_client/alpha_client 
$ python -c 'from build_summary import build_processed_data; build_processed_data()'


Plot has not been rewritten to work with new methods
(pyenv) ~/Alpha_client/alpha_client 
$ python -c 'from plot import work_with_files; work_with_files()'

