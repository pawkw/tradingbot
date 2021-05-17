import tkinter as tk
import logging
from connectors.binance_futures import BinanceFuturesClient

from interface.styling import *
from interface.logging_component import Logging
from interface.watchlist_component import Watchlist
logger = logging.getLogger()

class Root(tk.Tk):
    def __init__(self, client: BinanceFuturesClient):
        super().__init__()
        self.client = client
        self.title("Trading Bot")
        self.configure(bg=BG_COLOUR)

        self._left_frame = tk.Frame(self, bg=BG_COLOUR)
        self._left_frame.pack(side=tk.LEFT)
        self._right_frame = tk.Frame(self, bg=BG_COLOUR)
        self._right_frame.pack(side=tk.LEFT)  # Yes, on the left.

        # The dict() here is a place holder. For adding another exchange.
        self._watchlist_frame = Watchlist(self.client.get_contracts(), dict(), self._left_frame, bg=BG_COLOUR)
        self._watchlist_frame.pack(side=tk.TOP)

        self._logging_frame = Logging(self._left_frame, bg=BG_COLOUR)
        self._logging_frame.pack(side=tk.TOP)

        self._update_ui()

    def _update_ui(self):
        for log in self.client.logs:
            if not log['displayed']:
                # logger.debug('UI update')
                self._logging_frame.add_log(log['log'])
                log['displayed'] = True
        self.after(1500, self._update_ui)
