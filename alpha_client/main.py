import analysis
import client
import plot
from config import symbols

# api_data: (funds tuple){api call object}[date][technical indicator key][value]
# fundata: {funds object}[date][technical indicator][value]
# returns: {returns object}[symbol][date][technical indicator][calculation][value]

for symbol in symbols:
    api_data = client.call_api(symbol)
    fundata = client.build_data_object(symbol, api_data)
    returns = {}
    returns = analysis.build_returns(symbol, fundata, returns)
    plot.call_plot_3_y_values(symbols, returns)
