import random
from typing import List, Tuple

class RandomKnightWalk:
    KNIGHT_MOVES = [(-2, -1),(-2, 1),(-1, -2),(-1, 2),(1, -2),(1, 2),(2, -1),(2, 1)]

    def __init__(self, n: int, level: int = 0):
        self.n = n
        self.level = level
        self.board: List[List[int]] = [[-1 for _ in range(n)] for _ in range(n)]
        self.path: List[Tuple[int, int]] = []
        self.total_moves = 0
        self.dead_ends_hit = 0

    def is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.n and 0 <= y < self.n

    def is_unvisited(self, x: int, y: int) -> bool:
        return self.board[x][y] == -1

    def get_valid_moves(self, x: int, y: int) -> List[Tuple[int, int]]:
        valid_moves = []
        for dx, dy in self.KNIGHT_MOVES:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_position(next_x, next_y) and self.is_unvisited(next_x, next_y):
                valid_moves.append((next_x, next_y))
        return valid_moves

    def select_move(self, valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        random.shuffle(valid_moves)
        return valid_moves[0]

    def random_walk(self, start_x: int, start_y: int) -> bool:
        current_x, current_y = start_x, start_y
        move_number = 0
        self.board[current_x][current_y] = move_number
        self.path.append((current_x, current_y))
        self.total_moves += 1
        target_moves = self.n * self.n

        while move_number < target_moves - 1:
            valid_moves = self.get_valid_moves(current_x, current_y)
            if not valid_moves:
                self.dead_ends_hit += 1
                return False
            next_x, next_y = self.select_move(valid_moves)
            current_x, current_y = next_x, next_y
            move_number += 1
            self.board[current_x][current_y] = move_number
            self.path.append((current_x, current_y))
            self.total_moves += 1
        return True

    def solve(self, start_x: int, start_y: int) -> Tuple[bool, List[Tuple[int, int]]]:
        self.board = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        self.path = []
        self.total_moves = 0
        self.dead_ends_hit = 0
        if not self.is_valid_position(start_x, start_y):
            return False, []
        success = self.random_walk(start_x, start_y)
        return success, self.path.copy()

    def get_stats(self) -> dict:
        return {
            'total_moves': self.total_moves,
            'dead_ends_hit': self.dead_ends_hit,
            'coverage_percent': 100 * len(self.path) / (self.n * self.n) if self.n > 0 else 0,
            'board_size': self.n
        }
