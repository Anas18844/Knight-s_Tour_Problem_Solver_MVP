"""Backtracking algorithm with Warnsdorff's heuristic for Knight's Tour.

Warnsdorff's Rule: Always move the knight to the square from which the knight
will have the fewest onward moves. This heuristic dramatically improves performance.
"""

import time
from typing import List, Tuple, Optional, Callable
from .level3_enhanced import EnhancedBacktracking


class BacktrackingSolver(EnhancedBacktracking):

    def __init__(self, board_size: int, start_pos: Tuple[int, int] = (0, 0),
                 timeout: float = 60.0, progress_callback: Optional[Callable] = None):
        super().__init__(n=board_size, level=4)
        self.start_pos = start_pos
        self.timeout = timeout
        self.progress_callback = progress_callback
        self.solution_path = []
        self.start_time = None
        self.timed_out = False

    def _get_degree(self, x: int, y: int) -> int:
        count = 0
        for dx, dy in self.KNIGHT_MOVES:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_position(next_x, next_y) and self.is_unvisited(next_x, next_y):
                count += 1
        return count

    def _get_ordered_moves(self, x: int, y: int) -> List[Tuple[int, int]]:
        valid_moves = []
        for dx, dy in self.KNIGHT_MOVES:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_position(next_x, next_y) and self.is_unvisited(next_x, next_y):
                degree = self._get_degree(next_x, next_y)
                valid_moves.append((next_x, next_y, degree))

        valid_moves.sort(key=lambda move: move[2])
        return [(move[0], move[1]) for move in valid_moves]

    def _backtrack(self, x: int, y: int, move_count: int) -> bool:
        if self.start_time is not None and (time.time() - self.start_time) > self.timeout:
            self.timed_out = True
            return False

        self.recursive_calls += 1

        self.board[x][y] = move_count
        self.path.append((x, y))
        self.solution_path.append((x, y))

        if self.progress_callback and move_count % 5 == 0:
            progress = (move_count / (self.n ** 2)) * 100
            self.progress_callback(progress, f"Exploring move {move_count}/{self.n ** 2}")

        if move_count == self.n * self.n - 1:
            return True

        for next_x, next_y in self._get_ordered_moves(x, y):
            if self._backtrack(next_x, next_y, move_count + 1):
                return True

        self.backtrack_count += 1
        self.board[x][y] = -1
        self.path.pop()
        self.solution_path.pop()
        return False

    def solve(self) -> Tuple[bool, List[Tuple[int, int]], dict]:
        self.start_time = time.time()
        self.board = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        self.path = []
        self.solution_path = []
        self.recursive_calls = 0
        self.backtrack_count = 0
        self.timed_out = False

        start_x, start_y = self.start_pos

        if not self.is_valid_position(start_x, start_y):
            return False, [], {
                'execution_time': 0,
                'recursive_calls': 0,
                'error': 'Invalid start position'
            }

        success = self._backtrack(start_x, start_y, 0)
        execution_time = time.time() - self.start_time

        stats = {
            'execution_time': execution_time,
            'recursive_calls': self.recursive_calls,
            'solution_length': len(self.solution_path),
            'timed_out': self.timed_out,
            'algorithm': 'Backtracking with Warnsdorff\'s Heuristic'
        }

        if self.timed_out:
            stats['error'] = f'Timeout after {self.timeout} seconds'

        return success, self.solution_path.copy(), stats
