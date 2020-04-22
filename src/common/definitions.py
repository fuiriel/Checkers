from enum import Enum

# Define colors
orange = '#e9872e'
light_orange = '#ed994c'
light_blue = '#8aace3'
dark_blue = '#1a3f7b'
grey = '#a3a3a3'
black = 'black'
white = 'white'
red = 'red'
light_red = '#f77e7e'
cyan = 'cyan'
beige = '#ffe6c9'

EMPTY = 0
MAX_DEPTH = 3
BG_COLOR = '#143363'


class PlayerType(Enum):
    COMPUTER = 0
    USER = 1


PLAYERS = {'Computer': PlayerType.COMPUTER, 'Me': PlayerType.USER}


class ViewType(Enum):
    START = 0
    GAME = 1


# Colors of checker piece
class CheckerColor(Enum):
    ORANGE = orange
    BLUE = dark_blue


# waga damki
W_K = 1.2
# waga zwykłego pionka
W_C = 1.1
# waga bicia gracza
W_JP = 1.3
# waga bicia przeciwnika
W_JE = 1.8
# waga możliwych ruchów
W_PM = 1
