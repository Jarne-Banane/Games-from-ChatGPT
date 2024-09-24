import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 550
HEIGHT = 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Sudoku')

# Fonts
FONT = pygame.font.SysFont('Arial', 40)
SMALL_FONT = pygame.font.SysFont('Arial', 20)

# Colors
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)

# Sample Sudoku Board (0 represents empty cell)
BOARD = [
    [7, 8, 0, 4, 0, 0, 1, 2, 0],
    [6, 0, 0, 0, 7, 5, 0, 0, 9],
    [0, 0, 0, 6, 0, 1, 0, 7, 8],
    [0, 0, 7, 0, 4, 0, 2, 6, 0],
    [0, 0, 1, 0, 5, 0, 9, 3, 0],
    [9, 0, 4, 0, 6, 0, 0, 0, 5],
    [0, 7, 0, 3, 0, 0, 0, 1, 2],
    [1, 2, 0, 0, 0, 7, 4, 0, 0],
    [0, 4, 9, 2, 0, 6, 0, 0, 7]
]

class Grid:
    def __init__(self, rows, cols, width, height, board):
        self.rows = rows
        self.cols = cols
        self.cells = [[Cell(board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
        self.selected = None

    def draw(self, win):
        # Draw grid lines
        gap = WIDTH // 9
        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                thickness = 4
            else:
                thickness = 1
            pygame.draw.line(win, BLACK, (0, i * gap), (WIDTH, i * gap), thickness)
            pygame.draw.line(win, BLACK, (i * gap, 0), (i * gap, WIDTH), thickness)

        # Draw cells
        for row in self.cells:
            for cell in row:
                cell.draw(win)

    def select(self, row, col):
        # Reset all other cells
        for r in self.cells:
            for c in r:
                c.selected = False

        self.cells[row][col].selected = True
        self.selected = (row, col)

    def click(self, pos):
        if pos[0] < WIDTH and pos[1] < WIDTH:
            gap = WIDTH // 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y), int(x))
        else:
            return None

    def place(self, val):
        row, col = self.selected
        if self.cells[row][col].value == 0:
            self.cells[row][col].set_temp(val)

    def clear(self):
        row, col = self.selected
        if self.cells[row][col].value == 0:
            self.cells[row][col].set_temp(0)

    def is_finished(self):
        for row in self.cells:
            for cell in row:
                if cell.value == 0:
                    return False
        return True

class Cell:
    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def set_temp(self, val):
        self.temp = val

    def draw(self, win):
        gap = self.width // 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = FONT.render(str(self.temp), True, GRAY)
            win.blit(text, (x + 5, y + 5))
        elif self.value != 0:
            text = FONT.render(str(self.value), True, BLACK)
            win.blit(text, (x + (gap // 2 - text.get_width() // 2), y + (gap // 2 - text.get_height() // 2)))

        if self.selected:
            pygame.draw.rect(win, LIGHT_BLUE, (x, y, gap, gap), 3)

def redraw_window(win, board, time, strikes):
    win.fill(WHITE)
    # Draw time
    text = SMALL_FONT.render("Time: " + format_time(time), True, BLACK)
    win.blit(text, (WIDTH - 160, HEIGHT - 40))
    # Draw strikes
    text = SMALL_FONT.render("X " * strikes, True, RED)
    win.blit(text, (20, HEIGHT - 40))
    # Draw grid and board
    board.draw(win)

def format_time(secs):
    sec = secs % 60
    minute = secs // 60
    time_format = " " + str(minute) + ":" + str(sec).zfill(2)
    return time_format

def main():
    board = Grid(9, 9, WIDTH, WIDTH, BOARD)
    key = None
    run = True
    strikes = 0
    start = pygame.time.get_ticks()
    while run:
        play_time = (pygame.time.get_ticks() - start) // 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if board.selected:
                    if event.key == pygame.K_1:
                        key = 1
                    elif event.key == pygame.K_2:
                        key = 2
                    elif event.key == pygame.K_3:
                        key = 3
                    elif event.key == pygame.K_4:
                        key = 4
                    elif event.key == pygame.K_5:
                        key = 5
                    elif event.key == pygame.K_6:
                        key = 6
                    elif event.key == pygame.K_7:
                        key = 7
                    elif event.key == pygame.K_8:
                        key = 8
                    elif event.key == pygame.K_9:
                        key = 9
                    elif event.key == pygame.K_BACKSPACE:
                        board.clear()
                        key = None
                    elif event.key == pygame.K_RETURN:
                        row, col = board.selected
                        if board.cells[row][col].temp != 0:
                            if valid(BOARD, board.cells[row][col].temp, (row, col)):
                                board.cells[row][col].value = board.cells[row][col].temp
                                BOARD[row][col] = board.cells[row][col].temp
                                key = None
                                if board.is_finished():
                                    print("Game over")
                                    run = False
                            else:
                                print("Wrong move")
                                strikes += 1
                                if strikes >= 5:
                                    print("Too many mistakes. Game over.")
                                    run = False
                                board.cells[row][col].set_temp(0)
                                key = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key is not None:
            board.place(key)

        redraw_window(WIN, board, play_time, strikes)
        pygame.display.update()

def valid(board, num, pos):
    # Check row
    for i in range(len(board[0])):
        if board[pos[0]][i] == num and pos[1] != i:
            return False
    # Check column
    for i in range(len(board)):
        if board[i][pos[1]] == num and pos[0] != i:
            return False
    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num and (i, j) != pos:
                return False
    return True

if __name__ == "__main__":
    main()
