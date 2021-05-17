import tkinter as tk
import typing

from interface.styling import *

class StrategyEditor(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._commands_frame = tk.Frame(self, bg = BG_COLOUR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self, bg=BG_COLOUR)
        self._table_frame.pack(side=tk.TOP)

        self._add_button = tk.Button(self._commands_frame, text='Add strategy', font=GLOBAL_FONT,
                                     command=self._add_strategy_row, bg=BG_COLOUR2, fg=FG_COLOUR1)
        self._add_button.pack(side=tk.TOP)

        self.body_widgets = dict()

        self._headers = ['Strategy', 'Contract', 'Timeframe', 'Balance %', 'Tp %', 'Sl %']

        for position, header in enumerate(self._headers):
            h = tk.Label(self._table_frame, text=header, bg=BG_COLOUR, fg=FG_COLOUR1, font=BOLD_FONT)
            h.grid(row=0, column=position)
            self.body_widgets[header] = dict()

        self._body_index = 1

    def _add_strategy_row(self):
        pass

