import tkinter as tk
from src.common.definitions import *


class View(tk.Frame):
    def __init__(self, app_ref):
        super().__init__(app_ref, bg=BG_COLOR, relief='flat')
        self.app_ref = app_ref

    def get_max_depth_value(self):
        return self.app_ref.max_depth.get()

    def get_start_player_value(self):
        return self.app_ref.start_player.get()

    def get_start_player_type(self):
        return PLAYERS[self.get_start_player_value()]

    def display_view(self):
        pass

    def create_widgets(self):
        pass

    def destroy(self):
        self.grid_forget()
