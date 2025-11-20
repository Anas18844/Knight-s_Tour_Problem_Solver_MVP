"""Backtracking algorithm with Warnsdorff's heuristic for Knight's Tour."""

import time
from typing import List, Tuple, Optional, Callable


class BacktrackingSolver:
    """
    Solves Knight's Tour problem using backtracking with Warnsdorff's heuristic.

    Warnsdorff's Rule: Always move the knight to the square from which the knight
    will have the fewest onward moves. This heuristic dramatically improves performance.
    """

    # Knight's possible moves (L-shaped: 2 squares in one direction, 1 in perpendicular)
    MOVES = [
        (2, 1), (1, 2), (-1, 2), (-2, 1),
        (-2, -1), (-1, -2), (1, -2), (2, -1)
    ]

    def __init__(self, board_size: int, start_pos: Tuple[int, int] = (0, 0),
                timeout: float = 60.0, progress_callback: Optional[Callable] = None):
        """
        Initialize the backtracking solver.

        Args:
            board_size: Size of the chessboard (n x n)
            start_pos: Starting position (x, y)
            timeout: Maximum execution time in seconds
            progress_callback: Optional callback function for progress updates
        """
        self.board_size = board_size
        self.start_pos = start_pos
        self.timeout = timeout
        self.progress_callback = progress_callback

        self.board = [[-1 for _ in range(board_size)] for _ in range(board_size)]
        self.solution_path = []
        self.recursive_calls = 0
        self.start_time = None
        self.timed_out = False

    def is_valid_move(self, x: int, y: int) -> bool:
        """
        Check if a move is valid (within board and not visited).

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if move is valid, False otherwise
        """
        return (0 <= x < self.board_size and
                0 <= y < self.board_size and
                self.board[x][y] == -1)

    def get_degree(self, x: int, y: int) -> int:
        """
        Calculate the degree (number of unvisited neighbors) of a square.
        This implements Warnsdorff's heuristic.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Number of valid unvisited moves from this square
        """
        count = 0
        for dx, dy in self.MOVES:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_move(next_x, next_y):
                count += 1
        return count

    def get_ordered_moves(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Get all possible moves from current position, ordered by Warnsdorff's heuristic.
        Moves with fewer onward possibilities are tried first.

        Args:
            x: Current X coordinate
            y: Current Y coordinate

        Returns:
            List of valid moves sorted by degree (ascending)
        """
        valid_moves = []

        for dx, dy in self.MOVES:
            next_x, next_y = x + dx, y + dy

            if self.is_valid_move(next_x, next_y):
                degree = self.get_degree(next_x, next_y)
                valid_moves.append((next_x, next_y, degree))

        # Sort by degree (Warnsdorff's heuristic: prefer squares with fewer onward moves)
        valid_moves.sort(key=lambda move: move[2])

        return [(move[0], move[1]) for move in valid_moves]

    def solve_recursive(self, x: int, y: int, move_count: int) -> bool:
        """
        Recursive backtracking function to solve Knight's Tour.

        Args:
            x: Current X coordinate
            y: Current Y coordinate
            move_count: Number of moves made so far

        Returns:
            True if solution found, False otherwise
        """
        # Check timeout (ensure start_time is initialized before subtracting)
        if self.start_time is not None and (time.time() - self.start_time) > self.timeout:
            self.timed_out = True
            return False

        self.recursive_calls += 1

        # Mark current square as visited
        self.board[x][y] = move_count
        self.solution_path.append((x, y))

        # Send progress update
        if self.progress_callback and move_count % 5 == 0:
            progress = (move_count / (self.board_size ** 2)) * 100
            self.progress_callback(progress, f"Exploring move {move_count}/{self.board_size ** 2}")

        # Base case: all squares visited
        if move_count == self.board_size ** 2 - 1:
            return True

        # Try all possible moves (ordered by Warnsdorff's heuristic)
        for next_x, next_y in self.get_ordered_moves(x, y):
            if self.solve_recursive(next_x, next_y, move_count + 1):
                return True

        # Backtrack: unmark current square
        self.board[x][y] = -1
        self.solution_path.pop()

        return False

    def solve(self) -> Tuple[bool, List[Tuple[int, int]], dict]:
        """
        Solve the Knight's Tour problem.

        Returns:
            Tuple containing:
                - Success flag (True if solution found)
                - Solution path (list of coordinates)
                - Statistics dictionary
        """
        self.start_time = time.time()
        self.board = [[-1 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.solution_path = []
        self.recursive_calls = 0
        self.timed_out = False

        start_x, start_y = self.start_pos

        # Validate start position
        if not (0 <= start_x < self.board_size and 0 <= start_y < self.board_size):
            return False, [], {
                'execution_time': 0,
                'recursive_calls': 0,
                'error': 'Invalid start position'
            }

        success = self.solve_recursive(start_x, start_y, 0)
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

    def get_board_state(self) -> List[List[int]]:
        """
        Get current board state.

        Returns:
            2D list representing the board
        """
        return [row[:] for row in self.board]

    def print_solution(self):
        """Print the solution board in a readable format."""
        if not self.solution_path:
            print("No solution found")
            return

        print(f"\nKnight's Tour Solution ({self.board_size}x{self.board_size}):")
        print(f"Starting position: {self.start_pos}")
        print(f"Total moves: {len(self.solution_path)}")
        print(f"Recursive calls: {self.recursive_calls}")
        print("\nBoard (move order):")

        # Print column headers
        print("     ", end="")
        for i in range(self.board_size):
            print(f"{i:3}", end=" ")
        print()

        # Print board
        for i in range(self.board_size):
            print(f"  {i:2} ", end="")
            for j in range(self.board_size):
                print(f"{self.board[i][j]:3}", end=" ")
            print()
        print()
