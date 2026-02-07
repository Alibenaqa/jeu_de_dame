from typing import Optional, Dict, Tuple, List

from game.board import Board
from game.piece import WHITE, BLACK, Piece


class Game:
    def __init__(self):
        self.board = Board()
        self.turn = BLACK

        self.selected: Optional[Piece] = None
        self.valid_moves: Dict[Tuple[int, int], List[Piece]] = {}

        # UI effects
        self.last_captured_squares: List[Tuple[int, int]] = []
        self.capture_flash_frames: int = 0

        # True seulement quand une chaîne de captures est en cours (après une capture)
        self.in_chain: bool = False

    # -------------------------
    # Capture obligatoire + enchaînement
    # -------------------------
    def _capture_moves_only(self, moves: Dict[Tuple[int, int], List[Piece]]) -> Dict[Tuple[int, int], List[Piece]]:
        return {pos: caps for pos, caps in moves.items() if caps}

    def _has_any_capture(self, color: str) -> bool:
        for r in range(8):
            for c in range(8):
                p = self.board.get_piece(r, c)
                if p is None or p.color != color:
                    continue
                moves = self.board.get_valid_moves(p)
                if any(caps for caps in moves.values()):
                    return True
        return False

    def _piece_capture_moves(self, piece: Piece) -> Dict[Tuple[int, int], List[Piece]]:
        return self._capture_moves_only(self.board.get_valid_moves(piece))

    # -------------------------
    # Winner detection
    # -------------------------
    def _pieces_count(self, color: str) -> int:
        count = 0
        for r in range(8):
            for c in range(8):
                p = self.board.get_piece(r, c)
                if p is not None and p.color == color:
                    count += 1
        return count

    def _has_any_move(self, color: str) -> bool:
        must_capture = self._has_any_capture(color)
        for r in range(8):
            for c in range(8):
                p = self.board.get_piece(r, c)
                if p is None or p.color != color:
                    continue
                moves = self.board.get_valid_moves(p)
                if must_capture:
                    moves = self._capture_moves_only(moves)
                if moves:
                    return True
        return False

    def winner(self) -> Optional[str]:
        if self._pieces_count(BLACK) == 0:
            return WHITE
        if self._pieces_count(WHITE) == 0:
            return BLACK

        if not self._has_any_move(BLACK):
            return WHITE
        if not self._has_any_move(WHITE):
            return BLACK

        return None

    # -------------------------
    # UX : annuler sélection (si pas en chaîne)
    # -------------------------
    def cancel_selection(self) -> None:
        if not self.in_chain:
            self.selected = None
            self.valid_moves = {}

    # -------------------------
    # API de jeu
    # -------------------------
    def select(self, row: int, col: int) -> bool:
        """
        - Avant de jouer: tu peux changer de pièce librement
          (si capture obligatoire: seulement parmi celles qui capturent).
        - Pendant une chaîne (après capture + recapture possible): on bloque le changement.
        """
        if self.in_chain:
            return False

        piece = self.board.get_piece(row, col)
        if piece is None or piece.color != self.turn:
            return False

        moves = self.board.get_valid_moves(piece)

        # Capture obligatoire au niveau du joueur
        if self._has_any_capture(self.turn):
            moves = self._capture_moves_only(moves)
            if not moves:
                return False

        self.selected = piece
        self.valid_moves = moves
        return True

    def move_selected(self, row: int, col: int) -> bool:
        if self.selected is None:
            return False

        key = (row, col)
        if key not in self.valid_moves:
            return False

        captured = self.valid_moves[key]

        # capture obligatoire : si capture dispo et coup ne capture pas => interdit
        if self._has_any_capture(self.turn) and not captured:
            return False

        # reset effect data
        self.last_captured_squares = []
        self.capture_flash_frames = 0

        # jouer le coup
        self.board.move(self.selected, row, col)

        if captured:
            # effet capture
            self.last_captured_squares = [(p.row, p.col) for p in captured]
            self.capture_flash_frames = 18
            self.board.remove(captured)

            # ENCHAÎNEMENT: seulement maintenant (après capture)
            chain = self._piece_capture_moves(self.selected)
            if chain:
                self.in_chain = True
                self.valid_moves = chain
                return True  # même joueur, même pièce

        # fin du coup -> tour suivant
        self._next_turn()
        return True

    def _next_turn(self) -> None:
        self.selected = None
        self.valid_moves = {}
        self.in_chain = False
        self.turn = WHITE if self.turn == BLACK else BLACK