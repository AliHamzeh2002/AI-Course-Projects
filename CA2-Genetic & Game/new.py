import random
import time
import turtle
import math
import pprint
from copy import deepcopy

class OthelloUI:
    def __init__(self, board_size=6, square_size=60):
        self.board_size = board_size
        self.square_size = square_size
        self.screen = turtle.Screen()
        self.screen.setup(self.board_size * self.square_size + 50, self.board_size * self.square_size + 50)
        self.screen.bgcolor('white')
        self.screen.title('Othello')
        self.pen = turtle.Turtle()
        self.pen.hideturtle()
        self.pen.speed(0)
        turtle.tracer(0, 0)

    def draw_board(self, board):
        self.pen.penup()
        x, y = -self.board_size / 2 * self.square_size, self.board_size / 2 * self.square_size
        for i in range(self.board_size):
            self.pen.penup()
            for j in range(self.board_size):
                self.pen.goto(x + j * self.square_size, y - i * self.square_size)
                self.pen.pendown()
                self.pen.fillcolor('green')
                self.pen.begin_fill()
                self.pen.setheading(0)
                for _ in range(4):
                    self.pen.forward(self.square_size)
                    self.pen.right(90)
                self.pen.penup()
                self.pen.end_fill()
                self.pen.goto(x + j * self.square_size + self.square_size / 2,
                              y - i * self.square_size - self.square_size + 5)
                if board[i][j] == 1:
                    self.pen.fillcolor('white')
                    self.pen.begin_fill()
                    self.pen.circle(self.square_size / 2 - 5)
                    self.pen.end_fill()
                elif board[i][j] == -1:
                    self.pen.fillcolor('black')
                    self.pen.begin_fill()
                    self.pen.circle(self.square_size / 2 - 5)
                    self.pen.end_fill()

        turtle.update()


BOARD_SIZE = 6

class Board:
    def __init__(self, size):
        self.size = size
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.board[int(self.size / 2) - 1][int(self.size / 2) - 1] = self.board[int(self.size / 2)][
            int(self.size / 2)] = 1
        self.board[int(self.size / 2) - 1][int(self.size / 2)] = self.board[int(self.size / 2)][
            int(self.size / 2) - 1] = -1
    
    def get_map(self):
        return self.board.copy()
        
    def get_valid_moves(self, player):
        moves = set()
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            x, y = i, j
                            captured = []
                            while 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][
                                    y + dj] == -player:
                                captured.append((x + di, y + dj))
                                x += di
                                y += dj
                            if 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][
                                    y + dj] == player and len(captured) > 0:
                                moves.add((i, j))
        return list(moves)
    
    def make_move(self, player, move):
        i, j = move
        self.board[i][j] = player
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                x, y = i, j
                captured = []
                while 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][y + dj] == -player:
                    captured.append((x + di, y + dj))
                    x += di
                    y += dj
                if 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][y + dj] == player:
                    for (cx, cy) in captured:
                        self.board[cx][cy] = player
    
    def get_winner(self):
        white_count = self.count_coins(1)
        black_count = self.count_coins(-1)
        if white_count > black_count:
            return 1
        elif white_count < black_count:
            return -1
        else:
            return 0
                        
    def terminal_test(self):
        return len(self.get_valid_moves(1)) == 0 and len(self.get_valid_moves(-1)) == 0
    
    def count_coins(self, player):
        return sum([row.count(player) for row in self.board])
    
    def count_corner_coins(self, player):
        corner_coins = 0
        for i in [0, self.size - 1]:
            for j in [0, self.size - 1]:
                if self.board[i][j] == player:
                    corner_coins += 1
        return corner_coins
    
class Othello:
    def __init__(self, ui, minimax_depth=1, prune=True):
        self.size = BOARD_SIZE
        self.board = Board(self.size) 
        self.ui = OthelloUI(self.size) if ui else None
        self.current_turn = random.choice([1, -1])
        self.ai_agent = AI(1, minimax_depth, prune)
        
    def get_cpu_move(self):
        moves = self.board.get_valid_moves(-1)
        if len(moves) == 0:
            return None
        return random.choice(moves)

    def get_human_move(self):
        return self.ai_agent.get_move(deepcopy(self.board))
        
    def play(self):
        winner = None
        while not self.board.terminal_test():
            if self.ui:
                self.ui.draw_board(self.board.get_map())
            if self.current_turn == 1:
                move = self.get_human_move()
                if move:
                    self.board.make_move(self.current_turn, move)
            else:
                move = self.get_cpu_move()
                if move:
                    self.board.make_move(self.current_turn, move)
            self.current_turn = -self.current_turn
            if self.ui:
                self.ui.draw_board(self.board.get_map())
                time.sleep(1)
        winner = self.board.get_winner()
        return winner
    
class AI:
    def __init__(self, player, minimax_depth, prune):
        self.player = player
        self.minimax_depth = minimax_depth
        self.prune = prune
        self.visited_nodes = 0
        
    def end_match_evaluate(self, board):
        winner = board.get_winner()
        if winner == self.player:
            return 1000
        elif winner == -self.player:
            return -1000
        else:
            return 0
        
    def evaluate(self, board):            
        return  5 * self.calc_corner_heuristic(board) + 2 * self.calc_coins_heuristic(board) 
    
    def calc_mobility_heuristic(self, board):
        player_moves = len(board.get_valid_moves(self.player))
        enemy_moves = len(board.get_valid_moves(-self.player))
        if enemy_moves + player_moves == 0:
            return 0
        return (player_moves - enemy_moves) / (player_moves + enemy_moves)
    
    def calc_coins_heuristic(self, board):
        player_coins = board.count_coins(self.player)
        enemy_coins = board.count_coins(-self.player)
        return (player_coins - enemy_coins) / (player_coins + enemy_coins)
    
    def calc_corner_heuristic(self, board):
        player_corners = board.count_corner_coins(self.player)
        enemy_corners = board.count_corner_coins(-self.player)
        if enemy_corners + player_corners == 0:
            return 0
        return (player_corners - enemy_corners) / (player_corners + enemy_corners)
        
    def max_value(self, cur_board, cur_depth = 0, alpha = -math.inf, beta = math.inf, visited_nodes = 1, prev_no_move = 0):
        if cur_depth == self.minimax_depth:
            return None, self.evaluate(cur_board), visited_nodes
        valid_moves = cur_board.get_valid_moves(self.player)
        if len(valid_moves) == 0:
            if prev_no_move:
                return None, self.end_match_evaluate(cur_board), visited_nodes
            return self.min_value(cur_board, cur_depth + 1, alpha, beta, visited_nodes + 1, 1)
        best_move = None
        best_point = -math.inf
        for move in valid_moves:
            new_board = deepcopy(cur_board)
            new_board.make_move(self.player, move)
            next_move, point, visited_nodes = self.min_value(new_board, cur_depth + 1, alpha, beta, visited_nodes + 1)
            if best_point < point:
                best_point = point
                best_move = move
            if self.prune:
                if best_point >= beta:
                    return best_move, best_point, visited_nodes
                alpha = max(alpha, best_point) 
        return best_move, best_point, visited_nodes
            
    def min_value(self, cur_board, cur_depth = 0, alpha = -math.inf, beta = math.inf, visited_nodes = 1, prev_no_move = 0):
        if cur_depth == self.minimax_depth:
            return None, self.evaluate(cur_board), visited_nodes
        valid_moves = cur_board.get_valid_moves(-self.player)
        if len(valid_moves) == 0:
            if prev_no_move:
                return None, self.end_match_evaluate(cur_board), visited_nodes
            return self.max_value(cur_board, cur_depth + 1, alpha, beta, visited_nodes + 1, 1)
        best_move = None
        best_point = math.inf
        for move in valid_moves:
            new_board = deepcopy(cur_board)
            new_board.make_move(-self.player, move)
            next_move, point, visited_nodes = self.max_value(new_board, cur_depth + 1, alpha, beta, visited_nodes + 1)
            if best_point > point:
                best_point = point
                best_move = move
            if self.prune:
                if best_point <= alpha:
                    return best_move, best_point, visited_nodes
                beta = min(beta, best_point) 
        return best_move, best_point, visited_nodes
        
    def get_move(self, cur_board):
        best_move, point, visited_nodes = self.max_value(cur_board)
        self.visited_nodes += visited_nodes
        return best_move
 
game = Othello(ui = 1, minimax_depth = 3, prune = 1)
game.play()
# wins = 0
# visited_nodes = 0
# REPEAT = 150
# for i in range(REPEAT):        
#     game = Othello(ui = 0, minimax_depth = 5, prune = 1)
#     s = game.play()
#     visited_nodes += game.ai_agent.get_mean_visited_nodes()
#     #print(s)
#     if s == 1:
#         wins += 1
#     print(f"wins:{wins * 100 / (i+1)}% losses = {i + 1 - wins}, game:{i + 1}")
# print(f"mean visited moves:{visited_nodes / REPEAT} per game")
    


