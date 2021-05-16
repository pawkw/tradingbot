import tkinter as tk
import time

from interface.styling import *
from interface.logging_component import Logging

class Root(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Trading Bot")
        self.configure(bg=BG_COLOUR)

        self._left_frame = tk.Frame(self, bg=BG_COLOUR)
        self._left_frame.pack(side=tk.LEFT)
        self._right_frame = tk.Frame(self, bg=BG_COLOUR)
        self._right_frame.pack(side=tk.LEFT)  # Yes, on the left.

        self._logging_frame = Logging(self._left_frame, bg=BG_COLOUR)
        self._logging_frame.pack(side=tk.TOP)

        self._logging_frame.add_log("This is a test message.")
        time.sleep(5)
        self._logging_frame.add_log("Another message.")
