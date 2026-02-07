from game.game import Game
from game.piece import WHITE, BLACK, Piece

g = Game()
g.board.grid = [[None for _ in range(8)] for _ in range(8)]

black = Piece(2, 1, BLACK)
g.board.grid[2][1] = black

white = Piece(3, 2, WHITE)
g.board.grid[3][2] = white

g.turn = BLACK

print("select:", g.select(2, 1))
print("valid moves:", g.valid_moves)      # doit contenir (4,3) avec capture

print("try simple (3,0):", g.move_selected(3, 0))  # doit être False
print("try capture (4,3):", g.move_selected(4, 3)) # doit être True
print("removed:", g.board.grid[3][2] is None)      # doit être True