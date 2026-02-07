import pygame
from game.game import Game
from ui.renderer import Renderer, WIDTH, HEIGHT, SQUARE_SIZE, HUD_HEIGHT

FPS = 60


def get_row_col_from_mouse(pos):
    x, y = pos

    # clic dans le HUD => pas une case
    if y < HUD_HEIGHT:
        return None

    y -= HUD_HEIGHT
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE

    if 0 <= row < 8 and 0 <= col < 8:
        return row, col
    return None


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jeu de dames")

    clock = pygame.time.Clock()
    renderer = Renderer(screen)
    game = Game()

    running = True
    while running:
        clock.tick(FPS)

        winner = game.winner()

        # update capture flash timer
        if game.capture_flash_frames > 0:
            game.capture_flash_frames -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # reset button
                if renderer.get_reset_rect().collidepoint(mouse_pos):
                    game = Game()
                    continue

                # si gagnant => on bloque tout sauf reset
                if winner is not None:
                    continue

                rc = get_row_col_from_mouse(mouse_pos)
                if rc is None:
                    continue
                row, col = rc

                # 🔁 Recliquer la même pièce = annuler sélection (si pas en chaîne)
                if (
                    game.selected is not None
                    and (row, col) == (game.selected.row, game.selected.col)
                ):
                    game.cancel_selection()
                    continue

                if game.selected is None:
                    game.select(row, col)
                else:
                    moved = game.move_selected(row, col)
                    if not moved:
                        game.select(row, col)

        renderer.draw(game, winner)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()