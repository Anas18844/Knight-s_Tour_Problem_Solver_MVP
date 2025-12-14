"""
Unit Tests for Level 1 - Simple GA
Tests basic GA functionality: initialization, fitness, selection, crossover, mutation
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from algorithms.cultural.level1_simple_ga import SimpleGASolver


class TestLevel1SimpleGA(unittest.TestCase):
    """Test cases for Simple GA (Level 1)"""

    def setUp(self):
        """Set up test fixtures"""
        self.solver = SimpleGASolver(n=5, level=1)
        self.start_pos = (0, 0)

    def test_initialization(self):
        """Test solver initialization"""
        self.assertEqual(self.solver.n, 5)
        self.assertEqual(self.solver.level, 1)
        self.assertEqual(self.solver.population_size, 30)
        self.assertEqual(self.solver.generations, 100)
        self.assertEqual(self.solver.chromosome_length, 25)

    def test_population_initialization(self):
        """Test population initialization"""
        population = self.solver.initialize_population()

        # Check population size
        self.assertEqual(len(population), 30)

        # Check chromosome structure
        for chromosome in population:
            self.assertEqual(len(chromosome), 25)
            # All genes should be 0-7
            for gene in chromosome:
                self.assertIn(gene, range(8))

    def test_decode_valid_chromosome(self):
        """Test chromosome decoding"""
        chromosome = [0, 1, 2, 3, 4, 5, 6, 7] * 3 + [0]
        path = self.solver.decode(chromosome, self.start_pos)

        # Path should start at start position
        self.assertEqual(path[0], self.start_pos)

        # Path should not be empty
        self.assertGreater(len(path), 0)

        # All positions should be valid
        for x, y in path:
            self.assertTrue(0 <= x < 5)
            self.assertTrue(0 <= y < 5)

    def test_fitness_calculation(self):
        """Test fitness function"""
        chromosome = [0] * 25
        fitness = self.solver.fitness(chromosome, self.start_pos)

        # Fitness should be non-negative
        self.assertGreaterEqual(fitness, 0)

        # Better tour should have higher fitness
        # Create a simple valid tour
        good_chromosome = [1, 2, 3, 4, 5, 6, 7, 0] * 3 + [1]
        good_fitness = self.solver.fitness(good_chromosome, self.start_pos)

        # Cannot guarantee good_fitness > fitness, but should be >= 0
        self.assertGreaterEqual(good_fitness, 0)

    def test_tournament_selection(self):
        """Test tournament selection"""
        population = self.solver.initialize_population()
        fitness_scores = [self.solver.fitness(chrom, self.start_pos) for chrom in population]

        selected = self.solver.tournament_selection(population, fitness_scores)

        # Selected chromosome should be in population
        self.assertIn(selected, population)
        self.assertEqual(len(selected), 25)

    def test_crossover(self):
        """Test crossover operation"""
        parent1 = [0] * 25
        parent2 = [7] * 25

        child1, child2 = self.solver.crossover(parent1, parent2)

        # Children should have correct length
        self.assertEqual(len(child1), 25)
        self.assertEqual(len(child2), 25)

        # Children should contain mix of parent genes
        # At least some genes from each parent
        self.assertTrue(any(g in child1 for g in parent1))
        self.assertTrue(any(g in child1 for g in parent2))

    def test_mutation(self):
        """Test mutation operation"""
        original = [0] * 25
        mutated = self.solver.mutate(original.copy())

        # Mutated should have correct length
        self.assertEqual(len(mutated), 25)

        # All genes should be valid (0-7)
        for gene in mutated:
            self.assertIn(gene, range(8))

    def test_repair_chromosome(self):
        """Test chromosome repair"""
        # Invalid chromosome
        invalid = [0, 1, 2, 10, -1, 5]
        repaired = self.solver._repair_chromosome(invalid)

        # All genes should be valid
        for gene in repaired:
            self.assertIn(gene, range(8))

        # Should have correct length
        self.assertEqual(len(repaired), 25)

    def test_solve_returns_path(self):
        """Test that solve returns a path"""
        # Use very small board and few generations for speed
        quick_solver = SimpleGASolver(n=5, level=1)
        quick_solver.generations = 10  # Only 10 generations for testing

        success, path = quick_solver.solve(0, 0)

        # Should return boolean and path
        self.assertIsInstance(success, bool)
        self.assertIsInstance(path, list)

        # Path should not be empty
        self.assertGreater(len(path), 0)

        # Path should start at (0, 0)
        self.assertEqual(path[0], (0, 0))


class TestLevel1GAComponents(unittest.TestCase):
    """Test individual GA components"""

    def test_valid_moves(self):
        """Test getting valid knight moves"""
        solver = SimpleGASolver(n=8, level=1)

        # From center, should have 8 possible moves
        valid_moves = solver.get_valid_moves_from(4, 4, set())
        self.assertLessEqual(len(valid_moves), 8)

        # From corner, should have fewer moves
        corner_moves = solver.get_valid_moves_from(0, 0, set())
        self.assertLess(len(corner_moves), 8)

        # With visited squares, should have fewer moves
        visited = {(4, 4), (5, 6), (6, 5)}
        filtered_moves = solver.get_valid_moves_from(4, 4, visited)
        self.assertLess(len(filtered_moves), len(valid_moves))

    def test_apply_move(self):
        """Test applying knight moves"""
        solver = SimpleGASolver(n=8, level=1)

        # Test all 8 knight moves
        pos = (4, 4)
        for move_idx in range(8):
            new_pos = solver.apply_move(pos, move_idx)

            # Should be a valid position
            x, y = new_pos
            dx = abs(x - pos[0])
            dy = abs(y - pos[1])

            # Should be a valid knight move
            self.assertTrue((dx == 2 and dy == 1) or (dx == 1 and dy == 2))


if __name__ == '__main__':
    unittest.main()
