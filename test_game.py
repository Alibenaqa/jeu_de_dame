from game.game import Game

g = Game()

print("tour:", g.turn)

# sélectionner un pion noir en (2,1)
print("select:", g.select(2, 1))
print("valid:", g.valid_moves)

# jouer un coup simple vers (3,2)
print("move:", g.move_selected(3, 2))
print("tour:", g.turn)

# vérifier que la case (3,2) est occupée et (2,1) vide
p = g.board.get_piece(3, 2)
print("piece:", (p.row, p.col, p.color) if p else None)
print("old:", g.board.get_piece(2, 1))