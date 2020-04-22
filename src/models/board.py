from copy import deepcopy, copy
from threading import Timer
from typing import List, Dict, Tuple

from ai_algorithm import calculate_move_for_ai
from models.checker import Checker
from models.tile import Tile
from views.widgets import *


class Movement(Enum):
    BOTTOM_RIGHT = "bottom_right"
    TOP_RIGHT = "top_right"
    TOP_LEFT = "top_left"
    BOTTOM_LEFT = "bottom_left"


# Model planszy
class Board(tk.Canvas):
    WIDTH = 400
    HEIGHT = 400
    ROWS = 8
    COLUMNS = 8
    TILE_BORDER = .75

    tile_width = WIDTH // COLUMNS
    tile_height = HEIGHT // ROWS

    orange_checkers: Dict[Tuple[int, int], Checker] = {}
    blue_checkers: Dict[Tuple[int, int], Checker] = {}
    board: Dict[Tuple[int, int], Tile] = {}
    highlighted_tiles: List[Tile] = []
    current_checker: Checker or None = None

    force_jump = False

    def __init__(self, master):
        super().__init__(master, width=self.WIDTH + self.TILE_BORDER, height=self.HEIGHT + self.TILE_BORDER,
                         background=light_orange, bd=0, highlightthickness=0, relief='ridge')
        from views.board import BoardView
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
                self.board[(new_tile.row, new_tile.column)] = new_tile

    def create_checkers(self):
        for i in range(0, self.ROWS):
            if i == 3 or i == 4:
                continue
            for j in range(0, self.COLUMNS):
                if (i + j) % 2 == 1:
                    new_checker = Checker(self, i, j, self.tile_width, self.tile_height)
                    if new_checker.color == CheckerColor.BLUE:
                        self.blue_checkers[(new_checker.row, new_checker.column)] = new_checker
                    elif new_checker.color == CheckerColor.ORANGE:
                        self.orange_checkers[(new_checker.row, new_checker.column)] = new_checker
                        self.tag_bind(new_checker.id_tag, "<ButtonPress-1>", self.on_checker_click)

    def on_checker_click(self, event):
        if self.force_jump:
            return

        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        checker_id = self.find_closest(x, y)[0]
        (row, column, *args) = self.gettags(checker_id)
        checker = self.get_checker_object_from_row_col(int(row), int(column))
        captured = self.check_if_capture_moves_exists_and_assign_possible_moves()
        # sprawdza, czy pionek należy do aktualnego gracza i czy jest to pionek bijący
        if not checker or checker.color is not self.master.get_current_player().color \
                or (len(captured) > 0 and checker_id not in captured):
            return

        self.clear_highlighted_tiles()
        self.show_available_moves(checker)

    def on_highlighted_tile_click(self, event):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        tile_id = self.find_closest(x, y)[0]
        (row, column, *args) = self.gettags(tile_id)
        self.perform_move(int(row), int(column))

    def perform_move(self, row, column, quiet_move=False):
        dont_allow_switch_of_checkers = False

        # Jesli ten ruch byl bijacy to trzeba usunac pionek
        if len(self.current_checker.capture_moves) > 0:
            self.find_and_remove_checker_after_capture(row, column, quiet_move)
            # update lokacji
            self.update_checker_location(row, column, quiet_move)
            # jesli mamy kolejne bicia to ustawiamy flage
            dont_allow_switch_of_checkers = self.are_capture_moves_possible(self.current_checker)
            if not quiet_move and self.current_checker.king:
                self.master.get_current_player().reset_kings_moves_count()
        else:
            # update lokacji
            self.update_checker_location(row, column, quiet_move)
            if not quiet_move and self.current_checker.king:
                self.master.get_current_player().kings_moves_count += 1

        # sprawdza czy pionek może stać się damką
        self.current_checker.check_if_king_and_set(quiet_move)
        # wyczyszczenie poswietlonych plytek
        self.clear_highlighted_tiles()
        if not quiet_move and self.master.is_end_of_game():
            self.master.end_game()
            return

        self.current_checker.normal_moves = []

        # jesli nie mamy kolejnych bic to zmieniamy gracza
        if dont_allow_switch_of_checkers is not True:
            self.current_checker = None
            self.force_jump = False
            if not quiet_move:
                self.master.switch_current_player()
            return

        # wymuszenie kolejnego bicia
        self.force_jump = True

        if quiet_move:
            return

        if self.master.current_player_type is PlayerType.USER:
            self.show_available_moves(self.current_checker)
        else:
            Timer(0.5, self.run_ai).start()

    def update_checker_location(self, row, column, quiet_move):
        if self.current_checker.color is CheckerColor.ORANGE:
            del self.orange_checkers[(self.current_checker.row, self.current_checker.column)]
            self.orange_checkers[(row, column)] = self.current_checker
        else:
            del self.blue_checkers[(self.current_checker.row, self.current_checker.column)]
            self.blue_checkers[(row, column)] = self.current_checker

        # update lokacji
        self.current_checker.update_location(row, column, quiet_move)

    def show_available_moves(self, checker):
        self.current_checker = checker

        for move in self.current_checker.get_list_of_moves():
            tile = self.get_tile_object_from_row_col(move[0], move[1])
            self.highlighted_tiles.append(tile)
            tile.highlight()

    def calculate_available_moves(self, checker):
        if checker is None:
            return []

        checker.capture_moves = []
        checker.normal_moves = []

        # w zaleznosci od rodzaju pionka przeprowadzamy kalkulacje albo dla damy albo dla zwyklego piona
        if checker.king:
            self.calculate_king_moves(checker)
        else:
            self.calculate_checker_moves(checker)

    def clear_highlighted_tiles(self):
        for tile in self.highlighted_tiles:
            tile.unhighlight()
        self.highlighted_tiles.clear()

    def get_tile_object_from_row_col(self, row, column) -> Tile:
        return self.board.get((row, column))

    def get_checker_object_from_row_col(self, row, column) -> Checker:
        return {**self.blue_checkers, **self.orange_checkers}.get((row, column))

    def remove_checker(self, checker, quite_move=False):
        if checker.color == CheckerColor.ORANGE:
            del self.orange_checkers[(checker.row, checker.column)]
            if not quite_move:
                self.master.get_computer().reset_kings_moves_count()
                self.master.get_user().update_checkers_list(checker)
        else:
            del self.blue_checkers[(checker.row, checker.column)]
            if not quite_move:
                self.master.get_user().reset_kings_moves_count()
                self.master.get_computer().update_checkers_list(checker)

    def calculate_checker_moves(self, checker):
        # ta funkcja jest zawsze dla uzytkownika, wiec kolor zawsze bedzie orange
        if checker.color == CheckerColor.ORANGE:
            normal_dash = [[-1, -1], [-1, 1]]
        else:
            normal_dash = [[1, 1], [1, -1]]

        # capture_dash to ruchy bijace, wiec pionek musi sie poruszyc o 2 pola na skos, zamiast o 1
        capture_dash = [[-2, -2], [-2, 2], [2, -2], [2, 2]]
        for dash in capture_dash:
            # sprawdz czy współrzędne mieszczą się w granicach i na polu bijacym jest pionek,
            # jesli tak to dodaj do mozliwych ruchow
            if self.is_valid_move(checker.row + dash[0], checker.column + dash[1], checker):
                checker.capture_moves.append([checker.row + dash[0], checker.column + dash[1]])
        if len(checker.capture_moves) == 0:
            for dash in normal_dash:
                # Podobnie jak dla bijacych, tylko tutaj nie sprawdzamy dodatkowo pola bijącego
                if self.is_valid_move(checker.row + dash[0], checker.column + dash[1], checker):
                    checker.normal_moves.append([checker.row + dash[0], checker.column + dash[1]])

    def find_and_remove_checker_after_capture(self, row, column, quite_move=False):
        if row > self.current_checker.row:
            row_dictionary = list(range(self.current_checker.row + 1, row))
            if column < self.current_checker.column:
                column_dictionary = list(range(self.current_checker.column - 1, column, -1))
            else:
                column_dictionary = list(range(self.current_checker.column + 1, column))
        else:
            row_dictionary = list(range(row + 1, self.current_checker.row))
            if column > self.current_checker.column:
                column_dictionary = list(range(column - 1, self.current_checker.column, -1))
            else:
                column_dictionary = list(range(column + 1, self.current_checker.column))

        points = list(zip(row_dictionary, column_dictionary))
        for point in points:
            checker = self.get_checker_object_from_row_col(point[0], point[1])
            if checker is not None and checker.color is not self.current_checker.color:
                self.remove_checker(checker, quite_move)
                return

    def check_if_capture_moves_exists_and_assign_possible_moves(self, checkers: Dict[str, Checker] = None) -> List[str]:
        if checkers is None:
            checkers = self.master.get_current_player().checkers

        captured = []
        for c in checkers.values():
            if self.are_capture_moves_possible(c):
                captured.append(c.id_tag)
        return captured

    def are_capture_moves_possible(self, checker):
        self.calculate_available_moves(checker)
        return len(checker.capture_moves) > 0

    def is_valid_move(self, row, col, current_checker):
        if 0 <= row < self.ROWS and 0 <= col < self.COLUMNS:
            checker = self.get_checker_object_from_row_col(row, col)
            # Jezeli sprawdzamy ruchy bijace, to dodatkowo na bijacym polu musi znajdowac sie pionek przeciwnika
            if abs(row - current_checker.row) == 2:
                middle_row = (row + current_checker.row) / 2
                middle_col = (col + current_checker.column) / 2
                middle_checker = self.get_checker_object_from_row_col(middle_row, middle_col)
                return checker is None and middle_checker and middle_checker.color is not current_checker.color
            return checker is None
        else:
            return False

    def calculate_king_moves(self, checker):
        self.find_possible_king_moves(Movement.TOP_LEFT, checker)
        self.find_possible_king_moves(Movement.TOP_RIGHT, checker)
        self.find_possible_king_moves(Movement.BOTTOM_LEFT, checker)
        self.find_possible_king_moves(Movement.BOTTOM_RIGHT, checker)

    def find_possible_king_moves(self, movement, checker):
        opposite_checkers_on_line = []

        #sprawdzamy ruchy w kazda mozliwa strone w petli, poniewaz dama moze sie ruszyc o dowolna dlugosc po skosie
        if movement == Movement.BOTTOM_LEFT:
            j = checker.column
            for i in range(checker.row + 1, Board.ROWS):
                j -= 1
                if j >= 0:
                    if self.get_king_move(i, j, opposite_checkers_on_line, checker) is not True:
                        break
                else:
                    break

        elif movement == Movement.TOP_RIGHT:
            j = checker.row
            for i in range(checker.column + 1, Board.COLUMNS):
                j -= 1
                if j >= 0:
                    if self.get_king_move(j, i, opposite_checkers_on_line, checker) is not True:
                        break
                else:
                    break

        elif movement == Movement.BOTTOM_RIGHT:
            j = checker.row
            for i in range(checker.column + 1, Board.COLUMNS):
                j += 1
                if j < Board.ROWS:
                    if self.get_king_move(j, i, opposite_checkers_on_line, checker) is not True:
                        break
                else:
                    break

        elif movement == Movement.TOP_LEFT:
            j = checker.column
            for i in range(checker.row - 1, -1, -1):
                j -= 1
                if j >= 0:
                    if self.get_king_move(i, j, opposite_checkers_on_line, checker) is not True:
                        break
                else:
                    break

    def get_king_move(self, row, col, opposite_checkers_on_line, checker):
        if 0 <= row < self.ROWS and 0 <= col < self.COLUMNS:
            # funkcja sprawdza czy ruch na dane pole jest mozliwy, jezeli tak to dodaje te wspolrzedne
            # do skokow bijacych lub zwyklych, w zaleznosci czy pomiedzy tymi polami byl pionek przeciwnika
            if len(opposite_checkers_on_line) == 2:
                return False
            validated_checker = self.get_checker_object_from_row_col(row, col)
            if validated_checker is not None:
                if validated_checker.color is not checker.color:
                    opposite_checkers_on_line.append(1)
                else:
                    return False
            else:
                if len(opposite_checkers_on_line) > 0:
                    checker.capture_moves.append([row, col])
                else:
                    checker.normal_moves.append([row, col])
        return True

    def unbind_all_tags(self):
        checkers = [*self.blue_checkers.values(), *self.orange_checkers.values()]
        for c in checkers:
            self.tag_unbind(c.id_tag, "<ButtonPress-1>")

    def get_copy_of_board(self):
        board_copy = deepcopy(self)
        board_copy.orange_checkers = deepcopy(board_copy.orange_checkers)
        board_copy.blue_checkers = deepcopy(board_copy.blue_checkers)
        return board_copy

    def run_ai(self):
        board_copy = self.get_copy_of_board()
        import time
        start = time.time_ns()
        # zwraca obiekt klasy AIMove
        ai_move = calculate_move_for_ai(board_copy, 0)
        end = time.time_ns()
        print(f"{end - start}")
        print('AI move:', [ai_move.checker.row, ai_move.checker.column], [ai_move.row, ai_move.col])
        self.current_checker = self.get_checker_object_from_row_col(ai_move.checker.row, ai_move.checker.column)
        self.current_checker.capture_moves = ai_move.checker.capture_moves
        self.perform_move(ai_move.row, ai_move.col)
