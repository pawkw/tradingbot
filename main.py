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
    APIKEY = keys.SANDBOX_APIKEY if keys.SANDBOX_ON else keys.ACTUAL_APIKEY
    APISECRET = keys.SANDBOX_APISECRET if keys.SANDBOX_ON else keys.ACTUAL_APISECRET

    logger.debug('Program start')
    client = BinanceFuturesClient(APIKEY, APISECRET, keys.SANDBOX_ON)
    logger.debug('Client started')
    root = tk.Tk()
    logger.debug('TK root set')
    root.mainloop()
    logger.debug('End program')
