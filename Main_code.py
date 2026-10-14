import os
import random
import pygame
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Tile Club - Match Puzzle")
BACKGROUND_COLOR = (35, 24, 58)
PURPLE = (100, 60, 160)
DARK_PURPLE = (43, 27, 70)
LIGHT_PURPLE = (190, 150, 255)
GOLD = (255, 205, 90)
WHITE = (255, 255, 255)
GREEN = (90, 220, 140)
RED = (255, 100, 120)
GRAY = (170, 170, 180)

font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 76)
button_font = pygame.font.Font(None, 38)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
TILES_DIR = os.path.join(ASSETS_DIR, "tiles")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")

def load_image(path):
    if not os.path.isfile(path):
        print(f"Image not found: {path}")
        return None
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error as error:
        print(f"Could not load image: {path}")
        print(error)
        return None

background = load_image(os.path.join(IMAGES_DIR, "background.png"))
card_back = load_image(os.path.join(TILES_DIR, "card_back.png"))

TILE_FILES = [
    "tile_strawberry.png",
    "tile_grapes.png",
    "tile_orange.png",
    "tile_apple.png",
    "tile_banana.png",
    "tile_watermelon.png",
    "tile_lemon.png",
    "tile_pink_flower.png",
    "tile_white_flower.png",
    "tile_purple_flower.png",
    "tile_blue_flower.png",
    "tile_leaf.png",
    "tile_mushroom.png",
    "tile_butterfly.png",
    "tile_ladybug.png",
    "tile_paw.png",
    "tile_star.png",
    "tile_heart.png",
    "tile_clover.png",
    "tile_pinecone.png",
    "tile_snowflake.png",
]

tile_images = {}

for tile_id, filename in enumerate(TILE_FILES):
    image_path = os.path.join(TILES_DIR, filename)
    image = load_image(image_path)
    if image is not None:
        tile_images[tile_id] = image

MUSIC_PATH = os.path.join(MUSIC_DIR, "background.mp3")
AUDIO_AVAILABLE = False
music_enabled = False
music_volume = 0.25

try:
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()
    AUDIO_AVAILABLE = True
except pygame.error as error:
    print("Audio is unavailable:", error)

def toggle_music():
    global music_enabled

    if not AUDIO_AVAILABLE:
        print("Audio is unavailable on this system.")
        return

    if music_enabled:
        pygame.mixer.music.stop()
        music_enabled = False
        return

    if not os.path.isfile(MUSIC_PATH):
        print("Music file not found:", MUSIC_PATH)
        return

    try:
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1)
        music_enabled = True
    except pygame.error as error:
        music_enabled = False
        print("Music error:", error)

def change_volume(value):
    global music_volume
    music_volume = max(0.0, min(1.0, value))

    if AUDIO_AVAILABLE:
        pygame.mixer.music.set_volume(music_volume)

def draw_background():
    if background is not None:
        image = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))
        screen.blit(image, (0, 0))
    else:
        screen.fill(BACKGROUND_COLOR)

def draw_center_text(text, y, text_font, color=WHITE):
    surface = text_font.render(text, True, color)
    rect = surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(surface, rect)

def draw_button(rect, text, selected=False):
    color = GOLD if selected else PURPLE
    text_color = DARK_PURPLE if selected else WHITE

    pygame.draw.rect(screen, color, rect, border_radius=15)
    pygame.draw.rect(screen, LIGHT_PURPLE, rect, width=3, border_radius=15)

    label = button_font.render(text, True, text_color)
    screen.blit(label, label.get_rect(center=rect.center))

current_page = "menu"
player_name = ""
name_input = ""
name_error = ""

play_rect = pygame.Rect(325, 280, 250, 65)
settings_rect = pygame.Rect(325, 365, 250, 65)
exit_rect = pygame.Rect(325, 450, 250, 65)
music_button_rect = pygame.Rect(300, 300, 300, 60)
back_settings_rect = pygame.Rect(325, 480, 250, 60)
back_name_rect = pygame.Rect(220, 450, 200, 60)
start_game_rect = pygame.Rect(480, 450, 200, 60)
back_game_rect = pygame.Rect(25, 20, 120, 45)
restart_rect = pygame.Rect(755, 20, 120, 45)
slider_rect = pygame.Rect(300, 410, 300, 10)
name_input_rect = pygame.Rect(250, 320, 400, 60)

slider_dragging = False
name_input_active = True

COLS = 7
ROWS = 6
CARD_SIZE = 76
GAP = 8
GRID_WIDTH = COLS * CARD_SIZE + (COLS - 1) * GAP
GRID_HEIGHT = ROWS * CARD_SIZE + (ROWS - 1) * GAP
GRID_X = (WIDTH - GRID_WIDTH) // 2
GRID_Y = 145

cards = []
first_card = None
second_card = None
matched_pairs = 0
moves = 0
game_over = False
win_message = ""
hide_timer = 0

def create_deck():
    global cards

    available_ids = list(tile_images.keys())[:21]

    if not available_ids:
        available_ids = list(range(21))

    deck = available_ids * 2
    random.shuffle(deck)
    cards = []

    for tile_id in deck:
        cards.append({
            "id": tile_id,
            "revealed": False,
            "matched": False,
            "rect": pygame.Rect(0, 0, CARD_SIZE, CARD_SIZE),
        })

    position_cards()

def position_cards():
    for index, card in enumerate(cards):
        row = index // COLS
        col = index % COLS
        x = GRID_X + col * (CARD_SIZE + GAP)
        y = GRID_Y + row * (CARD_SIZE + GAP)
        card["rect"] = pygame.Rect(x, y, CARD_SIZE, CARD_SIZE)

def restart_game():
    global first_card, second_card, matched_pairs
    global moves, game_over, win_message, hide_timer

    first_card = None
    second_card = None
    matched_pairs = 0
    moves = 0
    game_over = False
    win_message = ""
    hide_timer = 0

    create_deck()

def draw_card(card):
    rect = card["rect"]
    shadow_rect = rect.move(3, 4)

    pygame.draw.rect(screen, DARK_PURPLE, shadow_rect, border_radius=12)

    if card["revealed"] or card["matched"]:
        pygame.draw.rect(screen, WHITE, rect, border_radius=12)

        image = tile_images.get(card["id"])

        if image is not None:
            picture = pygame.transform.smoothscale(
                image, (CARD_SIZE - 10, CARD_SIZE - 10)
            )
            screen.blit(picture, (rect.x + 5, rect.y + 5))
        else:
            label = font.render(str(card["id"] + 1), True, DARK_PURPLE)
            screen.blit(label, label.get_rect(center=rect.center))

        border_color = GREEN if card["matched"] else GOLD
    else:
        if card_back is not None:
            picture = pygame.transform.smoothscale(
                card_back, (CARD_SIZE, CARD_SIZE)
            )
            screen.blit(picture, rect.topleft)
        else:
            pygame.draw.rect(screen, PURPLE, rect, border_radius=12)
            pygame.draw.circle(screen, GOLD, rect.center, 13, width=3)

        border_color = LIGHT_PURPLE

    pygame.draw.rect(
        screen, border_color, rect, width=3, border_radius=12
    )

def draw_menu():
    draw_background()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((20, 10, 35, 110))
    screen.blit(overlay, (0, 0))

    draw_center_text("TILE CLUB", 155, title_font, GOLD)
    draw_center_text("MATCH PUZZLE", 215, font, WHITE)

    draw_button(play_rect, "PLAY")
    draw_button(settings_rect, "SETTINGS")
    draw_button(exit_rect, "EXIT")

    draw_center_text("Find all matching pairs!", 570, small_font, WHITE)

def draw_name_page():
    draw_background()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((20, 10, 35, 130))
    screen.blit(overlay, (0, 0))

    draw_center_text("ENTER YOUR NAME", 200, title_font, GOLD)

    pygame.draw.rect(screen, WHITE, name_input_rect, border_radius=12)
    pygame.draw.rect(
        screen,
        GOLD if name_input_active else LIGHT_PURPLE,
        name_input_rect,
        width=3,
        border_radius=12,
    )

    displayed_name = name_input

    if name_input_active and pygame.time.get_ticks() % 1000 < 500:
        displayed_name += "|"

    name_surface = font.render(displayed_name, True, DARK_PURPLE)
    screen.blit(name_surface, name_surface.get_rect(center=name_input_rect.center))

    draw_button(back_name_rect, "BACK")
    draw_button(start_game_rect, "START")

    if name_error:
        draw_center_text(name_error, 410, small_font, RED)

    draw_center_text("Type your name and press START", 550, small_font, WHITE)

def draw_settings():
    draw_background()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((20, 10, 35, 130))
    screen.blit(overlay, (0, 0))

    draw_center_text("SETTINGS", 175, title_font, GOLD)

    music_text = "MUSIC: ON" if music_enabled else "MUSIC: OFF"
    draw_button(music_button_rect, music_text)

    draw_center_text("Music Volume", 385, font, WHITE)

    pygame.draw.rect(screen, GRAY, slider_rect, border_radius=6)

    filled_width = int(slider_rect.width * music_volume)
    filled_rect = pygame.Rect(
        slider_rect.x,
        slider_rect.y,
        filled_width,
        slider_rect.height,
    )
    pygame.draw.rect(screen, GOLD, filled_rect, border_radius=6)

    knob_x = slider_rect.x + int(slider_rect.width * music_volume)
    pygame.draw.circle(screen, WHITE, (knob_x, slider_rect.centery), 13)

    volume_percent = int(music_volume * 100)
    draw_center_text(f"{volume_percent}%", 445, small_font, WHITE)
    draw_button(back_settings_rect, "BACK")

def update_volume_from_mouse(mouse_x):
    value = (mouse_x - slider_rect.x) / slider_rect.width
    change_volume(value)

def draw_game():
    draw_background()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((20, 10, 35, 115))
    screen.blit(overlay, (0, 0))

    draw_button(back_game_rect, "MENU")
    draw_button(restart_rect, "RESTART")

    draw_center_text("MATCH THE PAIRS", 78, font, GOLD)
    draw_center_text(
        f"Player: {player_name}",
        105,
        small_font,
        WHITE,
    )
    draw_center_text(
        f"Moves: {moves}     Matched pairs: {matched_pairs}/21",
        130,
        small_font,
        WHITE,
    )

    for card in cards:
        draw_card(card)

    if game_over:
        panel = pygame.Rect(220, 285, 460, 130)

        pygame.draw.rect(screen, DARK_PURPLE, panel, border_radius=20)
        pygame.draw.rect(
            screen, GOLD, panel, width=3, border_radius=20
        )

        draw_center_text(win_message, 330, title_font, GOLD)
        draw_center_text(f"Total moves: {moves}", 375, font, WHITE)

def handle_card_click(mouse_pos):
    global first_card, second_card, moves
    global hide_timer, game_over, win_message, matched_pairs

    if game_over:
        return

    if first_card is not None and second_card is not None:
        return

    for card in cards:
        if not card["rect"].collidepoint(mouse_pos):
            continue

        if card["revealed"] or card["matched"]:
            return

        card["revealed"] = True

        if first_card is None:
            first_card = card
        else:
            second_card = card
            moves += 1

            if first_card["id"] == second_card["id"]:
                first_card["matched"] = True
                second_card["matched"] = True

                first_card = None
                second_card = None
                matched_pairs += 1

                if matched_pairs == 21:
                    game_over = True
                    win_message = "YOU WIN!"
            else:
                hide_timer = pygame.time.get_ticks() + 800

        return

def start_named_game():
    global player_name, name_error, current_page

    cleaned_name = name_input.strip()

    if not cleaned_name:
        name_error = "Please enter your name!"
        return

    player_name = cleaned_name
    name_error = ""
    restart_game()
    current_page = "game"

restart_game()
running = True

while running:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if current_page == "name":
                if event.key == pygame.K_RETURN:
                    start_named_game()
                elif event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                elif event.unicode.isprintable() and len(name_input) < 24:
                    name_input += event.unicode
                    name_error = ""

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if current_page == "menu":
                    if play_rect.collidepoint(mouse_pos):
                        name_input = ""
                        name_error = ""
                        name_input_active = True
                        current_page = "name"
                    elif settings_rect.collidepoint(mouse_pos):
                        current_page = "settings"
                    elif exit_rect.collidepoint(mouse_pos):
                        running = False

                elif current_page == "name":
                    if name_input_rect.collidepoint(mouse_pos):
                        name_input_active = True
                    elif start_game_rect.collidepoint(mouse_pos):
                        start_named_game()
                    elif back_name_rect.collidepoint(mouse_pos):
                        current_page = "menu"

                elif current_page == "settings":
                    if music_button_rect.collidepoint(mouse_pos):
                        toggle_music()
                    elif back_settings_rect.collidepoint(mouse_pos):
                        current_page = "menu"
                    elif slider_rect.inflate(0, 25).collidepoint(mouse_pos):
                        slider_dragging = True
                        update_volume_from_mouse(mouse_pos[0])

                elif current_page == "game":
                    if back_game_rect.collidepoint(mouse_pos):
                        current_page = "menu"
                    elif restart_rect.collidepoint(mouse_pos):
                        restart_game()
                    else:
                        handle_card_click(mouse_pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                slider_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if current_page == "settings" and slider_dragging:
                update_volume_from_mouse(mouse_pos[0])

    if (
        first_card is not None
        and second_card is not None
        and hide_timer
        and pygame.time.get_ticks() >= hide_timer
    ):
        first_card["revealed"] = False
        second_card["revealed"] = False
        first_card = None
        second_card = None
        hide_timer = 0

    if current_page == "menu":
        draw_menu()
    elif current_page == "name":
        draw_name_page()
    elif current_page == "settings":
        draw_settings()
    elif current_page == "game":
        draw_game()

    pygame.display.flip()
    
pygame.quit()
