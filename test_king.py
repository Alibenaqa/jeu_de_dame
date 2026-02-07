from game.board import Board
from game.piece import WHITE, BLACK, Piece

b = Board()

# 1) On vide le plateau pour un test clean
b.grid = [[None for _ in range(8)] for _ in range(8)]

# 2) On place une dame noire au centre
king = Piece(4, 3, BLACK)
king.make_king()
b.grid[4][3] = king

# 3) On place un ennemi blanc sur une diagonale, avec de la place derrière
enemy = Piece(2, 1, WHITE)
b.grid[2][1] = enemy

moves = b.get_valid_moves(king)

print("is_king:", king.is_king)
print("moves:", moves)

# Juste pour vérifier la capture : on doit voir des cases derrière (2,1),
# par exemple (1,0) avec [enemy] si c'est dans la diagonale.