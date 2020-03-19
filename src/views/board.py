from src.models.checker import Checker
from src.models.player import Player
from src.models.tile import Tile
from src.views.view import View
from src.views.widgets import *


# Widok planszy
class BoardView(View):
    current_player_type = None

    def __init__(self, app_ref):
        super().__init__(app_ref)
        self.current_player_label = Label(self, '', 20)
        self.current_player_checker_label = Button(self, '')
        self.current_player_checker_label.config(state=tk.DISABLED, width=5)
        self.max_depth_label = Label(self, '', 12)
        self.board = Board(self)
        self.players = {
            PlayerType.COMPUTER: Player(self, PlayerType.COMPUTER, self.board.blue_checkers),
            PlayerType.USER: Player(self, PlayerType.USER, self.board.orange_checkers)
        }

    def display_view(self):
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(16, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(4, weight=1)
        self.create_widgets()

        self.max_depth_label['text'] = self.get_max_depth_label()
        self.set_new_current_player(self.get_start_player_type())

    def create_widgets(self):
        self.current_player_label.grid(column=0, row=0)
        self.current_player_checker_label.grid(column=3, row=0)
        self.board.grid(column=0, row=2, rowspan=14, columnspan=3)
        Label(self, 'SCOREBOARD', 15).grid(column=3, row=4)
        self.players[PlayerType.USER].get_scoreboard().grid(column=3, row=5)
        self.players[PlayerType.COMPUTER].get_scoreboard().grid(column=3, row=6)
        self.max_depth_label.grid(column=3, row=16)

    def get_current_player(self):
        return self.players[self.current_player_type]

    def get_max_depth_label(self):
        return 'Max depth: {}'.format(self.get_max_depth_value())

    def set_new_current_player(self, new_player_type):
        self.current_player_type = new_player_type
        self.update_current_player_label()
        self.update_current_player_checker_label()

    def update_current_player_label(self):
        label = 'Player: {}'.format(self.get_current_player().name)
        self.current_player_label['text'] = label

    def update_current_player_checker_label(self):
        self.current_player_checker_label['background'] = self.get_current_player().color.value

    def switch_current_player(self):
        new_player_type = PlayerType((self.current_player_type.value + 1) % 2)
        self.set_new_current_player(new_player_type)


class Board(tk.Canvas):
    WIDTH = 400
    HEIGHT = 400
    ROWS = 8
    COLUMNS = 8
    TILE_BORDER = .75

    tile_width = WIDTH // COLUMNS
    tile_height = HEIGHT // ROWS

    orange_checkers = []
    blue_checkers = []
    board = []
    highlighted_tiles = []
    current_checker = None

    def __init__(self, parent):
        super().__init__(parent, width=self.WIDTH + self.TILE_BORDER, height=self.HEIGHT + self.TILE_BORDER,
                         background=light_orange, bd=0, highlightthickness=0, relief='ridge')
        self.parent = parent
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
                    self.tag_bind(new_checker.id_tag, "<ButtonPress-1>", self.on_checker_click)

    def on_checker_click(self, event):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        checker_id = self.find_closest(x, y)[0]
        self.clear_highlighted_tiles()
        self.show_available_moves(checker_id)

    def on_highlighted_tile_click(self, event):

        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        tile_id = self.find_closest(x, y)[0]
        tile: Tile = self.get_tile_object_from_id(tile_id)

        # remove checker if needed
        removed = False
        if self.are_capture_moves_possible():
            self.remove_checker_after_capture(tile)
            removed = True

        self.current_checker.update_location(tile.row, tile.column)
        self.clear_highlighted_tiles()

        # if checker was removed and more checker can be removed
        # todo force to use the same checker as before when multiple capture
        if (self.are_capture_moves_possible() and removed) is not True:
            self.parent.switch_current_player()

        self.current_checker = None

    def show_available_moves(self, checker_id):
        self.current_checker = self.get_checker_object_from_id(checker_id)
        if self.current_checker is None or self.current_checker.color != self.master.get_current_player().color:
            return
        list_of_moves: [] = []

        # fixme: atrapa poruszania pionkiem
        # todo: przeliczenie możliwych ruchów(done), skoków(done), wymuszeń skoków(done), uwzględniając damkę
        if self.current_checker == Checker.king:
            self.calculate_king_horizontal_moves()
            self.calculate_king_vertical_moves()
        else:
            list_of_moves = self.calculate_checker_moves()

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

    # todo Fix me
    def remove_checker_after_capture(self, tile):
        col = (self.current_checker.column + tile.column)/2
        row = (self.current_checker.row + tile.row)/2
        checker = self.get_checker_object_from_row_col(row, col)

        if checker.color == CheckerColor.ORANGE:
            self.master.players[PlayerType.COMPUTER].delete_checkers(checker.id_tag)
        else:
            self.master.players[PlayerType.USER].delete_checkers(checker.id_tag)

    def calculate_checker_moves(self):

        row = self.current_checker.row
        col = self.current_checker.column
        if self.current_checker.color == CheckerColor.ORANGE:
            normal_dash = [[-1, -1], [-1, 1]]
        else:
            normal_dash = [[1, 1], [1, -1]]

        capture_dash = [[-2, -2], [-2, 2], [2, -2], [2, 2]]
        normal_moves = []
        capture_moves = []

        for dash in normal_dash:
            if self.is_valid_move(row + dash[0], col + dash[1]):
                normal_moves.append([row + dash[0], col + dash[1]])
        for dash in capture_dash:
            if self.is_valid_move(row + dash[0], col + dash[1]):
                capture_moves.append([row + dash[0], col + dash[1]])

        # must take capture move if possible
        if capture_moves:
            return capture_moves
        else:
            return normal_moves

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
                middle_row = (row + self.current_checker.row)/2
                middle_col = (col + self.current_checker.column)/2
                middle_checker = self.get_checker_object_from_row_col(middle_row, middle_col)
                return checker is None and middle_checker is not None and middle_checker.color is not self.current_checker.color
            return checker is None
        else:
            return False

    def calculate_king_horizontal_moves(self):
        # todo implementacja
        pass

    def calculate_king_vertical_moves(self):
        # todo implementacja
        pass

