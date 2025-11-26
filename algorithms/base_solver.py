from typing import List, Tuple
from abc import ABC, abstractmethod


class BaseSolver(ABC):
    KNIGHT_MOVES = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

    def __init__(self, n: int, level: int = 0):
        self.n = n
        self.level = level
        self.start_pos = None

    @abstractmethod
    def solve(self, start_x: int, start_y: int) -> Tuple[bool, List[Tuple[int, int]]]:
        raise NotImplementedError("Subclasses must implement solve()")

    def is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.n and 0 <= y < self.n

    def get_valid_moves_from(self, x: int, y: int, visited: set) -> List[Tuple[int, int]]:
        valid_moves = []
        for dx, dy in self.KNIGHT_MOVES:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_position(next_x, next_y) and (next_x, next_y) not in visited:
                valid_moves.append((next_x, next_y))
        return valid_moves

    def get_move_index(self, current_pos: Tuple[int, int], next_pos: Tuple[int, int]) -> int:
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        try:
            return self.KNIGHT_MOVES.index((dx, dy))
        except ValueError:
            return -1

    def apply_move(self, pos: Tuple[int, int], move_index: int) -> Tuple[int, int]:
        if move_index < 0 or move_index >= len(self.KNIGHT_MOVES):
            return pos
        dx, dy = self.KNIGHT_MOVES[move_index]
        return (pos[0] + dx, pos[1] + dy)
