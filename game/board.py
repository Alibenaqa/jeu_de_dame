from game.piece import Piece, WHITE, BLACK

ROWS, COLS = 8, 8


class Board:
    def __init__(self):
        # Grille 8x8 : None = case vide, Piece = pion/dame
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.create_board()

    def create_board(self) -> None:
        """Place les 12 pions noirs (haut) et 12 pions blancs (bas) sur cases foncées."""
        for row in range(ROWS):
            for col in range(COLS):
                # On ne place que sur les cases foncées
                if (row + col) % 2 == 1:
                    if row < 3:          # lignes 0,1,2 : noirs
                        self.grid[row][col] = Piece(row, col, BLACK)
                    elif row > 4:        # lignes 5,6,7 : blancs
                        self.grid[row][col] = Piece(row, col, WHITE)

    def get_piece(self, row: int, col: int):
        """Retourne la pièce présente sur (row, col) ou None."""
        return self.grid[row][col]

    def move(self, piece: Piece, row: int, col: int) -> None:
        """Déplace une pièce sur (row, col) sans vérifier la validité du coup."""
        # 1) on vide l’ancienne case
        self.grid[piece.row][piece.col] = None

        # 2) on place la pièce sur la nouvelle case
        self.grid[row][col] = piece

        # 3) on met à jour la position dans l’objet Piece
        piece.move_to(row, col)

        # 4) Promotion en dame
        if piece.color == WHITE and row == 0:
            piece.make_king()
        elif piece.color == BLACK and row == ROWS - 1:
            piece.make_king()

    def remove(self, pieces) -> None:
        """Supprime une ou plusieurs pièces du plateau (capture)."""
        # Si on ne passe rien, on ne fait rien
        if pieces is None:
            return

        # Autoriser une seule pièce OU une liste de pièces
        if isinstance(pieces, Piece):
            pieces = [pieces]

        for piece in pieces:
            if piece is None:
                continue

            # Sécurité : on vérifie que la pièce est bien à cet endroit
            if (
                0 <= piece.row < ROWS
                and 0 <= piece.col < COLS
                and self.grid[piece.row][piece.col] is piece
            ):
                self.grid[piece.row][piece.col] = None

    def get_valid_moves(self, piece: Piece):
        """Retourne les coups valides pour une pièce.
        Format: {(row, col): [pieces_capturées]}
        """
        moves = {}
        row, col = piece.row, piece.col

        # =========================
        # CAS DAME
        # =========================
        if piece.is_king:
            directions = [
                (-1, -1), (-1, 1),
                (1, -1),  (1, 1)
            ]

            for d_row, d_col in directions:
                r, c = row + d_row, col + d_col
                captured = None

                while 0 <= r < ROWS and 0 <= c < COLS:
                    target = self.grid[r][c]

                    # Case vide -> déplacement possible (avec ou sans capture)
                    if target is None:
                        moves[(r, c)] = [] if captured is None else [captured]

                    # Pièce alliée -> bloqué
                    elif target.color == piece.color:
                        break

                    # Pièce ennemie
                    else:
                        if captured is not None:
                            break  # déjà capturé dans cette direction
                        captured = target

                    r += d_row
                    c += d_col

            return moves

                  # =========================
        # CAS PION (déplacement avant, capture avant)
        # =========================

        # déplacements simples (avant)
        if piece.color == WHITE:
            move_dirs = [(-1, -1), (-1, 1)]
        else:  # BLACK
            move_dirs = [(1, -1), (1, 1)]

        # captures (avant ET arrière — règle enchaînement)
        capture_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        # 1) Déplacements simples
        for d_row, d_col in move_dirs:
            new_row = row + d_row
            new_col = col + d_col
            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                if self.grid[new_row][new_col] is None:
                    moves[(new_row, new_col)] = []

        # 2) Captures
        for d_row, d_col in capture_dirs:
            mid_row = row + d_row
            mid_col = col + d_col
            land_row = row + 2 * d_row
            land_col = col + 2 * d_col

            if (
                0 <= mid_row < ROWS and 0 <= mid_col < COLS
                and 0 <= land_row < ROWS and 0 <= land_col < COLS
            ):
                mid_piece = self.grid[mid_row][mid_col]
                if (
                    mid_piece is not None
                    and mid_piece.color != piece.color
                    and self.grid[land_row][land_col] is None
                ):
                    moves[(land_row, land_col)] = [mid_piece]

        return moves