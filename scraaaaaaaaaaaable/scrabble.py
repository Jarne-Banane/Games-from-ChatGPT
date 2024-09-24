import pygame
import sys
import random
import string

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 40
BOARD_POS = (50, 50)
BOARD_SIZE = (15, 15)  # Scrabble board is 15x15

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (173, 216, 230)
BROWN = (205, 133, 63)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
PINK = (255, 105, 180)
DARK_GREEN = (34, 139, 34)
GRAY = (169, 169, 169)
LIGHT_GRAY = (211, 211, 211)

# Load dictionary
try:
    with open('words.txt', 'r') as f:
        VALID_WORDS = set(word.strip().lower() for word in f)
except FileNotFoundError:
    print("Dictionary file 'words.txt' not found.")
    sys.exit()

# Letter distribution and values (standard Scrabble)
LETTER_FREQUENCY = {
    'A': (9, 1), 'B': (2, 3), 'C': (2, 3), 'D': (4, 2), 'E': (12, 1),
    'F': (2, 4), 'G': (3, 2), 'H': (2, 4), 'I': (9, 1), 'J': (1, 8),
    'K': (1, 5), 'L': (4, 1), 'M': (2, 3), 'N': (6, 1), 'O': (8, 1),
    'P': (2, 3), 'Q': (1, 10), 'R': (6, 1), 'S': (4, 1), 'T': (6, 1),
    'U': (4, 1), 'V': (2, 4), 'W': (2, 4), 'X': (1, 8), 'Y': (2, 4),
    'Z': (1, 10), '_': (2, 0)  # Blank tiles
}

LETTER_POOL = []
for letter, (frequency, _) in LETTER_FREQUENCY.items():
    LETTER_POOL.extend([letter] * frequency)
random.shuffle(LETTER_POOL)

# Fonts
FONT = pygame.font.SysFont('Arial', 24)
SMALL_FONT = pygame.font.SysFont('Arial', 16)

# Create the screen object
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Scrabble Game')

class Button:
    def __init__(self, text, pos, size=(150, 50)):
        self.text = text
        self.rect = pygame.Rect(pos, size)
        self.color = GRAY
        self.hover_color = LIGHT_GRAY
        self.text_surface = FONT.render(text, True, BLACK)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, self.hover_color, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_rect = self.text_surface.get_rect(center=self.rect.center)
        surface.blit(self.text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class Tile:
    def __init__(self, letter, position, is_blank=False):
        self.letter = letter
        self.value = LETTER_FREQUENCY[letter][1]
        self.rect = pygame.Rect(position[0], position[1], TILE_SIZE, TILE_SIZE)
        self.position = position
        self.dragging = False
        self.is_blank = is_blank
        self.assigned_letter = letter if not is_blank else None

    def draw(self, surface):
        pygame.draw.rect(surface, BROWN, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 1)
        if self.is_blank and self.assigned_letter:
            letter_surface = FONT.render(self.assigned_letter.upper(), True, BLACK)
            value_surface = SMALL_FONT.render(str(self.value), True, BLACK)
        else:
            letter_surface = FONT.render(self.letter.upper(), True, WHITE)
            value_surface = SMALL_FONT.render(str(self.value), True, WHITE)
        surface.blit(letter_surface, (self.rect.x + 5, self.rect.y + 5))
        surface.blit(value_surface, (self.rect.x + TILE_SIZE - 15, self.rect.y + TILE_SIZE - 20))

class BoardSquare:
    def __init__(self, x, y, multiplier=None):
        self.rect = pygame.Rect(BOARD_POS[0] + x * TILE_SIZE, BOARD_POS[1] + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.multiplier = multiplier  # ('DL', 'TL', 'DW', 'TW') or None
        self.tile = None

    def draw(self, surface):
        if self.multiplier == 'TW':
            color = RED
        elif self.multiplier == 'DW':
            color = PINK
        elif self.multiplier == 'TL':
            color = BLUE
        elif self.multiplier == 'DL':
            color = DARK_GREEN
        else:
            color = GREEN
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 1)
        if self.tile:
            self.tile.rect.topleft = self.rect.topleft
            self.tile.draw(surface)
        else:
            if self.multiplier:
                text = SMALL_FONT.render(self.multiplier, True, WHITE)
                surface.blit(text, (self.rect.x + 2, self.rect.y + 2))

class Board:
    def __init__(self):
        self.grid = [[BoardSquare(x, y) for x in range(BOARD_SIZE[0])] for y in range(BOARD_SIZE[1])]
        self.word_multipliers = [[1 for _ in range(BOARD_SIZE[0])] for _ in range(BOARD_SIZE[1])]
        self.letter_multipliers = [[1 for _ in range(BOARD_SIZE[0])] for _ in range(BOARD_SIZE[1])]
        self.setup_multipliers()

    def setup_multipliers(self):
        # Define special squares based on Scrabble board layout
        triple_word_coords = [(0,0), (0,7), (0,14), (7,0), (7,14), (14,0), (14,7), (14,14)]
        double_word_coords = [(1,1), (2,2), (3,3), (4,4), (13,13), (12,12), (11,11), (10,10),
                              (1,13), (2,12), (3,11), (4,10), (13,1), (12,2), (11,3), (10,4),
                              (7,7)]
        triple_letter_coords = [(5,1), (9,1), (1,5), (5,5), (9,5), (13,5),
                                (1,9), (5,9), (9,9), (13,9), (5,13), (9,13)]
        double_letter_coords = [(3,0), (11,0), (6,2), (8,2), (0,3), (7,3), (14,3),
                                (2,6), (6,6), (8,6), (12,6), (3,7), (11,7),
                                (2,8), (6,8), (8,8), (12,8), (0,11), (7,11),
                                (14,11), (6,12), (8,12), (3,14), (11,14)]

        for y in range(BOARD_SIZE[1]):
            for x in range(BOARD_SIZE[0]):
                if (x, y) in triple_word_coords:
                    self.grid[y][x].multiplier = 'TW'
                    self.word_multipliers[y][x] = 3
                elif (x, y) in double_word_coords:
                    self.grid[y][x].multiplier = 'DW'
                    self.word_multipliers[y][x] = 2
                elif (x, y) in triple_letter_coords:
                    self.grid[y][x].multiplier = 'TL'
                    self.letter_multipliers[y][x] = 3
                elif (x, y) in double_letter_coords:
                    self.grid[y][x].multiplier = 'DL'
                    self.letter_multipliers[y][x] = 2

    def draw(self, surface):
        for row in self.grid:
            for square in row:
                square.draw(surface)

    def place_tile(self, tile, pos):
        x, y = pos
        square = self.grid[y][x]
        if square.tile is None:
            square.tile = tile
            return True
        return False

    def reset_temp_tiles(self):
        for row in self.grid:
            for square in row:
                if square.tile and square.tile.dragging:
                    square.tile = None

    def get_words(self):
        words = []
        # Check horizontally and vertically
        for direction in ['horizontal', 'vertical']:
            for idx in range(BOARD_SIZE[0]):
                word = ''
                word_score = 0
                word_multiplier = 1
                tiles_in_word = []
                for jdx in range(BOARD_SIZE[1]):
                    x, y = (jdx, idx) if direction == 'horizontal' else (idx, jdx)
                    square = self.grid[y][x]
                    if square.tile:
                        tile = square.tile
                        letter = tile.assigned_letter.lower() if tile.is_blank else tile.letter.lower()
                        lm = self.letter_multipliers[y][x] if tile.dragging else 1
                        wm = self.word_multipliers[y][x] if tile.dragging else 1
                        word_multiplier *= wm
                        word_score += tile.value * lm
                        word += letter
                        tiles_in_word.append(tile)
                    else:
                        if len(word) > 1:
                            if word in VALID_WORDS:
                                words.append((word, word_score * word_multiplier))
                            else:
                                return []  # Invalid word formed
                        word = ''
                        word_score = 0
                        word_multiplier = 1
                        tiles_in_word = []
                if len(word) > 1:
                    if word in VALID_WORDS:
                        words.append((word, word_score * word_multiplier))
                    else:
                        return []  # Invalid word formed
        return words

    def finalize_tiles(self):
        for row in self.grid:
            for square in row:
                if square.tile:
                    square.tile.dragging = False

class Player:
    def __init__(self):
        self.rack = []
        self.refill_rack()

    def refill_rack(self):
        while len(self.rack) < 7 and LETTER_POOL:
            letter = LETTER_POOL.pop()
            is_blank = letter == '_'
            tile = Tile(letter, (0, 0), is_blank)
            self.rack.append(tile)

    def draw_rack(self, surface):
        rack_x = BOARD_POS[0]
        rack_y = BOARD_POS[1] + BOARD_SIZE[1] * TILE_SIZE + 20
        for i, tile in enumerate(self.rack):
            tile.rect.topleft = (rack_x + i * (TILE_SIZE + 5), rack_y)
            tile.draw(surface)

def draw_ui(surface, score, message=''):
    pygame.draw.rect(surface, WHITE, (0, 0, SCREEN_WIDTH, 40))
    score_surface = FONT.render(f'Score: {score}', True, BLACK)
    surface.blit(score_surface, (10, 5))
    message_surface = FONT.render(message, True, RED)
    surface.blit(message_surface, (200, 5))

def main():
    clock = pygame.time.Clock()
    player = Player()
    board = Board()
    selected_tile = None
    score = 0
    message = ''
    running = True

    # Buttons
    submit_button = Button('Submit Word', (SCREEN_WIDTH - 350, 10))
    pass_button = Button('Pass Turn', (SCREEN_WIDTH - 180, 10))

    while running:
        SCREEN.fill(BLACK)
        draw_ui(SCREEN, score, message)
        board.draw(SCREEN)
        player.draw_rack(SCREEN)
        submit_button.draw(SCREEN)
        pass_button.draw(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check if buttons are clicked
                    if submit_button.is_clicked(event):
                        # Finalize the move
                        words = board.get_words()
                        if words:
                            total_score = sum([word[1] for word in words])
                            score += total_score
                            message = f'You scored {total_score} points!'
                            board.finalize_tiles()
                            player.refill_rack()
                        else:
                            message = 'Invalid word formed!'
                            board.reset_temp_tiles()
                            temp_tiles = [square.tile for row in board.grid for square in row if square.tile and square.tile.dragging]
                            player.rack.extend(temp_tiles)
                            for row in board.grid:
                                for square in row:
                                    if square.tile and square.tile.dragging:
                                        square.tile = None
                    elif pass_button.is_clicked(event):
                        # Pass turn
                        board.reset_temp_tiles()
                        player.refill_rack()
                        message = 'Turn passed.'
                    else:
                        # Tile selection
                        for tile in player.rack:
                            if tile.rect.collidepoint(event.pos):
                                selected_tile = tile
                                tile.dragging = True
                                mouse_x, mouse_y = event.pos
                                offset_x = tile.rect.x - mouse_x
                                offset_y = tile.rect.y - mouse_y

                        # Assign letter to blank tile
                        if selected_tile and selected_tile.is_blank:
                            assigned_letter = None

                            # Wait for key press to assign letter
                            waiting_for_letter = True
                            while waiting_for_letter:
                                for e in pygame.event.get():
                                    if e.type == pygame.KEYDOWN:
                                        if e.unicode.isalpha():
                                            assigned_letter = e.unicode.upper()
                                            selected_tile.assigned_letter = assigned_letter
                                            selected_tile.value = LETTER_FREQUENCY[assigned_letter][1]
                                            waiting_for_letter = False
                                            break
                                    elif e.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()
                                clock.tick(60)

                elif event.button == 3 and selected_tile:
                    # Right-click cancels dragging
                    selected_tile.dragging = False
                    selected_tile = None

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and selected_tile:
                    selected_tile.dragging = False
                    placed = False
                    for y in range(BOARD_SIZE[1]):
                        for x in range(BOARD_SIZE[0]):
                            square = board.grid[y][x]
                            if square.rect.collidepoint(event.pos):
                                if board.place_tile(selected_tile, (x, y)):
                                    player.rack.remove(selected_tile)
                                    placed = True
                    if not placed:
                        selected_tile.rect.topleft = selected_tile.position
                    selected_tile = None

            elif event.type == pygame.MOUSEMOTION:
                if selected_tile and selected_tile.dragging:
                    mouse_x, mouse_y = event.pos
                    selected_tile.rect.x = mouse_x - TILE_SIZE // 2
                    selected_tile.rect.y = mouse_y - TILE_SIZE // 2

        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main()
