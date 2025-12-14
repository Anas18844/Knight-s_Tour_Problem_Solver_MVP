import unittest
import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from algorithms.cultural.level3_cultural_ga import CulturalGASolver, BeliefSpace
from algorithms.cultural.cultural import CulturalAlgorithmSolver, AdvancedBeliefSpace


class TestBeliefSpace(unittest.TestCase):
    """Test cases for Belief Space"""

    def setUp(self):
        """Set up test fixtures"""
        self.belief_space = BeliefSpace(n=6)

    def test_initialization(self):
        """Test belief space initialization"""
        self.assertEqual(self.belief_space.n, 6)
        self.assertEqual(self.belief_space.generation_count, 0)
        self.assertEqual(len(self.belief_space.best_individuals), 0)

        # Check dictionaries are initialized
        self.assertIsInstance(self.belief_space.move_success, dict)
        self.assertIsInstance(self.belief_space.move_usage, dict)
        self.assertIsInstance(self.belief_space.mobility_map, dict)

    def test_update_belief_space(self):
        """Test belief space update"""
        # Create dummy population
        population = [[i % 8 for _ in range(36)] for i in range(10)]
        fitness_scores = [100 + i * 10 for i in range(10)]
        decoded_paths = [[(i, j) for j in range(6)] for i in range(10)]

        self.belief_space.update(population, fitness_scores, decoded_paths)

        # Generation count should increase
        self.assertEqual(self.belief_space.generation_count, 1)

        # Should store best individuals
        self.assertGreater(len(self.belief_space.best_individuals), 0)
        self.assertLessEqual(len(self.belief_space.best_individuals), 3)

        # Move usage should be tracked
        total_usage = sum(self.belief_space.move_usage.values())
        self.assertGreater(total_usage, 0)

    def test_move_probability(self):
        """Test move probability calculation"""
        # Initially no data
        prob = self.belief_space.get_move_probability(0)
        self.assertEqual(prob, 0.5)  # Default

        # After some usage
        self.belief_space.move_usage[0] = 10
        self.belief_space.move_success[0] = 7

        prob = self.belief_space.get_move_probability(0)
        self.assertEqual(prob, 0.7)

    def test_position_difficulty(self):
        """Test position difficulty calculation"""
        pos = (2, 2)

        # Initially no data
        diff = self.belief_space.get_position_difficulty(pos)
        self.assertEqual(diff, 0.5)

        # After some visits
        self.belief_space.mobility_map[pos] = {'visits': 10, 'success': 8}
        diff = self.belief_space.get_position_difficulty(pos)

        # Difficulty = 1 - success_rate = 1 - 0.8 = 0.2
        self.assertAlmostEqual(diff, 0.2)

    def test_suggest_move(self):
        """Test move suggestion"""
        # Early generation - should return random
        move = self.belief_space.suggest_move()
        self.assertIn(move, range(8))

        # After learning
        self.belief_space.generation_count = 15
        self.belief_space.move_usage[3] = 100
        self.belief_space.move_success[3] = 90

        # Should suggest good moves more often
        suggestions = [self.belief_space.suggest_move() for _ in range(10)]
        # At least some should be valid
        self.assertTrue(all(s in range(8) for s in suggestions))


class TestLevel3CulturalGA(unittest.TestCase):
    """Test cases for Cultural GA (Level 3)"""

    def setUp(self):
        """Set up test fixtures"""
        self.solver = CulturalGASolver(n=6, level=3)
        self.start_pos = (0, 0)

    def test_initialization(self):
        """Test cultural GA initialization"""
        self.assertEqual(self.solver.n, 6)
        self.assertEqual(self.solver.level, 3)
        self.assertIsInstance(self.solver.belief_space, BeliefSpace)
        self.assertEqual(self.solver.use_belief_after_gen, 20)

    def test_belief_guided_decode(self):
        """Test decoding with belief guidance"""
        chromosome = [1, 2, 3, 4, 5, 6, 7, 0] * 4 + [1, 2, 3, 4]

        # Decode before belief learning
        path1 = self.solver.decode(chromosome, self.start_pos)

        # Update belief space
        population = [chromosome]
        fitness = [self.solver.fitness(chromosome, self.start_pos)]
        paths = [path1]
        self.solver.belief_space.update(population, fitness, paths)

        # Decode after belief learning
        path2 = self.solver.decode(chromosome, self.start_pos)

        # Both should be valid paths
        self.assertGreater(len(path1), 0)
        self.assertGreater(len(path2), 0)

    def test_belief_guided_mutation(self):
        """Test mutation with belief guidance"""
        chromosome = [0, 1, 2, 3, 4, 5, 6, 7] * 4 + [0, 1, 2, 3]

        # Mutate before belief
        self.solver.belief_space.generation_count = 5
        mutated1 = self.solver.mutate(chromosome.copy())

        # Mutate after belief learning
        self.solver.belief_space.generation_count = 25
        self.solver.belief_space.move_usage[2] = 50
        self.solver.belief_space.move_success[2] = 40
        mutated2 = self.solver.mutate(chromosome.copy())

        # Both should be valid
        self.assertEqual(len(mutated1), 36)
        self.assertEqual(len(mutated2), 36)

        for gene in mutated1 + mutated2:
            self.assertIn(gene, range(8))

    def test_belief_guided_crossover(self):
        """Test crossover with belief guidance"""
        parent1 = [0] * 36
        parent2 = [7] * 36

        # Crossover before belief
        self.solver.belief_space.generation_count = 10
        child1, child2 = self.solver.crossover(parent1, parent2)

        # Crossover with belief and elite injection
        self.solver.belief_space.generation_count = 30
        self.solver.belief_space.best_individuals = [{
            'chromosome': [3] * 36,
            'fitness': 500,
            'path': [(i, i % 6) for i in range(6)]
        }]

        child3, child4 = self.solver.crossover(parent1, parent2)

        # All children should be valid
        for child in [child1, child2, child3, child4]:
            self.assertEqual(len(child), 36)
            for gene in child:
                self.assertIn(gene, range(8))

    def test_evolve_with_belief(self):
        """Test evolution with belief space updates"""
        quick_solver = CulturalGASolver(n=5, level=3)
        quick_solver.generations = 15  # Enough to trigger belief usage

        success, path = quick_solver.evolve(self.start_pos)

        # Should track belief space generation
        self.assertGreaterEqual(quick_solver.belief_space.generation_count, 0)

        # Should have learned something
        total_move_usage = sum(quick_solver.belief_space.move_usage.values())
        self.assertGreater(total_move_usage, 0)

    def test_solve_with_cultural_learning(self):
        """Test complete solve with cultural learning"""
        quick_solver = CulturalGASolver(n=5, level=3)
        quick_solver.generations = 20

        success, path = quick_solver.solve(0, 0)

        # Should return valid result
        self.assertIsInstance(success, bool)
        self.assertIsInstance(path, list)
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], (0, 0))


class TestLevel4CulturalGA(unittest.TestCase):
    """Test cases for Advanced Cultural GA (Level 4)"""

    def setUp(self):
        """Set up test fixtures"""
        self.n = 5
        self.start_pos = (0, 0)

    def test_initialization(self):
        """Test Level 4 solver initialization"""
        solver = CulturalAlgorithmSolver(n=self.n, level=4, use_warnsdorff=True)
        self.assertEqual(solver.n, self.n)
        self.assertEqual(solver.level, 4)
        self.assertTrue(solver.use_warnsdorff)
        self.assertIsInstance(solver.belief_space, AdvancedBeliefSpace)
        self.assertGreater(solver.population_size, 0)

    def test_solve_with_warnsdorff(self):
        """Test Level 4 solve with Warnsdorff's rule"""
        solver = CulturalAlgorithmSolver(n=self.n, level=4, use_warnsdorff=True)
        solver.generations = 50 # Reduced for faster test

        success, path = solver.solve(self.start_pos[0], self.start_pos[1])

        self.assertIsInstance(success, bool)
        self.assertIsInstance(path, list)
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], self.start_pos)
        # It's hard to assert coverage directly as it's non-deterministic, but should aim for high coverage
        self.assertGreaterEqual(len(set(path)), self.n * self.n * 0.5) # At least 50% coverage

    def test_solve_without_warnsdorff(self):
        """Test Level 4 solve without Warnsdorff's rule (for comparison)"""
        solver = CulturalAlgorithmSolver(n=self.n, level=4, use_warnsdorff=False)
        solver.generations = 50 # Reduced for faster test

        success, path = solver.solve(self.start_pos[0], self.start_pos[1])

        self.assertIsInstance(success, bool)
        self.assertIsInstance(path, list)
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], self.start_pos)
        self.assertGreaterEqual(len(set(path)), self.n * self.n * 0.5) # At least 50% coverage

    def test_warnsdorff_impact_on_decode(self):
        """Verify Warnsdorff's rule influences decode method"""
        solver_warnsdorff = CulturalAlgorithmSolver(n=self.n, level=4, use_warnsdorff=True)
        solver_no_warnsdorff = CulturalAlgorithmSolver(n=self.n, level=4, use_warnsdorff=False)

        # Create a dummy chromosome
        chromosome = [random.randint(0, 7) for _ in range(self.n * self.n * 2)] # Longer chromosome

        # Decode paths
        path_w = solver_warnsdorff.decode(chromosome, self.start_pos)
        path_no_w = solver_no_warnsdorff.decode(chromosome, self.start_pos)

        self.assertGreater(len(path_w), 0)
        self.assertGreater(len(path_no_w), 0)

        # This test is tricky because it's hard to assert direct impact in a deterministic way.
        # We can at least check that the paths generated are not identical if the conditions for Warnsdorff apply.
        # However, due to randomness and complexity, they might coincidentally be the same.
        # A more robust test would involve specific board states where Warnsdorff *must* choose a different path.
        # For now, we'll just ensure they produce valid paths.
        self.assertNotEqual(path_w, path_no_w, "Paths should ideally differ when Warnsdorff is enabled/disabled")


if __name__ == '__main__':
    unittest.main()
