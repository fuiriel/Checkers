import tkinter as tk
from src.common.definitions import *


class View(tk.Frame):
    def __init__(self, app_ref):
        super().__init__(app_ref, bg=dark_blue, relief='flat')
        self.app_ref = app_ref

    def display_view(self):
        pass

    def create_widgets(self):
        pass

    def destroy(self):
        self.grid_forget()
