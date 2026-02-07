from game.board import Board
from game.piece import WHITE, BLACK, Piece

b = Board()
b.grid = [[None for _ in range(8)] for _ in range(8)]

p = Piece(2, 1, BLACK)
b.grid[2][1] = p

# 1ère capture possible: ennemi à (3,2), landing à (4,3)
e1 = Piece(3, 2, WHITE)
b.grid[3][2] = e1

# 2ème capture possible après landing: ennemi à (5,4), landing à (6,5)
e2 = Piece(5, 4, WHITE)
b.grid[5][4] = e2

print("moves1:", b.get_valid_moves(p))  # doit contenir (4,3) avec capture e1

# jouer 1ère capture
b.move(p, 4, 3)
b.remove([e1])

print("after1 pos:", p.row, p.col)
print("moves2:", b.get_valid_moves(p))  # doit contenir (6,5) avec capture e2