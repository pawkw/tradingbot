import tkinter as tk
import logging
from connectors.binance_futures import BinanceFuturesClient

from interface.styling import *
from interface.logging_component import Logging
from interface.watchlist_component import Watchlist
from interface.trades_component import TradesWatch
from interface.strategy_componenet import StrategyEditor
logger = logging.getLogger()

class Root(tk.Tk):
    def __init__(self, binance_client: BinanceFuturesClient):
        super().__init__()
        self.binance_client = binance_client
        self.coinbase_client = dict() # Place holder
        self.title("Trading Bot")
        self.configure(bg=BG_COLOUR)

        self._left_frame = tk.Frame(self, bg=BG_COLOUR)
        self._left_frame.pack(side=tk.LEFT)
        self._right_frame = tk.Frame(self, bg=BG_COLOUR)
        self._right_frame.pack(side=tk.LEFT)  # Yes, on the left.

        # The dict() here is a place holder. For adding another exchange.
        self._watchlist_frame = Watchlist(self.binance_client.get_contracts(), dict(), self._left_frame, bg=BG_COLOUR)
        self._watchlist_frame.pack(side=tk.TOP)

        self._logging_frame = Logging(self._left_frame, bg=BG_COLOUR)
        self._logging_frame.pack(side=tk.TOP)

        self._strategy_frame = StrategyEditor(self._right_frame, bg=BG_COLOUR)
        self._strategy_frame.pack(side=tk.TOP)

        self._trades_frame = TradesWatch(self._right_frame, bg=BG_COLOUR)
        self._trades_frame.pack(side=tk.TOP)

        self._update_ui()

    def _update_ui(self):
        # Update logs
        for log in self.binance_client.logs:
            if not log['displayed']:
                # logger.debug('UI update')
                self._logging_frame.add_log(log['log'])
                log['displayed'] = True

        # Update watchlist
        try:
            for key, value in self._watchlist_frame.body_widgets['symbol'].items():
                symbol = self._watchlist_frame.body_widgets['symbol'][key].cget('text')
                exchange = self._watchlist_frame.body_widgets['exchange'][key].cget('text')

                if exchange == 'Binance':
                    if symbol not in self.binance_client.contracts:
                        continue

                    if symbol not in self.binance_client.prices:
                        self.binance_client.get_bid_ask(self.binance_client.contracts[symbol])
                        continue

                    precision = self.binance_client.contracts[symbol].price_decimals

                    prices = self.binance_client.prices[symbol]

                elif exchange == 'CoinBase':
                    if symbol not in self.coinbase_client:
                        continue

                    if symbol not in self.coinbase_client.prices:
                        self.coinbase_client.get_bid_ask(self.coinbase_client.contracts[symbol])
                        continue

                    precision = self.binance_client.contracts[symbol].price_decimals

                    prices = self.binance_client[symbol]

                else:
                    continue

                if prices['bid'] is not None:
                    price_str = "{0:.{prec}f}".format(prices['bid'], prec=precision)
                    self._watchlist_frame.body_widgets['bid_var'][key].set(price_str)
                if prices['ask'] is not None:
                    price_str = "{0:.{prec}f}".format(prices['ask'], prec=precision)
                    self._watchlist_frame.body_widgets['ask_var'][key].set(price_str)
        except RuntimeError as e:
            logger.error('Runtime Error while updating watchlist.')
        self.after(1500, self._update_ui)
