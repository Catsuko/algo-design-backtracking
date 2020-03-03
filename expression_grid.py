import math
import random


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


class SudokuExpression:

    def __init__(self, rows, columns, placements=[]):
        self.rows = rows
        self.columns = columns
        self.placements = placements

    # TODO: Prioritise expressions with division over others.
    def first_empty_slot(self):
        return [n for n in range(9) if n not in self.placements][0]

    def add_number(self, n, i):
        if 1 > n > 9:
            raise ValueError("%d is not a valid number, must be between 1-9" % n)
        row_count = len(self.rows)
        col_count = len(self.columns)
        x = math.floor(i / float(row_count))
        y = i % col_count
        rows = [self.rows[x].add_number(n, y) if row_x == x else self.rows[row_x] for row_x in range(row_count)]
        cols = [self.columns[y].add_number(n, x) if col_y == y else self.columns[col_y] for col_y in range(col_count)]
        return SudokuExpression(rows, cols, self.placements + [i])

    def print_all_expressions(self):
        for exp in self.rows:
            print(repr(exp))
        for exp in self.columns:
            print(repr(exp))

    def invalid(self):
        results = [exp.invalid() for exp in self.rows] + [exp.invalid() for exp in self.columns]
        return any(results)

    def __repr__(self):
        lines = []
        row_count = len(self.rows)
        columns = [str(column) for column in self.columns]
        for y in range(row_count):
            lines.append(str(self.rows[y]))
            if y < row_count - 1:
                lines.append(''.join([columns[math.floor(i/2.0)][2*(y+1)-1] if i % 2 == 0 else ' ' for i in range(row_count*2-1)]))
        return '\n' + '\n'.join(lines) + '\n'


class Expression:

    def __init__(self, numbers, operators, result):
        self.numbers = numbers
        self.operators = operators
        self.result = result

    @classmethod
    def unfilled(cls, operators, result):
        return cls([None] * 3, operators, result)

    def priority(self):
        return sum([ord(operator) for operator in self.operators])

    def open_indices(self):
        return [i for i in range(len(self.numbers)) if self.numbers[i] is None]

    def add_number(self, n, i):
        updated_numbers = [n if j == i else self.numbers[j] for j in range(len(self.numbers))]
        return Expression(updated_numbers, self.operators, self.result)

    def invalid(self):
        return self.__check_invalid_division(0) or \
               self.__check_invalid_division(1) or \
               (self.__has_all_numbers() and eval(str(self)) != self.result)

    def __has_all_numbers(self):
        return all([n is not None for n in self.numbers])

    def __check_invalid_division(self, operator_index):
        return self.operators[operator_index] == '/' and \
               (self.numbers[operator_index] in [1, 2, 3, 5, 7] or self.numbers[operator_index+1] in [5, 6, 7, 8, 9])

    def __str__(self):
        numbers_length = len(self.numbers)
        operators_length = len(self.operators)
        tokens = [None] * (numbers_length + operators_length)
        for i in range(numbers_length):
            tokens[2*i] = '_' if self.numbers[i] is None else str(self.numbers[i])
        for i in range(operators_length):
            tokens[2*(i+1)-1] = self.operators[i]
        return "".join(tokens)

    def __repr__(self):
        return "%s = %d (%s)" % (str(self), self.result, "Invalid" if self.invalid() else "Valid")


def backtrack(available_numbers, puzzle, finished_flag):
    print(puzzle)
    finished_flag.tick()
    if len(available_numbers) == 0 and not puzzle.invalid():
        finished_flag.mark_finished()
        print(puzzle)
        print(finished_flag)
        puzzle.print_all_expressions()
    else:
        candidates = construct_candidates(available_numbers, puzzle)
        for c in candidates:
            next_nums = [num for num in available_numbers if not c == num]
            backtrack(next_nums, puzzle.add_number(c, puzzle.first_empty_slot()), finished_flag)
            if finished_flag.is_finished():
                return


# TODO: Is there a way an unfilled expression could give possible candidates?
def construct_candidates(available_numbers, puzzle):
    return [] if puzzle.invalid() else sorted(available_numbers, reverse=True)


easy_puzzle = SudokuExpression(
    [
        Expression.unfilled(['/', '-'], 2),
        Expression.unfilled(['+', '-'], 7),
        Expression.unfilled(['*', '+'], 13),
    ],
    [
        Expression.unfilled(['*', '/'], 18),
        Expression.unfilled(['+', '/'], 6),
        Expression.unfilled(['*', '-'], 2)
    ]
)
second_easy_puzzle = SudokuExpression(
    [
        Expression.unfilled(['+', '/'], 11),
        Expression.unfilled(['/', '-'], 1),
        Expression.unfilled(['-', '*'], -33)
    ],
    [
        Expression.unfilled(['*', '/'], 36),
        Expression.unfilled(['+', '-'], 5),
        Expression.unfilled(['*', '+'], 10),
    ]
)

# EASY PUZZLE
# Naive score: 2046
# Sort candidates so largest is first: 63
# Invalid if dividing a prime number: 59
# Invalid if dividing by a number larger than 5: 31

# SECOND EASY PUZZLE
# Invalid if dividing by a number larger than 5: 60
backtrack([n+1 for n in range(9)], easy_puzzle, FinishedFlag())
