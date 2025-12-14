import random
from typing import List, Tuple, Set
from .level1_simple_ga import SimpleGASolver


class EnhancedGASolver(SimpleGASolver):

    def __init__(self, n: int, level: int = 2, verbose: bool = False):
        super().__init__(n=n, level=level, verbose=verbose)
        self.diversity_weight = 0.05
        self.mobility_weight = 2.0
        self.population_diversity = []

    def _get_mobility(self, pos: Tuple[int, int], visited: Set[Tuple[int, int]]) -> int:
        count = 0
        for dx, dy in self.KNIGHT_MOVES:
            next_x, next_y = pos[0] + dx, pos[1] + dy
            if self.is_valid_position(next_x, next_y) and (next_x, next_y) not in visited:
                count += 1
        return count

    def decode(self, chromosome: List[int], start_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        path = [start_pos]
        visited = {start_pos}
        current_pos = start_pos

        for move_index in chromosome:
            if len(visited) >= self.n * self.n:
                break

            next_pos = self.apply_move(current_pos, move_index)

            if self.is_valid_position(next_pos[0], next_pos[1]) and next_pos not in visited:
                mobility = self._get_mobility(next_pos, visited | {next_pos})
                if mobility > 0 or len(visited) < 5:
                    path.append(next_pos)
                    visited.add(next_pos)
                    current_pos = next_pos
                    continue

            valid_moves = self.get_valid_moves_from(current_pos[0], current_pos[1], visited)
            if not valid_moves:
                break

            best_move = None
            max_score = -1
            for candidate in valid_moves:
                mobility = self._get_mobility(candidate, visited | {candidate})
                future_moves = len(self.get_valid_moves_from(candidate[0], candidate[1], visited | {candidate}))
                score = mobility * 2 + future_moves
                if score > max_score:
                    max_score = score
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
        total_mobility = 0
        visited_set = set()

        for i, pos in enumerate(path):
            visited_set.add(pos)
            mobility = self._get_mobility(pos, visited_set)
            total_mobility += mobility

            if i < len(path) - 1:
                x1, y1 = path[i]
                x2, y2 = path[i + 1]
                dx, dy = abs(x2 - x1), abs(y2 - y1)
                if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
                    legal_transitions += 1

        repeat_penalty = 0
        if len(path) > len(set(path)):
            repeat_penalty = (len(path) - len(set(path))) * 5

        avg_mobility = total_mobility / len(path) if len(path) > 0 else 0
        fitness_score = (unique_count * 10 +
                        legal_transitions * 5 +
                        avg_mobility * self.mobility_weight -
                        repeat_penalty)

        return float(fitness_score)

    def mutate(self, chromosome: List[int]) -> List[int]:
        if random.random() > self.mutation_rate:
            return chromosome

        mutated = chromosome.copy()
        num_mutations = random.randint(1, 2)

        for _ in range(num_mutations):
            pos = random.randint(0, len(mutated) - 1)

            if random.random() < 0.2:
                mutated[pos] = random.randint(0, 7)
            else:
                move_scores = []
                for move_idx in range(8):
                    if pos > 0 and mutated[pos - 1] == move_idx:
                        continue
                    move_scores.append((move_idx, random.random() + (move_idx % 3)))

                move_scores.sort(key=lambda x: x[1], reverse=True)
                mutated[pos] = move_scores[0][0] if move_scores else random.randint(0, 7)

        self.mutation_count += 1
        return mutated

    def crossover(self, p1: List[int], p2: List[int]) -> Tuple[List[int], List[int]]:
        if len(p1) < 2 or len(p2) < 2:
            return p1.copy(), p2.copy()

        point1 = random.randint(1, len(p1) - 2)
        point2 = random.randint(point1 + 1, len(p1))

        child1 = p1[:point1] + p2[point1:point2] + p1[point2:]
        child2 = p2[:point1] + p1[point1:point2] + p2[point2:]

        child1 = self._heuristic_repair(child1)
        child2 = self._heuristic_repair(child2)

        self.crossover_count += 1
        return child1, child2

    def _heuristic_repair(self, chromosome: List[int]) -> List[int]:
        repaired = []
        for i, gene in enumerate(chromosome):
            if 0 <= gene <= 7:
                if i > 0 and len(repaired) > 0 and repaired[-1] == gene:
                    alternatives = [g for g in range(8) if g != gene]
                    repaired.append(random.choice(alternatives) if alternatives else gene)
                else:
                    repaired.append(gene)
            else:
                repaired.append(random.randint(0, 7))

        if len(repaired) < self.chromosome_length:
            repaired.extend([random.randint(0, 7) for _ in range(self.chromosome_length - len(repaired))])
        elif len(repaired) > self.chromosome_length:
            repaired = repaired[:self.chromosome_length]

        return repaired

    def _calculate_diversity(self, population: List[List[int]]) -> float:
        if len(population) < 2:
            return 0.0

        total_diff = 0
        comparisons = 0

        for i in range(min(10, len(population))):
            for j in range(i + 1, min(10, len(population))):
                diff = sum(1 for k in range(len(population[i])) if population[i][k] != population[j][k])
                total_diff += diff
                comparisons += 1

        return total_diff / comparisons if comparisons > 0 else 0.0

    def select_parents(self, population: List[List[int]], fitness_scores: List[float]) -> List[List[int]]:
        diversity_bonus = self._calculate_diversity(population) * self.diversity_weight
        adjusted_scores = [f + diversity_bonus for f in fitness_scores]

        sorted_indices = sorted(range(len(adjusted_scores)), key=lambda i: adjusted_scores[i], reverse=True)
        elite = [population[i] for i in sorted_indices[:self.elitism_count]]
        parents = elite.copy()

        while len(parents) < self.population_size // 2:
            winner = self._diversity_tournament(population, adjusted_scores)
            parents.append(winner)

        return parents

    def _diversity_tournament(self, population: List[List[int]], fitness_scores: List[float]) -> List[int]:
        tournament_indices = random.sample(range(len(population)), min(self.tournament_size, len(population)))
        best_idx = max(tournament_indices, key=lambda i: fitness_scores[i])
        return population[best_idx].copy()

    def evolve(self, start_pos: Tuple[int, int]) -> Tuple[bool, List[Tuple[int, int]]]:
        population = self.initialize_population()
        self.generation_best_fitness = []
        self.generation_avg_fitness = []
        self.population_diversity = []
        self.mutation_count = 0
        self.crossover_count = 0

        # Verbose: Initial configuration output
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"LEVEL 2: ENHANCED GENETIC ALGORITHM")
            print(f"{'='*70}")
            print(f"Board Size: {self.n}x{self.n} ({self.n*self.n} squares)")
            print(f"Start Position: {start_pos}")
            print(f"Population Size: {self.population_size}")
            print(f"Generations: {self.generations}")
            print(f"Mutation Rate: {self.mutation_rate:.2%}")
            print(f"Elitism: Top {self.elitism_count} preserved")
            print(f"\nLevel 2 Enhancements:")
            print(f"  • Mobility Weight: {self.mobility_weight}")
            print(f"  • Diversity Weight: {self.diversity_weight}")
            print(f"  • Heuristic Repair: Enabled")
            print(f"  • Smart Mutation: Enabled")
            print(f"{'='*70}\n")

        for generation in range(self.generations):
            fitness_scores = [self.fitness(chrom, start_pos) for chrom in population]

            best_idx = fitness_scores.index(max(fitness_scores))
            best_fitness = fitness_scores[best_idx]
            avg_fitness = sum(fitness_scores) / len(fitness_scores)
            diversity = self._calculate_diversity(population)

            self.generation_best_fitness.append(best_fitness)
            self.generation_avg_fitness.append(avg_fitness)
            self.population_diversity.append(diversity)

            if best_fitness > self.best_fitness:
                self.best_fitness = best_fitness
                self.best_path = self.decode(population[best_idx], start_pos)

            # Verbose: Show progress every 10 generations
            if self.verbose and generation % 10 == 0:
                unique_squares = len(set(self.best_path))
                avg_mobility = 0
                if self.best_path:
                    visited_set = set()
                    total_mobility = 0
                    for pos in self.best_path:
                        visited_set.add(pos)
                        total_mobility += self._get_mobility(pos, visited_set)
                    avg_mobility = total_mobility / len(self.best_path)

                print(f"\nGeneration {generation:3d}/{self.generations}")
                print(f"  Fitness: Best={best_fitness:6.1f} | Avg={avg_fitness:6.1f} | Min={min(fitness_scores):6.1f} | Max={max(fitness_scores):6.1f}")
                print(f"  Coverage: {unique_squares}/{self.n*self.n} squares ({unique_squares/(self.n*self.n)*100:.1f}%)")
                print(f"  Path Length: {len(self.best_path)} moves")
                print(f"  Level 2 Metrics:")
                print(f"    - Population Diversity: {diversity:.2f}")
                print(f"    - Avg Mobility: {avg_mobility:.2f}")
                print(f"    - Genetic Ops: {self.crossover_count} crossovers (with repair), {self.mutation_count} mutations (smart)")

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

        # Verbose: Final summary
        if self.verbose:
            target_squares = self.n * self.n
            unique_visited = len(set(self.best_path))
            success = unique_visited == target_squares

            print(f"\n{'='*70}")
            print(f"LEVEL 2 FINAL RESULTS")
            print(f"{'='*70}")
            print(f"Success: {'✓ Complete Tour!' if success else '✗ Partial Tour'}")
            print(f"Coverage: {unique_visited}/{target_squares} squares ({unique_visited/target_squares*100:.1f}%)")
            print(f"Path Length: {len(self.best_path)} moves")
            print(f"Best Fitness: {self.best_fitness:.1f}")
            print(f"Final Diversity: {self.population_diversity[-1]:.2f}")
            print(f"Total Genetic Operations:")
            print(f"  - Crossovers (with heuristic repair): {self.crossover_count}")
            print(f"  - Mutations (smart selection): {self.mutation_count}")
            print(f"{'='*70}\n")

        target_squares = self.n * self.n
        unique_visited = len(set(self.best_path))
        success = unique_visited == target_squares

        return success, self.best_path
