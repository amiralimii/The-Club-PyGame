import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tile Club - Match Puzzle Games")

clock = pygame.time.Clock()

BACKGROUND = (24, 32, 44)
PANEL = (37, 48, 62)
TILE_COLOR = (245, 226, 190)
TILE_SHADOW = (153, 119, 83)
WHITE = (255, 255, 255)
GOLD = (255, 194, 65)
GREEN = (93, 190, 125)
RED = (235, 85, 85)

font = pygame.font.SysFont("segoeui", 25, bold=True)
small_font = pygame.font.SysFont("segoeui", 18)
title_font = pygame.font.SysFont("segoeui", 38, bold=True)

TILE_SIZE = 72
GAP = 9
TRAY_LIMIT = 7
MATCH_COUNT = 3
SYMBOLS = ["★", "◆", "●", "♣", "♥", "✿", "▲"]

tile_font = pygame.font.SysFont("segoeuisymbol", 34, bold=True)

board = []
tray = []
score = 0
level = 1
message = "Match 3 identical tiles!"
game_over = False
selected_hint = None

def create_board():
    """Create a board containing groups of matching tiles."""
    tiles = []
    for symbol in SYMBOLS:
        tiles.extend([symbol] * 6)

    random.shuffle(tiles)

    result = []

    for row in range(6):
        for col in range(7):
            index = row * 7 + col

            result.append({
                "symbol": tiles[index],
                "x": 0,
                "y": 0,
                "active": True
            })

    return result


def restart_game():
    global board, tray, score, level
    global message, game_over, selected_hint

    board = create_board()
    tray = []
    score = 0
    level = 1
    message = "Match 3 identical tiles!"
    game_over = False
    selected_hint = None

def draw_text(text, font_obj, color, x, y, center=False):
    image = font_obj.render(str(text), True, color)
    rect = image.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(image, rect)

def draw_button(text, x, y, width, height, color):
    rect = pygame.Rect(x, y, width, height)

    pygame.draw.rect(
        screen, color, rect,
        border_radius=12
    )

    pygame.draw.rect(
        screen, (255, 255, 255), rect,
        width=2, border_radius=12
    )

    draw_text(
        text, small_font, WHITE,
        rect.centerx, rect.centery, True
    )

    return rect

def draw_tile(symbol, x, y, highlighted=False):
    
    pygame.draw.rect(
        screen, TILE_SHADOW,
        (x + 3, y + 5, TILE_SIZE, TILE_SIZE),
        border_radius=12
    )

    pygame.draw.rect(
        screen, TILE_COLOR,
        (x, y, TILE_SIZE, TILE_SIZE),
        border_radius=12
    )

    border_color = GOLD if highlighted else (255, 248, 224)

    pygame.draw.rect(
        screen, border_color,
        (x, y, TILE_SIZE, TILE_SIZE),
        width=3 if highlighted else 2,
        border_radius=12
    )

    symbol_surface = tile_font.render(symbol, True, (60, 67, 78))
    symbol_rect = symbol_surface.get_rect(
        center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2)
    )

    screen.blit(symbol_surface, symbol_rect)

def check_matches():
    global tray, score, message, level

    matched = []

    for symbol in set(tray):
        count = tray.count(symbol)

        if count >= MATCH_COUNT:
            matched.append(symbol)

    for symbol in matched:
        removed = 0
        new_tray = []

        for item in tray:
            if item == symbol and removed < MATCH_COUNT:
                removed += 1
            else:
                new_tray.append(item)

        tray = new_tray
        score += 100
        message = "Great match! +100 points"

    if score >= level * 500:
        level += 1
        message = f"Level {level} unlocked!"

def select_tile(tile):
    global tray, message, game_over, selected_hint

    if game_over or not tile["active"]:
        return

    if len(tray) >= TRAY_LIMIT:
        game_over = True
        message = "No space left! Restart to play again."
        return

    tile["active"] = False
    tray.append(tile["symbol"])
    selected_hint = None

    check_matches()

    if len(tray) >= TRAY_LIMIT:
        game_over = True
        message = "Game over! Press Restart."

def draw_game():
    screen.fill(BACKGROUND)
    draw_text(
        "TILE CLUB",
        title_font, GOLD,
        WIDTH // 2, 35, True
    )
    draw_text(
        "MATCH PUZZLE GAMES",
        small_font, WHITE,
        WIDTH // 2, 72, True
    )
    pygame.draw.rect(
        screen, PANEL,
        (25, 100, 850, 48),
        border_radius=12
    )
    draw_text(f"Score: {score}", font, WHITE, 45, 108)
    draw_text(f"Level: {level}", font, GOLD, 390, 108)
    draw_text(
        f"Tray: {len(tray)}/{TRAY_LIMIT}",
        font, WHITE, 670, 108
    )
    pygame.draw.rect(
        screen, PANEL,
        (115, 165, 670, 385),
        border_radius=18
    )
    start_x = 175
    start_y = 185
    for index, tile in enumerate(board):
        row = index // 7
        col = index % 7
        x = start_x + col * (TILE_SIZE + GAP)
        y = start_y + row * (TILE_SIZE + GAP)
        tile["x"] = x
        tile["y"] = y
        if tile["active"]:
            draw_tile(
                tile["symbol"], x, y,
                highlighted=(selected_hint == index)
            )
    draw_text(
        "YOUR TILE TRAY",
        small_font, WHITE,
        WIDTH // 2, 574, True
    )
    tray_width = 7 * 66 + 6 * 5
    tray_x = (WIDTH - tray_width) // 2
    for index in range(TRAY_LIMIT):
        x = tray_x + index * 71
        y = 592
        pygame.draw.rect(
            screen, (17, 23, 33),
            (x, y, 66, 66),
            border_radius=10
        )
        if index < len(tray):
            draw_tile(tray[index], x, y)
    restart_rect = draw_button(
        "RESTART", 235, 665, 125, 30, GREEN
    )
    hint_rect = draw_button(
        "HINT", 387, 665, 100, 30, (74, 128, 210)
    )
    shuffle_rect = draw_button(
        "SHUFFLE", 515, 665, 125, 30, (145, 96, 190)
    )
    draw_text(
        message, small_font,
        RED if game_over else WHITE,
        WIDTH // 2, 555, True
    )
    if game_over:
        draw_text(
            "GAME OVER",
            title_font, RED,
            WIDTH // 2, 315, True
        )
    return restart_rect, hint_rect, shuffle_rect
restart_game()
running = True
while running:
    restart_rect, hint_rect, shuffle_rect = draw_game()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if restart_rect.collidepoint(event.pos):
                restart_game()
                continue
            if hint_rect.collidepoint(event.pos):
                candidates = [
                    (i, tile)
                    for i, tile in enumerate(board)
                    if tile["active"] and tile["symbol"] in tray
                ]
                if candidates:
                    selected_hint = candidates[0][0]
                    message = "Try the highlighted tile!"
                else:
                    message = "Find matching symbols!"
                continue
            if shuffle_rect.collidepoint(event.pos):
                if not game_over:
                    remaining = [
                        tile["symbol"]
                        for tile in board if tile["active"]
                    ]
                    random.shuffle(remaining)
                    index = 0
                    for tile in board:
                        if tile["active"]:
                            tile["symbol"] = remaining[index]
                            index += 1
                    selected_hint = None
                    message = "Remaining tiles shuffled!"
                continue
            for index, tile in enumerate(board):
                if not tile["active"]:
                    continue
                rect = pygame.Rect(
                    tile["x"], tile["y"],
                    TILE_SIZE, TILE_SIZE
                )
                if rect.collidepoint(event.pos):
                    select_tile(tile)
                    break
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()
