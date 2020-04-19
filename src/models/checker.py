from copy import copy, deepcopy

from common.definitions import *
from common.utils import calc_dimensions


# Model pionka
class Checker:
    CHECKER_BORDER = 4.5
    id_tag = None
    king = False
    king_moves_count = 0

    def __init__(self, board, row, column, width, height):
        self.board = board
        self.row = row
        self.column = column
        self.width = width
        self.height = height
        self.color = CheckerColor.BLUE if row < 3 else CheckerColor.ORANGE
        self.dimensions = calc_dimensions(row, column, width, height, self.CHECKER_BORDER)
        self.create_checker()

    def __deepcopy__(self, memo=None):
        _dontcopy = ('tk', 'board')
        clone = copy(self)
        for name, value in vars(self).items():
            if name not in _dontcopy:
                setattr(clone, name, deepcopy(value))
        return clone

    def is_king(self):
        return self.king

    def set_as_king(self, quiet_move=False):
        if not self.king:
            self.king = True
            if not quiet_move:
                self.board.itemconfig(self.id_tag, width=5)

    def create_checker(self):
        self.id_tag = self.board.create_oval(self.dimensions,
                                             fill=self.color.value,
                                             outline=beige,
                                             width=2,
                                             tags=(self.row, self.column)
                                             )

    def update_location(self, new_row, new_column, quiet_move=False):
        self.row = new_row
        self.column = new_column
        if not quiet_move:
            self.dimensions = calc_dimensions(new_row, new_column, self.width, self.height, self.CHECKER_BORDER)
            self.board.coords(self.id_tag, self.dimensions)
        if self.is_king():
            self.king_moves_count += 1

    def check_if_king_and_set(self, quiet_move=False):
        if ((self.row == 0 and self.color == CheckerColor.ORANGE)
            or (self.row == 7 and self.color == CheckerColor.BLUE))\
                and len(self.board.capture_moves) == 0:
            self.set_as_king(quiet_move)

    def to_string(self):
        return f"[{self.color}, {self.id_tag}, ({self.row}, {self.column})]"
