import pygame

from game.game import Game
from game.piece import WHITE, BLACK
from ui.renderer import Renderer, WIDTH, HEIGHT, SQUARE_SIZE, HUD_HEIGHT
from ai.minimax_bot import MinimaxBot

FPS = 60

BOT_THINK_MS = 650     # < 1 seconde, “fait semblant”
MOVE_ANIM_MS = 220     # vitesse de glisse d’un coup
STEP_PAUSE_MS = 80     # mini pause entre étapes d’une chaîne


def get_row_col_from_mouse(pos):
    x, y = pos
    if y < HUD_HEIGHT:
        return None

    y -= HUD_HEIGHT
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE

    if 0 <= row < 8 and 0 <= col < 8:
        return row, col
    return None


def cell_center_px(row: int, col: int):
    cx = col * SQUARE_SIZE + SQUARE_SIZE // 2
    cy = HUD_HEIGHT + row * SQUARE_SIZE + SQUARE_SIZE // 2
    return cx, cy


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jeu de dames")

    clock = pygame.time.Clock()
    renderer = Renderer(screen)

    game = Game()

    # HUMAIN = BLACK, BOT = WHITE
    human_color = BLACK
    bot = MinimaxBot(WHITE, depth=3)  # tu peux monter à 4 si c'est fluide

    # --- Bot state ---
    bot_plan = None          # (start_pos, seq)
    bot_seq_index = 0
    bot_think_until = None
    bot_step_ready_at = 0

    # --- Animation state ---
    anim = None  # {"from":(r,c), "to":(r,c), "start":ms, "dur":ms, "meta":{...}}

    # turn tracking (fix blocage)
    prev_turn = game.turn

    running = True
    while running:
        dt = clock.tick(FPS)
        now = pygame.time.get_ticks()

        winner = game.winner()

        # update capture flash timer
        if game.capture_flash_frames > 0:
            game.capture_flash_frames -= 1

        # -------------------------
        # Update animation
        # -------------------------
        moving_draw = None
        if anim is not None:
            fr = anim["from"]
            to = anim["to"]
            start = anim["start"]
            dur = anim["dur"]
            meta = anim["meta"]

            t = (now - start) / float(dur)
            if t >= 1.0:
                # animation finie -> on applique vraiment le move côté Game
                tr, tc = to
                game.move_selected(tr, tc)

                anim = None
                bot_step_ready_at = now + STEP_PAUSE_MS
            else:
                fx, fy = cell_center_px(fr[0], fr[1])
                tx, ty = cell_center_px(to[0], to[1])
                mx = fx + (tx - fx) * t
                my = fy + (ty - fy) * t
                moving_draw = {"from": fr, "pixel": (mx, my), "meta": meta}

        # -------------------------
        # Reset bot state on turn change (FIX)
        # -------------------------
        if game.turn != prev_turn:
            bot_plan = None
            bot_seq_index = 0
            bot_think_until = None
            bot_step_ready_at = now
            prev_turn = game.turn

        # -------------------------
        # Events
        # -------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # reset button
                if renderer.get_reset_rect().collidepoint(mouse_pos):
                    game = Game()
                    bot_plan = None
                    bot_seq_index = 0
                    bot_think_until = None
                    bot_step_ready_at = 0
                    anim = None
                    prev_turn = game.turn
                    continue

                if winner is not None:
                    continue

                # si une animation est en cours, on ignore les clics
                if anim is not None:
                    continue

                # si c'est le tour du bot, on ignore les clics
                if game.turn != human_color:
                    continue

                rc = get_row_col_from_mouse(mouse_pos)
                if rc is None:
                    continue
                row, col = rc

                # Recliquer la même pièce = annuler sélection (si pas en chaîne)
                if game.selected is not None and (row, col) == (game.selected.row, game.selected.col):
                    game.cancel_selection()
                    continue

                # Sélection / move du joueur (AVEC animation)
                if game.selected is None:
                    game.select(row, col)
                else:
                    # si destination valide -> on anime (au lieu de téléporter)
                    if (row, col) in game.valid_moves:
                        fr = (game.selected.row, game.selected.col)
                        piece = game.board.get_piece(fr[0], fr[1])
                        if piece is not None:
                            anim = {
                                "from": fr,
                                "to": (row, col),
                                "start": now,
                                "dur": MOVE_ANIM_MS,
                                "meta": {"color": piece.color, "is_king": piece.is_king},
                            }
                    else:
                        # sinon: essayer de sélectionner une autre pièce
                        game.select(row, col)

        # -------------------------
        # Bot thinking + bot animation play
        # -------------------------
        bot_thinking = False
        if winner is None and game.turn == bot.color and anim is None:
            # 1) si pas encore de plan, le bot calcule et démarre un timer de “réflexion”
            if bot_plan is None:
                best = bot.choose_move_sequence(game.board, game.turn)
                bot_plan = best
                bot_seq_index = 0
                bot_think_until = now + BOT_THINK_MS
                bot_step_ready_at = bot_think_until

            # 2) attendre un peu (fake thinking)
            if bot_think_until is not None and now < bot_think_until:
                bot_thinking = True
            else:
                # 3) exécuter la séquence, étape par étape, avec animation
                if bot_plan is not None:
                    start_pos, seq = bot_plan

                    # sélectionner la pièce au début
                    if bot_seq_index == 0 and game.selected is None:
                        sr, sc = start_pos
                        game.select(sr, sc)

                    # si c’est le moment de jouer la prochaine étape
                    if (
                        now >= bot_step_ready_at
                        and bot_seq_index < len(seq)
                        and game.selected is not None
                    ):
                        fr = (game.selected.row, game.selected.col)
                        to = seq[bot_seq_index]

                        piece = game.board.get_piece(fr[0], fr[1])
                        if piece is None:
                            bot_plan = None
                            bot_think_until = None
                        else:
                            anim = {
                                "from": fr,
                                "to": to,
                                "start": now,
                                "dur": MOVE_ANIM_MS,
                                "meta": {"color": piece.color, "is_king": piece.is_king},
                            }
                            bot_seq_index += 1

        # -------------------------
        # Draw
        # -------------------------
        renderer.draw(game, winner, thinking=bot_thinking, moving=moving_draw)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()