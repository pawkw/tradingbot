import logging
import tkinter as tk
from connectors.binance_futures import BinanceFuturesClient
import keys  # This is keys.py, that defines APIKEY, APISECRET, etc.

logger = logging.getLogger()

######################
# Set up logging
######################

logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s :: %(message)s")
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

######################
# Main loop
######################

if __name__ == "__main__":

    root = tk.Tk()
    client = BinanceFuturesClient(keys.APIKEY, keys.APISECRET, keys.PASSPHRASE, True)
    data = client.get_balances()
    data = client.get_historical_data('BTC-USD', '1h')
    for candle in data:
        print("Time: %d Open: %f.2 Low: %f.2 High: %f.2 Close: %f.2 Vol: %f.2" % (candle['time'], candle['open'], candle['low'],
                                                                                  candle['high'], candle['close'], candle['volume']))

    root.mainloop()