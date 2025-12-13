import random
from typing import List, Tuple
import sys
sys.path.append('..')
from algorithms.base_solver import BaseSolver


class SimpleGASolver(BaseSolver):

    def __init__(self, n: int, level: int = 1):
        super().__init__(n=n, level=level)
        self.population_size = 30
        self.generations = 100 # 1 -> 2 -> ... -> 100 
        self.mutation_rate = 0.3
        self.chromosome_length = n * n
        self.elitism_count = 2
        self.tournament_size = 3
        self.best_fitness = 0
        self.best_path = [] # Best path -> Best chromosome
        self.generation_best_fitness = []
        self.generation_avg_fitness = []
        self.mutation_count = 0
        self.crossover_count = 0

    def initialize_population(self) -> List[List[int]]:
        population = []
        for _ in range(self.population_size):
            chromosome = [random.randint(0, 7) for _ in range(self.chromosome_length)]
            population.append(chromosome)
        return population 

    def decode(self, chromosome: List[int], start_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        path = [start_pos]
        visited = {start_pos}
        current_pos = start_pos

        for move_index in chromosome:
            if len(visited) >= self.n * self.n:
                break

            next_pos = self.apply_move(current_pos, move_index)

            if self.is_valid_position(next_pos[0], next_pos[1]) and next_pos not in visited:
                path.append(next_pos)
                visited.add(next_pos)
                current_pos = next_pos
            else:
                valid_moves = self.get_valid_moves_from(current_pos[0], current_pos[1], visited)
                if not valid_moves:
                    break

                best_move = None
                max_future_moves = -1
                for candidate in valid_moves[:min(3, len(valid_moves))]:
                    future_moves = len(self.get_valid_moves_from(candidate[0], candidate[1], visited | {candidate}))
                    if future_moves > max_future_moves:
                        max_future_moves = future_moves
                        best_move = candidate

                if best_move is None:
                    best_move = valid_moves[0]

                path.append(best_move)
                visited.add(best_move)
                current_pos = best_move

        return path

    def fitness(self, chromosome: List[int], start_pos: Tuple[int, int]) -> float:
        path = self.decode(chromosome, start_pos)
        if not path:
            return 0.0

        unique_count = len(path)
        legal_transitions = 0

        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            dx, dy = abs(x2 - x1), abs(y2 - y1)
            if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
                legal_transitions += 1

        fitness_score = unique_count * 10 + legal_transitions * 5
        return float(fitness_score)

    def select_parents(self, population: List[List[int]], fitness_scores: List[float]) -> List[List[int]]:
        sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)
        elite = [population[i] for i in sorted_indices[:self.elitism_count]]
        parents = elite.copy()
        while len(parents) < self.population_size // 2:
            winner = self.tournament_selection(population, fitness_scores)
            parents.append(winner)
        return parents

    def tournament_selection(self, population: List[List[int]], fitness_scores: List[float]) -> List[int]:
        tournament_indices = random.sample(range(len(population)), min(self.tournament_size, len(population)))
        best_idx = max(tournament_indices, key=lambda i: fitness_scores[i])
        return population[best_idx].copy()

    def crossover(self, p1: List[int], p2: List[int]) -> Tuple[List[int], List[int]]:
        if len(p1) < 2 or len(p2) < 2:
            return p1.copy(), p2.copy()

        point1 = random.randint(1, len(p1) - 2)
        point2 = random.randint(point1 + 1, len(p1))

        child1 = p1[:point1] + p2[point1:point2] + p1[point2:]
        child2 = p2[:point1] + p1[point1:point2] + p2[point2:]

        child1 = self._repair_chromosome(child1)
        child2 = self._repair_chromosome(child2)

        self.crossover_count += 1
        return child1, child2

    def _repair_chromosome(self, chromosome: List[int]) -> List[int]:
        repaired = []
        for gene in chromosome:
            if 0 <= gene <= 7:
                repaired.append(gene)
            else:
                repaired.append(random.randint(0, 7))

        if len(repaired) < self.chromosome_length:
            repaired.extend([random.randint(0, 7) for _ in range(self.chromosome_length - len(repaired))])
        elif len(repaired) > self.chromosome_length:
            repaired = repaired[:self.chromosome_length]

        return repaired

    def mutate(self, chromosome: List[int]) -> List[int]:
        if random.random() > self.mutation_rate:
            return chromosome

        mutated = chromosome.copy()
        num_mutations = random.randint(1, 3)

        for _ in range(num_mutations):
            pos = random.randint(0, len(mutated) - 1)

            if pos > 0:
                prev_move = mutated[pos - 1]
                candidate_moves = list(range(8))
                candidate_moves.remove(prev_move) if prev_move in candidate_moves else None
                mutated[pos] = random.choice(candidate_moves) if candidate_moves else random.randint(0, 7)
            else:
                mutated[pos] = random.randint(0, 7)

        self.mutation_count += 1
        return mutated

    def evolve(self, start_pos: Tuple[int, int]) -> Tuple[bool, List[Tuple[int, int]]]:
        population = self.initialize_population()
        self.generation_best_fitness = []
        self.generation_avg_fitness = []
        self.mutation_count = 0
        self.crossover_count = 0

        for generation in range(self.generations):
            fitness_scores = [self.fitness(chrom, start_pos) for chrom in population]

            best_idx = fitness_scores.index(max(fitness_scores))
            best_fitness = fitness_scores[best_idx]
            avg_fitness = sum(fitness_scores) / len(fitness_scores)

            self.generation_best_fitness.append(best_fitness)
            self.generation_avg_fitness.append(avg_fitness)

            if best_fitness > self.best_fitness:
                self.best_fitness = best_fitness
                self.best_path = self.decode(population[best_idx], start_pos)

            parents = self.select_parents(population, fitness_scores)

            new_population = []
            sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)
            for i in sorted_indices[:self.elitism_count]:
                new_population.append(population[i].copy())

            while len(new_population) < self.population_size:
                p1 = random.choice(parents)
                p2 = random.choice(parents)
                child1, child2 = self.crossover(p1, p2)
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)

            population = new_population

        target_squares = self.n * self.n
        unique_visited = len(set(self.best_path))
        success = unique_visited == target_squares

        return success, self.best_path

    def solve(self, start_x: int, start_y: int) -> Tuple[bool, List[Tuple[int, int]]]:
        self.start_pos = (start_x, start_y)
        self.best_fitness = 0
        self.best_path = []
        success, path = self.evolve(self.start_pos)
        return success, path
