"""
Level 0 - Random Knight Walk

This is a simple baseline algorithm that demonstrates random human-like
movement of a knight until it gets stuck. This is NOT backtracking,
NOT brute force, and NOT heuristic-based.

Purpose: Provides a baseline for comparison with intelligent algorithms.
Expected: Will rarely (if ever) complete a full tour, especially on larger boards.
"""

import random
from typing import List, Tuple, Optional


class RandomKnightWalk:
    """
    Simple random walk algorithm for Knight's Tour.

    This algorithm moves the knight randomly to valid unvisited squares
    until no more moves are available (dead-end) or all squares are visited.
    """

    # Knight's 8 possible moves as (dx, dy) coordinate deltas
    KNIGHT_MOVES = [
        (-2, -1), (-2, 1),  # Up-left, Up-right
        (-1, -2), (-1, 2),  # Left-up, Left-down
        (1, -2), (1, 2),    # Right-up, Right-down
        (2, -1), (2, 1)     # Down-left, Down-right
    ]

    def __init__(self, n: int, level: int = 0, timeout: float = 60.0):
        """
        Initialize the Random Knight Walk solver.

        Args:
            n: Board size (n x n)
            level: Algorithm level (always 0 for this implementation)
            timeout: Not used in this simple algorithm
        """
        self.n = n
        self.level = level
        self.timeout = timeout

        # Board state: -1 = unvisited, 0+ = move number
        self.board: List[List[int]] = [[-1 for _ in range(n)] for _ in range(n)]

        # Solution path tracking
        self.path: List[Tuple[int, int]] = []

        # Statistics
        self.total_moves = 0
        self.dead_ends_hit = 0

    def is_valid_position(self, x: int, y: int) -> bool:
        """
        Check if a position is within board bounds.

        Args:
            x: Row coordinate
            y: Column coordinate

        Returns:
            True if position is valid, False otherwise
        """
        return 0 <= x < self.n and 0 <= y < self.n

    def is_unvisited(self, x: int, y: int) -> bool:
        """
        Check if a square has not been visited yet.

        Args:
            x: Row coordinate
            y: Column coordinate

        Returns:
            True if square is unvisited, False otherwise
        """
        return self.board[x][y] == -1

    def get_valid_moves(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Get all valid unvisited moves from current position.

        Args:
            x: Current row position
            y: Current column position

        Returns:
            List of valid (next_x, next_y) positions
        """
        valid_moves = []

        # Try all 8 possible knight moves
        for dx, dy in self.KNIGHT_MOVES:
            next_x = x + dx
            next_y = y + dy

            # Check if move is within bounds and square is unvisited
            if self.is_valid_position(next_x, next_y) and self.is_unvisited(next_x, next_y):
                valid_moves.append((next_x, next_y))

        return valid_moves

    def select_move(self, valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        """
        Select next move from list of valid moves.
        This method is meant to be overridden by subclasses.

        Args:
            valid_moves: List of valid (x, y) positions

        Returns:
            Selected (x, y) position
        """
        # Level 0: Random selection
        random.shuffle(valid_moves)
        return valid_moves[0]

    def random_walk(self, start_x: int, start_y: int) -> bool:
        """
        Perform random walk starting from given position.

        Algorithm:
        1. Mark starting position as visited
        2. Get all valid unvisited moves from current position
        3. If no valid moves → stop (dead-end reached)
        4. Select next move using select_move() method
        5. Move knight to that position
        6. Repeat from step 2

        Args:
            start_x: Starting row position
            start_y: Starting column position

        Returns:
            True if complete tour found (all squares visited), False otherwise
        """
        # Start at initial position
        current_x = start_x
        current_y = start_y
        move_number = 0

        # Mark starting square as visited
        self.board[current_x][current_y] = move_number
        self.path.append((current_x, current_y))
        self.total_moves += 1

        # Target: visit all n*n squares
        target_moves = self.n * self.n

        # Continue until stuck or complete
        while move_number < target_moves - 1:
            # Get all valid moves from current position
            valid_moves = self.get_valid_moves(current_x, current_y)

            # If no valid moves, we hit a dead-end
            if not valid_moves:
                self.dead_ends_hit += 1
                return False  # Failed to complete tour

            # Select next move (can be overridden by subclasses)
            next_x, next_y = self.select_move(valid_moves)

            # Move to next position
            current_x = next_x
            current_y = next_y
            move_number += 1

            # Mark as visited
            self.board[current_x][current_y] = move_number
            self.path.append((current_x, current_y))
            self.total_moves += 1

        # If we've made n*n moves, we completed the tour!
        return True

    def solve(self, start_x: int, start_y: int) -> Tuple[bool, List[Tuple[int, int]]]:
        """
        Main solve method - attempts random walk from starting position.

        Args:
            start_x: Starting row position
            start_y: Starting column position

        Returns:
            Tuple of (success: bool, path: List of (x,y) coordinates)
        """
        # Reset board and path
        self.board = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        self.path = []
        self.total_moves = 0
        self.dead_ends_hit = 0

        # Validate starting position
        if not self.is_valid_position(start_x, start_y):
            print(f"Error: Invalid starting position ({start_x}, {start_y})")
            return False, []

        # Perform random walk
        success = self.random_walk(start_x, start_y)

        # Return results
        if success:
            print(f"Random walk SUCCESS! Completed {self.n}x{self.n} tour.")
        else:
            print(f"Random walk stopped at move {len(self.path)}/{self.n*self.n}")
            print(f"Coverage: {len(self.path)}/{self.n*self.n} squares "
                  f"({100*len(self.path)/(self.n*self.n):.1f}%)")

        return success, self.path.copy()

    def get_stats(self) -> dict:
        """
        Get statistics about the random walk.

        Returns:
            Dictionary with statistics
        """
        return {
            'total_moves': self.total_moves,
            'dead_ends_hit': self.dead_ends_hit,
            'coverage_percent': 100 * len(self.path) / (self.n * self.n) if self.n > 0 else 0,
            'board_size': self.n
        }


# Example usage and testing
if __name__ == "__main__":
    print("=== Level 0: Random Knight Walk ===\n")

    # Test on small board (5x5)
    print("Test 1: 5x5 board, starting at (0, 0)")
    solver = RandomKnightWalk(n=5)
    success, path = solver.solve(0, 0)
    stats = solver.get_stats()

    print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    print(f"Coverage: {stats['coverage_percent']:.1f}%")
    print(f"Path length: {len(path)}/25")
    print()

    # Test multiple attempts on 6x6 (show randomness)
    print("Test 2: Multiple random attempts on 6x6 board")
    print("Starting position: (2, 2) - center\n")

    attempts = 5
    best_coverage = 0
    best_path = []

    for i in range(attempts):
        solver = RandomKnightWalk(n=6)
        success, path = solver.solve(2, 2)
        stats = solver.get_stats()

        coverage = stats['coverage_percent']
        print(f"Attempt {i+1}: {len(path)}/36 squares ({coverage:.1f}%)")

        if coverage > best_coverage:
            best_coverage = coverage
            best_path = path

    print(f"\nBest attempt: {len(best_path)}/36 squares ({best_coverage:.1f}%)")

    # Test on 8x8 (standard chessboard)
    print("\n" + "="*50)
    print("Test 3: 8x8 board (standard chessboard)")
    print("Starting at corner (0, 0) - most challenging\n")

    solver = RandomKnightWalk(n=8)
    success, path = solver.solve(0, 0)
    stats = solver.get_stats()

    print(f"Result: {'COMPLETE TOUR!' if success else 'Incomplete'}")
    print(f"Coverage: {stats['coverage_percent']:.1f}%")
    print(f"Squares visited: {len(path)}/64")

    if len(path) > 0:
        print(f"\nFirst 10 moves: {path[:10]}")
        print(f"Last 5 moves: {path[-5:]}")
