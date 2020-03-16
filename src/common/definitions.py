from enum import Enum


# Define colors
light_orange = '#ed994c'
orange = '#e9872e'
dark_blue = '#1a3f7b'
grey = '#a3a3a3'
black = 'black'
white = 'white'
red = 'red'
light_red = '#f77e7e'

EMPTY = 0

PLAYERS = ['Computer', 'Me']


class ViewType(Enum):
    START = 0
    GAME = 1


# Colors of checkcer piece
class CheckerColor(Enum):
    WHITE = white
    RED = red
