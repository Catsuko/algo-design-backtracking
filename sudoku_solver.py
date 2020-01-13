import math


class FinishedFlag:

    def __init__(self):
        self.finished = False
        self.counter = 0

    def is_finished(self):
        return self.finished

    def mark_finished(self):
        self.finished = True

    def tick(self):
        self.counter = self.counter + 1

    def __str__(self):
        return "Finished: %s (%d)" % (self.finished, self.counter)


MAX_CANDIDATES = 2
SECTOR_DIMENSION = 3
DIMENSION = 9
NCELLS = DIMENSION * DIMENSION
finished_flag = FinishedFlag()


class Board:

    def __init__(self):
        self.m = [[None] * DIMENSION for y in range(DIMENSION)]
        self.moves = [None] * (NCELLS + 1)
        self.free_cells = NCELLS

    def plan_move(self, k, move):
        self.moves[k] = move

    def fill(self, x, y, n):
        if self.m[y][x] is None:
            self.free_cells = self.free_cells - 1
        self.m[y][x] = n

    def free(self, x, y):
        if self.m[y][x] is not None:
            self.free_cells = self.free_cells + 1
            self.m[y][x] = None

    def dead_end_exists(self):
        return any([self.m[y][x] is None and len(self.possible_values(x, y)) is 0 for x in range(DIMENSION) for y in range(DIMENSION)])

    def next_open_square(self):
        squares_by_moves = [((x, y), len(self.possible_values(x, y))) for x in range(DIMENSION) for y in range(DIMENSION) if self.m[y][x] is None]
        return sorted(squares_by_moves, key=lambda s: s[1])[0][0] if len(squares_by_moves) > 0 else None

    def possible_values(self, x, y):
        return [n for n in range(1, DIMENSION + 1) if self.is_valid_move(x, y, n)]

    def is_valid_move(self, x, y, n):
        return not self.is_in_row(y, n) and not self.is_in_column(x, n) and not self.is_in_sector(x, y, n)

    def is_in_row(self, y,  n):
        return any([val for val in self.m[y] if val is n])

    def is_in_column(self, x, n):
        return any([row for row in self.m if row[x] is n])

    def is_in_sector(self, x, y, n):
        sector_x_start = SECTOR_DIMENSION * math.floor(x / SECTOR_DIMENSION)
        sector_x_range = range(sector_x_start, sector_x_start + SECTOR_DIMENSION)
        sector_y_start = SECTOR_DIMENSION * math.floor(y / SECTOR_DIMENSION)
        sector_y_range = range(sector_y_start, sector_y_start + SECTOR_DIMENSION)
        return any([(sx, sy) for sx in sector_x_range for sy in sector_y_range if self.m[sy][sx] is n])

    def __str__(self):
        return '\n'.join([' '.join([str(contents) if contents else '-' for contents in row]) for row in self.m])


def backtrack(a, k, board):
    finished_flag.tick()
    if is_a_solution(a, k, board):
        process_solution(a, k, board)
    else:
        k = k + 1
        candidates = construct_candidates(a, k, board)
        for c in candidates:
            a[k] = c
            make_move(a, k, board)
            backtrack(a, k, board)
            unmake_move(a, k, board)
            if finished_flag.is_finished():
                return


def is_a_solution(a, k, board):
    return board.free_cells is 0


def process_solution(a, k, board):
    print(board)
    finished_flag.mark_finished()


def construct_candidates(a, k, board):
    next_move = board.next_open_square()
    if next_move is None or board.dead_end_exists():
        return []
    board.plan_move(k, next_move)
    return board.possible_values(next_move[0], next_move[1])


def make_move(a, k, board):
    move = board.moves[k]
    board.fill(move[0], move[1], a[k])


def unmake_move(a, k, board):
    move = board.moves[k]
    board.free(move[0], move[1])


def generate_solution(board):
    buffer = [0] * NCELLS
    backtrack(buffer, 0, board)

easy_board = Board()
easy_board.fill(1, 0, 8)
easy_board.fill(0, 1, 9)
easy_board.fill(1, 1, 3)
easy_board.fill(0, 2, 4)
easy_board.fill(4, 0, 7)
easy_board.fill(5, 0, 2)
easy_board.fill(3, 1, 4)
easy_board.fill(3, 2, 6)
easy_board.fill(4, 2, 1)
easy_board.fill(6, 0, 1)
easy_board.fill(7, 2, 5)
easy_board.fill(0, 3, 5)
easy_board.fill(1, 3, 6)
easy_board.fill(1, 5, 1)
easy_board.fill(3, 4, 3)
easy_board.fill(5, 4, 7)
easy_board.fill(7, 3, 8)
easy_board.fill(7, 5, 6)
easy_board.fill(8, 5, 2)
easy_board.fill(1, 6, 2)
easy_board.fill(2, 8, 3)
easy_board.fill(4, 6, 3)
easy_board.fill(5, 6, 9)
easy_board.fill(5, 7, 6)
easy_board.fill(3, 8, 8)
easy_board.fill(4, 8, 4)
easy_board.fill(8, 6, 1)
easy_board.fill(7, 7, 9)
easy_board.fill(8, 7, 8)
easy_board.fill(7, 8, 2)
print(easy_board)
generate_solution(easy_board)
print(finished_flag)