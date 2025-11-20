"""
SolverManager - Unified interface for all Knight's Tour solvers.

This module provides a clean, modular way to manage and run different
algorithm implementations at various levels.
"""

import time
from typing import Dict, Tuple, Optional, Any


class SolverManager:
    """
    Manages all Knight's Tour solver algorithms and levels.

    Stores solvers in a dictionary: solvers[(algorithm_name, level)] = SolverInstance
    Provides unified interface for running and comparing solvers.
    """

    def __init__(self):
        """Initialize the solver manager with empty solver registry."""
        self.solvers: Dict[Tuple[str, int], Any] = {}
        self._register_default_solvers()

    def _register_default_solvers(self):
        """Register all available solver implementations."""
        # Import solvers here to avoid circular imports
        from algorithms.backtracking import BacktrackingSolver
        from algorithms.cultural import CulturalAlgorithmSolver
        from algorithms.level0_random import RandomKnightWalk
        from algorithms.level1_ordered import OrderedKnightWalk

        # Register Level 0 - Random Walk (baseline)
        self.solvers[("Random Walk", 0)] = RandomKnightWalk

        # Register Level 1 - Ordered Walk (deterministic baseline)
        self.solvers[("Ordered Walk", 1)] = OrderedKnightWalk

        # Level 2 and 3 will be added in future

        # Register Level 4 - Backtracking with Warnsdorff's Heuristic
        self.solvers[("Backtracking", 4)] = BacktrackingSolver

        # Register Cultural Algorithm solvers
        self.solvers[("Cultural Algorithm", 1)] = CulturalAlgorithmSolver

    def register_solver(self, algorithm_name: str, level: int, solver_class):
        """
        Register a new solver implementation.

        Args:
            algorithm_name: Name of the algorithm (e.g., "Backtracking")
            level: Level number (0, 1, 2, 3, etc.)
            solver_class: The solver class to instantiate
        """
        self.solvers[(algorithm_name, level)] = solver_class

    def solve(self, algorithm_name: str, level: int, N: int, start_pos: Tuple[int, int],
              timeout: float = 60.0) -> Dict[str, Any]:
        """
        Main solving method - runs specified algorithm at given level.

        Args:
            algorithm_name: Name of algorithm ("Backtracking", "Cultural Algorithm", etc.)
            level: Algorithm level (0, 1, 2, 3)
            N: Board size (NxN)
            start_pos: Starting position as (x, y) tuple
            timeout: Maximum solving time in seconds

        Returns:
            Dictionary with unified result format:
            {
                'success': bool,
                'path': List[Tuple[int, int]],
                'execution_time': float,
                'algorithm': str,
                'level': int,
                'board_size': int,
                'start_position': Tuple[int, int],
                'solution_length': int,
                'stats': {
                    'recursive_calls': int,
                    'backtrack_count': int,
                    'nodes_explored': int,
                    # ... other algorithm-specific stats
                }
            }
        """
        # Get solver class
        solver_key = (algorithm_name, level)
        if solver_key not in self.solvers:
            return {
                'success': False,
                'error': f"Solver not found: {algorithm_name} Level {level}",
                'algorithm': algorithm_name,
                'level': level,
                'board_size': N,
                'start_position': start_pos,
                'execution_time': 0.0,
                'path': [],
                'solution_length': 0,
                'stats': {}
            }

        # Create solver instance
        solver_class = self.solvers[solver_key]
        start_x, start_y = start_pos

        # Measure execution time
        start_time = time.time()

        try:
            # Different solvers have different initialization patterns
            # Random Walk (Level 0): __init__(n, level=0, timeout=60.0)
            # Ordered Walk (Level 1): __init__(n, level=1, timeout=60.0)
            # Backtracking (Level 4): __init__(board_size, start_pos, timeout=60.0)
            # Cultural: __init__(board_size, start_pos, timeout=60.0)

            if "Random Walk" in algorithm_name or "Ordered Walk" in algorithm_name:
                solver = solver_class(n=N, level=level, timeout=timeout)
                success, path = solver.solve(start_x, start_y)

                # Extract stats from walk solvers (Level 0 and 1)
                stats = {
                    'total_moves': getattr(solver, 'total_moves', 0),
                    'dead_ends_hit': getattr(solver, 'dead_ends_hit', 0),
                    'coverage_percent': 100 * len(path) / (N * N) if N > 0 else 0,
                }

            elif "Backtracking" in algorithm_name:
                solver = solver_class(board_size=N, start_pos=start_pos, timeout=timeout)
                success, path, solve_stats = solver.solve()

                # Extract stats from backtracking solver
                stats = {
                    'recursive_calls': getattr(solver, 'recursive_calls', 0),
                    'backtrack_count': solve_stats.get('backtrack_count', 0),
                    'nodes_explored': getattr(solver, 'recursive_calls', 0),
                }

            elif "Cultural" in algorithm_name:
                solver = solver_class(board_size=N, start_pos=start_pos, timeout=timeout)
                success, path, solve_stats = solver.solve()

                # Extract stats from cultural algorithm solver
                stats = {
                    'generations': solve_stats.get('generations_run', 0),
                    'population_size': solve_stats.get('population_size', 0),
                    'best_fitness': solve_stats.get('best_fitness', 0),
                }

            else:
                # Generic solver interface
                solver = solver_class(N, level=level, timeout=timeout)
                success, path = solver.solve(start_x, start_y)
                stats = {}

            execution_time = time.time() - start_time

            # Build unified result dictionary
            result = {
                'success': success,
                'path': path if success else [],
                'execution_time': execution_time,
                'algorithm': algorithm_name,
                'level': level,
                'board_size': N,
                'start_position': start_pos,
                'solution_length': len(path) if success else 0,
                'stats': stats
            }

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'algorithm': algorithm_name,
                'level': level,
                'board_size': N,
                'start_position': start_pos,
                'execution_time': execution_time,
                'path': [],
                'solution_length': 0,
                'stats': {}
            }

    def run_all_backtracking_levels(self, N: int, start_pos: Tuple[int, int],
                                   timeout: float = 60.0) -> Dict[int, Dict[str, Any]]:
        """
        Run all available Backtracking levels and return results.

        Args:
            N: Board size
            start_pos: Starting position
            timeout: Timeout for each level

        Returns:
            Dictionary mapping level -> result dict
        """
        results = {}

        # Find all registered backtracking levels
        backtracking_levels = [level for (algo, level) in self.solvers.keys()
                              if algo == "Backtracking"]

        for level in sorted(backtracking_levels):
            print(f"Running Backtracking Level {level}...")
            result = self.solve("Backtracking", level, N, start_pos, timeout)
            results[level] = result

        return results

    def run_all_ca_levels(self, N: int, start_pos: Tuple[int, int],
                         timeout: float = 60.0) -> Dict[int, Dict[str, Any]]:
        """
        Run all available Cultural Algorithm levels and return results.

        Args:
            N: Board size
            start_pos: Starting position
            timeout: Timeout for each level

        Returns:
            Dictionary mapping level -> result dict
        """
        results = {}

        # Find all registered cultural algorithm levels
        ca_levels = [level for (algo, level) in self.solvers.keys()
                    if algo == "Cultural Algorithm"]

        for level in sorted(ca_levels):
            print(f"Running Cultural Algorithm Level {level}...")
            result = self.solve("Cultural Algorithm", level, N, start_pos, timeout)
            results[level] = result

        return results

    def compare_best_levels(self, N: int, start_pos: Tuple[int, int],
                           timeout: float = 60.0) -> Dict[str, Dict[str, Any]]:
        """
        Run the best level of each algorithm and compare results.

        Args:
            N: Board size
            start_pos: Starting position
            timeout: Timeout for each solver

        Returns:
            Dictionary with comparison results:
            {
                'Backtracking': result_dict,
                'Cultural Algorithm': result_dict,
                'fastest': algorithm_name,
                'most_efficient': algorithm_name
            }
        """
        comparison = {}

        # Run best Backtracking level (Level 1 for now)
        if ("Backtracking", 1) in self.solvers:
            print("Running best Backtracking level...")
            comparison['Backtracking'] = self.solve("Backtracking", 1, N, start_pos, timeout)

        # Run best Cultural Algorithm level (Level 1 for now)
        if ("Cultural Algorithm", 1) in self.solvers:
            print("Running best Cultural Algorithm level...")
            comparison['Cultural Algorithm'] = self.solve("Cultural Algorithm", 1, N, start_pos, timeout)

        # Determine fastest
        fastest_algo = None
        fastest_time = float('inf')
        for algo_name, result in comparison.items():
            # Skip if result is not a dict (avoid processing metadata keys)
            if not isinstance(result, dict):
                continue
            if result.get('success', False) and result['execution_time'] < fastest_time:
                fastest_time = result['execution_time']
                fastest_algo = algo_name

        comparison['fastest'] = fastest_algo

        # Determine most efficient (fewest nodes explored for successful solutions)
        most_efficient = None
        fewest_nodes = float('inf')
        for algo_name, result in comparison.items():
            # Skip if result is not a dict (avoid processing metadata keys)
            if not isinstance(result, dict):
                continue
            if result.get('success', False):
                nodes = result['stats'].get('recursive_calls',
                       result['stats'].get('nodes_explored', float('inf')))
                if nodes < fewest_nodes:
                    fewest_nodes = nodes
                    most_efficient = algo_name

        comparison['most_efficient'] = most_efficient

        return comparison

    def run_optimal(self, N: int, start_pos: Tuple[int, int],
                   timeout: float = 60.0) -> Dict[str, Any]:
        """
        Automatically select and run the optimal solver for given board size.

        Strategy:
        - Small boards (5-8): Use Backtracking Level 1 (fastest)
        - Medium boards (9-10): Use Backtracking Level 1
        - Large boards (11+): Try Cultural Algorithm if Backtracking times out

        Args:
            N: Board size
            start_pos: Starting position
            timeout: Maximum time allowed

        Returns:
            Result dictionary from optimal solver
        """
        print(f"Selecting optimal solver for {N}x{N} board...")

        # For most cases, Backtracking Level 1 with Warnsdorff is optimal
        result = self.solve("Backtracking", 1, N, start_pos, timeout)

        # If Backtracking failed or timed out on large board, try Cultural Algorithm
        if not result['success'] and N >= 11:
            print("Backtracking failed, trying Cultural Algorithm...")
            result = self.solve("Cultural Algorithm", 1, N, start_pos, timeout)

        return result

    def get_available_solvers(self) -> Dict[str, list]:
        """
        Get list of all available solvers organized by algorithm.

        Returns:
            Dictionary mapping algorithm name -> list of available levels
        """
        algorithms = {}

        for (algo_name, level) in self.solvers.keys():
            if algo_name not in algorithms:
                algorithms[algo_name] = []
            algorithms[algo_name].append(level)

        # Sort levels
        for algo_name in algorithms:
            algorithms[algo_name].sort()

        return algorithms

    def print_available_solvers(self):
        """Print all available solvers to console."""
        available = self.get_available_solvers()

        print("\n=== Available Knight's Tour Solvers ===")
        for algo_name, levels in available.items():
            print(f"\n{algo_name}:")
            for level in levels:
                print(f"  - Level {level}")
        print("\n" + "="*40)


# Example usage
if __name__ == "__main__":
    # Create manager
    manager = SolverManager()

    # Show available solvers
    manager.print_available_solvers()

    # Test solve
    print("\n--- Testing 8x8 board from (0,0) ---")
    result = manager.solve("Backtracking", 1, 8, (0, 0))

    print(f"\nSuccess: {result['success']}")
    print(f"Time: {result['execution_time']:.4f}s")
    print(f"Solution length: {result['solution_length']}")
    print(f"Recursive calls: {result['stats'].get('recursive_calls', 'N/A')}")

    # Test optimal solver
    print("\n--- Testing optimal solver for 8x8 ---")
    result = manager.run_optimal(8, (0, 0))
    print(f"Success: {result['success']}")
    print(f"Time: {result['execution_time']:.4f}s")
