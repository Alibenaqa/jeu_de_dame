from game.board import Board
from game.piece import WHITE, BLACK, Piece


class Game:
    def __init__(self):
        self.board = Board()
        self.turn = BLACK  # BLACK commence
        self.selected: Piece | None = None
        self.valid_moves: dict[tuple[int, int], list[Piece]] = {}

    # -------------------------
    # B9 : capture obligatoire + enchaînement
    # -------------------------
    def _capture_moves_only(self, moves: dict[tuple[int, int], list[Piece]]):
        """Ne garde que les coups qui capturent (liste non vide)."""
        return {pos: caps for pos, caps in moves.items() if caps}

    def _has_any_capture(self, color: str) -> bool:
        """True si le joueur `color` a au moins une capture disponible."""
        for r in range(8):
            for c in range(8):
                p = self.board.get_piece(r, c)
                if p is None or p.color != color:
                    continue
                moves = self.board.get_valid_moves(p)
                if any(caps for caps in moves.values()):
                    return True
        return False

    def _piece_capture_moves(self, piece: Piece) -> dict[tuple[int, int], list[Piece]]:
        """Coups de capture disponibles pour UNE pièce."""
        return self._capture_moves_only(self.board.get_valid_moves(piece))

    def select(self, row: int, col: int) -> bool:
        """Sélectionne une pièce et calcule ses coups.

        - Si une chaîne de captures est en cours, on ne peut pas changer de pièce.
        - Si une capture existe pour le joueur, on ne peut sélectionner qu'une pièce qui capture.
        """
        # 1) Si on est en pleine chaîne, on ne change pas de pièce
        if self.selected is not None:
            chain = self._piece_capture_moves(self.selected)
            if chain:
                return False

        piece = self.board.get_piece(row, col)
        if piece is None or piece.color != self.turn:
            return False

        moves = self.board.get_valid_moves(piece)

        # 2) Capture obligatoire au niveau du joueur
        if self._has_any_capture(self.turn):
            moves = self._capture_moves_only(moves)
            if not moves:
                return False

        self.selected = piece
        self.valid_moves = moves
        return True

    def move_selected(self, row: int, col: int) -> bool:
        """Joue un coup si la destination est valide.

        - Si capture obligatoire et le coup ne capture pas => interdit
        - Si capture faite et recapture possible => on continue avec la même pièce (tour ne change pas)
        """
        if self.selected is None:
            return False

        key = (row, col)
        if key not in self.valid_moves:
            return False

        captured = self.valid_moves[key]

        # Capture obligatoire (au niveau joueur)
        if self._has_any_capture(self.turn) and not captured:
            return False

        # Appliquer le déplacement
        self.board.move(self.selected, row, col)

        # Si capture, enlever la pièce capturée
        if captured:
            self.board.remove(captured)

            # 3) ENCHAÎNEMENT : si la même pièce peut recapturer -> on continue
            chain = self._piece_capture_moves(self.selected)
            if chain:
                self.valid_moves = chain
                return True  # même tour, même pièce

        # Sinon: fin du coup -> tour suivant
        self._next_turn()
        return True

    def _next_turn(self) -> None:
        """Passe au joueur suivant et reset la sélection."""
        self.selected = None
        self.valid_moves = {}
        self.turn = WHITE if self.turn == BLACK else BLACK