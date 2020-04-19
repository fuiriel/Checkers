import tkinter as tk
import tkinter.ttk as tkk

from src.common.definitions import *
from src.common.utils import gen_font


class Button(tk.Button):
    def __init__(self, master, text):
        super().__init__(master)
        font = gen_font(14, True)
        self.configure(activebackground=light_orange, activeforeground=BG_COLOR, background=orange,
                       foreground=BG_COLOR, borderwidth='4', disabledforeground=light_orange, font=font,
                       pady='0', relief="raised", text=text)


class Label(tk.Label):
    def __init__(self, master, text, font_size=15):
        super().__init__(master)
        font = gen_font(font_size, True)
        self.configure(background=BG_COLOR, font=font, foreground=orange, text=text)


class NumberBox(tk.Spinbox):
    def __init__(self, master, variable):
        super().__init__(master, state='readonly', justify='center')
        self['textvariable'] = variable
        font = gen_font(12)
        self.configure(background=white, font=font, foreground=black, relief='flat', from_=0, to=15)


class Select(tkk.Combobox):
    def __init__(self, master, variable, *values):
        super().__init__(master, state='readonly', justify='center')
        self['textvariable'] = variable
        self['values'] = values
        font = gen_font(12)
        self.configure(background=white, font=font, foreground=black)

        self.current(0)
