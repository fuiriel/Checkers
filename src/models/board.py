from copy import deepcopy, copy
from threading import Timer
from typing import List

from src.ai_algorithm import calculate_move_for_ai
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
    force_jump = False

    def __init__(self, master):
        super().__init__(master, width=self.WIDTH + self.TILE_BORDER, height=self.HEIGHT + self.TILE_BORDER,
                         background=light_orange, bd=0, highlightthickness=0, relief='ridge')
        from src.views.board import BoardView
        self.master: BoardView = master
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.create_board()

    def __deepcopy__(self, memo=None):
        _dontcopy = ('tk', 'master')
        clone = copy(self)
        for name, value in vars(self).items():
            if name not in _dontcopy:
                setattr(clone, name, deepcopy(value))
        return clone

    def create_board(self):
        self.create_tiles()
        self.create_checkers()

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
                        self.tag_bind(new_checker.id_tag, "<ButtonPress-1>", self.on_checker_click)

    def on_checker_click(self, event):
        if self.force_jump:
            return

        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        checker_id = self.find_closest(x, y)[0]
        checker = self.get_checker_object_from_id(checker_id)

        # sprawdza, czy pionek należy do aktualnego gracza
        if not checker or checker.color is not self.master.get_current_player().color:
            return

        self.clear_highlighted_tiles()
        # wymuszenie poruszania po planszy jedynie bijącymi pionkami - jeśli takowe istnieją
        captured = self.get_all_checkers_with_capture_moves()
        if len(captured) > 0 and not captured.count(checker_id):
            return

        self.show_available_moves(checker)

    def on_highlighted_tile_click(self, event):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        tile_id = self.find_closest(x, y)[0]
        self.perform_move(tile_id)

    def perform_move(self, tile_id, quiet_move=False):
        tile: Tile = self.get_tile_object_from_id(tile_id)
        dont_allow_switch_of_checkers = False

        # Jesli ten ruch byl bijacy to trzeba usunac pionek
        if len(self.capture_moves) > 0:
            self.find_and_remove_checker_after_capture(tile, quiet_move)
            # update lokacji
            self.current_checker.update_location(tile.row, tile.column, quiet_move)
            # jesli mamy kolejne bicia to ustawiamy flage
            dont_allow_switch_of_checkers = self.are_capture_moves_possible()
        else:
            # update lokacji
            self.current_checker.update_location(tile.row, tile.column, quiet_move)

        # wyczyszczenie poswietlonych plytek
        self.clear_highlighted_tiles()
        if not quiet_move and self.master.is_end_of_game():
            self.master.end_game()
            return

        self.capture_moves = []
        self.normal_moves = []

        # jesli nie mamy kolejnych bic to zmieniamy gracza
        if dont_allow_switch_of_checkers is not True or quiet_move:
            self.current_checker = None
            self.force_jump = False
            if not quiet_move:
                self.master.switch_current_player()
            return

        # wymuszenie kolejnego bicia
        self.force_jump = True
        if self.master.current_player_type is PlayerType.USER:
            self.show_available_moves(self.current_checker)
        else:
            Timer(0.5, self.run_ai).start()

    def show_available_moves(self, checker):
        list_of_moves = self.calculate_avaible_moves(checker)

        for move in list_of_moves:
            tile = self.get_tile_object_from_row_col(move[0], move[1])
            self.highlighted_tiles.append(tile)
            tile.highlight()

    def calculate_avaible_moves(self, checker):
        self.current_checker = checker
        if self.current_checker is None:
            return []

        self.capture_moves = []
        self.normal_moves = []

        if self.current_checker.king:
            self.calculate_king_moves()
        else:
            self.calculate_checker_moves()

        # must take capture moves if possible
        return self.capture_moves if len(self.capture_moves) > 0 else self.normal_moves

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

    def get_checker_object_from_id(self, checker_id) -> Checker:
        checkers = [*self.blue_checkers, *self.orange_checkers]
        searched_checker = list(filter(lambda checker: (checker.id_tag == checker_id), checkers))
        return searched_checker[0] if len(searched_checker) else None

    def get_checker_object_from_row_col(self, row, column):
        checkers = [*self.blue_checkers, *self.orange_checkers]
        searched_checker = list(filter(lambda checker: (checker.row == row and checker.column == column), checkers))
        return searched_checker[0] if len(searched_checker) else None

    def remove_checker(self, row, col, quite_move=False):
        checker = self.get_checker_object_from_row_col(row, col)
        if checker.color == CheckerColor.ORANGE:
            self.orange_checkers.remove(checker)
            if not quite_move:
                self.master.get_computer().reset_kings_moves_count()
                self.master.get_user().update_checkers_list(checker)
        else:
            self.blue_checkers.remove(checker)
            if not quite_move:
                self.master.get_user().reset_kings_moves_count()
                self.master.get_computer().update_checkers_list(checker)

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

    def find_and_remove_checker_after_capture(self, tile, quite_move=False):
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
            if checker is not None and checker.color is not self.current_checker.color:
                self.remove_checker(point[0], point[1], quite_move)

    def get_all_checkers_with_capture_moves(self, checkers=None):
        if checkers is None:
            checkers = self.master.get_current_player().checkers

        captured = []
        current_checker_cache = self.current_checker
        for c in checkers:
            self.current_checker = c
            if self.are_capture_moves_possible():
                captured.append(c.id_tag)
        self.current_checker = current_checker_cache
        return captured

    def are_capture_moves_possible(self):
        self.capture_moves = []

        if self.current_checker.king:
            self.calculate_king_moves()
        else:
            self.calculate_checker_moves()
        return len(self.capture_moves) > 0

    def is_valid_move(self, row, col):
        if 0 <= row < self.ROWS and 0 <= col < self.COLUMNS:
            checker = self.get_checker_object_from_row_col(row, col)
            # if we are checking for capture move make sure there is checker between
            if abs(row - self.current_checker.row) == 2:
                middle_row = (row + self.current_checker.row) / 2
                middle_col = (col + self.current_checker.column) / 2
                middle_checker = self.get_checker_object_from_row_col(middle_row, middle_col)
                return checker is None and middle_checker and middle_checker.color is not self.current_checker.color
            return checker is None
        else:
            return False

    def calculate_king_moves(self):
        self.find_possible_king_moves(Movement.TOP_LEFT)
        self.find_possible_king_moves(Movement.TOP_RIGHT)
        self.find_possible_king_moves(Movement.BOTTOM_LEFT)
        self.find_possible_king_moves(Movement.BOTTOM_RIGHT)

    def find_possible_king_moves(self, movement):
        row = self.current_checker.row
        col = self.current_checker.column
        opposite_checkers_on_line = []

        if movement == Movement.BOTTOM_LEFT:
            j = col
            for i in range(row + 1, Board.ROWS):
                j -= 1
                if j >= 0:
                    if self.get_king_move(i, j, opposite_checkers_on_line) is not True:
                        break
                else:
                    break

        if movement == Movement.TOP_RIGHT:
            j = row
            for i in range(col + 1, Board.COLUMNS):
                j -= 1
                if j >= 0:
                    if self.get_king_move(j, i, opposite_checkers_on_line) is not True:
                        break
                else:
                    break

        if movement == Movement.BOTTOM_RIGHT:
            j = row
            for i in range(col + 1, Board.COLUMNS):
                j += 1
                if j < Board.ROWS:
                    if self.get_king_move(j, i, opposite_checkers_on_line) is not True:
                        break
                else:
                    break

        if movement == Movement.TOP_LEFT:
            j = col
            for i in range(row - 1, -1, -1):
                j -= 1
                if j >= 0:
                    if self.get_king_move(i, j, opposite_checkers_on_line) is not True:
                        break
                else:
                    break

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

    def get_copy_of_board(self):
        board_copy = deepcopy(self)
        board_copy.orange_checkers = deepcopy(board_copy.orange_checkers)
        board_copy.blue_checkers = deepcopy(board_copy.blue_checkers)
        return board_copy

    def run_ai(self):
        board_copy = self.get_copy_of_board()
        # zwraca obiekt klasy Move
        ai_move = calculate_move_for_ai(board_copy, 0)
        print('AI move:', [ai_move.checker.row, ai_move.checker.column], [ai_move.tile.row, ai_move.tile.column])
        self.current_checker = self.get_checker_object_from_id(ai_move.checker.id_tag)
        self.capture_moves = ai_move.capture_moves
        self.perform_move(ai_move.tile.id_val, False)
