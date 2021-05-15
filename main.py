import logging
import tkinter as tk
from connectors.binance_futures import BinanceFuturesClient
import binance_keys  # This is binance_keys.py, that defines APIKEY, APISECRET, etc.
from interface.root_component import Root
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
    APIKEY = binance_keys.SANDBOX_APIKEY if binance_keys.SANDBOX_ON else binance_keys.ACTUAL_APIKEY
    APISECRET = binance_keys.SANDBOX_APISECRET if binance_keys.SANDBOX_ON else binance_keys.ACTUAL_APISECRET

    logger.debug('Program start')
    # client = BinanceFuturesClient(APIKEY, APISECRET, binance_keys.SANDBOX_ON)
    logger.debug('Client started')
    root = Root()
    logger.debug('TK root set')
    root.mainloop()
    logger.debug('End program')
    exit(0)