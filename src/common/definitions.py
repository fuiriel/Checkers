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


def set_max_depth(max_depth):
    MAX_DEPTH = max_depth


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
