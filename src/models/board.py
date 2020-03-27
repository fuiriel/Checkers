from typing import List
from src.models.checker import Checker
from src.models.tile import Tile
from src.views.widgets import *


class Movement(Enum):
    BOTTOM_RIGHT = "bottom_right"
    TOP_RIGHT = "top_right"
    TOP_LEFT = "top_left"
    BOTTOM_LEFT = "bottom_left"


class Board(tk.Canvas):
    WIDTH = 400
    HEIGHT = 400
    ROWS = 8
    COLUMNS = 8
    TILE_BORDER = .75

    tile_width = WIDTH // COLUMNS
    tile_height = HEIGHT // ROWS

    orange_checkers: List[Checker] = []
    blue_checkers: List[Checker] = []
    board: List[Tile] = []
    highlighted_tiles: List[Tile] = []
    current_checker: Checker or None = None

    capture_moves: List[List[int]] = []
    normal_moves: List[List[int]] = []
    capture_checkers: List[Checker] = []
    dont_allow_switch_of_checkers = False

    def __init__(self, master):
        super().__init__(master, width=self.WIDTH + self.TILE_BORDER, height=self.HEIGHT + self.TILE_BORDER,
                         background=light_orange, bd=0, highlightthickness=0, relief='ridge')
        from src.views.board import BoardView
        self.master: BoardView = master
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.create_board()

    def create_board(self):
        self.create_tiles()
        self.create_checkers()
        self.get_tile_object_from_id(1)

    def create_tiles(self):
        for i in range(0, self.ROWS):
            for j in range(0, self.COLUMNS):
                new_tile = Tile(self, j, i, self.tile_width, self.tile_height, self.TILE_BORDER)
                self.board.append(new_tile)

    def create_checkers(self):
        for i in range(0, self.ROWS):
            if i == 3 or i == 4:
                continue
            for j in range(0, self.COLUMNS):
                if (i + j) % 2 == 1:
                    new_checker = Checker(self, i, j, self.tile_width, self.tile_height)
                    if new_checker.color == CheckerColor.BLUE:
                        self.blue_checkers.append(new_checker)
                    elif new_checker.color == CheckerColor.ORANGE:
                        self.orange_checkers.append(new_checker)
                        new_checker.set_as_king()
                    self.tag_bind(new_checker.id_tag, "<ButtonPress-1>", self.on_checker_click)

    def on_checker_click(self, event):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        checker_id = self.find_closest(x, y)[0]
        self.clear_highlighted_tiles()
        # jesli mamy kolejne bicie to blokujemy możliwość ruchu innymi pionkami
        if self.dont_allow_switch_of_checkers and self.get_checker_object_from_id(checker_id) == self.current_checker:
            self.show_available_moves(checker_id)
        else:
            self.show_available_moves(checker_id)

    def on_highlighted_tile_click(self, event):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        tile_id = self.find_closest(x, y)[0]
        tile: Tile = self.get_tile_object_from_id(tile_id)

        # Jesli ten ruch byl bijacy to trzeba usunac pionek
        if len(self.capture_moves) > 0:
            self.find_and_remove_checker_after_capture(tile)
            # jesli mamy kolejne bicia to ustawiamy flage
            self.dont_allow_switch_of_checkers = self.are_capture_moves_possible()

        # update lokacji i wyczyszczenie poswietlonych plytek
        self.current_checker.update_location(tile.row, tile.column)
        self.clear_highlighted_tiles()
        if self.master.is_end_of_game():
            self.master.end_game()

        self.capture_moves = []
        self.normal_moves = []

        # jesli nie mamy kolejnych bic to zmieniamy gracza
        if self.dont_allow_switch_of_checkers is not True:
            self.current_checker = None
            self.master.switch_current_player()
            return

        # # force to use the same checker as before when multiple capture
        # self.show_available_moves(self.current_checker.id_tag)

    def show_available_moves(self, checker_id):
        self.current_checker = self.get_checker_object_from_id(checker_id)
        if self.current_checker is None or self.current_checker.color != self.master.get_current_player().color:
            return

        self.capture_moves = []
        self.normal_moves = []

        if self.current_checker.king:
            self.calculate_king_moves()
        else:
            self.calculate_checker_moves()

        # must take capture moves if possible
        if len(self.capture_moves) > 0:
            list_of_moves = self.capture_moves
        else:
            list_of_moves = self.normal_moves

        for move in list_of_moves:
            self.highlighted_tiles.append(self.get_tile_object_from_row_col(move[0], move[1]))

        for tile in self.highlighted_tiles:
            tile.highlight()

    def clear_highlighted_tiles(self):
        for tile in self.highlighted_tiles:
            tile.unhighlight()
        self.highlighted_tiles.clear()

    def get_tile_object_from_id(self, tile_id):
        searched_tile = list(filter(lambda tile: (tile.id_val == tile_id), self.board))
        return searched_tile[0] if len(searched_tile) else None

    def get_tile_object_from_row_col(self, row, column):
        searched_tile = list(filter(lambda tile: (tile.row == row and tile.column == column), self.board))
        return searched_tile[0] if len(searched_tile) else None

    def get_checker_object_from_id(self, checker_id):
        checkers = [*self.blue_checkers, *self.orange_checkers]
        searched_checker = list(filter(lambda checker: (checker.id_tag == checker_id), checkers))
        return searched_checker[0] if len(searched_checker) else None

    def get_checker_object_from_row_col(self, row, column):
        checkers = [*self.blue_checkers, *self.orange_checkers]
        searched_checker = list(filter(lambda checker: (checker.row == row and checker.column == column), checkers))
        return searched_checker[0] if len(searched_checker) else None

    def remove_checker(self, row, col):
        checker = self.get_checker_object_from_row_col(row, col)
        if checker.color == CheckerColor.ORANGE:
            self.master.get_computer().reset_kings_moves_count()
            self.master.get_user().delete_checker(checker)
        else:
            self.master.get_user().reset_kings_moves_count()
            self.master.get_computer().delete_checker(checker)

        pass

    def calculate_checker_moves(self):

        row = self.current_checker.row
        col = self.current_checker.column

        if self.current_checker.color == CheckerColor.ORANGE:
            normal_dash = [[-1, -1], [-1, 1]]
        else:
            normal_dash = [[1, 1], [1, -1]]

        capture_dash = [[-2, -2], [-2, 2], [2, -2], [2, 2]]

        for dash in normal_dash:
            if self.is_valid_move(row + dash[0], col + dash[1]):
                self.normal_moves.append([row + dash[0], col + dash[1]])
        for dash in capture_dash:
            if self.is_valid_move(row + dash[0], col + dash[1]):
                self.capture_moves.append([row + dash[0], col + dash[1]])

        pass

    def find_and_remove_checker_after_capture(self, tile):
        if tile.row > self.current_checker.row:
            row_dictionary = list(range(self.current_checker.row, tile.row))
            if tile.column < self.current_checker.column:
                column_dictionary = list(range(self.current_checker.column, tile.column, -1))
            else:
                column_dictionary = list(range(self.current_checker.column, tile.column))
        else:
            row_dictionary = list(range(tile.row, self.current_checker.row))
            if tile.column > self.current_checker.column:
                column_dictionary = list(range(tile.column, self.current_checker.column, -1))
            else:
                column_dictionary = list(range(tile.column, self.current_checker.column))

        points = []
        index = 0
        for row in row_dictionary:
            points.append([row, column_dictionary[index]])
            index += 1

        for point in points:
            checker = self.get_checker_object_from_row_col(point[0], point[1])
            if checker is not None and checker.color is not self.master.get_current_player().color:
                self.remove_checker(point[0], point[1])

        pass

    def are_capture_moves_possible(self):
        capture_moves = []
        capture_dash = [[-2, -2], [-2, 2], [2, -2], [2, 2]]
        row = self.current_checker.row
        col = self.current_checker.column

        for dash in capture_dash:
            if self.is_valid_move(row + dash[0], col + dash[1]):
                capture_moves.append([row + dash[0], col + dash[1]])

        return len(capture_moves) != 0

    def is_valid_move(self, row, col):
        if 0 <= row < self.ROWS and 0 <= col < self.COLUMNS:
            checker = self.get_checker_object_from_row_col(row, col)
            # if we are checking for capture move make sure there is checker between
            if abs(row - self.current_checker.row) == 2:
                middle_row = (row + self.current_checker.row) / 2
                middle_col = (col + self.current_checker.column) / 2
                middle_checker = self.get_checker_object_from_row_col(middle_row, middle_col)
                return checker is None and middle_checker is not None and middle_checker.color is not self.current_checker.color
            return checker is None
        else:
            return False

    def calculate_king_moves(self):

        self.find_possible_king_moves(Movement.TOP_LEFT)
        self.find_possible_king_moves(Movement.TOP_RIGHT)
        self.find_possible_king_moves(Movement.BOTTOM_LEFT)
        self.find_possible_king_moves(Movement.BOTTOM_RIGHT)

        pass

    def find_possible_king_moves(self, movement):
        row = self.current_checker.row
        col = self.current_checker.column
        opposite_checkers_on_line = []
        # should_continue = True

        if movement == Movement.BOTTOM_LEFT:
            j = col
            for i in range(row + 1, Board.ROWS):
                j -= 1
                if j >= 0:
                    if self.get_king_move(i, j, opposite_checkers_on_line) is not True:
                        break
                else:
                    break
            pass

        if movement == Movement.TOP_RIGHT:
            j = row
            for i in range(col + 1, Board.COLUMNS):
                j -= 1
                if j >= 0:
                    if self.get_king_move(j, i, opposite_checkers_on_line) is not True:
                        break
                else:
                    break
            pass

        if movement == Movement.BOTTOM_RIGHT:
            j = row
            for i in range(col + 1, Board.COLUMNS):
                j += 1
                if j < Board.ROWS:
                    if self.get_king_move(j, i, opposite_checkers_on_line) is not True:
                        break
                else:
                    break
            pass

        if movement == Movement.TOP_LEFT:
            j = col
            for i in range(row - 1, -1, -1):
                j -= 1
                if j >= 0:
                    if self.get_king_move(i, j, opposite_checkers_on_line) is not True:
                        break
                else:
                    break
            pass

        pass

    def get_king_move(self, row, col, opposite_checkers_on_line):
        if 0 <= row < self.ROWS and 0 <= col < self.COLUMNS:
            if len(opposite_checkers_on_line) == 2:
                return False
            validated_checker = self.get_checker_object_from_row_col(row, col)
            if validated_checker is not None:
                if validated_checker.color is not self.current_checker.color:
                    opposite_checkers_on_line.append(1)
                else:
                    return False
            else:
                if len(opposite_checkers_on_line) > 0:
                    self.capture_moves.append([row, col])
                else:
                    self.normal_moves.append([row, col])
        return True

    def unbind_all_tags(self):
        checkers = [*self.blue_checkers, *self.orange_checkers]
        for c in checkers:
            self.tag_unbind(c.id_tag, "<ButtonPress-1>")
