from src.common.definitions import *
from src.models.checker import Checker
from src.views.widgets import Label


# Model gracza
class Player:
    checkers_count = 12
    checkers = []

    def __init__(self, master, player_type, checkers):
        self.type = player_type
        self.name = list(PLAYERS.keys())[player_type.value]
        self.color = CheckerColor.ORANGE if self.type == PlayerType.USER else CheckerColor.BLUE
        self.score_label_base = 'Computer: {}' if self.type == PlayerType.COMPUTER else 'Me: {}'
        self.scoreboard = Label(master, self.get_player_score_label(), 13)
        self.checkers = checkers

    def get_checkers_count(self):
        return self.checkers_count

    def delete_checkers(self, *checker_ids):
        delete_checkers = list(filter(lambda checker: (checker_ids.count(checker.id_tag)), self.checkers))
        for dc in delete_checkers:
            dc.board.delete(dc.id_tag)
            self.checkers.remove(dc)
        self.checkers_count = len(self.checkers)
        self.update_scoreboard()

    def get_player_score_label(self):
        return self.score_label_base.format(self.get_checkers_count())

    def get_scoreboard(self):
        return self.scoreboard

    def update_scoreboard(self):
        self.scoreboard['text'] = self.get_player_score_label()

