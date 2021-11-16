import os
import random
from time import time


# enum (kinda) that contains different terminal print styles that I will use
class styles:
    # text colours
    BLACK_TEXT = '\033[30m'
    RED_TEXT = '\033[31m'
    GREEN_TEXT = '\033[32m'
    BLUE_TEXT = '\033[34m'
    PURPLE_TEXT = '\033[35m'
    # text backgrounds
    BLACK_BG = '\033[40m'
    RED_BG = '\033[41m'
    GREEN_BG = '\033[42m'
    BLUE_BG = '\033[44m'
    PURPLE_BG = '\033[45m'
    # text effects
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    STRIKETHROUGH = '\033[09m'
    # resets style back to normal, do this after each line just to be safe
    RESET = '\033[0m'

# enum (kinda) that contains different emojis that I will use. This makes it easier to acces it throughout code, rather than copy/pasting each time
class emojis:
    HAPPY = '😃'
    SAD = '😟'
    MOUSE = '🐭'
    CAT_ACTIVE = '😼'
    CAT_INACTIVE = '😿'
    CHEESE = '🧀'


# function that renders the game board (and a border) based on its render dictionary legend
def render(board: list[list[int]], update: bool=True):
    # renders as an update by deleting what is already there
    if update:
        print('\033[0;0H')

    border_length = len(board[0]) + 2
    print(BOARD_RENDER_DICT[1] * border_length + styles.RESET)  # top border
    for row in board:
        print(BOARD_RENDER_DICT[1], end='')                     # left side border
        for col in row:
            print(BOARD_RENDER_DICT[col], end='')               # the actual game tiles (done row by row)
        print(BOARD_RENDER_DICT[1] + styles.RESET)              # right side border
    print(BOARD_RENDER_DICT[1] * border_length + styles.RESET)  # bottom border

# function to place the blocks on the board at the start of a game
def place_blocks(board: list[list[int]], width: int, height: int):
    for i in range(3, height - 3):
        for j in range(3, width - 3):
            # turning each block on the board, inset by 3, into a block
            board[i][j] = 2
    return board

# function to place the walls on the board at the start of a game
def place_walls(board: list[list[int]], width: int, height: int, empties: dict[int, list[int]], num_walls: int):
    # generating the base possibilities list (every tile in the game)
    possibilities = []
    for i in range(height):
        for j in range(width):
            possibilities.append((i, j))
    # omitting every tile less than 3 blocks away from the player from possibilites
    for i in range(height//2 + 2, height//2 - 3, -1):
        for j in range(width//2 + 2, width//2 - 3, -1):
            del possibilities[width * i + j]
    # randomly placing walls on the board and removing those spaces from the empty list
    for _ in range(num_walls):
        new_wall = random.choice(possibilities)
        del possibilities[possibilities.index(new_wall)]
        board[new_wall[0]][new_wall[1]] = 1
        # removing the now occupied space from the empties list, unless it's already been taken off due to being where a block was
        if not (2 < new_wall[0] < 18 and 2 < new_wall[1] < 18):
            del empties[new_wall[0]][empties[new_wall[0]].index(new_wall[1])]
    return board, empties

# function to place the enemies on the board at any point of a game
def place_enemies(board: list[list[int]], empties: dict[int, list[int]], num_enemies: int):
    # generating the possibilities list based off the empties
    possibilities = []
    for i in empties:
        for j in empties[i]:
            possibilities.append((i, j))
    # randomly placing enemies on the board, adding them to an enemies list, and removing those spaces from the empties list
    enemies = []
    for _ in range(num_enemies):
        new_enemy = random.choice(possibilities)
        del possibilities[possibilities.index(new_enemy)]
        board[new_enemy[0]][new_enemy[1]] = 4
        enemies.append(new_enemy)
        del empties[new_enemy[0]][empties[new_enemy[0]].index(new_enemy[1])]
    return board, empties, enemies

# function to generate the empties dict at the start of a game
def generate_empties(width: int, height: int):
    empties = {}
    for i in range(3):
        empties[i] = [i for i in range(width)]
    # this section leaves out the middle part that will be taken up by blocks
    for i in range(3, height - 3):
        empties[i] = [0, 1, 2, width - 3, width - 2, width - 1]
    for i in range(height - 3, height):
        empties[i] = [i for i in range(width)]
    return empties

# function to generate and set up a new board for a game
def generate_board(width: int, height: int, num_walls: int, num_enemies: int):
    board = [[0 for _ in range(width)] for _ in range(height)]
    board = place_blocks(board, width, height)
    empties = generate_empties(width, height)
    board, empties = place_walls(board, width, height, empties, num_walls)
    board, empties, cats = place_enemies(board, empties, num_enemies)
    player = (height//2, width//2)
    board[player[0]][player[1]] = 3
    return board, empties, cats, player


# the width and height of the board
WIDTH = 21
HEIGHT = 21

# dictionary for rendering different tiles on the terminal from the board array
BOARD_RENDER_DICT = {
    0: styles.BLACK_BG + styles.BLACK_TEXT + '  ',                  # empty space
    1: styles.BLUE_BG + styles.BLUE_TEXT + '  ',                    # wall (unmoveable)
    2: styles.GREEN_BG + styles.GREEN_TEXT + '  ',                  # block (moveable)
    3: styles.BLACK_BG + styles.BLACK_TEXT + emojis.MOUSE,          # player (mouse)
    4: styles.BLACK_BG + styles.BLACK_TEXT + emojis.CAT_ACTIVE,     # active enemy (cat)
    5: styles.BLACK_BG + styles.BLACK_TEXT + emojis.CAT_INACTIVE,   # inactive enemy (cat)
    6: styles.BLACK_BG + styles.BLACK_TEXT + emojis.CHEESE,         # cheese
}

# variables to set up the game with
NUM_WALLS = 19
NUM_ENEMIES = 3

# variables to keep track of time with (1 = 1 second)
enemy_move_start_time = time()
ENEMY_MOVE_TIME_DIFFERENCE = 1
enemy_spawn_start_time = time()
ENEMY_SPAWN_TIME_DIFFERENCE = 180
framerate_start_time = time()
FRAMERATE = 1/60

# generating a board
board, empties, enemies, player = generate_board(WIDTH, HEIGHT, NUM_WALLS, NUM_ENEMIES)


# preparing the terminal for the game
if os.name == 'nt':     # Windows support (untested as of yet). Largely "borrowed" from https://stackoverflow.com/questions/5174810/how-to-turn-off-blinking-cursor-in-command-window
    import msvcrt
    import ctypes
    class _CursorInfo(ctypes.Structure):
        _fields_ = [('size', ctypes.c_int), ('visible', ctypes.c_byte)]
    ci = _CursorInfo()
    handle = ctypes.windll.kernel32.GetStdHandle(-11)
    ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
    ci.visible = False
    ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    os.system('cls')
else:                   # Unix support (tested on Macos)
    # removes cursor with unicode(?) and clears the terminal screen
    print('\033[?25l')
    os.system('clear')


# the main game loop
while True:
    if time() - framerate_start_time > FRAMERATE:
        framerate_start_time = time()
        render(board)