from src.views.view import View
from src.views.widgets import *


# Widok planszy
class BoardView(View):
    BOARD_SIZE = [400, 400]
    ROWS = 8
    COLUMNS = 8

    piece_width = BOARD_SIZE[0] // COLUMNS
    piece_height = BOARD_SIZE[1] // ROWS
    redCount = 12
    greyCount = 12

    def __init__(self, app_ref):
        super().__init__(app_ref)
        self.textbox_label = Label(self, 'TU BĘDZIE TAKA PLANSZA, ŻE HOHO', 20)
        self.board = self.create_board()

    def display_view(self):
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        self.textbox_label.grid(column=0, row=0)

    def create_board(self):
        board = [[EMPTY for column in range(self.COLUMNS)] for row in range(self.ROWS)]
        return board
