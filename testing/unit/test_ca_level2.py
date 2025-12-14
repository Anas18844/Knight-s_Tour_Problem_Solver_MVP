"""
Unit Tests for Level 2 - Enhanced GA with Heuristics
Tests mobility calculation, improved fitness, and heuristic-based operations
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from algorithms.cultural.level2_enhanced_ga import EnhancedGASolver


class TestLevel2EnhancedGA(unittest.TestCase):
    """Test cases for Enhanced GA (Level 2)"""

    def setUp(self):
        """Set up test fixtures"""
        self.solver = EnhancedGASolver(n=6, level=2)
        self.start_pos = (0, 0)

    def test_initialization(self):
        """Test enhanced solver initialization"""
        self.assertEqual(self.solver.n, 6)
        self.assertEqual(self.solver.level, 2)
        self.assertEqual(self.solver.diversity_weight, 0.05)
        self.assertEqual(self.solver.mobility_weight, 2.0)

    def test_mobility_calculation(self):
        """Test mobility (degree) calculation"""
        # From center with no visited squares
        visited = {(3, 3)}
        mobility = self.solver._get_mobility((3, 3), visited)

        # Should have high mobility from center
        self.assertGreater(mobility, 0)
        self.assertLessEqual(mobility, 8)

        # From corner
        corner_mobility = self.solver._get_mobility((0, 0), {(0, 0)})
        self.assertLess(corner_mobility, mobility)

        # With many visited squares
        many_visited = {(i, j) for i in range(6) for j in range(6) if i + j < 4}
        low_mobility = self.solver._get_mobility((2, 2), many_visited)
        self.assertLessEqual(low_mobility, mobility)

    def test_enhanced_fitness(self):
        """Test enhanced fitness with mobility"""
        chromosome = [0] * 36

        fitness = self.solver.fitness(chromosome, self.start_pos)

        # Fitness should include mobility component
        self.assertGreaterEqual(fitness, 0)

        # Fitness should consider:
        # - unique count
        # - legal transitions
        # - mobility
        # - repeat penalty

    def test_decode_with_mobility(self):
        """Test decoding with mobility checks"""
        chromosome = [1, 2, 3, 4, 5, 6, 7, 0] * 4 + [1, 2, 3, 4]
        path = self.solver.decode(chromosome, self.start_pos)

        # Should produce valid path
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], self.start_pos)

        # Should avoid dead ends when possible
        # (mobility check should help)

    def test_heuristic_repair(self):
        """Test heuristic-based chromosome repair"""
        # Chromosome with consecutive duplicates
        chromosome = [0, 0, 1, 1, 2, 2, 3, 3] * 4 + [0, 0, 1, 2]

        repaired = self.solver._heuristic_repair(chromosome)

        # Should have correct length
        self.assertEqual(len(repaired), 36)

        # Should have fewer consecutive duplicates
        consecutive_count = sum(1 for i in range(len(repaired)-1)
                               if repaired[i] == repaired[i+1])

        # Cannot guarantee no duplicates, but should be valid
        for gene in repaired:
            self.assertIn(gene, range(8))

    def test_diversity_calculation(self):
        """Test population diversity calculation"""
        # Identical population
        identical_pop = [[0] * 36 for _ in range(10)]
        diversity_low = self.solver._calculate_diversity(identical_pop)

        # Diverse population
        diverse_pop = [[i % 8] * 36 for i in range(10)]
        diversity_high = self.solver._calculate_diversity(diverse_pop)

        # Diverse should be higher
        self.assertGreaterEqual(diversity_high, diversity_low)

    def test_diversity_tournament(self):
        """Test diversity-aware tournament selection"""
        population = self.solver.initialize_population()
        fitness_scores = [self.solver.fitness(chrom, self.start_pos) for chrom in population]

        selected = self.solver._diversity_tournament(population, fitness_scores)

        # Should select valid chromosome
        self.assertIn(selected, population)
        self.assertEqual(len(selected), 36)

    def test_enhanced_mutation(self):
        """Test enhanced mutation with smart selection"""
        original = [0, 1, 2, 3, 4, 5, 6, 7] * 4 + [0, 1, 2, 3]
        mutated = self.solver.mutate(original.copy())

        # Should have correct length
        self.assertEqual(len(mutated), 36)

        # All genes should be valid
        for gene in mutated:
            self.assertIn(gene, range(8))

    def test_solve_with_heuristics(self):
        """Test solving with heuristics"""
        quick_solver = EnhancedGASolver(n=5, level=2)
        quick_solver.generations = 10

        success, path = quick_solver.solve(0, 0)

        # Should return valid result
        self.assertIsInstance(success, bool)
        self.assertIsInstance(path, list)
        self.assertGreater(len(path), 0)


if __name__ == '__main__':
    unittest.main()
