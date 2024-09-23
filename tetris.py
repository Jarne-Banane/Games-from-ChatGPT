import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
s_width = 800
s_height = 700
play_width = 300    # 300 // 10 = 30 width per block
play_height = 600   # 600 // 20 = 30 height per block
block_size = 30

# Top-left coordinates of the play area
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

# Shape formats
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# List of shapes and their colors
shapes = [S, Z, I, O, J, L, T]
shape_colors = [
    (0, 255, 0),     # Green
    (255, 0, 0),     # Red
    (0, 255, 255),   # Cyan
    (255, 255, 0),   # Yellow
    (255, 165, 0),   # Orange
    (0, 0, 255),     # Blue
    (128, 0, 128)    # Purple
]

class Piece:
    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0

def create_grid(locked_positions={}):
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def convert_shape_format(shape):
    positions = []
    format_shape = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format_shape):
        row = list(line)
        for j, char in enumerate(row):
            if char == '0':
                positions.append((shape.x + j - 2, shape.y + i - 4))
    return positions

def valid_space(shape, grid):
    accepted_positions = [
        [(x, y) for x in range(10) if grid[y][x] == (0,0,0)] for y in range(20)
    ]
    accepted_positions = [pos for sublist in accepted_positions for pos in sublist]
    formatted = convert_shape_format(shape)
    for pos in formatted:
        if pos not in accepted_positions and pos[1] > -1:
            return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Piece(5, 0, random.choice(shapes))

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(
        label, 
        (top_left_x + play_width // 2 - label.get_width() // 2,
         top_left_y + play_height // 2 - label.get_height() // 2)
    )

def draw_grid(surface, grid):
    for y in range(len(grid)):
        pygame.draw.line(
            surface, (128,128,128),
            (top_left_x, top_left_y + y * block_size),
            (top_left_x + play_width, top_left_y + y * block_size)
        )
        for x in range(len(grid[y])):
            pygame.draw.line(
                surface, (128,128,128),
                (top_left_x + x * block_size, top_left_y),
                (top_left_x + x * block_size, top_left_y + play_height)
            )

def clear_rows(grid, locked_positions):
    inc = 0
    for y in range(len(grid)-1, -1, -1):
        row = grid[y]
        if (0,0,0) not in row:
            inc += 1
            ind = y
            for x in range(len(row)):
                try:
                    del locked_positions[(x, y)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked_positions), key=lambda k: k[1])[::-1]:
            x, y = key
            if y < ind:
                new_key = (x, y + inc)
                locked_positions[new_key] = locked_positions.pop(key)
    return inc

def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape:', True, (255,255,255))
    start_x = top_left_x + play_width + 50
    start_y = top_left_y + play_height // 2 - 100
    format_shape = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format_shape):
        row = list(line)
        for j, char in enumerate(row):
            if char == '0':
                pygame.draw.rect(
                    surface, shape.color,
                    (start_x + j * block_size, start_y + i * block_size, block_size, block_size)
                )
    surface.blit(label, (start_x + 10, start_y - 30))

def update_score(new_score):
    score = max_score()
    with open('scores.txt', 'w') as f:
        if int(score) < new_score:
            f.write(str(new_score))
        else:
            f.write(str(score))

def max_score():
    try:
        with open('scores.txt', 'r') as f:
            score = f.readline().strip()
        return score
    except:
        return '0'

def draw_window(surface, grid, score=0, high_score=0):
    surface.fill((0,0,0))
    # Title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', True, (255,255,255))
    surface.blit(
        label, 
        (top_left_x + play_width // 2 - label.get_width() // 2, 30)
    )
    # Current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', True, (255,255,255))
    surface.blit(label, (top_left_x - 200, top_left_y + 200))
    # High score
    label = font.render(f'High Score: {high_score}', True, (255,255,255))
    surface.blit(label, (top_left_x - 200, top_left_y + 240))
    # Draw grid and border
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(
                surface, grid[y][x],
                (top_left_x + x * block_size, top_left_y + y * block_size, block_size, block_size)
            )
    pygame.draw.rect(
        surface, (255,0,0),
        (top_left_x, top_left_y, play_width, play_height), 5
    )
    draw_grid(surface, grid)

def main():
    global grid
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run_game = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    score = 0
    high_score = int(max_score())
    while run_game:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()
        # Piece falling mechanism
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run_game = False
                pygame.display.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
        shape_pos = convert_shape_format(current_piece)
        # Add piece to the grid
        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color
        # Piece has landed
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            # Clear rows and update score
            cleared_rows = clear_rows(grid, locked_positions)
            if cleared_rows:
                score += cleared_rows * 10
        draw_window(win, grid, score, high_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()
        # Check for game over
        if check_lost(locked_positions):
            draw_text_middle(win, 'You Lost!', 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(2000)
            run_game = False
            update_score(score)
    pygame.display.quit()

def main_menu():
    global win
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')
    run = True
    while run:
        win.fill((0,0,0))
        draw_text_middle(win, 'Press Any Key To Play', 60, (255,255,255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()

if __name__ == '__main__':
    main_menu()
