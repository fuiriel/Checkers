from src.common.definitions import *
from src.common.utils import calc_dimensions


# Model pionka
class Checker:
    king = False
    neNeighbor = []
    nwNeighbor = []
    seNeighbor = []
    swNeighbor = []

    CHECKER_BORDER = 4.5
    id_tag = None

    def __init__(self, board, row, column, width, height):
        self.board = board
        self.row = row
        self.column = column
        self.width = width
        self.height = height
        self.color = CheckerColor.BLUE if row < 3 else CheckerColor.ORANGE
        self.dimensions = calc_dimensions(row, column, width, height, self.CHECKER_BORDER)
        self.create_checker()
        self.assign_neighbors()

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
        self.assign_neighbors()
        if (new_row == 0 and self.color == CheckerColor.BLUE) or (new_row == 7 and self.color == CheckerColor.ORANGE):
            self.set_as_king()

    def assign_neighbors(self):
        north_row, south_row, east_col, west_col = (None, None, None, None)

        if (self.row - 1) >= 0:
            north_row = self.row - 1
        if (self.row + 1) <= 7:
            south_row = self.row + 1
        if (self.column - 1) >= 0:
            west_col = self.column - 1
        if (self.column + 1) <= 7:
            east_col = self.column + 1

        self.neNeighbor = (north_row, east_col)
        self.nwNeighbor = (north_row, west_col)
        self.seNeighbor = (south_row, east_col)
        self.swNeighbor = (south_row, west_col)
