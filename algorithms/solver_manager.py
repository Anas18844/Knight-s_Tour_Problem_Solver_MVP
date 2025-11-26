import time
from typing import Dict, Tuple, Optional, Any


class SolverManager:

    def __init__(self):
        """Initialize the solver manager with empty solver registry."""
        self.solvers: Dict[Tuple[str, int], Any] = {}
        self._register_default_solvers()

    def _register_default_solvers(self):
        from algorithms.backtracking import RandomKnightWalk as BTRandomWalk, OrderedKnightWalk, PureBacktracking, EnhancedBacktracking, BacktrackingSolver
        from algorithms.cultural import RandomKnightWalk as CARandomWalk, SimpleGASolver, EnhancedGASolver, CulturalGASolver, CulturalAlgorithmSolver
        from algorithms.level0_random import RandomKnightWalk

        self.solvers[("Random Walk", 0)] = RandomKnightWalk
        self.solvers[("Backtracking", 0)] = BTRandomWalk
        self.solvers[("Ordered Walk", 1)] = OrderedKnightWalk
        self.solvers[("Backtracking", 1)] = OrderedKnightWalk
        self.solvers[("Pure Backtracking", 2)] = PureBacktracking
        self.solvers[("Backtracking", 2)] = PureBacktracking
        self.solvers[("Enhanced Backtracking", 3)] = EnhancedBacktracking
        self.solvers[("Backtracking", 3)] = EnhancedBacktracking
        self.solvers[("Backtracking", 4)] = BacktrackingSolver
        self.solvers[("Cultural Algorithm", 0)] = CARandomWalk
        self.solvers[("Simple GA", 1)] = SimpleGASolver
        self.solvers[("Cultural Algorithm", 1)] = SimpleGASolver
        self.solvers[("Enhanced GA", 2)] = EnhancedGASolver
        self.solvers[("Cultural Algorithm", 2)] = EnhancedGASolver
        self.solvers[("Cultural GA", 3)] = CulturalGASolver
        self.solvers[("Cultural Algorithm", 3)] = CulturalGASolver
        self.solvers[("Cultural Algorithm", 4)] = CulturalAlgorithmSolver

    def register_solver(self, algorithm_name: str, level: int, solver_class):
        self.solvers[(algorithm_name, level)] = solver_class

    def solve(self, algorithm_name: str, level: int, N: int, start_pos: Tuple[int, int],
              timeout: float = 60.0) -> Dict[str, Any]:
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

            if "Random Walk" in algorithm_name or "Ordered Walk" in algorithm_name or "Pure Backtracking" in algorithm_name or "Enhanced Backtracking" in algorithm_name or "Simple GA" in algorithm_name or "Enhanced GA" in algorithm_name or "Cultural GA" in algorithm_name or (algorithm_name == "Cultural Algorithm" and level in [0, 1, 2, 3]):
                solver = solver_class(n=N, level=level)
                success, path = solver.solve(start_x, start_y)

                unique_squares = len(set(path)) if path else 0
                stats = {
                    'total_moves': getattr(solver, 'total_moves', 0),
                    'dead_ends_hit': getattr(solver, 'dead_ends_hit', 0),
                    'coverage_percent': 100 * unique_squares / (N * N) if N > 0 else 0,
                    'recursive_calls': getattr(solver, 'recursive_calls', 0),
                    'backtrack_count': getattr(solver, 'backtrack_count', 0),
                    'best_fitness': getattr(solver, 'best_fitness', 0),
                    'generations': getattr(solver, 'generations', 0),
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
        print(f"Selecting optimal solver for {N}x{N} board...")

        # For most cases, Backtracking Level 1 with Warnsdorff is optimal
        result = self.solve("Backtracking", 1, N, start_pos, timeout)

        # If Backtracking failed or timed out on large board, try Cultural Algorithm
        if not result['success'] and N >= 11:
            print("Backtracking failed, trying Cultural Algorithm...")
            result = self.solve("Cultural Algorithm", 1, N, start_pos, timeout)

        return result

    def get_available_solvers(self) -> Dict[str, list]:
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
