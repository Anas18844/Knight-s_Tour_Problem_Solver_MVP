"""Unit tests for Cultural Algorithm."""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.cultural import CulturalAlgorithmSolver, Individual, BeliefSpace


class TestIndividual:
    """Test cases for Individual class."""

    def test_initialization(self):
        """Test individual initialization."""
        ind = Individual(board_size=8, start_pos=(0, 0))

        assert ind.board_size == 8
        assert ind.start_pos == (0, 0)
        assert len(ind.path) == 1
        assert ind.path[0] == (0, 0)
        assert (0, 0) in ind.visited
        assert ind.fitness == 0

    def test_add_move(self):
        """Test adding moves to individual."""
        ind = Individual(board_size=8, start_pos=(0, 0))

        ind.add_move((2, 1))
        assert len(ind.path) == 2
        assert (2, 1) in ind.visited
        assert ind.path[-1] == (2, 1)


class TestBeliefSpace:
    """Test cases for BeliefSpace class."""

    def test_initialization(self):
        """Test belief space initialization."""
        bs = BeliefSpace(board_size=8)

        assert bs.board_size == 8
        assert bs.best_fitness == 0
        assert len(bs.best_path) == 0
        assert len(bs.valid_knight_moves) == 8

    def test_update_with_individuals(self):
        """Test belief space update."""
        bs = BeliefSpace(board_size=8)

        # Create individuals
        ind1 = Individual(board_size=8, start_pos=(0, 0))
        ind1.fitness = 10
        ind1.add_move((2, 1))
        ind1.add_move((3, 3))

        ind2 = Individual(board_size=8, start_pos=(0, 0))
        ind2.fitness = 20
        ind2.add_move((1, 2))

        individuals = [ind1, ind2]
        bs.update(individuals)

        # Best fitness should be updated
        assert bs.best_fitness == 20
        assert bs.best_solution.fitness == 20


class TestCulturalAlgorithmSolver:
    """Test cases for CulturalAlgorithmSolver."""

    def test_initialization(self):
        """Test solver initialization."""
        solver = CulturalAlgorithmSolver(board_size=8, start_pos=(0, 0),
                                        population_size=50, max_generations=100)

        assert solver.board_size == 8
        assert solver.start_pos == (0, 0)
        assert solver.population_size == 50
        assert solver.max_generations == 100
        assert isinstance(solver.belief_space, BeliefSpace)

    def test_valid_move_detection(self):
        """Test valid move detection."""
        solver = CulturalAlgorithmSolver(board_size=8)

        assert solver.is_valid_move(0, 0) == True
        assert solver.is_valid_move(7, 7) == True
        assert solver.is_valid_move(-1, 0) == False
        assert solver.is_valid_move(8, 0) == False

    def test_get_valid_moves(self):
        """Test getting valid moves."""
        solver = CulturalAlgorithmSolver(board_size=8)

        visited = {(0, 0)}
        moves = solver.get_valid_moves((0, 0), visited)

        # From (0,0) knight can move to 2 positions
        assert len(moves) == 2
        assert all(m not in visited for m in moves)

    def test_fitness_calculation(self):
        """Test fitness calculation."""
        solver = CulturalAlgorithmSolver(board_size=8)

        ind = Individual(board_size=8, start_pos=(0, 0))
        ind.add_move((2, 1))
        ind.add_move((3, 3))

        fitness = solver.calculate_fitness(ind)

        # Fitness should be at least the number of unique squares
        assert fitness >= len(ind.visited)

    def test_create_individual(self):
        """Test individual creation."""
        solver = CulturalAlgorithmSolver(board_size=8)
        individual = solver.create_individual()

        assert isinstance(individual, Individual)
        assert individual.board_size == 8
        assert len(individual.path) >= 1
        assert individual.fitness > 0

        # Verify path contains valid knight moves
        for i in range(len(individual.path) - 1):
            x1, y1 = individual.path[i]
            x2, y2 = individual.path[i + 1]
            dx, dy = abs(x2 - x1), abs(y2 - y1)
            assert (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

    def test_initialize_population(self):
        """Test population initialization."""
        solver = CulturalAlgorithmSolver(board_size=8, population_size=20)
        solver.initialize_population()

        assert len(solver.population) == 20
        assert all(isinstance(ind, Individual) for ind in solver.population)
        assert all(ind.fitness > 0 for ind in solver.population)

    def test_select_parents(self):
        """Test parent selection."""
        solver = CulturalAlgorithmSolver(board_size=8, population_size=20)
        solver.initialize_population()

        parent1, parent2 = solver.select_parents()

        assert isinstance(parent1, Individual)
        assert isinstance(parent2, Individual)
        assert parent1 in solver.population
        assert parent2 in solver.population

    def test_crossover(self):
        """Test crossover operation."""
        solver = CulturalAlgorithmSolver(board_size=8)

        parent1 = solver.create_individual()
        parent2 = solver.create_individual()

        offspring = solver.crossover(parent1, parent2)

        assert isinstance(offspring, Individual)
        assert offspring.board_size == 8
        assert len(offspring.path) >= 1
        assert offspring.path[0] == solver.start_pos

    def test_mutation(self):
        """Test mutation operation."""
        solver = CulturalAlgorithmSolver(board_size=8)
        individual = solver.create_individual()

        original_path_len = len(individual.path)
        solver.mutate(individual, mutation_rate=1.0)  # Force mutation

        # Path should be modified
        assert isinstance(individual, Individual)
        assert len(individual.path) >= 1

    def test_evolve_generation(self):
        """Test generation evolution."""
        solver = CulturalAlgorithmSolver(board_size=6, population_size=20)
        solver.initialize_population()

        initial_pop = solver.population.copy()
        solver.evolve_generation()

        # Population size should remain constant
        assert len(solver.population) == 20

        # Some individuals should be different (not all elite)
        different = sum(1 for i in range(20) if solver.population[i] != initial_pop[i])
        assert different > 0

    def test_solve_small_board(self):
        """Test solving a small board."""
        solver = CulturalAlgorithmSolver(board_size=5, start_pos=(0, 0),
                                        population_size=50,
                                        max_generations=100,
                                        timeout=10.0)

        success, path, stats = solver.solve()

        assert isinstance(success, bool)
        assert isinstance(path, list)
        assert isinstance(stats, dict)

        # Verify statistics
        assert 'execution_time' in stats
        assert 'generations' in stats
        assert 'best_fitness' in stats
        assert 'algorithm' in stats

        if success:
            assert len(path) == 25  # 5x5 board
            assert path[0] == (0, 0)

    def test_timeout_handling(self):
        """Test timeout functionality."""
        solver = CulturalAlgorithmSolver(board_size=10, timeout=0.001)
        success, path, stats = solver.solve()

        # Should timeout and return partial solution
        assert isinstance(stats, dict)
        if stats.get('timed_out'):
            assert 'error' in stats


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
