"""
Semi-Magic Square validator for Knight's Tour.

A Knight's Tour can be represented as a semi-magic square where:
- Numbers 1 to n² are placed on an n×n board according to the knight's path
- The tour is semi-magic if certain row/column sums have interesting properties

This module provides utilities to check if a knight's tour forms a semi-magic square.
"""

from typing import List, Tuple, Optional


class SemiMagicSquareValidator:
    """
    Validates and analyzes semi-magic square properties of Knight's Tour solutions.

    A semi-magic square has equal row sums and equal column sums (but row sum != column sum).
    A true magic square additionally has equal diagonal sums.
    """

    def __init__(self, board_size: int):
        """
        Initialize validator.

        Args:
            board_size: Size of the board (n x n)
        """
        self.board_size = board_size
        self.magic_constant = (board_size * (board_size ** 2 + 1)) // 2

    def path_to_board(self, path: List[Tuple[int, int]]) -> List[List[int]]:
        """
        Convert knight's tour path to numbered board.

        Args:
            path: List of (x, y) coordinates in order

        Returns:
            2D board with move numbers
        """
        board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]

        for move_number, (x, y) in enumerate(path, start=1):
            board[x][y] = move_number

        return board

    def calculate_row_sums(self, board: List[List[int]]) -> List[int]:
        """
        Calculate sum of each row.

        Args:
            board: 2D board with move numbers

        Returns:
            List of row sums
        """
        return [sum(row) for row in board]

    def calculate_column_sums(self, board: List[List[int]]) -> List[int]:
        """
        Calculate sum of each column.

        Args:
            board: 2D board with move numbers

        Returns:
            List of column sums
        """
        return [sum(board[i][j] for i in range(self.board_size))
                for j in range(self.board_size)]

    def calculate_diagonal_sums(self, board: List[List[int]]) -> Tuple[int, int]:
        """
        Calculate sums of main and anti diagonals.

        Args:
            board: 2D board with move numbers

        Returns:
            Tuple of (main_diagonal_sum, anti_diagonal_sum)
        """
        main_diagonal = sum(board[i][i] for i in range(self.board_size))
        anti_diagonal = sum(board[i][self.board_size - 1 - i]
                          for i in range(self.board_size))

        return main_diagonal, anti_diagonal

    def is_semi_magic(self, board: List[List[int]]) -> bool:
        """
        Check if board is semi-magic square.

        A semi-magic square has:
        - All row sums equal
        - All column sums equal
        - Row sum may differ from column sum

        Args:
            board: 2D board with move numbers

        Returns:
            True if semi-magic, False otherwise
        """
        row_sums = self.calculate_row_sums(board)
        column_sums = self.calculate_column_sums(board)

        # Check if all row sums are equal
        rows_equal = len(set(row_sums)) == 1

        # Check if all column sums are equal
        columns_equal = len(set(column_sums)) == 1

        return rows_equal and columns_equal

    def is_magic(self, board: List[List[int]]) -> bool:
        """
        Check if board is a true magic square.

        A magic square has:
        - All row sums equal to magic constant
        - All column sums equal to magic constant
        - Both diagonal sums equal to magic constant

        Args:
            board: 2D board with move numbers

        Returns:
            True if magic square, False otherwise
        """
        row_sums = self.calculate_row_sums(board)
        column_sums = self.calculate_column_sums(board)
        main_diag, anti_diag = self.calculate_diagonal_sums(board)

        # Check if all sums equal magic constant
        all_sums = row_sums + column_sums + [main_diag, anti_diag]

        return all(s == self.magic_constant for s in all_sums)

    def analyze_path(self, path: List[Tuple[int, int]]) -> dict:
        """
        Perform complete analysis of knight's tour path for magic square properties.

        Args:
            path: List of (x, y) coordinates in order

        Returns:
            Dictionary with analysis results
        """
        if len(path) != self.board_size ** 2:
            return {
                'valid': False,
                'error': f'Incomplete path: {len(path)}/{self.board_size ** 2} squares'
            }

        board = self.path_to_board(path)
        row_sums = self.calculate_row_sums(board)
        column_sums = self.calculate_column_sums(board)
        main_diag, anti_diag = self.calculate_diagonal_sums(board)

        is_semi_magic = self.is_semi_magic(board)
        is_magic = self.is_magic(board)

        # Calculate statistics
        row_sum_range = max(row_sums) - min(row_sums)
        col_sum_range = max(column_sums) - min(column_sums)

        analysis = {
            'valid': True,
            'board_size': self.board_size,
            'is_semi_magic': is_semi_magic,
            'is_magic': is_magic,
            'magic_constant': self.magic_constant,
            'row_sums': row_sums,
            'column_sums': column_sums,
            'main_diagonal_sum': main_diag,
            'anti_diagonal_sum': anti_diag,
            'row_sum_range': row_sum_range,
            'column_sum_range': col_sum_range,
            'row_sums_equal': len(set(row_sums)) == 1,
            'column_sums_equal': len(set(column_sums)) == 1,
            'diagonals_equal': main_diag == anti_diag
        }

        # Add classification
        if is_magic:
            analysis['classification'] = 'Magic Square'
        elif is_semi_magic:
            analysis['classification'] = 'Semi-Magic Square'
        elif len(set(row_sums)) == 1 or len(set(column_sums)) == 1:
            analysis['classification'] = 'Partially Magic'
        else:
            analysis['classification'] = 'Non-Magic'

        return analysis

    def print_analysis(self, path: List[Tuple[int, int]]):
        """
        Print detailed analysis of knight's tour path.

        Args:
            path: List of (x, y) coordinates in order
        """
        analysis = self.analyze_path(path)

        if not analysis['valid']:
            print(f"Error: {analysis['error']}")
            return

        print("\n" + "="*60)
        print("SEMI-MAGIC SQUARE ANALYSIS")
        print("="*60)

        print(f"\nBoard Size: {self.board_size}x{self.board_size}")
        print(f"Classification: {analysis['classification']}")
        print(f"Magic Constant (ideal): {self.magic_constant}")

        print(f"\nRow Sums: {analysis['row_sums']}")
        print(f"  - All equal: {analysis['row_sums_equal']}")
        print(f"  - Range: {analysis['row_sum_range']}")

        print(f"\nColumn Sums: {analysis['column_sums']}")
        print(f"  - All equal: {analysis['column_sums_equal']}")
        print(f"  - Range: {analysis['column_sum_range']}")

        print(f"\nDiagonal Sums:")
        print(f"  - Main: {analysis['main_diagonal_sum']}")
        print(f"  - Anti: {analysis['anti_diagonal_sum']}")
        print(f"  - Equal: {analysis['diagonals_equal']}")

        print(f"\nMagic Properties:")
        print(f"  - Semi-Magic: {analysis['is_semi_magic']}")
        print(f"  - Full Magic: {analysis['is_magic']}")

        # Print board
        board = self.path_to_board(path)
        print("\nNumbered Board (move order):")
        print("     ", end="")
        for i in range(self.board_size):
            print(f"{i:4}", end="")
        print()

        for i in range(self.board_size):
            print(f"  {i:2} ", end="")
            for j in range(self.board_size):
                print(f"{board[i][j]:4}", end="")
            print()

        print("="*60 + "\n")


def check_knight_tour_magic_properties(path: List[Tuple[int, int]], board_size: int) -> dict:
    """
    Convenience function to check magic square properties of a knight's tour.

    Args:
        path: List of (x, y) coordinates in order
        board_size: Size of the board

    Returns:
        Dictionary with analysis results
    """
    validator = SemiMagicSquareValidator(board_size)
    return validator.analyze_path(path)
