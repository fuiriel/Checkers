from src.common.definitions import *
from src.views.board import BoardView
from src.views.start import StartView
import tkinter as tk


class CheckersApp(tk.Canvas):
    WINDOW_HEIGHT = 600
    WINDOW_WIDTH = 600
    TITLE = 'Checkers game'
    BG_COLOR = dark_blue
    ICON_PATH = '../assets/checkers.ico'

    def __init__(self, master):
        super().__init__(master, bg=self.BG_COLOR)
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.columnconfigure(0, weight=1, minsize=600)
        self.rowconfigure(0, weight=1, minsize=600)
        master.title(self.TITLE)
        master.resizable(0, 0)
        master.minsize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        master.iconbitmap(self.ICON_PATH)

        self.start_player = tk.StringVar()
        self.max_depth = tk.IntVar(value=MAX_DEPTH)

        self.views = {
            ViewType.START: StartView(app_ref=self),
            ViewType.GAME: BoardView(app_ref=self)
        }
        self.current_view = self.views[ViewType.START]
        self.current_view.display_view()

    def change_view(self, view_type):
        self.current_view.destroy()
        self.current_view = self.views[view_type]
        self.current_view.display_view()
