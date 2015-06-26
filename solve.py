import pprint
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
from PIL import Image
import cProfile

N = 20
RANGE = range(1, 5 + 1)

im = Image.open('canvas.png')
im = im.resize((N, 20))

data = list(im.getdata())

COLOR_MAP = {
    (153, 153, 153, 255): 0,
    (229, 70, 97, 255): 1,
    (255, 166, 68, 255): 2,
    (153, 138, 47, 255): 3,
    (44, 89, 79, 255): 4,
    (0, 45, 64, 255): 5,
}

class Board(object):

    def __init__(self, data=None):
        if data is None:
            return

        iter_data = iter(data)
        self.board = map(COLOR_MAP.get, data)
        self.frontier = set([(0, 0)])
        self.left = N * N - 1

    def clone(self):
        b = Board()
        b.board = self.board[:]
        b.frontier = self.frontier.copy()
        b.left = self.left
        return b

    def play(self, color):
        def _recur(x, y):
            pos = x * N + y
            if self.board[pos] != color:
                return 0
            self.board[pos] = 0
            new_frontier.add((x, y))
            self.left -= 1
            return  1 + (
                (x > 0 and _recur(x - 1, y)) +
                (x < N - 1 and _recur(x + 1, y)) +
                (y > 0 and _recur(x, y - 1)) +
                (y < N - 1 and _recur(x, y + 1))
            )

        new_frontier = set()
        flipped = 0
        for x, y in self.frontier:
            pos = x * N + y
            next_to_colored = 0
            if x > 0 and self.board[pos - N]:
                r = _recur(x - 1, y)
                flipped += r
                next_to_colored += not r
            if x < N - 1 and self.board[pos + N]:
                r = _recur(x + 1, y)
                flipped += r
                next_to_colored += not r
            if y > 0 and self.board[pos - 1]:
                r = _recur(x, y - 1)
                flipped += r
                next_to_colored += not r
            if y < N - 1 and self.board[pos + 1]:
                r = _recur(x, y + 1)
                flipped += r
                next_to_colored += not r
            if next_to_colored:
                new_frontier.add((x, y))
        self.frontier = new_frontier
        return flipped

    def debug(self):
        for i in xrange(N):
            for j in xrange(N):
                if self.board[i * N + j] == 0:
                    if (i, j) in self.frontier:
                        print '.',
                    else:
                        print ' ',
                else:
                    print self.board[i * N + j],
            print ''

    def hash(self):
        return str(self.board)


class PathGen(object):

    def __init__(self):
        self.paths = []

    def search(self, last_board, path):
        if len(path) == 12:
            self.paths.append( (last_board.left, path) )
            return

        plan = []
        for color in RANGE:
            board = last_board.clone()
            flipped = board.play(color)
            plan.append( (flipped, color, board) )

        plan.sort(reverse=True)

        for flipped, color, board in plan:
            new_path = path + [color]

            if flipped == 0:
                continue

            self.search(board, new_path)


class Tester(object):

    def __init__(self):
        self.min_length = 99
        self.cache = {}

        self.hits = 0
        self.misses = 0

    def search(self, last_board, path):
        if self.min_length < len(path) + 2:
            return None

        hx = last_board.hash()
        #print self.hits, self.misses
        if hx in self.cache:
            self.hits += 1
            return self.cache[hx]
        else:
            self.misses += 1

        stat = "           %-120s" % str(path)
        sys.stdout.write(stat)
        plan = []
        r = RANGE[:]
        if path:
            r.remove(path[-1])
        for color in r:
            board = last_board.clone()
            flipped = board.play(color)
            plan.append( (flipped, color, board) )

        plan.sort(reverse=True)
        sys.stdout.write('\b' * 131)

        min_path = None

        for flipped, color, board in plan:
            new_path = path + [color]

            if flipped == 0:
                continue

            if board.left == 0:
                to_add = [color]

                if self.min_length > len(new_path):
                    self.min_length = len(new_path)
                print "SO FAR:", self.min_length, new_path
                #if self.min_length == 24:
                #    sys.exit(1)
                break
            else:
                to_add = self.search(board, new_path)
                if to_add is None:
                    continue

            if min_path is None or len(min_path) > len(to_add):
                min_path = to_add

        self.cache[hx] = min_path
        return min_path

board = Board(data)

#path = Tester().search(board, [])
#cProfile.run('Tester().search(board, [])')

path_gen = PathGen()
path_gen.search(board, [])

paths = path_gen.paths
paths.sort()

for left, path in paths:
    print ' ' * 140 + '\b' * 140
    print 'Attempt: %d left' % (left,)
    new_board = board.clone()
    for leg in path:
        new_board.play(leg)
    min_path = Tester().search(new_board, path)
