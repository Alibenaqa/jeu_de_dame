from game.board import Board
from game.piece import BLACK

b = Board()

# 1) Prendre un pion noir
p = b.get_piece(2, 1)
print("avant:", p.row, p.col, p.color, "is_king=", p.is_king)

# 2) Vider la colonne/diagonale jusqu'en bas pour pouvoir le descendre sans être bloqué
# (on supprime ce qui gêne, c'est juste un test)
for r in range(3, 8):
    b.grid[r][2] = None  # on libère des cases possibles

# 3) Le déplacer directement sur la dernière ligne (simulation rapide)
b.move(p, 7, 2)

print("apres:", p.row, p.col, p.color, "is_king=", p.is_king)