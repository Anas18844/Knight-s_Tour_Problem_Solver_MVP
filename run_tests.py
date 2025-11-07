"""
Test runner script for Knight's Tour Problem Solver.

Runs all unit tests and displays results.
"""

import sys
import subprocess


def run_tests():
    """Run all tests using pytest."""
    print("="*70)
    print("KNIGHT'S TOUR PROBLEM SOLVER - TEST SUITE")
    print("="*70)
    print("\nRunning all unit tests...\n")

    try:
        # Run pytest with verbose output
        result = subprocess.run(
            ['pytest', 'tests/', '-v', '--tb=short'],
            capture_output=False,
            text=True
        )

        print("\n" + "="*70)
        if result.returncode == 0:
            print("✅ ALL TESTS PASSED!")
        else:
            print("❌ SOME TESTS FAILED")
        print("="*70)

        return result.returncode

    except FileNotFoundError:
        print("❌ Error: pytest not found. Please install it:")
        print("   pip install pytest")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def run_specific_test(test_file):
    """
    Run a specific test file.

    Args:
        test_file: Name of the test file (e.g., 'test_backtracking.py')
    """
    print(f"\nRunning {test_file}...\n")

    try:
        result = subprocess.run(
            ['pytest', f'tests/{test_file}', '-v'],
            capture_output=False,
            text=True
        )
        return result.returncode

    except Exception as e:
        print(f"Error: {e}")
        return 1


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Run specific test file
        test_file = sys.argv[1]
        if not test_file.startswith('test_'):
            test_file = 'test_' + test_file
        if not test_file.endswith('.py'):
            test_file = test_file + '.py'

        return run_specific_test(test_file)
    else:
        # Run all tests
        return run_tests()


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
