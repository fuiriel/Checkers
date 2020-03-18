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
                        self.tag_bind(new_checker.id_tag, "<ButtonPress-1>", self.on_checker_click)
                        self.orange_checkers.append(new_checker)

    def on_checker_click(self, event):
        if self.parent.current_player_type == PlayerType.COMPUTER:
            print('It\'s computer\'s turn!')
            return

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
        if not tile:
            print('Tile of id {} not found'.format(tile_id))
            return

        self.current_checker.update_location(tile.row, tile.column)
        self.clear_highlighted_tiles()
        self.current_checker = None
        self.parent.switch_current_player()

    def show_available_moves(self, checker_id):
        checker: Checker = self.get_checker_object_from_id(checker_id)
        if not checker:
            print('Checker of id {} not found'.format(checker_id))
            return
        self.current_checker = checker

        # fixme: atrapa poruszania pionkiem
        # todo: przeliczenie możliwych ruchów, skoków, wymuszeń skoków, uwzględniając damkę
        tile: Tile = self.get_tile_object_from_row_col(checker.row - 1, checker.column + 1)
        if not tile:
            print('Tile ({}, {}) not found'.format(checker.row - 1, checker.column + 1))
            return

        self.highlighted_tiles.append(tile)
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
