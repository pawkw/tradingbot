import tkinter as tk
import typing

from interface.styling import *
import logging

logger = logging.getLogger()


class StrategyEditor(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._all_contracts = ['BTCUSDT', 'ETHUSDT']

        self._all_timeframes = {'1m', '5m', '15m', '1h', '4h', '1d', '5d'}

        self._commands_frame = tk.Frame(self, bg=BG_COLOUR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self, bg=BG_COLOUR)
        self._table_frame.pack(side=tk.TOP)

        self._add_button = tk.Button(self._commands_frame, text='Add strategy', font=GLOBAL_FONT,
                                     command=self._add_strategy_row, bg=BG_COLOUR2, fg=FG_COLOUR1)
        self._add_button.pack(side=tk.TOP)

        self.body_widgets = dict()

        self._headers = ['Strategy', 'Contract', 'Timeframe', 'Balance %', 'Tp %', 'Sl %']

        self._base_params = [
            {'code_name': 'strategy_type', 'widget': tk.OptionMenu, 'data_type': str,
             'values': {'Technical', 'Breakout'}, 'width': 10},
            {'code_name': 'contract', 'widget': tk.OptionMenu, 'data_type': str,
             'values': self._all_contracts, 'width': 15},
            {'code_name': 'time_frame', 'widget': tk.OptionMenu, 'data_type': str,
             'values': self._all_timeframes, 'width': 15},
            {'code_name': 'balance_pct', 'widget': tk.Entry, 'data_type': str, 'width': 7},
            {'code_name': 'take_profit', 'widget': tk.Entry, 'data_type': str, 'width': 7},
            {'code_name': 'stop_loss', 'widget': tk.Entry, 'data_type': str, 'width': 7},
            {'code_name': 'parameters', 'widget': tk.Button, 'data_type': str, 'text': 'parameters',
             'bg': BG_COLOUR2, 'command': self._show_popup},
            {'code_name': 'activation', 'widget': tk.Button, 'data_type': str, 'text': 'off',
             'bg': 'darkred', 'command': self._switch_strategy},
            {'code_name': 'delete', 'widget': tk.Button, 'data_type': str, 'width': 7, 'text': 'X',
             'bg': 'darkred', 'command': self._delete_row},
        ]
        for position, header in enumerate(self._headers):
            h = tk.Label(self._table_frame, text=header, bg=BG_COLOUR, fg=FG_COLOUR1, font=BOLD_FONT)
            h.grid(row=0, column=position)
            self.body_widgets[header] = dict()

        for header in self._base_params:
            self.body_widgets[header['code_name']] = dict()
            if header['widget'] == tk.OptionMenu:
                self.body_widgets[header['code_name']+'_var'] = dict()

        self._body_index = 1

    def _add_strategy_row(self):
        b_index = self._body_index

        for col, base_param in enumerate(self._base_params):
            code_name = base_param['code_name']
            print(code_name)
            if base_param['widget'] == tk.OptionMenu:
                self.body_widgets[code_name+'_var'][b_index] = tk.StringVar()
                # self.body_widgets[code_name + "_var"][b_index].set(base_param['values'][0])
                self.body_widgets[code_name][b_index] = tk.OptionMenu(self._table_frame,
                                                                      self.body_widgets[code_name + '_var'][b_index],
                                                                      *base_param['values']
                                                                      )
                self.body_widgets[code_name][b_index].config(width=base_param['width'])
            elif base_param['widget'] == tk.Entry:
                self.body_widgets[code_name][b_index] = tk.Entry(self._table_frame, justify=tk.CENTER)
            elif base_param['widget'] == tk.Button:
                self.body_widgets[code_name][b_index] = tk.Button(self._table_frame, text=base_param['text'],
                                                        bg=base_param['bg'], fg=FG_COLOUR1,
                                                        command=lambda frozen_command=base_param['command']:
                                                        frozen_command(b_index))
            else:
                continue
            self.body_widgets[code_name][b_index].grid(row=b_index, column=col)
            print(self.body_widgets[code_name][b_index])
        self._body_index += 1

    def _show_popup(self, row: int):
        # Find x and y coords of button that was clicked.
        x = self.body_widgets['parameters'][row].winfo_rootx()
        y = self.body_widgets['parameters'][row].winfo_rooty()

        # Make window
        self._pop_up_window = tk.Toplevel(self)
        self._pop_up_window.wm_title('Parameters')
        self._pop_up_window.config(bg=BG_COLOUR)
        self._pop_up_window.attributes("-topmost", "true")  # Stay on top.
        self._pop_up_window.grab_set()  # Turn off main window buttons.

        # Move window to coords above.
        self._pop_up_window.geometry(f"+{x - 80}+{y + 30}")

    def _switch_strategy(self, row: int):
        print('Switch')
        pass

    def _delete_row(self, b_index: int):
        # Run through the columns, forgetting cells and removing entries... and I'm all out of entries.
        logger.debug('Delete row: %s', b_index)
        for element in self._base_params:
            print(self.body_widgets[element['code_name']])
            self.body_widgets[element['code_name']][b_index].grid_forget()
            print(element)
            del self.body_widgets[element['code_name']][b_index]
