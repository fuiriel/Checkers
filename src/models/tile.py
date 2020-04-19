from common.definitions import *
from common.utils import calc_dimensions


# model pojedynczej "płytki" planszy
class Tile:
    id_val = None

    def __init__(self, board, row, column, width, height, border):
        self.board = board
        self.row = row
        self.column = column
        self.color = white if (row + column) % 2 == 0 else light_blue
        self.dimensions = calc_dimensions(row, column, width, height, border)
        self.create_tile()

    def create_tile(self):
        self.id_val = self.board.create_rectangle(self.dimensions, fill=self.color, tags=(self.row, self.column))

    def highlight(self):
        self.board.itemconfig(self.id_val, fill=grey)
        self.board.tag_bind(self.id_val, "<ButtonPress-1>", self.board.on_highlighted_tile_click)

    def unhighlight(self):
        self.board.itemconfig(self.id_val, fill=self.color)
        self.board.tag_unbind(self.id_val, "<ButtonPress-1>")
