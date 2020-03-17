from src.common.definitions import *
from src.views.widgets import Label


# Model gracza
class Player:
    checkers_count = 12

    def __init__(self, master, player_type):
        self.type = player_type
        self.name = list(PLAYERS.keys())[player_type.value]
        self.color = CheckerColor.ORANGE if self.type == PlayerType.USER else CheckerColor.BLUE
        self.score_label_base = 'Computer: {}' if self.type == PlayerType.COMPUTER else 'Mine: {}'
        self.scoreboard = Label(master, self.get_player_score_label(), 13)

    def get_checkers_count(self):
        return self.checkers_count

    def set_checkers_count(self, new_):
        self.checkers_count = new_
        self.update_scoreboard()

    def get_player_score_label(self):
        return self.score_label_base.format(self.get_checkers_count())

    def get_scoreboard(self):
        return self.scoreboard

    def update_scoreboard(self):
        self.scoreboard['text'] = self.get_player_score_label()

