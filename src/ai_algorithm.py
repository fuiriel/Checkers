from copy import deepcopy
import random
from typing import List

from src.common.definitions import *


# model ruchu wykonywanego w algorytmie AI
class AIMove:
    weight = None

    def __init__(self, checker, tile, capture_moves):
        self.checker = checker
        self.tile = tile
        self.capture_moves = capture_moves

    # wykonuje ruch na planszy
    def perform(self, board):
        board.current_checker = deepcopy(self.checker)
        board.capture_moves = self.capture_moves
        board.perform_move(self.tile.id_val, True)


def calculate_move_for_ai(board, depth) -> AIMove:

    alpha = float('-inf')
    beta = float('inf')
    current_player = PlayerType.COMPUTER
    possible_moves = get_all_possible_moves(board, current_player)

    heuristics = []
    # todo zablokowac mozliwosc ruchu naszego, gdy AI oblicza ruch ( ja pierdole jak wolno XD )
    # todo dodac brak przekazania kontroli przy mozliwosci kolejnego bicia, zeby komputer mogl robic multi bicie
    # Iterujemy po wszystkich mozliwych ruchach i dodajemy do heurystyki
    # jej wartosc po dojsciu do maksymalnej glebokosci
    for move in possible_moves:
        temp_board = board.get_copy_of_board()
        move.perform(temp_board)
        if current_player is PlayerType.COMPUTER:
            switched_player = PlayerType.USER
        else:
            switched_player = PlayerType.COMPUTER
        heuristics.append(min_max(temp_board, depth + 1, switched_player, alpha, beta))

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


def min_max(board, depth, switched_player, alpha, beta):

    # jesli doszlismy do maksymalnej glebokosci to zwroc heurystyke dla tego stanu
    if depth == MAX_DEPTH:
        return calculate_heuristic(board, switched_player)

    # znajdz wszystkie aktualne ruchy w tej petli
    possible_moves = get_all_possible_moves(board, switched_player)

    # jesli komputer to szukamy wartosci maksymalnej
    if switched_player == PlayerType.COMPUTER:
        best_value = float('-inf')
        for move in possible_moves:
            temp_board = board.get_copy_of_board()
            move.perform(temp_board)
            if switched_player is PlayerType.COMPUTER:
                switched_player = PlayerType.USER
            else:
                switched_player = PlayerType.COMPUTER
            value = min_max(temp_board, depth + 1, switched_player, alpha, beta)
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
            if switched_player is PlayerType.COMPUTER:
                switched_player = PlayerType.USER
            else:
                switched_player = PlayerType.COMPUTER
            value = min_max(temp_board, depth + 1, switched_player, alpha, beta)
            best_value = min(best_value, value)
            alpha = min(alpha, best_value)
            if alpha >= beta:
                break

    return best_value


def calculate_heuristic(board, player):

    # waga damy to 1.5, waga pionka to 1
    # value_for_user = ilosc_dam * wartosc_krola + ilosc_zwyklych * 1
    # value_for_ai = to samo
    # todo dodac mozliwosc dostepu do pionkow zeby moc wyliczyc ilosc dla dowolnego gracza
    if player == PlayerType.COMPUTER:
        heuristic = 5
    else:
        heuristic = 4
    return heuristic


# zwraca listę możliwych ruchów na planszy dla danego gracza
def get_all_possible_moves(board, player_type) -> List[AIMove]:
    checkers = board.orange_checkers if player_type is PlayerType.USER else board.blue_checkers
    captured = board.get_all_checkers_with_capture_moves(checkers)

    moves = []
    current_checker_cache = board.current_checker
    for c in checkers:
        board.current_checker = c
        list_of_moves = board.calculate_avaible_moves(c.id_tag)

        if len(list_of_moves) > 0 and (len(captured) == 0 or captured.count(c.id_tag)):
            moves += map(lambda move:
                         AIMove(c, board.get_tile_object_from_row_col(move[0], move[1]), board.capture_moves),
                         list_of_moves)
    board.current_checker = current_checker_cache

    print(len(moves), player_type, list(map(lambda m: (m.checker.row, m.checker.column, m.capture_moves), moves)))
    return moves
