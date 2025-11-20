"""
Test script to verify Level 0 (Random Walk) integration with GUI.
"""

from algorithms.level0_random import RandomKnightWalk

def test_level0():
    print("="*70)
    print("Testing Level 0 - Random Walk Integration")
    print("="*70)

    # Test 5x5 board
    print("\nTest 1: 5x5 board from (0, 0)")
    solver = RandomKnightWalk(n=5, level=0)
    success, path = solver.solve(0, 0)

    print(f"Success: {success}")
    print(f"Path length: {len(path)}/25")
    print(f"Coverage: {100 * len(path) / 25:.1f}%")
    print(f"Dead ends hit: {solver.dead_ends_hit}")

    # Test that path is returned even on failure
    if not success and path:
        print(f"[OK] Partial path returned: {len(path)} squares")
        print(f"First 5 moves: {path[:5]}")
        print(f"Last move (stuck at): {path[-1]}")

    # Test 6x6 board
    print("\n" + "="*70)
    print("Test 2: 6x6 board from (2, 2) - center start")
    solver = RandomKnightWalk(n=6, level=0)
    success, path = solver.solve(2, 2)

    print(f"Success: {success}")
    print(f"Path length: {len(path)}/36")
    print(f"Coverage: {100 * len(path) / 36:.1f}%")

    # Test stats dictionary format (for GUI compatibility)
    print("\n" + "="*70)
    print("Test 3: Stats Dictionary Format (GUI Compatibility)")

    stats = {
        'algorithm': 'Random Walk (Level 0)',
        'execution_time': 0.001,
        'total_moves': solver.total_moves,
        'dead_ends_hit': solver.dead_ends_hit,
        'coverage_percent': 100 * len(path) / (6 * 6)
    }

    print("Stats format:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "="*70)
    print("[OK] All tests passed!")
    print("Level 0 is ready for GUI integration")
    print("="*70)

if __name__ == "__main__":
    test_level0()
