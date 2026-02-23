from typing import List, Tuple, Optional, Dict
import math

from game.board import Board
from game.piece import Piece, WHITE, BLACK

Pos = Tuple[int, int]
MoveSeq = List[Pos]


def opponent(color: str) -> str:
    return WHITE if color == BLACK else BLACK


def clone_board(board: Board) -> Board:
    new_b = Board()
    new_b.grid = [[None for _ in range(8)] for _ in range(8)]
    for r in range(8):
        for c in range(8):
            p = board.grid[r][c]
            if p is None:
                continue
            cp = Piece(p.row, p.col, p.color)
            if p.is_king:
                cp.make_king()
            new_b.grid[r][c] = cp
    return new_b


def capture_moves_only(moves: Dict[Pos, List[Piece]]) -> Dict[Pos, List[Piece]]:
    return {pos: caps for pos, caps in moves.items() if caps}


def any_capture_exists(board: Board, color: str) -> bool:
    for r in range(8):
        for c in range(8):
            p = board.grid[r][c]
            if p is None or p.color != color:
                continue
            moves = board.get_valid_moves(p)
            if any(caps for caps in moves.values()):
                return True
    return False


def get_piece(board: Board, pos: Pos) -> Optional[Piece]:
    r, c = pos
    return board.grid[r][c]


def remove_by_positions(board: Board, positions: List[Pos]) -> None:
    for r, c in positions:
        if 0 <= r < 8 and 0 <= c < 8:
            board.grid[r][c] = None


def apply_single_step(board: Board, from_pos: Pos, to_pos: Pos, captured_positions: List[Pos]) -> None:
    piece = get_piece(board, from_pos)
    if piece is None:
        return
    tr, tc = to_pos
    board.move(piece, tr, tc)
    if captured_positions:
        remove_by_positions(board, captured_positions)


def gen_capture_sequences(board: Board, start_pos: Pos) -> List[Tuple[Board, MoveSeq]]:
    piece = get_piece(board, start_pos)
    if piece is None:
        return []

    moves = capture_moves_only(board.get_valid_moves(piece))
    if not moves:
        return [(board, [])]

    results: List[Tuple[Board, MoveSeq]] = []
    for to_pos, captured in moves.items():
        captured_positions = [(p.row, p.col) for p in captured]
        b2 = clone_board(board)
        apply_single_step(b2, start_pos, to_pos, captured_positions)
        for b_final, seq in gen_capture_sequences(b2, to_pos):
            results.append((b_final, [to_pos] + seq))
    return results


def generate_all_turn_moves(board: Board, color: str) -> List[Tuple[Board, Pos, MoveSeq]]:
    moves_list: List[Tuple[Board, Pos, MoveSeq]] = []
    must_capture = any_capture_exists(board, color)

    for r in range(8):
        for c in range(8):
            p = board.grid[r][c]
            if p is None or p.color != color:
                continue

            base_moves = board.get_valid_moves(p)
            if must_capture:
                base_moves = capture_moves_only(base_moves)
                if not base_moves:
                    continue

            start_pos = (r, c)
            for to_pos, captured in base_moves.items():
                captured_positions = [(x.row, x.col) for x in captured]
                b2 = clone_board(board)
                apply_single_step(b2, start_pos, to_pos, captured_positions)

                if captured_positions:
                    chains = gen_capture_sequences(b2, to_pos)
                    for b_final, extra_seq in chains:
                        moves_list.append((b_final, start_pos, [to_pos] + extra_seq))
                else:
                    moves_list.append((b2, start_pos, [to_pos]))

    # Tri : captures en premier pour améliorer le pruning alpha-bêta
    moves_list.sort(key=lambda m: len(m[2]), reverse=True)
    return moves_list


# ------------------------------------------------------------------
# Table de bonus positionnel par case (8x8)
# Pions noirs avancent vers les lignes 4-7, blancs vers 0-3.
# ------------------------------------------------------------------
_CENTER_BONUS = [
    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [0.00, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.00],
    [0.00, 0.02, 0.05, 0.06, 0.06, 0.05, 0.02, 0.00],
    [0.00, 0.02, 0.06, 0.10, 0.10, 0.06, 0.02, 0.00],
    [0.00, 0.02, 0.06, 0.10, 0.10, 0.06, 0.02, 0.00],
    [0.00, 0.02, 0.05, 0.06, 0.06, 0.05, 0.02, 0.00],
    [0.00, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.00],
    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
]


def evaluate(board: Board, color: str) -> float:
    MAN_VAL  = 1.0
    KING_VAL = 3.2       # dame nettement plus forte
    ADV      = 0.04      # bonus d'avancement par rangée
    MOB      = 0.04      # bonus de mobilité
    BACK_ROW = 0.18      # garder des pions sur la rangée arrière (défense)

    opp = opponent(color)
    my_score  = 0.0
    opp_score = 0.0
    my_mob    = 0
    opp_mob   = 0

    for r in range(8):
        for c in range(8):
            p = board.grid[r][c]
            if p is None:
                continue

            val = KING_VAL if p.is_king else MAN_VAL
            pos_bonus = _CENTER_BONUS[r][c]
            mob = len(board.get_valid_moves(p))

            if p.color == color:
                my_score += val + pos_bonus
                if not p.is_king:
                    # avancement vers la promotion
                    adv_row = r if color == BLACK else (7 - r)
                    my_score += ADV * adv_row
                    # protection rangée arrière
                    back = 0 if color == BLACK else 7
                    if r == back:
                        my_score += BACK_ROW
                my_mob += mob
            else:
                opp_score += val + pos_bonus
                if not p.is_king:
                    adv_row = r if opp == BLACK else (7 - r)
                    opp_score += ADV * adv_row
                    back = 0 if opp == BLACK else 7
                    if r == back:
                        opp_score += BACK_ROW
                opp_mob += mob

    score = (my_score - opp_score) + MOB * (my_mob - opp_mob)
    return score


def terminal_winner(board: Board) -> Optional[str]:
    black_exists = white_exists = False
    for r in range(8):
        for c in range(8):
            p = board.grid[r][c]
            if p is None:
                continue
            if p.color == BLACK:
                black_exists = True
            else:
                white_exists = True

    if not black_exists:
        return WHITE
    if not white_exists:
        return BLACK
    if not generate_all_turn_moves(board, BLACK):
        return WHITE
    if not generate_all_turn_moves(board, WHITE):
        return BLACK
    return None


def minimax(board: Board, depth: int, alpha: float, beta: float,
            current: str, bot_color: str):
    win = terminal_winner(board)
    if win is not None:
        return (10000.0, None) if win == bot_color else (-10000.0, None)

    if depth == 0:
        return evaluate(board, bot_color), None

    moves = generate_all_turn_moves(board, current)
    if not moves:
        return (-10000.0, None) if current == bot_color else (10000.0, None)

    best_move = None

    if current == bot_color:
        best_val = -math.inf
        for b2, start_pos, seq in moves:
            val, _ = minimax(b2, depth - 1, alpha, beta, opponent(current), bot_color)
            if val > best_val:
                best_val = val
                best_move = (start_pos, seq)
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break
        return best_val, best_move
    else:
        best_val = math.inf
        for b2, start_pos, seq in moves:
            val, _ = minimax(b2, depth - 1, alpha, beta, opponent(current), bot_color)
            if val < best_val:
                best_val = val
                best_move = (start_pos, seq)
            beta = min(beta, best_val)
            if beta <= alpha:
                break
        return best_val, best_move


class MinimaxBot:
    def __init__(self, color: str, depth: int = 6):
        self.color = color
        self.depth = depth

    def choose_move_sequence(self, board: Board, turn_color: str):
        _, best = minimax(board, self.depth, -math.inf, math.inf, turn_color, self.color)
        return best
