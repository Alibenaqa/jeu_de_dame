import pygame
from game.game import Game
from ui.renderer import Renderer, WIDTH, HEIGHT, SQUARE_SIZE

FPS = 60


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_row_col_from_mouse(pygame.mouse.get_pos())

                # Si aucune pièce sélectionnée -> tenter select
                if game.selected is None:
                    game.select(row, col)
                else:
                    # sinon tenter move, sinon reselect une autre pièce
                        moved = game.move_selected(row, col)
                        print("CLICK:", (row, col), "moved=", moved, "turn=", game.turn)

                        if game.selected:
                            print("selected:", (game.selected.row, game.selected.col), "valid_moves:", list(game.valid_moves.keys()))
                        else:
                            print("selected: None")

                        if not moved:
                            ok = game.select(row, col)
                            print("select=", ok, "turn=", game.turn)
                            if game.selected:
                                print("selected:", (game.selected.row, game.selected.col), "valid_moves:", list(game.valid_moves.keys()))

        renderer.draw(game)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()