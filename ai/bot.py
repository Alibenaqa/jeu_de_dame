import random
from typing import Tuple
from game.game import Game
from game.piece import WHITE, BLACK

class RandomBot:
    def __init__(self, color: str):
        self.color = color

    def choose_move(self, game: Game):
        moves = game.legal_moves_for(self.color)
        if not moves:
            return None
        return random.choice(moves)