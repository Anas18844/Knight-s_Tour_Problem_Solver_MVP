import time
from typing import List, Tuple
from .level1_ordered import OrderedKnightWalk


class PureBacktracking(OrderedKnightWalk):

    def __init__(self, n: int, level: int = 2):
        super().__init__(n=n, level=level)
        self.backtrack_count = 0
        self.recursive_calls = 0

    def solve(self, start_x: int, start_y: int) -> Tuple[bool, List[Tuple[int, int]]]:
        self.board = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        self.path = []
        self.total_moves = 0
        self.dead_ends_hit = 0
        self.backtrack_count = 0
        self.recursive_calls = 0

        if not self.is_valid_position(start_x, start_y):
            return False, []

        success = self._backtrack(start_x, start_y, 0)
        return success, self.path.copy()

    def _backtrack(self, x: int, y: int, move_count: int) -> bool:
        self.recursive_calls += 1

        self.board[x][y] = move_count
        self.path.append((x, y))

        if move_count == self.n * self.n - 1:
            return True

        valid_moves = self.get_valid_moves(x, y)

        for next_x, next_y in valid_moves:
            if self._backtrack(next_x, next_y, move_count + 1):
                return True

        self.backtrack_count += 1
        self.board[x][y] = -1
        self.path.pop()
        return False
