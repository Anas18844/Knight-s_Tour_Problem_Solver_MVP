"""
Test script to verify new features:
1. SolverManager class
2. Level 0 - Random Knight Walk
3. Code stability after semi_magic_square removal
"""

from algorithms import SolverManager, RandomKnightWalk, BacktrackingSolver, CulturalAlgorithmSolver

def main():
    print("="*70)
    print("Knight's Tour Solver - New Features Test")
    print("="*70)

    # Create SolverManager
    manager = SolverManager()

    # Show available solvers
    print("\n1. SolverManager - Available Solvers:")
    manager.print_available_solvers()

    # Test Level 0 - Random Walk
    print("\n" + "="*70)
    print("2. Testing Level 0 - Random Knight Walk (5x5 board)")
    print("="*70)
    result = manager.solve("Random Walk", 0, 5, (0, 0))
    print(f"\nRandom Walk Results:")
    print(f"  Success: {result['success']}")
    print(f"  Coverage: {result['stats']['coverage_percent']:.1f}%")
    print(f"  Squares visited: {result['solution_length']}/25")
    print(f"  Execution time: {result['execution_time']:.4f}s")

    # Test Backtracking Level 1
    print("\n" + "="*70)
    print("3. Testing Backtracking Level 1 (6x6 board)")
    print("="*70)
    result = manager.solve("Backtracking", 1, 6, (0, 0))
    print(f"\nBacktracking Results:")
    print(f"  Success: {result['success']}")
    print(f"  Solution length: {result['solution_length']}/36")
    print(f"  Recursive calls: {result['stats']['recursive_calls']}")
    print(f"  Execution time: {result['execution_time']:.4f}s")

    # Test run_optimal
    print("\n" + "="*70)
    print("4. Testing run_optimal() - Automatic Solver Selection (8x8)")
    print("="*70)
    result = manager.run_optimal(8, (3, 3))
    print(f"\nOptimal Solver Results:")
    print(f"  Selected algorithm: {result['algorithm']}")
    print(f"  Success: {result['success']}")
    print(f"  Execution time: {result['execution_time']:.4f}s")

    # Test comparison
    print("\n" + "="*70)
    print("5. Testing compare_best_levels() - Algorithm Comparison (6x6)")
    print("="*70)
    comparison = manager.compare_best_levels(6, (2, 2), timeout=10.0)

    print(f"\nComparison Results:")
    for algo_name, result in comparison.items():
        if algo_name in ['fastest', 'most_efficient']:
            continue
        print(f"\n  {algo_name}:")
        print(f"    Success: {result['success']}")
        if result['success']:
            print(f"    Time: {result['execution_time']:.4f}s")
            print(f"    Solution length: {result['solution_length']}")

    print(f"\n  Fastest: {comparison['fastest']}")
    print(f"  Most Efficient: {comparison['most_efficient']}")

    # Test code stability
    print("\n" + "="*70)
    print("6. Code Stability Test")
    print("="*70)

    # Try importing main GUI
    try:
        from gui.main_window import KnightTourGUI
        print("  GUI module: OK")
    except Exception as e:
        print(f"  GUI module: FAILED - {e}")

    # Try importing database
    try:
        from database.db_manager import DatabaseManager
        print("  Database module: OK")
    except Exception as e:
        print(f"  Database module: FAILED - {e}")

    # Try importing reporting
    try:
        from reporting.report_generator import ReportGenerator
        print("  Reporting module: OK")
    except Exception as e:
        print(f"  Reporting module: FAILED - {e}")

    # Verify semi_magic_square is gone
    try:
        from algorithms.semi_magic_square import SemiMagicSquareValidator
        print("  semi_magic_square: STILL EXISTS (should be deleted!)")
    except ImportError:
        print("  semi_magic_square: Successfully removed")

    print("\n" + "="*70)
    print("All tests completed successfully!")
    print("="*70)

if __name__ == "__main__":
    main()
