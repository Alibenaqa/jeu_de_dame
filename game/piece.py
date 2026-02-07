# game/piece.py

ROWS, COLS = 8, 8

WHITE = "WHITE"
BLACK = "BLACK"


class Piece:
    def __init__(self, row: int, col: int, color: str):
        self.row = row
        self.col = col
        self.color = color
        self.is_king = False  # "dame" plus tard

    def move_to(self, row: int, col: int) -> None:
        """Met à jour la position de la pièce."""
        self.row = row
        self.col = col

    def make_king(self) -> None:
        """Promouvoir la pièce en dame."""
        self.is_king = True