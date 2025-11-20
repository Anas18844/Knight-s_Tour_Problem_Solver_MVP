"""
Level 1 - Ordered Knight Walk

This algorithm extends Level 0 by using a fixed, deterministic move order
instead of random selection. This provides reproducible, predictable behavior.

Key Differences from Level 0:
- Moves are tried in a fixed predetermined order
- Same starting position → same result every time
- No randomness, fully deterministic
- Still no backtracking, no heuristics
"""

from typing import List, Tuple
from algorithms.level0_random import RandomKnightWalk


class OrderedKnightWalk(RandomKnightWalk):
    """
    Ordered walk algorithm for Knight's Tour.

    Extends RandomKnightWalk but uses fixed move ordering instead of random selection.
    This makes the algorithm deterministic and reproducible.
    """

    def __init__(self, n: int, level: int = 1, timeout: float = 60.0):
        """
        Initialize the Ordered Knight Walk solver.

        Args:
            n: Board size (n x n)
            level: Algorithm level (always 1 for this implementation)
            timeout: Not used in this simple algorithm
        """
        # Call parent constructor to reuse all initialization logic
        super().__init__(n=n, level=level, timeout=timeout)

    def select_move(self, valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        """
        Select next move from list of valid moves using fixed ordering.

        Level 1 override: Instead of random selection, we use the first valid move
        according to the predefined KNIGHT_MOVES order. This ensures deterministic,
        reproducible behavior.

        The KNIGHT_MOVES order is:
        [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
         (1, -2), (1, 2), (2, -1), (2, 1)]

        Args:
            valid_moves: List of valid (x, y) positions

        Returns:
            Selected (x, y) position (first one in KNIGHT_MOVES order)
        """
        # Level 1: Use first valid move (already ordered by KNIGHT_MOVES in get_valid_moves)
        # Since get_valid_moves iterates through KNIGHT_MOVES in order,
        # valid_moves is already in the fixed order we want
        return valid_moves[0]

    def solve(self, start_x: int, start_y: int) -> Tuple[bool, List[Tuple[int, int]]]:
        """
        Main solve method - attempts ordered walk from starting position.

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

        # Perform ordered walk (reuses parent's random_walk method)
        # The only difference is select_move() uses fixed order instead of random
        success = self.random_walk(start_x, start_y)

        # Return results
        if success:
            print(f"Ordered walk SUCCESS! Completed {self.n}x{self.n} tour.")
        else:
            print(f"Ordered walk stopped at move {len(self.path)}/{self.n*self.n}")
            print(f"Coverage: {len(self.path)}/{self.n*self.n} squares "
                  f"({100*len(self.path)/(self.n*self.n):.1f}%)")

        return success, self.path.copy()


# Example usage and testing
if __name__ == "__main__":
    print("="*70)
    print("Level 1: Ordered Knight Walk")
    print("="*70)

    # Test deterministic behavior - run same configuration twice
    print("\nTest 1: Deterministic Behavior (5x5 board from (0,0))")
    print("Running twice with same parameters...\n")

    solver1 = OrderedKnightWalk(n=5, level=1)
    success1, path1 = solver1.solve(0, 0)

    solver2 = OrderedKnightWalk(n=5, level=1)
    success2, path2 = solver2.solve(0, 0)

    print(f"\nRun 1: {len(path1)}/25 squares")
    print(f"Run 2: {len(path2)}/25 squares")

    # Check if paths are identical
    if path1 == path2:
        print("[OK] Paths are IDENTICAL - Fully deterministic!")
    else:
        print("[ERROR] Paths differ - Not deterministic!")

    print(f"\nPath 1 (first 10): {path1[:10]}")
    print(f"Path 2 (first 10): {path2[:10]}")

    # Test on 6x6 board
    print("\n" + "="*70)
    print("Test 2: 6x6 board from center (2, 2)")
    print("="*70)

    solver = OrderedKnightWalk(n=6, level=1)
    success, path = solver.solve(2, 2)
    stats = solver.get_stats()

    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    print(f"Coverage: {stats['coverage_percent']:.1f}%")
    print(f"Squares visited: {len(path)}/36")

    # Test determinism again
    solver_check = OrderedKnightWalk(n=6, level=1)
    success_check, path_check = solver_check.solve(2, 2)

    if path == path_check:
        print("[OK] Deterministic behavior confirmed for 6x6")

    # Test on 8x8 board
    print("\n" + "="*70)
    print("Test 3: 8x8 board (standard chessboard) from (0, 0)")
    print("="*70)

    solver = OrderedKnightWalk(n=8, level=1)
    success, path = solver.solve(0, 0)
    stats = solver.get_stats()

    print(f"\nResult: {'COMPLETE TOUR!' if success else 'Incomplete'}")
    print(f"Coverage: {stats['coverage_percent']:.1f}%")
    print(f"Squares visited: {len(path)}/64")

    if len(path) > 0:
        print(f"\nFirst 10 moves: {path[:10]}")
        print(f"Last 5 moves: {path[-5:]}")

    # Comparison with Level 0
    print("\n" + "="*70)
    print("Test 4: Comparison with Level 0 (Random Walk)")
    print("="*70)

    from algorithms.level0_random import RandomKnightWalk

    # Level 0 - run 3 times, should get different results
    print("\nLevel 0 (Random) - 5 runs on 6x6:")
    random_coverages = []
    for i in range(5):
        solver0 = RandomKnightWalk(n=6, level=0)
        success0, path0 = solver0.solve(2, 2)
        coverage = 100 * len(path0) / 36
        random_coverages.append(coverage)
        print(f"  Run {i+1}: {len(path0)}/36 ({coverage:.1f}%)")

    # Level 1 - run 3 times, should get same result
    print("\nLevel 1 (Ordered) - 5 runs on 6x6:")
    ordered_coverages = []
    for i in range(5):
        solver1 = OrderedKnightWalk(n=6, level=1)
        success1, path1 = solver1.solve(2, 2)
        coverage = 100 * len(path1) / 36
        ordered_coverages.append(coverage)
        print(f"  Run {i+1}: {len(path1)}/36 ({coverage:.1f}%)")

    # Check variability
    random_variance = max(random_coverages) - min(random_coverages)
    ordered_variance = max(ordered_coverages) - min(ordered_coverages)

    print(f"\nLevel 0 variance: {random_variance:.1f}% (should be > 0)")
    print(f"Level 1 variance: {ordered_variance:.1f}% (should be 0)")

    if ordered_variance == 0:
        print("[OK] Level 1 is fully deterministic!")
    else:
        print("[ERROR] Level 1 has variance - not deterministic!")

    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70)
