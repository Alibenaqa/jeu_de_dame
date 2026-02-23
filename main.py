import pygame
import threading

from game.game import Game
from game.piece import WHITE, BLACK
from ui.renderer import (Renderer, WIDTH, HEIGHT, SQUARE_SIZE,
                          HUD_HEIGHT, BORDER, cell_center_px)
from ai.minimax_bot import MinimaxBot, clone_board

FPS           = 60
MOVE_ANIM_MS  = 220
STEP_PAUSE_MS = 120


def get_row_col_from_mouse(pos):
    x, y = pos
    if y < HUD_HEIGHT + BORDER:
        return None
    col = (x - BORDER) // SQUARE_SIZE
    row = (y - HUD_HEIGHT - BORDER) // SQUARE_SIZE
    if 0 <= row < 8 and 0 <= col < 8:
        return row, col
    return None


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jeu de dames")

    clock    = pygame.time.Clock()
    renderer = Renderer(screen)
    game     = Game()

    human_color = BLACK
    bot         = MinimaxBot(WHITE, depth=5)

    # Bot threading state
    bot_plan          = None
    bot_seq_index     = 0
    bot_step_ready_at = 0
    bot_thread        = None
    bot_result        = [None]

    # Animation state
    anim      = None
    prev_turn = game.turn

    def reset_game():
        nonlocal game, bot_plan, bot_seq_index, bot_step_ready_at
        nonlocal bot_thread, anim, prev_turn
        game              = Game()
        bot_plan          = None
        bot_seq_index     = 0
        bot_step_ready_at = 0
        bot_thread        = None
        bot_result[0]     = None
        anim              = None
        prev_turn         = game.turn

    running = True
    while running:
        clock.tick(FPS)
        now    = pygame.time.get_ticks()
        winner = game.winner()

        if game.capture_flash_frames > 0:
            game.capture_flash_frames -= 1

        # ── Animation ────────────────────────────────────────────────
        moving_draw = None
        if anim is not None:
            t = (now - anim["start"]) / float(anim["dur"])
            if t >= 1.0:
                game.move_selected(*anim["to"])
                anim = None
                bot_step_ready_at = now + STEP_PAUSE_MS
            else:
                fx, fy = cell_center_px(*anim["from"])
                tx, ty = cell_center_px(*anim["to"])
                moving_draw = {
                    "from":  anim["from"],
                    "pixel": (fx + (tx - fx) * t, fy + (ty - fy) * t),
                    "meta":  anim["meta"],
                }

        # ── Turn change ───────────────────────────────────────────────
        if game.turn != prev_turn:
            bot_plan          = None
            bot_seq_index     = 0
            bot_thread        = None
            bot_result[0]     = None
            bot_step_ready_at = now
            prev_turn         = game.turn

        # ── Events ───────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mp = pygame.mouse.get_pos()

                if renderer.get_reset_rect().collidepoint(mp):
                    reset_game()
                    continue

                if winner is not None or anim is not None:
                    continue
                if game.turn != human_color:
                    continue

                rc = get_row_col_from_mouse(mp)
                if rc is None:
                    continue
                row, col = rc

                if (game.selected is not None
                        and (row, col) == (game.selected.row, game.selected.col)):
                    game.cancel_selection()
                    continue

                if game.selected is None:
                    game.select(row, col)
                else:
                    if (row, col) in game.valid_moves:
                        fr    = (game.selected.row, game.selected.col)
                        piece = game.board.get_piece(*fr)
                        if piece is not None:
                            anim = {
                                "from":  fr,
                                "to":    (row, col),
                                "start": now,
                                "dur":   MOVE_ANIM_MS,
                                "meta":  {"color": piece.color,
                                          "is_king": piece.is_king},
                            }
                    else:
                        game.select(row, col)

        # ── Bot (threaded) ───────────────────────────────────────────
        bot_thinking = False
        if winner is None and game.turn == bot.color and anim is None:

            if bot_plan is None:
                if bot_thread is None:
                    board_snap = clone_board(game.board)
                    turn_snap  = game.turn
                    bot_result[0] = None

                    def _think(b=board_snap, t=turn_snap):
                        bot_result[0] = bot.choose_move_sequence(b, t)

                    bot_thread = threading.Thread(target=_think, daemon=True)
                    bot_thread.start()

                if bot_thread is not None and bot_thread.is_alive():
                    bot_thinking = True
                else:
                    bot_plan          = bot_result[0]
                    bot_thread        = None
                    bot_seq_index     = 0
                    bot_step_ready_at = now + 280

            if bot_plan is not None:
                start_pos, seq = bot_plan

                if bot_seq_index == 0 and game.selected is None:
                    game.select(*start_pos)

                if (now >= bot_step_ready_at
                        and bot_seq_index < len(seq)
                        and game.selected is not None):
                    fr    = (game.selected.row, game.selected.col)
                    to    = seq[bot_seq_index]
                    piece = game.board.get_piece(*fr)
                    if piece is None:
                        bot_plan   = None
                        bot_thread = None
                    else:
                        anim = {
                            "from":  fr,
                            "to":    to,
                            "start": now,
                            "dur":   MOVE_ANIM_MS,
                            "meta":  {"color": piece.color,
                                      "is_king": piece.is_king},
                        }
                        bot_seq_index += 1

        # ── Draw ─────────────────────────────────────────────────────
        renderer.draw(game, winner, thinking=bot_thinking, moving=moving_draw)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
