from game.board import Board

b = Board()

# prendre un pion noir
p = b.get_piece(2, 1)

moves = b.get_valid_moves(p)
print(moves)