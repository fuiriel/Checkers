from typing import Dict, Tuple

from common.definitions import *
from models.checker import Checker
from views.widgets import Label


# Model gracza
class Player:
    checkers: Dict[Tuple[int, int], Checker] = {}
    checkers_count = 12
    kings_moves_count = 0

    def __init__(self, master, player_type, checkers):
        self.type = player_type
        self.name = list(PLAYERS.keys())[player_type.value]
        self.color = CheckerColor.ORANGE if self.type == PlayerType.USER else CheckerColor.BLUE
        self.score_label_base = 'Computer: {}' if self.type == PlayerType.COMPUTER else 'Me: {}'
        self.scoreboard = Label(master, self.get_player_score_label(), 13)
        self.checkers = checkers
        self.master = master

    def get_checkers_count(self):
        return self.checkers_count

    def update_checkers_list(self, checker):
        self.checkers_count = len(self.checkers)
        checker.board.delete(checker.id_tag)
        self.update_scoreboard()

    def get_player_score_label(self):
        return self.score_label_base.format(self.get_checkers_count())

    def get_scoreboard(self):
        return self.scoreboard

    def update_scoreboard(self):
        self.scoreboard['text'] = self.get_player_score_label()

    def reset_kings_moves_count(self):
        self.kings_moves_count = 0

    def get_kings_moves_count(self):
        return self.kings_moves_count
