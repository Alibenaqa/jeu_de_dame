import pygame
from typing import Optional
from game.piece import WHITE, BLACK

ROWS, COLS = 8, 8
SQUARE_SIZE = 80
HUD_HEIGHT = 70

WIDTH = COLS * SQUARE_SIZE
HEIGHT = ROWS * SQUARE_SIZE + HUD_HEIGHT

PADDING = 10


class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 64, bold=True)

        # Bouton reset dans la barre du haut
        self.reset_rect = pygame.Rect(WIDTH - 140, 15, 120, 40)

    def get_reset_rect(self) -> pygame.Rect:
        return self.reset_rect

    def draw_hud(self, game) -> None:
        pygame.draw.rect(self.screen, (35, 35, 35), (0, 0, WIDTH, HUD_HEIGHT))

        turn_text = f"Turn: {game.turn}"
        text_surf = self.font.render(turn_text, True, (255, 255, 255))
        self.screen.blit(text_surf, (15, 22))

        pygame.draw.rect(self.screen, (70, 70, 70), self.reset_rect, border_radius=8)
        pygame.draw.rect(self.screen, (180, 180, 180), self.reset_rect, 2, border_radius=8)

        rtxt = self.font.render("Reset", True, (255, 255, 255))
        rtxt_rect = rtxt.get_rect(center=self.reset_rect.center)
        self.screen.blit(rtxt, rtxt_rect)

    def draw_board(self) -> None:
        pygame.draw.rect(self.screen, (240, 217, 181), (0, HUD_HEIGHT, WIDTH, HEIGHT - HUD_HEIGHT))

        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 1:
                    x = col * SQUARE_SIZE
                    y = HUD_HEIGHT + row * SQUARE_SIZE
                    pygame.draw.rect(self.screen, (181, 136, 99), (x, y, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self, board) -> None:
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.grid[row][col]
                if piece is None:
                    continue

                center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = HUD_HEIGHT + row * SQUARE_SIZE + SQUARE_SIZE // 2
                radius = SQUARE_SIZE // 2 - PADDING

                color = (245, 245, 245) if piece.color == WHITE else (30, 30, 30)
                pygame.draw.circle(self.screen, color, (center_x, center_y), radius)

                if piece.is_king:
                    pygame.draw.circle(self.screen, (200, 0, 0), (center_x, center_y), radius // 2, 3)

    # ✅ CHANGÉ ICI : points style chess.com
    def draw_selection(self, game) -> None:
        if game.selected is None:
            return

        # surligner la case sélectionnée
        r, c = game.selected.row, game.selected.col
        pygame.draw.rect(
            self.screen,
            (0, 180, 0),
            (c * SQUARE_SIZE, HUD_HEIGHT + r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
            4,
        )

        # points sur les destinations possibles
        for (mr, mc), captured in game.valid_moves.items():
            cx = mc * SQUARE_SIZE + SQUARE_SIZE // 2
            cy = HUD_HEIGHT + mr * SQUARE_SIZE + SQUARE_SIZE // 2

            if captured:
                # capture : anneau rouge (plus visible)
                pygame.draw.circle(self.screen, (255, 80, 80), (cx, cy), 14, 3)
            else:
                # move normal : point bleu
                pygame.draw.circle(self.screen, (0, 120, 255), (cx, cy), 10)

    def draw_capture_flash(self, game) -> None:
        if game.capture_flash_frames <= 0:
            return
        for (r, c) in game.last_captured_squares:
            pygame.draw.rect(
                self.screen,
                (255, 60, 60),
                (c * SQUARE_SIZE, HUD_HEIGHT + r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                6,
            )

    def draw_winner_overlay(self, winner: str) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        txt = f"{winner} WINS"
        surf = self.big_font.render(txt, True, (255, 255, 255))
        rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(surf, rect)

        small = self.font.render("Click Reset to play again", True, (220, 220, 220))
        srect = small.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
        self.screen.blit(small, srect)

    def draw(self, game, winner: Optional[str]) -> None:
        self.draw_hud(game)
        self.draw_board()
        self.draw_pieces(game.board)
        self.draw_selection(game)
        self.draw_capture_flash(game)
        if winner is not None:
            self.draw_winner_overlay(winner)