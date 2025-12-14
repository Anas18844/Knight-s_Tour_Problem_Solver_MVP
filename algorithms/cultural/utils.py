"""
Utility classes and functions for the Knight's Tour solvers.
"""

from typing import List, Tuple, Set

class MobilityManager:
    """
    Manages and caches the mobility of squares on the board to speed up
    calculations for heuristics like Warnsdorff's rule.
    """

    def __init__(self, n: int, visited: Set[Tuple[int, int]]):
        """
        Initializes the mobility manager.

        Args:
            n: The size of the board.
            visited: The set of already visited squares.
        """
        self.n = n
        self.KNIGHT_MOVES = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                             (1, -2), (1, 2), (2, -1), (2, 1)]
        self.mobility_cache = {}
        self._initialize_mobility(visited)

    def _is_valid(self, x: int, y: int) -> bool:
        """Check if a position is on the board."""
        return 0 <= x < self.n and 0 <= y < self.n

    def _calculate_mobility(self, x: int, y: int, visited: Set[Tuple[int, int]]) -> int:
        """Calculate the mobility of a single square."""
        count = 0
        for dx, dy in self.KNIGHT_MOVES:
            nx, ny = x + dx, y + dy
            if self._is_valid(nx, ny) and (nx, ny) not in visited:
                count += 1
        return count

    def _initialize_mobility(self, visited: Set[Tuple[int, int]]):
        """Pre-calculate the mobility for all unvisited squares."""
        for r in range(self.n):
            for c in range(self.n):
                if (r, c) not in visited:
                    self.mobility_cache[(r, c)] = self._calculate_mobility(r, c, visited)

    def get_mobility(self, x: int, y: int) -> int:
        """Get the mobility of a square from the cache."""
        return self.mobility_cache.get((x, y), 0)

    def update_after_move(self, move: Tuple[int, int], visited: Set[Tuple[int, int]]):
        """
        Update the mobility cache after a move has been made.
        The `visited` set should already include the new `move`.
        """
        # The moved-to square no longer has mobility
        if move in self.mobility_cache:
            del self.mobility_cache[move]

        # Update mobility of all neighbors of the new move
        for dx, dy in self.KNIGHT_MOVES:
            nx, ny = move[0] + dx, move[1] + dy
            if self._is_valid(nx, ny) and (nx, ny) in self.mobility_cache:
                # Re-calculate mobility for affected neighbors
                self.mobility_cache[(nx, ny)] = self._calculate_mobility(nx, ny, visited)

