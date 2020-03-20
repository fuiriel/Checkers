from src.common.definitions import *
from src.common.utils import calc_dimensions


# Model pionka
class Checker:
    CHECKER_BORDER = 4.5
    id_tag = None
    king = False

    def __init__(self, board, row, column, width, height):
        self.board = board
        self.row = row
        self.column = column
        self.width = width
        self.height = height
        self.color = CheckerColor.BLUE if row < 3 else CheckerColor.ORANGE
        self.dimensions = calc_dimensions(row, column, width, height, self.CHECKER_BORDER)
        self.create_checker()

    def is_king(self):
        return self.king

    def set_as_king(self):
        if not self.king:
            self.king = True
            self.board.itemconfig(self.id_tag, width=5)

    def create_checker(self):
        self.id_tag = self.board.create_oval(self.dimensions, fill=self.color.value, outline=beige, width=2)

    def update_location(self, new_row, new_column):
        self.row = new_row
        self.column = new_column
        self.dimensions = calc_dimensions(new_row, new_column, self.width, self.height, self.CHECKER_BORDER)
        self.board.coords(self.id_tag, self.dimensions)
        if (new_row == 0 and self.color == CheckerColor.BLUE) or (new_row == 7 and self.color == CheckerColor.ORANGE):
            self.set_as_king()
