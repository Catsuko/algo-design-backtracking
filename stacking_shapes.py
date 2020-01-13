# TODO: Small optimizations by using sets instead of arrays when dealing with collections of points,
#       then point lookup can be done in constant time
from functools import reduce


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


class CompositeShape:

    def __init__(self, shapes=[]):
        self.shapes = shapes

    def add(self, shape):
        if self.overlaps(shape):
            raise Exception("Cannot add shape, it overlaps an existing shape.")
        return CompositeShape(self.shapes + [shape])

    def move(self, x, y):
        return self.__on_shapes(lambda shape: shape.move(x, y))

    def rotate(self):
        return self.__on_shapes(lambda shape: shape.rotate())

    def flip(self):
        return self.__on_shapes(lambda shape: shape.flip())

    def includes(self, x, y):
        return any([shape.includes(x, y) for shape in self.shapes])

    def overlaps(self, other):
        return any([shape.overlaps(other) for shape in self.shapes])

    def fits_in(self, other):
        return all([shape.fits_in(other) for shape in self.shapes])

    def clip_with(self, other_shape):
        return reduce(lambda points, shape: points + shape.clip_with(other_shape), self.shapes, [])

    def to_map(self):
        point_map = {}
        for shape in self.shapes:
            point_map.update(shape.to_map())
        return point_map

    def area(self):
        return reduce(lambda total, shape: total + shape.area(), self.shapes, 0)

    def __on_shapes(self, delegate):
        return CompositeShape([delegate(shape) for shape in self.shapes])

    def __str__(self):
        return "Composite Shape (made of %d shapes)" % len(self.shapes)


class Shape:

    def __init__(self, points, key, x=0, y=0):
        self.points = points
        self.key = key
        self.x = x
        self.y = y

    def move(self, x, y):
        return Shape(self.points, self.key, x, y)

    def rotate(self):
        return self.__with_points([(y, -x) for x, y in self.points])

    def flip(self):
        return self.__with_points([(x, -y) for x, y in self.points])

    def includes(self, x, y):
        return (x, y) in self.__world_points()

    def overlaps(self, other):
        return any([other.includes(x, y) for x, y in self.__world_points()])

    def fits_in(self, other):
        return len(self.clip_with(other)) is 0

    def clip_with(self, other_shape):
        return [(x, y) for x, y in self.__world_points() if not other_shape.includes(x, y)]

    def to_map(self):
        point_map = {}
        for point in self.__world_points():
            point_map[point] = self.key
        return point_map

    def area(self):
        return len(self.points)

    def orientations(self):
        flipped_and_rotated = [self]
        for _ in range(3):
            flipped_and_rotated.append(flipped_and_rotated[len(flipped_and_rotated)-1].rotate())
        flipped_and_rotated.append(self.flip())
        for _ in range(3):
            flipped_and_rotated.append(flipped_and_rotated[len(flipped_and_rotated) - 1].rotate())
        unique = []
        for orientation in flipped_and_rotated:
            if not any([o.same_structure(orientation) for o in unique]):
                unique.append(orientation)
        return unique

    def __world_points(self):
        return [(self.x + x, self.y + y) for x, y in self.points]

    def __with_points(self, points):
        return Shape(points, self.key, self.x, self.y)

    def same_structure(self, other):
        moved_other = other.move(self.x, self.y)
        return all([moved_other.includes(x, y) for x, y in self.points])

    def matches(self, other):
        return other.key == self.key

    def __str__(self):
        return "Shape %s at %s (Area: %d)" % (self.key, (self.x, self.y), self.area())


class Board:

    def __init__(self, placed_pieces, bounds):
        self.placed_pieces = placed_pieces
        self.bounds = bounds

    def add(self, shape):
        if not shape.fits_in(self.bounds):
            raise Exception("Cannot add shape, it exceeds the bounds of the Puzzle.")
        return Board(self.placed_pieces.add(shape), self.bounds)

    def can_hold(self, shape):
        return shape.fits_in(self.bounds) and not shape.overlaps(self.placed_pieces)

    def is_full(self):
        return len(self.open_points()) is 0

    def open_points(self):
        return self.bounds.clip_with(self.placed_pieces)

    def __str__(self):
        point_map = self.bounds.to_map()
        point_map.update(self.placed_pieces.to_map())
        x_coords = [point[0] for point in point_map.keys()]
        y_coords = [point[1] for point in point_map.keys()]
        x_min = min(x_coords)
        x_max = max(x_coords)
        y_min = min(y_coords)
        y_max = max(y_coords)
        contents_str = ''
        for y in range(y_min, y_max + 1):
            for x in range(x_min, x_max + 1):
                contents_str = contents_str + (str(point_map[(x, y)]) if (x, y) in point_map else ' ')
            contents_str = contents_str + '\n'
        return contents_str


def smallest_continuous_area(points):
    smallest = len(points)
    points_to_check = points.copy()
    while len(points_to_check) > 0:
        connected = []
        fill_connected(points_to_check[0], connected, points)
        smallest = min(smallest, len(connected))
        [points_to_check.remove(p) for p in connected if p in points_to_check]
    return smallest


def fill_connected(p, connected, points):
    connected.append(p)
    neighbours = [(x, y) for x, y in points if abs(x - p[0]) + abs(y - p[1]) == 1]
    for n in neighbours:
        if n not in connected:
            fill_connected(n, connected, points)


def backtrack(available_pieces, board, finished_flag):
    print(board)
    finished_flag.tick()
    if board.is_full():
        finished_flag.mark_finished()
        print(board)
        print(finished_flag)
    else:
        candidates = construct_candidates(available_pieces, board)
        for c in candidates:
            next_pieces = [piece for piece in available_pieces if not c.matches(piece)]
            backtrack(next_pieces, board.add(c), finished_flag)
            if finished_flag.is_finished():
                return


def construct_candidates(available_pieces, board):
    open_points = board.open_points()
    smallest_area = smallest_continuous_area(board.open_points())
    pieces_by_size = sorted(available_pieces, key=lambda shape: -shape.area())
    if len(available_pieces) > 0 and pieces_by_size[len(pieces_by_size) - 1].area() <= smallest_area:
        largest_piece = pieces_by_size[0]
        arrangements = []
        for oriented_piece in largest_piece.orientations():
            for x, y in open_points:
                moved_piece = oriented_piece.move(x, y)
                if board.can_hold(moved_piece):
                    arrangements.append(moved_piece)
        return arrangements
    return []


poodle = Shape([(0, 0), (1, 0), (0, 1), (1, 1)], "b")
sausage_dog = Shape([(0, 0), (0, 1), (1, 1), (2, 1)], "d")
big_red = Shape([(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (2, 2)], "R")
lab = Shape([(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (2, 2), (3, 2)], "Y")
little_grey_dog = Shape([(0, 0), (0, 1)], "g")
bulldog = Shape([(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1)], "G")
long_green = Shape([(0, 0), (0, 1), (0, 2)], "l")
big_pink = Shape([(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1)], "P")
big_blue = Shape([(0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (2, 1), (2, 2), (3, 0), (3, 1), (3, 2)], "B")
little_mag = Shape([(0, 0), (1, 0), (1, 1)], "m")
big_violet = Shape([(0, 0), (0, 1), (1, 1), (2, 0), (2, 1), (2, 2), (3, 2)], "V")
corgi = Shape([(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 1)], "C")

# Puzzle - 1
# dogs_to_use = [big_red, lab, little_mag, little_grey_dog]
# board_bounds = Shape([(x, y) for x in range(5) for y in range(4)], ".")

# Puzzle - 2
# dogs_to_use = [big_red, bulldog, poodle, long_green, little_grey_dog]
# lhs = [(x, y) for x in range(2) for y in range(5)]
# rhs = [(x + 3, y) for x, y in lhs]
# center = [(2, 0), (2, 1), (2, 3), (2, 4)]
# board_bounds = Shape(lhs + rhs + center, '.')

# Puzzle - 3
# dogs_to_use = [sausage_dog, big_red, lab, little_grey_dog, poodle]
# board_bounds = Shape([(x, y) for x in range(5) for y in range(5)], '.')

# Puzzle - 4
# dogs_to_use = [big_red, bulldog, big_blue, sausage_dog, little_grey_dog, poodle]
# board_bounds = Shape([(x, y) for x in range(6) for y in range(6)], '.')

# Puzzle - 5
# dogs_to_use = [big_pink, sausage_dog, big_red, little_mag, long_green, poodle, little_grey_dog]
# lhs = [(x, y) for x in range(2) for y in range(7)]
# rhs = [(x + 4, y) for x, y in lhs]
# center = [(2, 0), (3, 0), (2, 6), (3, 6)]
# board_bounds = Shape(lhs + rhs + center, '.')

# Puzzle - 6
# dogs_to_use = [sausage_dog, bulldog, lab, big_violet, little_grey_dog, big_red, corgi]
# board_bounds = Shape([(x, y) for x in range(6) for y in range(7)], ".")

# Puzzle - 7
# lhs = [(x, y) for x in range(2) for y in range(7)]
# rhs = [(x + 5, y) for x, y in lhs]
# bottom = [(x + 2, y) for x in range(3) for y in range(2)]
# top = [(x, y + 5) for x, y in bottom]
# board_bounds = Shape(lhs + rhs + top + bottom, '.')
# dogs_to_use = [big_red, bulldog, little_mag, big_pink, little_grey_dog, lab, long_green]

# Puzzle - 8
center = [(x + 1, y + 1) for x in range(5) for y in range(7)]
v_edges = [(1, 0), (2, 0), (4, 0), (5, 0), (1, 8), (2, 8), (4, 8), (5, 8)]
h_edges = [(0, 2), (0, 3), (0, 5), (0, 6), (6, 2), (6, 3), (6, 5), (6, 6)]
board_bounds = Shape(center + v_edges + h_edges, ".")
dogs_to_use = [bulldog, lab, big_violet, big_pink, big_red, sausage_dog, little_mag, long_green, little_grey_dog]

# Puzzle - 11
# bottom = [(x, y) for x in range(7) for y in range(3)]
# top = [(x+2, y+3) for x in range(3) for y in range(2)]
# edges = [(1, 3), (2, 4), (3, 5), (4, 4), (5, 3)]
# board_bounds = Shape(bottom + top + edges, '.')
# dogs_to_use = [lab, little_grey_dog, big_red, corgi, sausage_dog, long_green]

# Puzzle - 12
# bottom = [(x, y) for x in range(6) for y in range(2)]
# middle = [(x, y+3) for x, y in bottom]
# top = [(x, y+3) for x, y in middle]
# edges = [(0, 2), (2, 2), (3, 2), (5, 2), (0, 5), (2, 5), (3, 5), (5, 5)]
# board_bounds = Shape(bottom + middle + top + edges, '.')
# dogs_to_use = [lab, little_mag, big_pink, poodle, big_red, bulldog, long_green, little_grey_dog]

# Puzzle - 13
# board_bounds = Shape([(x, y) for x in range(5) for y in range(11)], '.')
# dogs_to_use = [big_red, long_green, little_mag, big_blue, poodle, big_pink, corgi, lab, sausage_dog]

# Find the solution!
backtrack(dogs_to_use, Board(CompositeShape(), board_bounds), FinishedFlag())
