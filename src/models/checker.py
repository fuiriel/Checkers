from src.common.definitions import *


# Model pionka
class Checker:
    king = False
    neNeighbor = []
    nwNeighbor = []
    seNeighbor = []
    swNeighbor = []

    def __init__(self, row, column, color, id_tag):
        self.row = row
        self.column = column
        self.color = color
        self.id = id_tag
        self.assign_neighbors()

    def update_location(self, new_row, new_column):
        self.row = new_row
        self.column = new_column
        self.assign_neighbors()
        if (new_row == 0 and self.color == CheckerColor.BLUE) or (new_row == 7 and self.color == CheckerColor.ORANGE):
            if not self.king:
                self.king = True

    def assign_neighbors(self):
        north_row, south_row, east_col, west_col = (100, 100, 100, 100)

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
