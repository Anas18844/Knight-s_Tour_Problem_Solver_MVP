from typing import List, Tuple
from .level2_backtracking import PureBacktracking


class EnhancedBacktracking(PureBacktracking):

    def __init__(self, n: int, level: int = 3):
        super().__init__(n=n, level=level)

    def _get_degree(self, x: int, y: int) -> int:
        count = 0
        for dx, dy in self.KNIGHT_MOVES:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_position(next_x, next_y) and self.is_unvisited(next_x, next_y):
                count += 1
        return count

    def _has_isolated_neighbor(self, x: int, y: int) -> bool:
        temp_board_state = self.board[x][y]
        self.board[x][y] = 999

        for dx, dy in self.KNIGHT_MOVES:
            nx, ny = x + dx, y + dy
            if self.is_valid_position(nx, ny) and self.is_unvisited(nx, ny):
                if self._get_degree(nx, ny) == 0:
                    self.board[x][y] = temp_board_state
                    return True

        self.board[x][y] = temp_board_state
        return False

    def _backtrack(self, x: int, y: int, move_count: int) -> bool:
        self.recursive_calls += 1

        self.board[x][y] = move_count
        self.path.append((x, y))

        if move_count == self.n * self.n - 1:
            return True

        valid_moves = self.get_valid_moves(x, y)

        moves_with_degree = []
        for next_x, next_y in valid_moves:
            degree = self._get_degree(next_x, next_y)
            moves_with_degree.append((next_x, next_y, degree))

        moves_with_degree.sort(key=lambda m: m[2])

        for next_x, next_y, _ in moves_with_degree:
            if self._backtrack(next_x, next_y, move_count + 1):
                return True

        self.backtrack_count += 1
        self.board[x][y] = -1
        self.path.pop()
        return False
