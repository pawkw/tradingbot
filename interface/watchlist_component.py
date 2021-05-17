import tkinter as tk

from interface.styling import *

class Watchlist(tk.Frame):
    def __init__(self, binance_contracts, coinbase_contracts, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.binance_symbols = list(binance_contracts.keys())
        self.coinbase_symbols = list(coinbase_contracts.keys())
        self._commands_frame = tk.Frame(self, bg = BG_COLOUR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self, bg=BG_COLOUR)
        self._table_frame.pack(side=tk.TOP)

        self._binance_label = tk.Label(self._commands_frame, text='Binance', bg=BG_COLOUR, fg=FG_COLOUR1,
                                       font=BOLD_FONT)
        self._binance_label.grid(row=0, column=0)
        self._binance_entry = tk.Entry(self._commands_frame, fg=FG_COLOUR1, justify=tk.CENTER,
                                       insertbackground=FG_COLOUR1, bg=BG_COLOUR2)
        self._binance_entry.grid(row=1, column=0)
        self._binance_entry.bind("<Return>", self._add_binance_symbol)

        self._coinbase_label = tk.Label(self._commands_frame, text='Coinbase(N/A)', bg=BG_COLOUR, fg=FG_COLOUR1,
                                        font=BOLD_FONT)
        self._coinbase_label.grid(row=0, column=1)
        self._coinbase_entry = tk.Entry(self._commands_frame, fg=FG_COLOUR1, justify=tk.CENTER,
                                       insertbackground=FG_COLOUR1, bg=BG_COLOUR2)
        self._coinbase_entry.grid(row=1, column=1)
        self._coinbase_entry.bind('<Return>', self._add_coinbase_symbol)

        self.body_widgets = dict()

        self._headers = ['Symbol', 'Exchange', 'Bid', 'Ask']

        for position, header in enumerate(self._headers):
            h = tk.Label(self._table_frame, text=header.capitalize(), bg=BG_COLOUR, fg=FG_COLOUR1, font=BOLD_FONT)
            h.grid(row=0, column=position)

        for header in self._headers:
            self.body_widgets[header] = dict()
            if header in ['bid', 'ask']:
                self.body_widgets[h+'_var'] = dict()

        self._body_index = 1

    def _add_binance_symbol(self, event):
        symbol = event.widget.get()
        if symbol in self.binance_symbols:
            self._add_symbol(symbol, 'Binance')
            event.widget.delete(0, tk.END)

    def _add_coinbase_symbol(self, event):
        symbol = event.widget.get()
        if symbol in self.binance_symbols:
            self._add_symbol(symbol, 'CoinBase')
            event.widget.delete(0, tk.END)

    def _add_symbol(self, symbol: str, exchange: str):
        b_index = self._body_index

        self.body_widgets['symbol'][b_index] = tk.Label(self._table_frame, text=symbol, bg=BG_COLOUR, fg=FG_COLOUR2,
                                                        font=GLOBAL_FONT)
        self.body_widgets['symbol'][b_index].grid(row=b_index, column=0)

        self.body_widgets['exchange'][b_index] = tk.Label(self._table_frame, text=exchange, bg=BG_COLOUR, fg=FG_COLOUR2,
                                                          font=GLOBAL_FONT)
        self.body_widgets['exchange'][b_index].grid(row=b_index, column=1)

        self.body_widgets['bid_var'][b_index] = tk.StringVar()
        self.body_widgets['bid'][b_index] = tk.Label(self._table_frame, textvariable=self.body_widgets['bid_var'][b_index],
                                                     bg=BG_COLOUR, fg=FG_COLOUR2, font=GLOBAL_FONT)
        self.body_widgets['bid'][b_index].grid(row=b_index, column=2)

        self.body_widgets['ask_var'][b_index] = tk.StringVar()
        self.body_widgets['ask'][b_index] = tk.Label(self._table_frame, textvariable=self.body_widgets['ask_var'][b_index],
                                                     bg=BG_COLOUR, fg=FG_COLOUR2, font=GLOBAL_FONT)
        self.body_widgets['ask'][b_index].grid(row=b_index, column=3)

        self._body_index += 1
        return
