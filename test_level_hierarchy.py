"""
Comprehensive test for the level hierarchy system.

Tests:
1. Level 0 - Random Walk (non-deterministic)
2. Level 1 - Ordered Walk (deterministic, inherits from Level 0)
3. Level 4 - Backtracking (production solver)
4. SolverManager integration
5. GUI compatibility
"""

from algorithms import RandomKnightWalk, OrderedKnightWalk, BacktrackingSolver, SolverManager


def test_level0():
    """Test Level 0 - Random Walk."""
    print("="*70)
    print("TEST 1: Level 0 - Random Walk (Non-deterministic)")
    print("="*70)

    # Run 3 times, should get different results
    results = []
    for i in range(3):
        solver = RandomKnightWalk(n=6, level=0)
        success, path = solver.solve(2, 2)
        results.append(len(path))
        print(f"  Run {i+1}: {len(path)}/36 squares")

    # Check variance
    if len(set(results)) > 1:
        print("[OK] Results vary - non-deterministic as expected")
    else:
        print("[WARNING] All results identical - should be random!")

    return all(r > 0 for r in results)


def test_level1():
    """Test Level 1 - Ordered Walk (deterministic)."""
    print("\n" + "="*70)
    print("TEST 2: Level 1 - Ordered Walk (Deterministic)")
    print("="*70)

    # Run 3 times, should get SAME result
    paths = []
    for i in range(3):
        solver = OrderedKnightWalk(n=6, level=1)
        success, path = solver.solve(2, 2)
        paths.append(path)
        print(f"  Run {i+1}: {len(path)}/36 squares")

    # Check if all paths are identical
    if paths[0] == paths[1] == paths[2]:
        print("[OK] All paths identical - fully deterministic!")
        return True
    else:
        print("[ERROR] Paths differ - should be deterministic!")
        return False


def test_inheritance():
    """Test that Level 1 properly inherits from Level 0."""
    print("\n" + "="*70)
    print("TEST 3: Inheritance Structure")
    print("="*70)

    # Check inheritance
    print(f"  OrderedKnightWalk base class: {OrderedKnightWalk.__bases__[0].__name__}")

    if issubclass(OrderedKnightWalk, RandomKnightWalk):
        print("[OK] Level 1 inherits from Level 0")

        # Check that only select_move is overridden
        level0 = RandomKnightWalk(5, 0)
        level1 = OrderedKnightWalk(5, 1)

        # Both should have same methods
        level0_methods = set(dir(level0))
        level1_methods = set(dir(level1))

        if level0_methods == level1_methods:
            print("[OK] Level 1 has same methods as Level 0")
        else:
            print("[WARNING] Method sets differ")

        return True
    else:
        print("[ERROR] Level 1 does not inherit from Level 0!")
        return False


def test_level4():
    """Test Level 4 - Backtracking."""
    print("\n" + "="*70)
    print("TEST 4: Level 4 - Backtracking with Warnsdorff")
    print("="*70)

    solver = BacktrackingSolver(board_size=6, start_pos=(2, 2), timeout=10.0)
    success, path, stats = solver.solve()

    print(f"  Success: {success}")
    print(f"  Path length: {len(path)}/36")
    print(f"  Execution time: {stats.get('execution_time', 'N/A'):.4f}s")

    if success and len(path) == 36:
        print("[OK] Level 4 completes full tour")
        return True
    else:
        print("[WARNING] Level 4 did not complete tour")
        return False


def test_solver_manager():
    """Test SolverManager integration."""
    print("\n" + "="*70)
    print("TEST 5: SolverManager Integration")
    print("="*70)

    manager = SolverManager()

    # Check registered solvers
    available = manager.get_available_solvers()

    print("  Registered solvers:")
    for algo, levels in available.items():
        print(f"    {algo}: Levels {levels}")

    # Test Level 0
    print("\n  Testing Level 0 via SolverManager:")
    result0 = manager.solve("Random Walk", 0, 6, (2, 2))
    print(f"    Coverage: {result0['stats']['coverage_percent']:.1f}%")

    # Test Level 1
    print("\n  Testing Level 1 via SolverManager:")
    result1 = manager.solve("Ordered Walk", 1, 6, (2, 2))
    print(f"    Coverage: {result1['stats']['coverage_percent']:.1f}%")

    # Test Level 4
    print("\n  Testing Level 4 via SolverManager:")
    result4 = manager.solve("Backtracking", 4, 6, (2, 2))
    print(f"    Success: {result4['success']}")

    # Check that Level 1 is deterministic via SolverManager
    result1_check = manager.solve("Ordered Walk", 1, 6, (2, 2))
    if result1['path'] == result1_check['path']:
        print("[OK] Level 1 deterministic through SolverManager")
    else:
        print("[ERROR] Level 1 non-deterministic through SolverManager")
        return False

    return result4['success']


def test_performance_comparison():
    """Compare performance across levels."""
    print("\n" + "="*70)
    print("TEST 6: Performance Comparison (8x8 board)")
    print("="*70)

    manager = SolverManager()
    board_size = 8
    start = (3, 3)

    # Level 0 - Random (average of 3 runs)
    print("\n  Level 0 (Random Walk):")
    level0_coverages = []
    for _ in range(3):
        result = manager.solve("Random Walk", 0, board_size, start)
        level0_coverages.append(result['stats']['coverage_percent'])
    avg_coverage = sum(level0_coverages) / len(level0_coverages)
    print(f"    Average coverage: {avg_coverage:.1f}%")

    # Level 1 - Ordered
    print("\n  Level 1 (Ordered Walk):")
    result1 = manager.solve("Ordered Walk", 1, board_size, start)
    print(f"    Coverage: {result1['stats']['coverage_percent']:.1f}%")
    print(f"    Time: {result1['execution_time']:.4f}s")

    # Level 4 - Backtracking
    print("\n  Level 4 (Backtracking):")
    result4 = manager.solve("Backtracking", 4, board_size, start)
    print(f"    Success: {result4['success']}")
    print(f"    Time: {result4['execution_time']:.4f}s")

    # Summary
    print("\n  Performance Summary:")
    print(f"    Level 0: ~{avg_coverage:.0f}% coverage (random)")
    print(f"    Level 1: {result1['stats']['coverage_percent']:.0f}% coverage (deterministic)")
    print(f"    Level 4: {'100%' if result4['success'] else 'Failed'} (intelligent)")

    return True


def test_gui_compatibility():
    """Test GUI compatibility."""
    print("\n" + "="*70)
    print("TEST 7: GUI Compatibility")
    print("="*70)

    try:
        from gui.main_window import KnightTourGUI
        print("[OK] GUI imports successfully")

        # Check that all levels can be imported in GUI context
        from algorithms.level0_random import RandomKnightWalk
        from algorithms.level1_ordered import OrderedKnightWalk
        from algorithms.backtracking import BacktrackingSolver

        print("[OK] All level classes importable in GUI context")

        return True
    except Exception as e:
        print(f"[ERROR] GUI compatibility issue: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("LEVEL HIERARCHY COMPREHENSIVE TEST")
    print("="*70)

    tests = [
        ("Level 0 - Random Walk", test_level0),
        ("Level 1 - Ordered Walk", test_level1),
        ("Inheritance Structure", test_inheritance),
        ("Level 4 - Backtracking", test_level4),
        ("SolverManager", test_solver_manager),
        ("Performance Comparison", test_performance_comparison),
        ("GUI Compatibility", test_gui_compatibility),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n[ERROR] {name} failed with exception: {e}")
            results[name] = False

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {name}")

    total = len(results)
    passed = sum(results.values())

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n[OK] All tests PASSED! Level hierarchy working correctly.")
    else:
        print(f"\n[WARNING] {total - passed} test(s) FAILED!")

    print("="*70)


if __name__ == "__main__":
    main()
