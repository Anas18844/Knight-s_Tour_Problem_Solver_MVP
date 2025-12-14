"""
Manual Testing Script with Verbose Output
Run this to see detailed terminal output from each CA level
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from algorithms.cultural.level1_simple_ga import SimpleGASolver
from algorithms.cultural.level2_enhanced_ga import EnhancedGASolver
from algorithms.cultural.level3_cultural_ga import CulturalGASolver


def test_level1_verbose():
    """Test Level 1 with verbose output"""
    print("\n\n" + "#"*70)
    print("# TESTING LEVEL 1: SIMPLE GA WITH VERBOSE OUTPUT")
    print("#"*70)

    solver = SimpleGASolver(n=5, level=1, verbose=True)
    solver.generations = 30  # Reduced for demonstration

    success, path = solver.solve(0, 0)

    print("\nFinal Path:")
    print(f"  {path[:10]}... (showing first 10 moves)")
    print(f"\nUnique squares visited: {len(set(path))}/25")


def test_level2_verbose():
    """Test Level 2 with verbose output"""
    print("\n\n" + "#"*70)
    print("# TESTING LEVEL 2: ENHANCED GA WITH VERBOSE OUTPUT")
    print("#"*70)

    solver = EnhancedGASolver(n=5, level=2, verbose=True)
    solver.generations = 30

    success, path = solver.solve(0, 0)

    print("\nFinal Path:")
    print(f"  {path[:10]}... (showing first 10 moves)")
    print(f"\nUnique squares visited: {len(set(path))}/25")


def test_level3_verbose():
    """Test Level 3 with verbose output"""
    print("\n\n" + "#"*70)
    print("# TESTING LEVEL 3: CULTURAL GA WITH VERBOSE OUTPUT")
    print("#"*70)

    solver = CulturalGASolver(n=5, level=3, verbose=True)
    solver.generations = 30

    success, path = solver.solve(0, 0)

    print("\nFinal Path:")
    print(f"  {path[:10]}... (showing first 10 moves)")
    print(f"\nUnique squares visited: {len(set(path))}/25")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Test CA levels with verbose output')
    parser.add_argument('--level', '-l', type=int, choices=[1, 2, 3],
                       help='Test specific level (1, 2, or 3)')
    parser.add_argument('--all', '-a', action='store_true',
                       help='Test all levels')

    args = parser.parse_args()

    if args.level == 1:
        test_level1_verbose()
    elif args.level == 2:
        test_level2_verbose()
    elif args.level == 3:
        test_level3_verbose()
    elif args.all:
        test_level1_verbose()
        test_level2_verbose()
        test_level3_verbose()
    else:
        print("Usage: python manual_test_verbose.py --level 1")
        print("   or: python manual_test_verbose.py --all")
        print("\nRunning Level 1 by default...")
        test_level1_verbose()
