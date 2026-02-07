import pygame
from game.piece import WHITE, BLACK

ROWS, COLS = 8, 8
SQUARE_SIZE = 80
WIDTH = COLS * SQUARE_SIZE
HEIGHT = ROWS * SQUARE_SIZE

PADDING = 10


class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def draw_board(self) -> None:
        self.screen.fill((240, 217, 181))
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 1:
                    x = col * SQUARE_SIZE
                    y = row * SQUARE_SIZE
                    pygame.draw.rect(
                        self.screen, (181, 136, 99),
                        (x, y, SQUARE_SIZE, SQUARE_SIZE)
                    )

    def draw_pieces(self, board) -> None:
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.grid[row][col]
                if piece is None:
                    continue

                center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
                radius = SQUARE_SIZE // 2 - PADDING

                color = (245, 245, 245) if piece.color == WHITE else (30, 30, 30)
                pygame.draw.circle(self.screen, color, (center_x, center_y), radius)

                if piece.is_king:
                    pygame.draw.circle(self.screen, (200, 0, 0), (center_x, center_y), radius // 2, 3)

    def draw_selection(self, game) -> None:
        """Met en évidence la pièce sélectionnée et ses coups possibles."""
        if game.selected is None:
            return

        # surligner la case de la pièce sélectionnée
        r, c = game.selected.row, game.selected.col
        pygame.draw.rect(
            self.screen,
            (0, 180, 0),
            (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
            4
        )

        # surligner les destinations possibles
        for (mr, mc) in game.valid_moves.keys():
            pygame.draw.rect(
                self.screen,
                (0, 120, 255),
                (mc * SQUARE_SIZE, mr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                4
            )

    def draw(self, game) -> None:
        self.draw_board()
        self.draw_pieces(game.board)
        self.draw_selection(game)