from copy import deepcopy
import random
from typing import List

from src.common.definitions import *


# model ruchu wykonywanego w algorytmie AI
class AIMove:

    def __init__(self, checker, tile, capture_moves):
        self.checker = checker
        self.tile = tile
        self.capture_moves = capture_moves

    # wykonuje ruch na planszy
    def perform(self, board):
        board.current_checker = deepcopy(self.checker)
        board.capture_moves = self.capture_moves
        board.perform_move(self.tile.id_val, True)


def calculate_move_for_ai(self, board, depth) -> AIMove:

    alpha = float('-inf')
    beta = float('inf')
    current_player = PlayerType.COMPUTER
    possible_moves = get_all_possible_moves(board, current_player)

    heuristics = []
    # Iterujemy po wszystkich mozliwych ruchach i dodajemy do heurystyki
    # jej wartosc po dojsciu do maksymalnej glebokosci
    for move in possible_moves:
        temp_board = board.get_copy_of_board()
        move.perform(temp_board)
        if current_player is PlayerType.COMPUTER:
            switched_player = PlayerType.USER
        else:
            switched_player = PlayerType.COMPUTER
        heuristics.append(min_max(self, temp_board, depth + 1, switched_player, alpha, beta))

    # znajdujemy maksymalna heurystyke sposrod wszystkich znalezionych
    max_heuristic = float('-inf')
    for heuristic in heuristics:
        if heuristic > max_heuristic:
            max_heuristic = heuristic

    # odrzuc wszystkie ruchy, w ktorych heurystyka jest mniejsza niz maksymalna
    index = 0
    for heuristic in heuristics:
        if heuristic < max_heuristic:
            del heuristics[index]
            del possible_moves[index]
        index += 1

    # wylosuj sposrod pozostalych nastepny ruch i go zwroc
    return random.choice(possible_moves)


def min_max(self, board, depth, switched_player, alpha, beta):

    # jesli doszlismy do maksymalnej glebokosci to zwroc heurystyke dla tego stanu
    if depth == MAX_DEPTH:
        return calculate_heuristic(board)

    # znajdz wszystkie aktualne ruchy w tej petli
    possible_moves = get_all_possible_moves(board, switched_player)

    # jesli komputer to szukamy wartosci maksymalnej
    if switched_player == PlayerType.COMPUTER:
        best_value = float('-inf')
        for move in possible_moves:
            temp_board = board.get_copy_of_board()
            move.perform(temp_board)
            self.current_checker = move.checker
            self.calculate_checker_moves()
            if len(self.capture_moves) == 0:
                switched_player = PlayerType.USER
            value = min_max(self, temp_board, depth + 1, switched_player, alpha, beta)
            best_value = max(best_value, value)
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break
    # jesli użytkownik to szukamy wartosci minimalnej
    else:
        best_value = float('inf')
        for move in possible_moves:
            temp_board = board.get_copy_of_board()
            move.perform(temp_board)
            self.current_checker = move.checker
            self.calculate_checker_moves()
            if len(self.capture_moves) == 0:
                switched_player = PlayerType.COMPUTER
            value = min_max(self, temp_board, depth + 1, switched_player, alpha, beta)
            best_value = min(best_value, value)
            alpha = min(alpha, best_value)
            if alpha >= beta:
                break

    return best_value


def calculate_heuristic(board):
    # waga damy to 12, waga pionka to 10
    player_checkers = board.orange_checkers
    ai_checkers = board.blue_checkers
    kings_count_player = get_kings_count(player_checkers)
    kings_count_ai = get_kings_count(ai_checkers)

    heuristic = (kings_count_ai - kings_count_player) * 12 + \
                ((len(ai_checkers) - kings_count_ai) - (len(player_checkers) - kings_count_player)) * 10

    return heuristic


def get_kings_count(checkers):
    return len(list(filter(lambda c: c.king, checkers)))


# zwraca listę możliwych ruchów na planszy dla danego gracza
def get_all_possible_moves(board, player_type) -> List[AIMove]:
    checkers = board.orange_checkers if player_type is PlayerType.USER else board.blue_checkers
    captured = board.get_all_checkers_with_capture_moves(checkers)

    moves = []
    current_checker_cache = board.current_checker
    for c in checkers:
        board.current_checker = c
        list_of_moves = board.calculate_avaible_moves(c)

        if len(list_of_moves) > 0 and (len(captured) == 0 or captured.count(c.id_tag)):
            moves += map(lambda move:
                         AIMove(c, board.get_tile_object_from_row_col(move[0], move[1]), board.capture_moves),
                         list_of_moves)
    board.current_checker = current_checker_cache
    return moves
