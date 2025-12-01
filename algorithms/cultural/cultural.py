import time
import random
from typing import List, Tuple, Optional, Callable, Set


class Individual:

    def __init__(self, board_size: int, start_pos: Tuple[int, int]):
        self.board_size = board_size
        self.start_pos = start_pos
        self.path = [start_pos]
        self.fitness = 0
        self.visited = {start_pos}

    def add_move(self, position: Tuple[int, int]):
        self.path.append(position)
        self.visited.add(position)


class BeliefSpace:
    def __init__(self, board_size: int):
        self.board_size = board_size
        self.best_fitness = 0
        self.best_path = []

        # Normative knowledge: successful move patterns from each position
        self.successful_moves = {}  # {position: [list of good next moves]}

        self.best_solution = None
        self.valid_knight_moves = [(2, 1), (1, 2), (-1, 2), (-2, 1),(-2, -1), (-1, -2), (1, -2), (2, -1)]

    def update(self, individuals: List[Individual]):
        # Sort by fitness
        sorted_individuals = sorted(individuals, key=lambda ind: ind.fitness, reverse=True)

        # Update best solution
        best_individual = sorted_individuals[0]
        if best_individual.fitness > self.best_fitness:
            self.best_fitness = best_individual.fitness
            self.best_path = best_individual.path.copy()
            self.best_solution = best_individual

        # Learn from top performers (top 20%)
        top_performers = sorted_individuals[:max(1, len(sorted_individuals) // 5)]

        for individual in top_performers:
            # Extract successful move patterns
            for i in range(len(individual.path) - 1):
                current_pos = individual.path[i]
                next_pos = individual.path[i + 1]

                if current_pos not in self.successful_moves:
                    self.successful_moves[current_pos] = []

                if next_pos not in self.successful_moves[current_pos]:
                    self.successful_moves[current_pos].append(next_pos)

    def get_suggested_move(self, current_pos: Tuple[int, int],visited: Set[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        if current_pos in self.successful_moves:
            # Filter out already visited positions
            valid_suggestions = [
                pos for pos in self.successful_moves[current_pos]
                if pos not in visited
            ]
            if valid_suggestions:
                return random.choice(valid_suggestions)

        return None


class CulturalAlgorithmSolver:
    MOVES = [(2, 1), (1, 2), (-1, 2), (-2, 1),(-2, -1), (-1, -2), (1, -2), (2, -1)]

    def __init__(self, board_size: int, start_pos: Tuple[int, int] = (0, 0),population_size: int = 100, max_generations: int = 500,timeout: float = 60.0, progress_callback: Optional[Callable] = None):
        self.board_size = board_size
        self.start_pos = start_pos
        self.population_size = population_size
        self.max_generations = max_generations
        self.timeout = timeout
        self.progress_callback = progress_callback

        self.population = []
        self.belief_space = BeliefSpace(board_size)
        self.generation_count = 0
        self.best_solution = None
        self.start_time = None
        self.timed_out = False

    def is_valid_move(self, x: int, y: int) -> bool:
        return 0 <= x < self.board_size and 0 <= y < self.board_size

    def get_valid_moves(self, pos: Tuple[int, int],visited: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        x, y = pos
        valid_moves = []

        for dx, dy in self.MOVES:
            next_x, next_y = x + dx, y + dy
            next_pos = (next_x, next_y)

            if self.is_valid_move(next_x, next_y) and next_pos not in visited:
                valid_moves.append(next_pos)

        return valid_moves

    def calculate_fitness(self, individual: Individual) -> float:
        unique_squares = len(individual.visited)
        max_squares = self.board_size ** 2

        # Base fitness: percentage of board covered
        fitness = unique_squares

        # Bonus for complete tour
        if unique_squares == max_squares:
            fitness += 100

        # Penalty for invalid paths (shouldn't happen, but safety check)
        for i in range(len(individual.path) - 1):
            x1, y1 = individual.path[i]
            x2, y2 = individual.path[i + 1]
            dx, dy = abs(x2 - x1), abs(y2 - y1)

            # Check if move is valid knight move
            if not ((dx == 2 and dy == 1) or (dx == 1 and dy == 2)):
                fitness -= 10

        return fitness

    def create_individual(self) -> Individual:
        individual = Individual(self.board_size, self.start_pos)
        current_pos = self.start_pos
        max_moves = self.board_size ** 2

        for _ in range(max_moves - 1):
            # Try to get suggestion from belief space (30% of the time)
            next_pos = None
            if random.random() < 0.3:
                next_pos = self.belief_space.get_suggested_move(
                    current_pos, individual.visited
                )

            # If no suggestion or random choice, get valid moves
            if next_pos is None:
                valid_moves = self.get_valid_moves(current_pos, individual.visited)
                if not valid_moves:
                    break
                next_pos = random.choice(valid_moves)

            individual.add_move(next_pos)
            current_pos = next_pos

        individual.fitness = self.calculate_fitness(individual)
        return individual

    def initialize_population(self):
        self.population = []
        for _ in range(self.population_size):
            individual = self.create_individual()
            self.population.append(individual)

    def select_parents(self) -> Tuple[Individual, Individual]:
        tournament_size = 5

        # Tournament selection for parent 1
        tournament1 = random.sample(self.population, min(tournament_size, len(self.population)))
        parent1 = max(tournament1, key=lambda ind: ind.fitness)

        # Tournament selection for parent 2
        tournament2 = random.sample(self.population, min(tournament_size, len(self.population)))
        parent2 = max(tournament2, key=lambda ind: ind.fitness)

        return parent1, parent2

    def crossover(self, parent1: Individual, parent2: Individual) -> Individual:
        # Take initial portion from parent1
        crossover_point = random.randint(1, min(len(parent1.path), len(parent2.path)) - 1)

        child = Individual(self.board_size, self.start_pos)
        child.path = parent1.path[:crossover_point].copy()
        child.visited = set(child.path)

        # Try to extend with moves from parent2 that are valid
        current_pos = child.path[-1]

        for pos in parent2.path[crossover_point:]:
            if pos not in child.visited:
                # Check if this is a valid knight move
                x1, y1 = current_pos
                x2, y2 = pos
                dx, dy = abs(x2 - x1), abs(y2 - y1)

                if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
                    child.add_move(pos)
                    current_pos = pos

        # Fill remaining with greedy random moves
        max_moves = self.board_size ** 2
        while len(child.path) < max_moves:
            valid_moves = self.get_valid_moves(current_pos, child.visited)
            if not valid_moves:
                break
            next_pos = random.choice(valid_moves)
            child.add_move(next_pos)
            current_pos = next_pos

        child.fitness = self.calculate_fitness(child)
        return child

    def mutate(self, individual: Individual, mutation_rate: float = 0.2):
        if random.random() > mutation_rate or len(individual.path) < 3:
            return

        # Choose mutation point
        mutation_point = random.randint(1, len(individual.path) - 1)

        # Keep path up to mutation point
        individual.path = individual.path[:mutation_point]
        individual.visited = set(individual.path)

        # Rebuild from mutation point
        current_pos = individual.path[-1]
        max_moves = self.board_size ** 2

        while len(individual.path) < max_moves:
            valid_moves = self.get_valid_moves(current_pos, individual.visited)
            if not valid_moves:
                break
            next_pos = random.choice(valid_moves)
            individual.add_move(next_pos)
            current_pos = next_pos

        individual.fitness = self.calculate_fitness(individual)

    def evolve_generation(self):
        new_population = []

        # Elitism: keep top 10% of current population
        elite_size = max(1, self.population_size // 10)
        sorted_population = sorted(self.population, key=lambda ind: ind.fitness, reverse=True)
        new_population.extend(sorted_population[:elite_size])

        # Generate rest of new population
        while len(new_population) < self.population_size:
            parent1, parent2 = self.select_parents()
            offspring = self.crossover(parent1, parent2)
            self.mutate(offspring)
            new_population.append(offspring)

        self.population = new_population

    def solve(self) -> Tuple[bool, List[Tuple[int, int]], dict]:
        self.start_time = time.time()
        self.generation_count = 0
        self.timed_out = False

        # Initialize population
        self.initialize_population()

        target_fitness = self.board_size ** 2 + 100  # Complete tour with bonus

        # Evolution loop
        for generation in range(self.max_generations):
            # Check timeout
            if time.time() - self.start_time > self.timeout:
                self.timed_out = True
                break

            self.generation_count = generation + 1

            # Update belief space with current population
            self.belief_space.update(self.population)

            # Check for solution
            best_individual = max(self.population, key=lambda ind: ind.fitness)

            if self.progress_callback and generation % 10 == 0:
                progress = (best_individual.fitness / target_fitness) * 100
                self.progress_callback(
                    min(progress, 99),
                    f"Generation {generation}: Best fitness = {best_individual.fitness}"
                )

            # Check if solution found
            if best_individual.fitness >= target_fitness:
                self.best_solution = best_individual
                break

            # Evolve next generation
            self.evolve_generation()

        execution_time = time.time() - self.start_time

        # Get best solution
        if self.best_solution is None:
            self.best_solution = max(self.population, key=lambda ind: ind.fitness)

        success = len(self.best_solution.path) == self.board_size ** 2

        stats = {
            'execution_time': execution_time,
            'generations': self.generation_count,
            'best_fitness': self.best_solution.fitness,
            'solution_length': len(self.best_solution.path),
            'timed_out': self.timed_out,
            'algorithm': 'Cultural Algorithm'
        }

        if self.timed_out:
            stats['error'] = f'Timeout after {self.timeout} seconds'

        return success, self.best_solution.path.copy(), stats

    def print_solution(self):
        """Print the solution in readable format."""
        if not self.best_solution:
            print("No solution found")
            return

        print(f"\nCultural Algorithm Solution ({self.board_size}x{self.board_size}):")
        print(f"Generations: {self.generation_count}")
        print(f"Best fitness: {self.best_solution.fitness}")
        print(f"Path length: {len(self.best_solution.path)}")
        print(f"Coverage: {len(self.best_solution.visited)}/{self.board_size ** 2} squares")
