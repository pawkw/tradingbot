import tkinter as tk
import typing

from interface.styling import *

class TradesWatch(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.body_widgets = dict()

        self._table_frame = tk.Frame(self, bg=BG_COLOUR)
        self._table_frame.pack(side=tk.TOP)

        self._headers = ['time', 'symbol', 'exchange', 'strategy', 'side', 'quantity', 'status', 'pnl']

        for position, header in enumerate(self._headers):
            h = tk.Label(self._table_frame, text=header.capitalize(), bg=BG_COLOUR,
                         fg=FG_COLOUR1, font=BOLD_FONT)
            h.grid(row=0, column=position)
            if header in ['status', 'pnl']:
                self.body_widgets[header+'_var'] = dict()
            self.body_widgets[header] = dict()

        self._body_index = 1

    def add_trade(self, data: typing.Dict):
        row = self._body_index
        time_index = data['time']
        for position, header in data:
            self.body_widgets[header][time_index] = tk.Label(self._table_frame, text=data[header], bg=BG_COLOUR,
                                                             fg=FG_COLOUR2, font=GLOBAL_FONT)
            self.body_widgets[header][time_index].grid(row=row, column=position)
            if header in ['status', 'pnl']:
                self.body_widgets[header + '_var'][time_index] = tk.StringVar()
            print(data)

        self._body_index += 1
