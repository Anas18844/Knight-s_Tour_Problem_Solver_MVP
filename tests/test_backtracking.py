"""Unit tests for Backtracking algorithm."""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.backtracking import BacktrackingSolver


class TestBacktrackingSolver:
    """Test cases for BacktrackingSolver."""

    def test_initialization(self):
        """Test solver initialization."""
        solver = BacktrackingSolver(board_size=8, start_pos=(0, 0))
        assert solver.board_size == 8
        assert solver.start_pos == (0, 0)
        assert len(solver.board) == 8
        assert len(solver.board[0]) == 8

    def test_valid_move_detection(self):
        """Test valid move detection."""
        solver = BacktrackingSolver(board_size=8)

        # Test valid move
        assert solver.is_valid_move(0, 0) == True
        assert solver.is_valid_move(7, 7) == True

        # Test invalid moves (out of bounds)
        assert solver.is_valid_move(-1, 0) == False
        assert solver.is_valid_move(8, 0) == False
        assert solver.is_valid_move(0, -1) == False
        assert solver.is_valid_move(0, 8) == False

        # Test visited square
        solver.board[3][3] = 5
        assert solver.is_valid_move(3, 3) == False

    def test_degree_calculation(self):
        """Test Warnsdorff's heuristic degree calculation."""
        solver = BacktrackingSolver(board_size=8)

        # Corner has 2 moves
        degree = solver.get_degree(0, 0)
        assert degree == 2

        # Edge has typically 3-4 moves
        degree = solver.get_degree(0, 3)
        assert degree in [3, 4]

        # Center has 8 moves (initially)
        degree = solver.get_degree(4, 4)
        assert degree == 8

    def test_ordered_moves(self):
        """Test that moves are ordered by Warnsdorff's heuristic."""
        solver = BacktrackingSolver(board_size=8)

        moves = solver.get_ordered_moves(4, 4)

        # Should return 8 moves from center
        assert len(moves) == 8

        # Verify moves are ordered by degree (ascending)
        for i in range(len(moves) - 1):
            deg1 = solver.get_degree(moves[i][0], moves[i][1])
            deg2 = solver.get_degree(moves[i+1][0], moves[i+1][1])
            assert deg1 <= deg2

    def test_small_board_solution(self):
        """Test solving a small board (5x5)."""
        solver = BacktrackingSolver(board_size=5, start_pos=(0, 0), timeout=10.0)
        success, path, stats = solver.solve()

        assert isinstance(success, bool)
        assert isinstance(path, list)
        assert isinstance(stats, dict)

        if success:
            assert len(path) == 25  # 5x5 board
            assert path[0] == (0, 0)  # Starts at correct position

            # Verify all moves are valid knight moves
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]
                dx, dy = abs(x2 - x1), abs(y2 - y1)
                assert (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

            # Verify all squares visited exactly once
            assert len(set(path)) == 25

    def test_invalid_start_position(self):
        """Test handling of invalid start position."""
        solver = BacktrackingSolver(board_size=8, start_pos=(10, 10))
        success, path, stats = solver.solve()

        assert success == False
        assert 'error' in stats

    def test_timeout(self):
        """Test timeout functionality."""
        # Use very short timeout
        solver = BacktrackingSolver(board_size=12, start_pos=(0, 0), timeout=0.001)
        success, path, stats = solver.solve()

        # Might timeout on larger board with very short timeout
        if stats.get('timed_out'):
            assert 'error' in stats

    def test_statistics_returned(self):
        """Test that statistics are properly returned."""
        solver = BacktrackingSolver(board_size=6, timeout=10.0)
        success, path, stats = solver.solve()

        assert 'execution_time' in stats
        assert 'recursive_calls' in stats
        assert 'solution_length' in stats
        assert 'algorithm' in stats
        assert stats['algorithm'] == "Backtracking with Warnsdorff's Heuristic"

    def test_different_start_positions(self):
        """Test solving from different start positions."""
        positions = [(0, 0), (3, 3), (0, 4)]

        for pos in positions:
            solver = BacktrackingSolver(board_size=5, start_pos=pos, timeout=10.0)
            success, path, stats = solver.solve()

            if success:
                assert path[0] == pos


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
