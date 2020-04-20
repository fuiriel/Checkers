import random
from typing import List, Dict

from common.definitions import *


# model ruchu wykonywanego w algorytmie AI
class AIMove:

    def __init__(self, checker, move):
        self.checker = checker
        self.row = move[0]
        self.col = move[1]

    # wykonuje ruch na planszy
    def perform(self, board):
        board.current_checker = board.get_checker_object_from_row_col(self.checker.row, self.checker.column)
        board.current_checker.capture_moves = self.checker.capture_moves
        board.perform_move(self.row, self.col, True)


def calculate_move_for_ai(board, depth) -> AIMove:
    alpha = float('-inf')
    beta = float('inf')
    current_player = PlayerType.COMPUTER
    possible_moves = get_all_possible_moves(board, current_player)
    if len(possible_moves) == 1:
        return possible_moves[0]

    heuristics = []
    # Iterujemy po wszystkich mozliwych ruchach i dodajemy do heurystyki
    # jej wartosc po dojsciu do maksymalnej glebokosci
    for move in possible_moves:
        temp_board = board.get_copy_of_board()
        move.perform(temp_board)
        heuristics.append(min_max(temp_board, depth + 1, current_player, alpha, beta))

    # znajdujemy maksymalna heurystyke sposrod wszystkich znalezionych
    max_heuristic = float('-inf')
    max_heuristic = max(max_heuristic, max(heuristics))

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
    if depth == board.master.get_max_depth_value():
        return calculate_heuristic(board, switched_player)
    # znajdz wszystkie aktualne ruchy w tej petli
    possible_moves = get_all_possible_moves(board, switched_player)
    if len(possible_moves) == 1:
        return calculate_heuristic(board, switched_player)

    # jesli komputer to szukamy wartosci maksymalnej
    if switched_player == PlayerType.COMPUTER:
        best_value = float('-inf')
        for move in possible_moves:
            temp_board = board.get_copy_of_board()
            move.perform(temp_board)
            if not temp_board.force_jump:
                switched_player = PlayerType.USER
                value = min_max(temp_board, depth + 1, switched_player, alpha, beta)
            else:
                value = min_max(temp_board, depth, switched_player, alpha, beta)
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
            if not temp_board.force_jump:
                switched_player = PlayerType.COMPUTER
                value = min_max(temp_board, depth + 1, switched_player, alpha, beta)
            else:
                value = min_max(temp_board, depth, switched_player, alpha, beta)
            best_value = min(best_value, value)
            alpha = min(alpha, best_value)
            if alpha >= beta:
                break

    return best_value


def calculate_heuristic(board, current_player):
    if current_player is PlayerType.COMPUTER:
        enemy_checkers = board.orange_checkers
        self_checkers = board.blue_checkers
    else:
        enemy_checkers = board.blue_checkers
        self_checkers = board.orange_checkers

    kings_count_enemy = get_kings_count(enemy_checkers)
    kings_count_self = get_kings_count(self_checkers)

    enemy_captured = board.check_if_capture_moves_exists_and_assign_possible_moves(enemy_checkers)
    self_captured = board.check_if_capture_moves_exists_and_assign_possible_moves(self_checkers)

    enemy_possible_moves = get_all_possible_moves(board, enemy_checkers)
    self_possible_moves = get_all_possible_moves(board, enemy_checkers)

    heuristic = (kings_count_self - kings_count_enemy) * W_K + \
                ((len(self_checkers) - kings_count_self) - (len(enemy_checkers) - kings_count_enemy)) * W_C + \
                (len(self_captured) * W_JP - len(enemy_captured) * W_JE) + \
                (len(self_possible_moves) - len(enemy_possible_moves)) * W_PM
    return heuristic


def get_kings_count(checkers):
    return len(list(filter(lambda c: c.king, checkers.values())))


# zwraca listę możliwych ruchów na planszy dla danego gracza
def get_all_possible_moves(board, player_type) -> List[AIMove]:
    moves = []

    if board.current_checker is not None:
        board.calculate_available_moves(board.current_checker)
        list_of_moves = board.current_checker.get_list_of_moves()
        if len(list_of_moves) > 0:
            moves += map(lambda move: AIMove(board.current_checker, (move[0], move[1])), list_of_moves)
    else:
        from models.checker import Checker
        checkers: Dict[str, Checker] = board.orange_checkers if player_type is PlayerType.USER else board.blue_checkers
        captured: List[str] = board.check_if_capture_moves_exists_and_assign_possible_moves(checkers)
        for c in checkers.values():
            list_of_moves = c.get_list_of_moves()

            if len(list_of_moves) > 0 and (len(captured) == 0 or c.id_tag in captured):
                moves += map(lambda move: AIMove(c, (move[0], move[1])), list_of_moves)

    return moves
