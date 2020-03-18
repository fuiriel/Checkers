from src.models.checker import Checker
from src.models.player import Player
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
            PlayerType.COMPUTER: Player(self, PlayerType.COMPUTER),
            PlayerType.USER: Player(self, PlayerType.USER)
        }

    def display_view(self):
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(16, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(4, weight=1)
        self.create_widgets()

    def create_widgets(self):
        self.current_player_label.grid(column=0, row=0)
        self.current_player_checker_label.grid(column=3, row=0)
        self.board.grid(column=0, row=2, rowspan=14, columnspan=3)
        Label(self, 'SCOREBOARD', 15).grid(column=3, row=4)
        self.players[PlayerType.USER].get_scoreboard().grid(column=3, row=5)
        self.players[PlayerType.COMPUTER].get_scoreboard().grid(column=3, row=6)
        self.max_depth_label.grid(column=3, row=16)

        self.max_depth_label['text'] = self.get_max_depth_label()
        self.set_new_current_player(self.get_start_player_type())

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
    CHECKER_BORDER = TILE_BORDER * 6

    tile_width = WIDTH // COLUMNS
    tile_height = HEIGHT // ROWS

    orange_checkers = []
    blue_checkers = []

    def __init__(self, parent):
        super().__init__(parent, width=self.WIDTH + self.TILE_BORDER, height=self.HEIGHT + self.TILE_BORDER,
                         background=light_orange, bd=0, highlightthickness=0, relief='ridge')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.board = self.create_empty_board()
        self.create_board()

    def create_board(self):
        self.create_tiles()
        self.create_checkers()

    def create_empty_board(self):
        board = [[EMPTY for column in range(self.COLUMNS)] for row in range(self.ROWS)]
        return board

    def create_tiles(self):
        for i in range(0, self.COLUMNS):
            x1 = (i * self.tile_width) + self.TILE_BORDER
            x2 = ((i + 1) * self.tile_width) - self.TILE_BORDER
            for j in range(0, self.ROWS):
                y1 = (j * self.tile_height) + self.TILE_BORDER
                y2 = ((j + 1) * self.tile_height) - self.TILE_BORDER
                fill = white if (i + j) % 2 == 0 else light_blue
                id_rect = self.create_rectangle(x1, y1, x2, y2, fill=fill)
                self.board.append((id_rect, j, i, x1, x2, y1, y2))

    def create_checkers(self):
        for i in range(0, self.ROWS):
            if i == 3 or i == 4:
                continue
            y1 = (i * self.tile_width) + self.CHECKER_BORDER
            y2 = ((i + 1) * self.tile_width) - self.CHECKER_BORDER
            checker_color = CheckerColor.BLUE if i < 3 else CheckerColor.ORANGE
            for j in range(0, self.COLUMNS):
                if (i + j) % 2 == 1:
                    x1 = (j * self.tile_height) + self.CHECKER_BORDER
                    x2 = ((j + 1) * self.tile_height) - self.CHECKER_BORDER
                    id_tag = self.create_oval(x1, y1, x2, y2, fill=checker_color.value)
                    new_checker = Checker(i, j, checker_color, id_tag)
                    if checker_color == CheckerColor.BLUE:
                        self.blue_checkers.append((id_tag, new_checker))
                    elif checker_color == CheckerColor.ORANGE:
                        self.tag_bind(id_tag, "<ButtonPress-1>", self.on_checker_click)
                        self.orange_checkers.append((id_tag, new_checker))

    def on_checker_click(self, event):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        id_value = self.find_closest(x, y)[0]
        print(x, y, id_value)
        # TODO
