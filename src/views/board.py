from threading import Timer

from src.ai_algorithm import get_all_possible_moves
from src.models.board import Board
from src.models.player import Player
from src.views.view import View
from src.views.widgets import *


# Widok planszy
class BoardView(View):
    current_player_type: PlayerType = None

    def __init__(self, app_ref):
        super().__init__(app_ref)
        self.current_player_label = Label(self, '', 20)
        self.current_player_checker_label = Button(self, '')
        self.current_player_checker_label.config(state=tk.DISABLED, width=5)
        self.max_depth_label = Label(self, '', 12)
        self.board = Board(self)
        self.players: {PlayerType: Player} = {
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
        if new_player_type is PlayerType.COMPUTER:
            Timer(0.5, self.board.run_ai).start()

    def update_current_player_label(self):
        label = 'Player: {}'.format(self.get_current_player().name)
        self.current_player_label['text'] = label

    def update_current_player_checker_label(self):
        self.current_player_checker_label['background'] = self.get_current_player().color.value

    def switch_current_player(self):
        new_player_type = PlayerType((self.current_player_type.value + 1) % 2)
        self.set_new_current_player(new_player_type)

    def get_user(self):
        return self.players[PlayerType.USER]

    def get_computer(self):
        return self.players[PlayerType.COMPUTER]

    def end_game(self):
        winner_label = 'Winner is {}!'
        if self.get_computer().checkers_count > self.get_user().checkers_count:
            winner_label = winner_label.format(self.get_computer().name)
        elif self.get_computer().checkers_count < self.get_user().checkers_count:
            winner_label = winner_label.format(self.get_user().name)
        else:
            winner_label = 'Draw!'
        self.current_player_label['text'] = winner_label
        self.board.unbind_all_tags()

    def is_end_of_game(self):
        # one player has no checkers
        if self.get_computer().checkers_count == 0 or self.get_user().checkers_count == 0:
            return True

        # one player has locked moves
        copy = self.board.get_copy_of_board()
        copy.current_checker = None
        ai_possible_moves = get_all_possible_moves(copy, PlayerType.COMPUTER)
        user_possible_moves = get_all_possible_moves(copy, PlayerType.USER)
        if len(ai_possible_moves) == 0 or len(user_possible_moves) == 0:
            print('Jeden z graczy nie ma już możliwych ruchów do wykonania - koniec gry')
            return True

        # all players have locked king's moves
        if self.get_computer().get_kings_moves_count() == 15 and self.get_user().get_kings_moves_count() == 15:
            print('Każdy gracz wykonał po 15 ruchów damkami bez bić - koniec gry')
            return True
