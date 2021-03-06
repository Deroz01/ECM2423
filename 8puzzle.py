import numpy
from collections import deque

from copy import deepcopy
    
def empty_board():
    return numpy.zeros((3,3), dtype=int)

def initialise_board(top_left, top_mid, top_right, mid_left, mid_mid, mid_right, bottom_left, bottom_mid, bottom_right, dtype=[]):
    board = empty_board()
    board[0][0] = top_left
    board[0][1] = top_mid
    board[0][2] = top_right
    board[1][0] = mid_left
    board[1][1] = mid_mid
    board[1][2] = mid_right
    board[2][0] = bottom_left
    board[2][1] = bottom_mid
    board[2][2] = bottom_right
    return board

def goal_board():
    board = empty_board()
    for i in range(3):
        for j in range(3):
            board[i][j] = 3*i + j
    return board

def tile_pos(board, tile):
    pos = []
    for i in range(3):
        for j in range(3):
            if (board[i][j] == tile):
                pos = [i, j]
    return pos

def misplaced_tiles(current, goal=goal_board()):
    count = 0
    for i in range(3):
        for j in range(3):
            tile = board[i][j]
            if tile != goal_board()[i][j] and tile != 0:
                count += 1
    return count

def manhattan_to_goal_position(board, tile, goal=goal_board()):
    goal_x = tile_pos(goal, tile)[1]
    goal_y = tile_pos(goal, tile)[0]
    pos = tile_pos(board, tile)
    pos_x = pos[1]
    pos_y = pos[0]
    return abs((goal_x-pos_x)) + abs((goal_y-pos_y))

def sum_manhattan(board, goal=goal_board()):
    count = 0
    for tile in range(1, 9):
        count += manhattan_to_goal_position(board, tile, goal)
    return count

def out_of_position(board, tile, goal=goal_board()):
    out_of_col = 0
    out_of_row = 0
    goal_x = tile_pos(goal, tile)[1]
    goal_y = tile_pos(goal, tile)[0]
    pos = tile_pos(board, tile)
    pos_x = pos[1]
    pos_y = pos[0]
    if pos_x != goal_x: out_of_row = 1
    if pos_y != goal_y: out_of_col = 1
    return out_of_row + out_of_col

def sum_out_of_position(board, goal=goal_board()):
    count = 0
    for tile in range(9):
        count += out_of_position(board, tile, goal)
    return count

def copy(board):
    return deepcopy(board)

def possible_moves(board):
    zero_pos = tile_pos(board, 0)
    zero_pos_x, zero_pos_y = zero_pos[1], zero_pos[0]
    moves = []
    if zero_pos_x < 2:
        new_board = copy(board)
        new_board[zero_pos_y][zero_pos_x] = new_board[zero_pos_y][zero_pos_x+1]
        new_board[zero_pos_y][zero_pos_x+1] = 0
        moves.append(new_board)
    if zero_pos_x > 0:
        new_board = copy(board)
        new_board[zero_pos_y][zero_pos_x] = new_board[zero_pos_y][zero_pos_x-1]
        new_board[zero_pos_y][zero_pos_x-1] = 0
        moves.append(new_board)
    if zero_pos_y < 2:
        new_board = copy(board)
        new_board[zero_pos_y][zero_pos_x] = new_board[zero_pos_y+1][zero_pos_x]
        new_board[zero_pos_y+1][zero_pos_x] = 0
        moves.append(new_board)
    if zero_pos_y > 0:
        new_board = copy(board)
        new_board[zero_pos_y][zero_pos_x] = new_board[zero_pos_y-1][zero_pos_x]
        new_board[zero_pos_y-1][zero_pos_x] = 0
        moves.append(new_board)

    return moves

def make_move(board, move):
    zero_pos = tile_pos(board, 0)
    zero_pos_x, zero_pos_y = zero_pos[1], zero_pos[0]
    new_board = copy(board)
    if move == "UP":
        new_board[zero_pos_y][zero_pos_x] = new_board[zero_pos_y-1][zero_pos_x]
        new_board[zero_pos_y-1][zero_pos_x] = 0
    if move == "DOWN":
        new_board[zero_pos_y][zero_pos_x] = new_board[zero_pos_y+1][zero_pos_x]
        new_board[zero_pos_y+1][zero_pos_x] = 0
    if move == "LEFT":
        new_board[zero_pos_y][zero_pos_x] = new_board[zero_pos_y][zero_pos_x-1]
        new_board[zero_pos_y][zero_pos_x-1] = 0
    if move == "RIGHT":
        new_board[zero_pos_y][zero_pos_x] = new_board[zero_pos_y][zero_pos_x+1]
        new_board[zero_pos_y][zero_pos_x+1] = 0

    return new_board

    

class Puzzle:
    def __init__(self, board, g_cost, previous):
        self.board = board
        self.g_cost = g_cost
        self.previous = previous
        self.children = []
    def generateChildren(self):
        for mv in possible_moves(self.board):
            self.children.append(Puzzle(mv, self.g_cost+1, self))

    def previousPuzzles(self):
        puzzles = [self]
        curr = self
        while curr.previous is not None:
            curr = curr.previous
            puzzles.append(curr)
        return puzzles

    def __eq__(self, other):
        if type(other) == Puzzle:
            return str(self.board) == str(other.board)
        if type(other) == numpy.ndarray:
            return str(self.board) == str(other)
class Solver:
    def __init__(self, start, goal, heuristic='MANHATTAN'):
        self.start = start
        self.goal = goal
        self.heuristic = heuristic
        self.open = []
        self.closed = []

    def f_cost(self, current):
        f = self.h_cost(current) + current.g_cost
        return f

    def h_cost(self, current):
        h_val = 0
        if self.heuristic == 'OUT_OF_POSITION':
            h_val = sum_out_of_position(current.board)
        else:
            h_val = sum_manhattan(current.board)
        return h_val
    
    def process(self):
        """
        set current to be the board with the lowest f cost. at the start this will be the starting puzzle
        remove it from the open list and add to close list
        if this is the goal then stop here
        generate all children from the current node and add to the open list if not already or in the closed list
        sort by f cost, then h cost and repeat
        """
        self.open.append(self.start)
        i = 0
        while True:
            current = self.open[0]
            self.open.pop(0)
            self.closed.append(current)
            
            if current == self.goal:
                print("goal reached at iteration:", i)
                print("f cost of goal:", self.f_cost(current))
                return

            current.generateChildren()
            for child in current.children:
                if child in self.closed: continue
                if child not in self.open:
                    self.open.append(child)
            self.open.sort(key=lambda puzzle: (self.f_cost(puzzle), self.h_cost(puzzle)), reverse=False) #finds a solution easily, albeit a much longer f_cost, when i sort it by h_cost then f_cost but not the other way round
            #print("iteration:", i)
            i += 1

#######################


start_grid = initialise_board(7,2,4,5,0,6,8,3,1)
goal = goal_board()

puzzle = Puzzle(start_grid, 0, None)
mh_solver = Solver(puzzle, goal, heuristic='MANHATTAN')
mh_solver.process()
