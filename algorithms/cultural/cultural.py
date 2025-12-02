import time
import random
from typing import List, Tuple, Optional, Callable, Set, Dict


class Individual:

    def __init__(self, board_size: int, start_pos: Tuple[int, int]):
        self.board_size = board_size
        self.start_pos = start_pos
        self.path = [start_pos]
        self.fitness = 0.0
        self.visited = {start_pos}

    def add_move(self, position: Tuple[int, int]):
        self.path.append(position)
        self.visited.add(position)


class BeliefSpace:

    def __init__(self, board_size: int):
        self.board_size = board_size
        self.best_fitness = 0
        self.best_path = []
        self.best_solution = None
        self.valid_knight_moves = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]

        self.successful_moves = {}
        self.transition_quality = {}
        self.dangerous_transitions = set()
        self.good_patterns = []
        self.position_degrees = {}
        self.stagnation_counter = 0
        self.last_best_fitness = 0

    def update(self, individuals: List[Individual]):
        sorted_individuals = sorted(individuals, key=lambda ind: ind.fitness, reverse=True)
        best_individual = sorted_individuals[0]

        if best_individual.fitness > self.best_fitness:
            self.best_fitness = best_individual.fitness
            self.best_path = best_individual.path.copy()
            self.best_solution = best_individual
            self.stagnation_counter = 0
        else:
            if abs(best_individual.fitness - self.last_best_fitness) < 1:
                self.stagnation_counter += 1
            else:
                self.stagnation_counter = 0

        self.last_best_fitness = best_individual.fitness

        top_count = max(1, len(sorted_individuals) // 5)
        top_performers = sorted_individuals[:top_count]

        for individual in top_performers:
            for i in range(len(individual.path) - 1):
                current_pos = individual.path[i]
                next_pos = individual.path[i + 1]

                if current_pos not in self.successful_moves:
                    self.successful_moves[current_pos] = []

                if next_pos not in self.successful_moves[current_pos]:
                    self.successful_moves[current_pos].append(next_pos)

                transition = (current_pos, next_pos)
                if transition not in self.transition_quality:
                    self.transition_quality[transition] = {'success': 0, 'failure': 0}

                if individual.fitness > self.board_size ** 2 * 0.7:
                    self.transition_quality[transition]['success'] += 1
                else:
                    self.transition_quality[transition]['failure'] += 1

            if len(individual.path) >= self.board_size ** 2 * 0.7:
                for k in range(len(individual.path) - 2):
                    pattern = (individual.path[k], individual.path[k + 1], individual.path[k + 2])
                    if pattern not in [p[0] for p in self.good_patterns]:
                        self.good_patterns.append((pattern, individual.fitness))

        self.good_patterns.sort(key=lambda x: x[1], reverse=True)
        self.good_patterns = self.good_patterns[:15]

        bottom_performers = sorted_individuals[-max(1, len(sorted_individuals) // 10):]
        for individual in bottom_performers:
            if len(individual.path) < self.board_size ** 2 * 0.5:
                for i in range(len(individual.path) - 1):
                    transition = (individual.path[i], individual.path[i + 1])
                    self.dangerous_transitions.add(transition)

    def get_suggested_move(self, current_pos: Tuple[int, int], visited: Set[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        if current_pos in self.successful_moves:
            valid_suggestions = [pos for pos in self.successful_moves[current_pos] if pos not in visited]
            if valid_suggestions:
                scored_suggestions = []
                for pos in valid_suggestions:
                    transition = (current_pos, pos)
                    quality = self.transition_quality.get(transition, {'success': 1, 'failure': 1})
                    score = quality['success'] / max(1, quality['success'] + quality['failure'])
                    scored_suggestions.append((pos, score))

                scored_suggestions.sort(key=lambda x: x[1], reverse=True)

                if random.random() < 0.7:
                    return scored_suggestions[0][0]
                else:
                    return random.choice(scored_suggestions)[0]
        return None

    def is_good_transition(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        transition = (pos1, pos2)
        if transition in self.dangerous_transitions:
            return False

        if transition in self.transition_quality:
            quality = self.transition_quality[transition]
            return quality['success'] > quality['failure']

        return True

    def get_stagnation_level(self) -> float:
        return min(1.0, self.stagnation_counter / 30.0)


class CulturalAlgorithmSolver:
    MOVES = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]

    def __init__(self, board_size: int, start_pos: Tuple[int, int] = (0, 0),
                 population_size: int = 100, max_generations: int = 500,
                 timeout: float = 60.0, progress_callback: Optional[Callable] = None):
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
        self.base_mutation_rate = 0.2

    def is_valid_move(self, x: int, y: int) -> bool:
        return 0 <= x < self.board_size and 0 <= y < self.board_size

    def get_valid_moves(self, pos: Tuple[int, int], visited: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        x, y = pos
        valid_moves = []

        for dx, dy in self.MOVES:
            next_x, next_y = x + dx, y + dy
            next_pos = (next_x, next_y)

            if self.is_valid_move(next_x, next_y) and next_pos not in visited:
                valid_moves.append(next_pos)

        return valid_moves

    def get_degree(self, pos: Tuple[int, int], visited: Set[Tuple[int, int]]) -> int:
        return len(self.get_valid_moves(pos, visited))

    def calculate_fitness(self, individual: Individual) -> float:
        individual.visited = set(individual.path)
        unique_squares = len(individual.visited)
        max_squares = self.board_size ** 2

        fitness = unique_squares * 20

        if unique_squares == max_squares:
            fitness += 500

        legal_transitions = 0
        consecutive_segments = 0
        current_segment = 1
        low_degree_visits = 0

        visited_so_far = {individual.path[0]}
        for i in range(len(individual.path)):
            if i > 0:
                visited_so_far.add(individual.path[i])

            degree = self.get_degree(individual.path[i], visited_so_far)
            if degree <= 2:
                low_degree_visits += 1

            if i < len(individual.path) - 1:
                x1, y1 = individual.path[i]
                x2, y2 = individual.path[i + 1]
                dx, dy = abs(x2 - x1), abs(y2 - y1)

                if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
                    legal_transitions += 1
                    current_segment += 1
                else:
                    consecutive_segments += current_segment
                    current_segment = 1
                    fitness -= 30

        consecutive_segments += current_segment

        repeats = len(individual.path) - unique_squares
        repeat_penalty = repeats * 15

        fitness += legal_transitions * 10
        fitness += consecutive_segments * 4
        fitness += low_degree_visits * 5
        fitness -= repeat_penalty

        return fitness

    def create_individual(self) -> Individual:
        individual = Individual(self.board_size, self.start_pos)
        current_pos = self.start_pos
        max_moves = self.board_size ** 2

        for _ in range(max_moves - 1):
            next_pos = None

            if self.generation_count > 10 and random.random() < 0.5:
                next_pos = self.belief_space.get_suggested_move(current_pos, individual.visited)

            if next_pos is None:
                valid_moves = self.get_valid_moves(current_pos, individual.visited)
                if not valid_moves:
                    break

                if self.generation_count > 5:
                    scored_moves = []
                    for move in valid_moves:
                        degree = self.get_degree(move, individual.visited | {move})

                        quality_bonus = 0
                        if self.belief_space.is_good_transition(current_pos, move):
                            quality_bonus = 2

                        score = degree * 3 + quality_bonus + random.random() * 0.5
                        scored_moves.append((move, score))

                    scored_moves.sort(key=lambda x: x[1])

                    if random.random() < 0.7:
                        next_pos = scored_moves[0][0]
                    else:
                        next_pos = random.choice(scored_moves[:3] if len(scored_moves) >= 3 else scored_moves)[0]
                else:
                    degrees = [(move, self.get_degree(move, individual.visited | {move})) for move in valid_moves]
                    degrees.sort(key=lambda x: x[1])

                    if random.random() < 0.6:
                        next_pos = degrees[0][0]
                    else:
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

        tournament1 = random.sample(self.population, min(tournament_size, len(self.population)))
        parent1 = max(tournament1, key=lambda ind: ind.fitness)

        tournament2 = random.sample(self.population, min(tournament_size, len(self.population)))
        parent2 = max(tournament2, key=lambda ind: ind.fitness)

        return parent1, parent2

    def crossover(self, parent1: Individual, parent2: Individual) -> Individual:
        min_path_len = min(len(parent1.path), len(parent2.path))

        if min_path_len < 3:
            return self.create_individual()

        if self.generation_count > 15 and self.belief_space.best_solution and random.random() < 0.3:
            best_path = self.belief_space.best_path
            inject_size = max(3, min(len(best_path) // 4, min_path_len // 2))
            crossover_point = random.randint(1, min_path_len - inject_size)

            child = Individual(self.board_size, self.start_pos)
            child.path = parent1.path[:crossover_point].copy()
            child.visited = set(child.path)

            for pos in best_path[crossover_point:crossover_point + inject_size]:
                if pos not in child.visited:
                    x1, y1 = child.path[-1]
                    x2, y2 = pos
                    dx, dy = abs(x2 - x1), abs(y2 - y1)
                    if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
                        child.add_move(pos)
        else:
            segment_size = max(2, min_path_len // 3)
            crossover_point = random.randint(1, min_path_len - segment_size)

            child = Individual(self.board_size, self.start_pos)
            child.path = parent1.path[:crossover_point].copy()
            child.visited = set(child.path)

            for pos in parent2.path[crossover_point:crossover_point + segment_size]:
                if pos not in child.visited:
                    x1, y1 = child.path[-1]
                    x2, y2 = pos
                    dx, dy = abs(x2 - x1), abs(y2 - y1)
                    if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
                        child.add_move(pos)

        current_pos = child.path[-1]
        max_moves = self.board_size ** 2

        while len(child.path) < max_moves:
            valid_moves = self.get_valid_moves(current_pos, child.visited)
            if not valid_moves:
                break

            if self.generation_count > 10:
                scored_moves = []
                for move in valid_moves:
                    degree = self.get_degree(move, child.visited | {move})
                    quality_bonus = 2 if self.belief_space.is_good_transition(current_pos, move) else 0
                    score = degree * 2 + quality_bonus + random.random() * 0.3
                    scored_moves.append((move, score))

                scored_moves.sort(key=lambda x: x[1])
                next_pos = scored_moves[0][0] if random.random() < 0.8 else random.choice(scored_moves)[0]
            else:
                degrees = [(move, self.get_degree(move, child.visited | {move})) for move in valid_moves]
                degrees.sort(key=lambda x: x[1])
                next_pos = degrees[0][0] if random.random() < 0.7 else random.choice(valid_moves)

            child.add_move(next_pos)
            current_pos = next_pos

        child.fitness = self.calculate_fitness(child)
        return child

    def mutate(self, individual: Individual):
        stagnation = self.belief_space.get_stagnation_level()
        dynamic_rate = self.base_mutation_rate + (stagnation * 0.3)

        if random.random() > dynamic_rate or len(individual.path) < 3:
            return

        mutation_point = random.randint(1, len(individual.path) - 1)

        individual.path = individual.path[:mutation_point]
        individual.visited = set(individual.path)

        current_pos = individual.path[-1]
        max_moves = self.board_size ** 2

        while len(individual.path) < max_moves:
            valid_moves = self.get_valid_moves(current_pos, individual.visited)
            if not valid_moves:
                break

            if self.generation_count > 10 and random.random() < 0.7:
                suggested = self.belief_space.get_suggested_move(current_pos, individual.visited)
                if suggested:
                    next_pos = suggested
                else:
                    scored_moves = []
                    for move in valid_moves:
                        degree = self.get_degree(move, individual.visited | {move})
                        quality_bonus = 2 if self.belief_space.is_good_transition(current_pos, move) else 0
                        score = degree * 2 + quality_bonus
                        scored_moves.append((move, score))

                    scored_moves.sort(key=lambda x: x[1])
                    next_pos = scored_moves[0][0] if random.random() < 0.75 else random.choice(scored_moves)[0]
            else:
                degrees = [(move, self.get_degree(move, individual.visited | {move})) for move in valid_moves]
                degrees.sort(key=lambda x: x[1])
                next_pos = degrees[0][0] if random.random() < 0.65 else random.choice(valid_moves)

            individual.add_move(next_pos)
            current_pos = next_pos

        individual.fitness = self.calculate_fitness(individual)

    def local_search(self, individual: Individual):
        if len(individual.path) < 5:
            return

        original_path = individual.path.copy()
        original_fitness = individual.fitness
        best_fitness = original_fitness

        for _ in range(5):
            i = random.randint(1, len(individual.path) - 4)
            j = random.randint(i + 2, min(i + 5, len(individual.path) - 1))

            individual.path[i], individual.path[j] = individual.path[j], individual.path[i]
            new_fitness = self.calculate_fitness(individual)

            if new_fitness > best_fitness:
                best_fitness = new_fitness
                original_path = individual.path.copy()
            else:
                individual.path = original_path.copy()

        individual.fitness = best_fitness
        individual.visited = set(individual.path)

    def evolve_generation(self):
        new_population = []

        elite_size = max(2, self.population_size // 10)
        sorted_population = sorted(self.population, key=lambda ind: ind.fitness, reverse=True)
        new_population.extend(sorted_population[:elite_size])

        if self.generation_count > 20 and self.generation_count % 10 == 0:
            for i in range(min(2, len(sorted_population))):
                self.local_search(sorted_population[i])

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

        self.initialize_population()

        target_fitness = self.board_size ** 2 * 20 + 500

        for generation in range(self.max_generations):
            if time.time() - self.start_time > self.timeout:
                self.timed_out = True
                break

            self.generation_count = generation + 1

            self.belief_space.update(self.population)

            best_individual = max(self.population, key=lambda ind: ind.fitness)

            if self.progress_callback and generation % 10 == 0:
                progress = (best_individual.fitness / target_fitness) * 100
                self.progress_callback(
                    min(progress, 99),
                    f"Generation {generation}: Best fitness = {best_individual.fitness:.1f}"
                )

            if len(set(best_individual.path)) == self.board_size ** 2:
                self.best_solution = best_individual
                break

            self.evolve_generation()

        execution_time = time.time() - self.start_time

        if self.best_solution is None:
            self.best_solution = max(self.population, key=lambda ind: ind.fitness)

        success = len(set(self.best_solution.path)) == self.board_size ** 2

        stats = {
            'execution_time': execution_time,
            'generations': self.generation_count,
            'best_fitness': self.best_solution.fitness,
            'solution_length': len(self.best_solution.path),
            'coverage': len(set(self.best_solution.path)),
            'population_size': self.population_size,
            'timed_out': self.timed_out,
            'algorithm': 'Cultural Algorithm'
        }

        if self.timed_out:
            stats['error'] = f'Timeout after {self.timeout} seconds'

        return success, self.best_solution.path.copy(), stats
