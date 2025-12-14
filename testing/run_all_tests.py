"""
Test Runner for Cultural Algorithm Test Suite
Runs all unit tests and logic tests
"""

import unittest
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def run_test_suite():
    """Run all tests and generate report"""

    print("="*70)
    print(" KNIGHT'S TOUR - CULTURAL ALGORITHM TEST SUITE")
    print("="*70)
    print(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Get absolute paths
    test_dir = os.path.dirname(os.path.abspath(__file__))
    unit_dir = os.path.join(test_dir, 'unit')
    logic_dir = os.path.join(test_dir, 'logic')

    # Add unit tests
    print("Loading Unit Tests...")
    unit_tests = loader.discover(unit_dir, pattern='test_*.py')
    suite.addTests(unit_tests)
    unit_test_count = unit_tests.countTestCases()
    print(f"  ✓ Loaded {unit_test_count} unit tests")

    # Add logic tests
    print("Loading Logic Tests...")
    logic_tests = loader.discover(logic_dir, pattern='test_*.py')
    suite.addTests(logic_tests)
    logic_test_count = logic_tests.countTestCases()
    print(f"  ✓ Loaded {logic_test_count} logic tests")

    print()
    print(f"Total Tests: {suite.countTestCases()}")
    print("="*70)
    print()

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("="*70)
    print(" TEST SUMMARY")
    print("="*70)
    print(f" Tests Run:    {result.testsRun}")
    print(f" Successes:    {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" Failures:     {len(result.failures)}")
    print(f" Errors:       {len(result.errors)}")
    print(f" Skipped:      {len(result.skipped)}")
    print("="*70)

    if result.wasSuccessful():
        print(" ✓ ALL TESTS PASSED!")
    else:
        print(" ✗ SOME TESTS FAILED")

    print(f" Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    return result.wasSuccessful()


def run_specific_test(test_file):
    """Run a specific test file"""
    print(f"Running tests from {test_file}...")
    print("="*70)

    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern=test_file)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run Cultural Algorithm tests')
    parser.add_argument('--file', '-f', help='Run specific test file')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--logic', action='store_true', help='Run only logic tests')

    args = parser.parse_args()

    # Get absolute paths
    test_dir = os.path.dirname(os.path.abspath(__file__))
    unit_dir = os.path.join(test_dir, 'unit')
    logic_dir = os.path.join(test_dir, 'logic')

    if args.file:
        success = run_specific_test(args.file)
    elif args.unit:
        print("Running Unit Tests Only...")
        print("="*70)
        loader = unittest.TestLoader()
        suite = loader.discover(unit_dir, pattern='test_*.py')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        success = result.wasSuccessful()
    elif args.logic:
        print("Running Logic Tests Only...")
        print("="*70)
        loader = unittest.TestLoader()
        suite = loader.discover(logic_dir, pattern='test_*.py')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        success = result.wasSuccessful()
    else:
        success = run_test_suite()

    sys.exit(0 if success else 1)
