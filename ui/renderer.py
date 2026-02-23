import pygame
from typing import Optional
from game.piece import WHITE, BLACK

ROWS, COLS  = 8, 8
SQUARE_SIZE = 80
HUD_HEIGHT  = 70
BORDER      = 6

WIDTH  = COLS * SQUARE_SIZE + BORDER * 2
HEIGHT = ROWS * SQUARE_SIZE + HUD_HEIGHT + BORDER

# Palette douce et lisible
C_BG       = ( 14,  14,  18)
C_HUD_BG   = ( 22,  24,  32)
C_HUD_LINE = ( 50,  54,  70)
C_LIGHT_SQ = (238, 210, 165)
C_DARK_SQ  = (105,  55,  22)
C_FRAME    = ( 55,  28,   8)
C_SEL      = ( 72, 210, 100)
C_CAP_DOT  = (240,  80,  55)
C_MOVE_DOT = (255, 255, 255)
C_FLASH    = (255,  60,  60)

PADDING = 9


def _board_rect(row: int, col: int) -> pygame.Rect:
    return pygame.Rect(
        BORDER + col * SQUARE_SIZE,
        HUD_HEIGHT + BORDER + row * SQUARE_SIZE,
        SQUARE_SIZE, SQUARE_SIZE,
    )


def cell_center_px(row: int, col: int):
    r = _board_rect(row, col)
    return r.centerx, r.centery


class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        pygame.font.init()
        self.font     = pygame.font.SysFont("Arial", 20, bold=True)
        self.sm_font  = pygame.font.SysFont("Arial", 16)
        self.big_font = pygame.font.SysFont("Arial", 62, bold=True)

        self.reset_rect = pygame.Rect(
            WIDTH - 118, (HUD_HEIGHT - 36) // 2, 106, 36)

        self._cache: dict = {}   # (color_str, is_king) → Surface

    def get_reset_rect(self):
        return self.reset_rect

    # ── HUD ──────────────────────────────────────────────────────────
    def draw_hud(self, game, thinking: bool = False) -> None:
        pygame.draw.rect(self.screen, C_HUD_BG, (0, 0, WIDTH, HUD_HEIGHT))
        pygame.draw.line(self.screen, C_HUD_LINE,
                         (0, HUD_HEIGHT - 1), (WIDTH, HUD_HEIGHT - 1), 1)

        # Compteur de pièces
        bc = wc = 0
        for r in range(8):
            for c in range(8):
                p = game.board.grid[r][c]
                if p is None:
                    continue
                if p.color == BLACK:
                    bc += 1
                else:
                    wc += 1

        # Indicateur de tour : petit cercle coloré + texte
        dot_col = (235, 228, 215) if game.turn == WHITE else (40, 38, 35)
        dot_rim = (160, 152, 138) if game.turn == WHITE else (14, 12, 10)
        mid_y   = HUD_HEIGHT // 2
        pygame.draw.circle(self.screen, dot_rim, (20, mid_y), 13)
        pygame.draw.circle(self.screen, dot_col, (20, mid_y), 10)

        label = "Blancs" if game.turn == WHITE else "Noirs"
        t = self.font.render(f"{label}   {bc} ⬤ / {wc} ⬤", True, (205, 208, 220))
        self.screen.blit(t, (42, mid_y - t.get_height() // 2))

        if thinking:
            dots = "." * ((pygame.time.get_ticks() // 400) % 4)
            bt = self.sm_font.render(f"Bot réfléchit{dots}", True, (110, 190, 255))
            self.screen.blit(bt, (42, mid_y + t.get_height() // 2 - 1))

        # Bouton Reset
        pygame.draw.rect(self.screen, (38, 40, 56),
                         self.reset_rect, border_radius=7)
        pygame.draw.rect(self.screen, (80, 86, 122),
                         self.reset_rect, 2, border_radius=7)
        rt = self.font.render("Reset", True, (200, 208, 232))
        self.screen.blit(rt, rt.get_rect(center=self.reset_rect.center))

    # ── Board ────────────────────────────────────────────────────────
    def draw_board(self) -> None:
        bw = COLS * SQUARE_SIZE + BORDER * 2
        bh = ROWS * SQUARE_SIZE + BORDER

        # Ombre
        pygame.draw.rect(self.screen, (6, 3, 0),
                         (10, HUD_HEIGHT + 10, bw, bh), border_radius=5)
        # Cadre
        pygame.draw.rect(self.screen, C_FRAME,
                         (0, HUD_HEIGHT, bw, bh), border_radius=4)

        # Cases — propres, sans fioritures
        for row in range(ROWS):
            for col in range(COLS):
                color = C_DARK_SQ if (row + col) % 2 == 1 else C_LIGHT_SQ
                pygame.draw.rect(self.screen, color, _board_rect(row, col))

    # ── Pièce (propre et nette) ───────────────────────────────────────
    def _build(self, color_str: str, is_king: bool) -> pygame.Surface:
        SS     = 3
        radius = SQUARE_SIZE // 2 - PADDING
        r_hi   = radius * SS
        D      = r_hi * 2 + 20

        surf = pygame.Surface((D, D), pygame.SRCALPHA)
        cx = cy = D // 2

        if color_str == WHITE:
            base  = (235, 224, 205)   # corps principal
            hi    = (250, 243, 230)   # zone éclairée (haut-gauche)
            rim   = ( 85,  68,  48)   # rebord
            spec  = (255, 252, 245)   # reflet
            k_col = (190, 148,  22)
        else:
            base  = ( 55,  52,  48)
            hi    = ( 88,  84,  78)
            rim   = (  8,   6,   4)
            spec  = (210, 205, 198)
            k_col = (190, 148,  22)

        # 1. Ombre portée (douce)
        pygame.draw.circle(surf, (0, 0, 0, 45), (cx + 6, cy + 8), r_hi + 3)

        # 2. Corps plat
        pygame.draw.circle(surf, base, (cx, cy), r_hi)

        # 3. Zone éclairée haut-gauche (simple cercle décalé)
        pygame.draw.circle(surf, hi,
                           (cx - r_hi // 5, cy - r_hi // 6),
                           int(r_hi * 0.72))

        # 4. Rebord net
        pygame.draw.circle(surf, (*rim, 230), (cx, cy), r_hi, 5)

        # 5. Reflet spéculaire (tout petit, très doux)
        sr = max(3, r_hi // 8)
        sx, sy = cx - r_hi // 3, cy - r_hi // 3
        for s in range(sr, 0, -1):
            t = 1.0 - s / sr
            pygame.draw.circle(surf, (*spec, int(200 * t ** 1.2)), (sx, sy), s)

        # 6. Marqueur dame
        if is_king:
            pygame.draw.circle(surf, (*k_col, 220), (cx, cy), r_hi // 2 + 3, 4)
            pygame.draw.circle(surf, (*k_col, 130), (cx, cy), r_hi // 4)

        size_lo = radius * 2 + 10
        return pygame.transform.smoothscale(surf, (size_lo, size_lo))

    def _get(self, color_str: str, is_king: bool) -> pygame.Surface:
        key = (color_str, is_king)
        if key not in self._cache:
            self._cache[key] = self._build(color_str, is_king)
        return self._cache[key]

    def _draw_piece(self, color_str: str, is_king: bool, cx: int, cy: int) -> None:
        s = self._get(color_str, is_king)
        self.screen.blit(s, (cx - s.get_width() // 2, cy - s.get_height() // 2))

    # ── Pièces ───────────────────────────────────────────────────────
    def draw_pieces(self, board, moving_from=None,
                    moving_pixel=None, moving_meta=None) -> None:
        for row in range(ROWS):
            for col in range(COLS):
                if moving_from and (row, col) == moving_from:
                    continue
                p = board.grid[row][col]
                if p is None:
                    continue
                cx, cy = cell_center_px(row, col)
                self._draw_piece(p.color, p.is_king, cx, cy)

        if moving_pixel and moving_meta:
            mx, my = moving_pixel
            self._draw_piece(moving_meta["color"], moving_meta["is_king"],
                             int(mx), int(my))

    # ── Sélection + indicateurs ───────────────────────────────────────
    def draw_selection(self, game) -> None:
        if game.selected is None:
            return

        r, c = game.selected.row, game.selected.col
        pygame.draw.rect(self.screen, C_SEL, _board_rect(r, c), 3, border_radius=2)

        SS = 3   # supersampling pour des cercles nets
        for (mr, mc), captured in game.valid_moves.items():
            cx, cy = cell_center_px(mr, mc)
            if captured:
                # Anneau rouge antialiasé
                rr = 11
                pad = 5
                size_hi = (rr + pad) * 2 * SS
                s = pygame.Surface((size_hi, size_hi), pygame.SRCALPHA)
                ch = size_hi // 2
                pygame.draw.circle(s, C_CAP_DOT, (ch, ch), rr * SS, 3 * SS)
                size_lo = (rr + pad) * 2
                s_lo = pygame.transform.smoothscale(s, (size_lo, size_lo))
                self.screen.blit(s_lo, (cx - size_lo // 2, cy - size_lo // 2))
            else:
                # Point blanc antialiasé
                rr = 7
                pad = 4
                size_hi = (rr + pad) * 2 * SS
                s = pygame.Surface((size_hi, size_hi), pygame.SRCALPHA)
                ch = size_hi // 2
                pygame.draw.circle(s, (*C_MOVE_DOT, 148), (ch, ch), rr * SS)
                size_lo = (rr + pad) * 2
                s_lo = pygame.transform.smoothscale(s, (size_lo, size_lo))
                self.screen.blit(s_lo, (cx - size_lo // 2, cy - size_lo // 2))

    # ── Flash capture ─────────────────────────────────────────────────
    def draw_capture_flash(self, game) -> None:
        if game.capture_flash_frames <= 0:
            return
        alpha = min(185, game.capture_flash_frames * 12)
        for (r, c) in game.last_captured_squares:
            rect  = _board_rect(r, c)
            flash = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            flash.fill((*C_FLASH, alpha))
            self.screen.blit(flash, rect.topleft)

    # ── Victoire ──────────────────────────────────────────────────────
    def draw_winner_overlay(self, winner: str) -> None:
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((5, 6, 16, 172))
        self.screen.blit(ov, (0, 0))

        label = "Blancs" if winner == WHITE else "Noirs"
        s = self.big_font.render(f"{label} gagnent !", True, (255, 242, 150))
        self.screen.blit(s, s.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 24)))

        sm = self.font.render("Cliquez sur Reset pour rejouer", True, (185, 192, 215))
        self.screen.blit(sm, sm.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 46)))

    # ── Draw ─────────────────────────────────────────────────────────
    def draw(self, game, winner: Optional[str],
             thinking: bool = False, moving=None) -> None:
        self.screen.fill(C_BG)
        self.draw_board()
        self.draw_hud(game, thinking)

        mv_from  = moving.get("from")  if moving else None
        mv_pixel = moving.get("pixel") if moving else None
        mv_meta  = moving.get("meta")  if moving else None

        self.draw_pieces(game.board, mv_from, mv_pixel, mv_meta)
        self.draw_selection(game)
        self.draw_capture_flash(game)

        if winner:
            self.draw_winner_overlay(winner)
