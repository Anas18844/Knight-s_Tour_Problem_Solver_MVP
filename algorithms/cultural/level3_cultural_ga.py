import random
from typing import List, Tuple, Dict
from .level2_enhanced_ga import EnhancedGASolver


class BeliefSpace:

    def __init__(self, n: int):
        self.n = n
        self.move_success = {i: 0 for i in range(8)}
        self.move_usage = {i: 0 for i in range(8)}
        self.mobility_map = {}
        self.best_individuals = []
        self.generation_count = 0

    def update(self, population: List[List[int]], fitness_scores: List[float], decoded_paths: List[List[Tuple[int, int]]]):
        self.generation_count += 1

        sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)
        top_n = min(3, len(sorted_indices))

        self.best_individuals = []
        for i in range(top_n):
            idx = sorted_indices[i]
            self.best_individuals.append({
                'chromosome': population[idx].copy(),
                'fitness': fitness_scores[idx],
                'path': decoded_paths[idx].copy()
            })

        for i in range(min(5, len(sorted_indices))):
            idx = sorted_indices[i]
            chromosome = population[idx]
            path = decoded_paths[idx]
            fitness = fitness_scores[idx]

            for move_idx in chromosome:
                if 0 <= move_idx <= 7:
                    self.move_usage[move_idx] += 1
                    if fitness > 300:
                        self.move_success[move_idx] += 1

            for pos in path:
                if pos not in self.mobility_map:
                    self.mobility_map[pos] = {'visits': 0, 'success': 0}
                self.mobility_map[pos]['visits'] += 1
                if len(path) >= self.n * self.n * 0.8:
                    self.mobility_map[pos]['success'] += 1

    def get_move_probability(self, move_idx: int) -> float:
        if self.move_usage[move_idx] == 0:
            return 0.5
        success_rate = self.move_success[move_idx] / self.move_usage[move_idx]
        return success_rate

    def get_position_difficulty(self, pos: Tuple[int, int]) -> float:
        if pos not in self.mobility_map:
            return 0.5
        visits = self.mobility_map[pos]['visits']
        if visits == 0:
            return 0.5
        success = self.mobility_map[pos]['success']
        return 1.0 - (success / visits)

    def suggest_move(self) -> int:
        if self.generation_count < 10:
            return random.randint(0, 7)

        move_scores = []
        for move_idx in range(8):
            prob = self.get_move_probability(move_idx)
            usage = self.move_usage[move_idx]
            score = prob * 0.7 + (usage / max(1, sum(self.move_usage.values()))) * 0.3
            move_scores.append((move_idx, score))

        move_scores.sort(key=lambda x: x[1], reverse=True)

        if random.random() < 0.2:
            return random.randint(0, 7)

        return move_scores[0][0]


class CulturalGASolver(EnhancedGASolver):

    def __init__(self, n: int, level: int = 3, verbose: bool = False):
        super().__init__(n=n, level=level, verbose=verbose)
        self.belief_space = BeliefSpace(n)
        self.use_belief_after_gen = 20

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
                difficulty = self.belief_space.get_position_difficulty(next_pos)

                if mobility > 0 or (len(visited) < 5 and difficulty < 0.7):
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
                difficulty = self.belief_space.get_position_difficulty(candidate)

                score = mobility * 2 + future_moves - difficulty * 10
                if score > max_score:
                    max_score = score
                    best_move = candidate

            if best_move is None:
                best_move = valid_moves[0]

            path.append(best_move)
            visited.add(best_move)
            current_pos = best_move

        return path

    def mutate(self, chromosome: List[int]) -> List[int]:
        if random.random() > self.mutation_rate:
            return chromosome

        mutated = chromosome.copy()
        num_mutations = random.randint(1, 2)

        use_belief = self.belief_space.generation_count >= self.use_belief_after_gen

        for _ in range(num_mutations):
            pos = random.randint(0, len(mutated) - 1)

            if use_belief and random.random() < 0.7:
                suggested = self.belief_space.suggest_move()
                if pos > 0 and mutated[pos - 1] != suggested:
                    mutated[pos] = suggested
                else:
                    mutated[pos] = random.randint(0, 7)
            else:
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

        if self.belief_space.generation_count >= self.use_belief_after_gen and self.belief_space.best_individuals:
            if random.random() < 0.3:
                best = self.belief_space.best_individuals[0]['chromosome']
                point = random.randint(1, len(p1) - 1)
                child1 = p1[:point] + best[point:]
                child2 = p2[:point] + best[point:]
            else:
                point1 = random.randint(1, len(p1) - 2)
                point2 = random.randint(point1 + 1, len(p1))
                child1 = p1[:point1] + p2[point1:point2] + p1[point2:]
                child2 = p2[:point1] + p1[point1:point2] + p2[point2:]
        else:
            point1 = random.randint(1, len(p1) - 2)
            point2 = random.randint(point1 + 1, len(p1))
            child1 = p1[:point1] + p2[point1:point2] + p1[point2:]
            child2 = p2[:point1] + p1[point1:point2] + p2[point2:]

        child1 = self._heuristic_repair(child1)
        child2 = self._heuristic_repair(child2)

        self.crossover_count += 1
        return child1, child2

    def select_parents(self, population: List[List[int]], fitness_scores: List[float]) -> List[List[int]]:
        diversity_bonus = self._calculate_diversity(population) * self.diversity_weight

        if self.belief_space.generation_count >= self.use_belief_after_gen:
            knowledge_bonus = self.belief_space.generation_count * 0.01
            adjusted_scores = [f + diversity_bonus + knowledge_bonus for f in fitness_scores]
        else:
            adjusted_scores = [f + diversity_bonus for f in fitness_scores]

        sorted_indices = sorted(range(len(adjusted_scores)), key=lambda i: adjusted_scores[i], reverse=True)
        elite = [population[i] for i in sorted_indices[:self.elitism_count]]
        parents = elite.copy()

        while len(parents) < self.population_size // 2:
            winner = self._diversity_tournament(population, adjusted_scores)
            parents.append(winner)

        return parents

    def evolve(self, start_pos: Tuple[int, int]) -> Tuple[bool, List[Tuple[int, int]]]:
        population = self.initialize_population()
        self.generation_best_fitness = []
        self.generation_avg_fitness = []
        self.population_diversity = []
        self.mutation_count = 0
        self.crossover_count = 0
        self.belief_space = BeliefSpace(self.n)

        # Verbose: Initial configuration output
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"LEVEL 3: CULTURAL GENETIC ALGORITHM")
            print(f"{'='*70}")
            print(f"Board Size: {self.n}x{self.n} ({self.n*self.n} squares)")
            print(f"Start Position: {start_pos}")
            print(f"Population Size: {self.population_size}")
            print(f"Generations: {self.generations}")
            print(f"Mutation Rate: {self.mutation_rate:.2%}")
            print(f"Elitism: Top {self.elitism_count} preserved")
            print(f"\nLevel 3 Cultural Algorithm Features:")
            print(f"  • Belief Space: Active")
            print(f"  • Belief Guidance Starts: Generation {self.use_belief_after_gen}")
            print(f"  • Move Success Tracking: Enabled")
            print(f"  • Position Difficulty Learning: Enabled")
            print(f"  • Knowledge-Guided Mutation: Enabled")
            print(f"  • Elite Knowledge Injection: Enabled")
            print(f"{'='*70}\n")

        for generation in range(self.generations):
            decoded_paths = [self.decode(chrom, start_pos) for chrom in population]
            fitness_scores = [self.fitness(chrom, start_pos) for chrom in population]

            self.belief_space.update(population, fitness_scores, decoded_paths)

            best_idx = fitness_scores.index(max(fitness_scores))
            best_fitness = fitness_scores[best_idx]
            avg_fitness = sum(fitness_scores) / len(fitness_scores)
            diversity = self._calculate_diversity(population)

            self.generation_best_fitness.append(best_fitness)
            self.generation_avg_fitness.append(avg_fitness)
            self.population_diversity.append(diversity)

            if best_fitness > self.best_fitness:
                self.best_fitness = best_fitness
                self.best_path = decoded_paths[best_idx]

            # Verbose: Show progress every 10 generations
            if self.verbose and generation % 10 == 0:
                unique_squares = len(set(self.best_path))

                # Calculate belief space statistics
                total_move_usage = sum(self.belief_space.move_usage.values())
                move_success_rates = {}
                for move_idx in range(8):
                    if self.belief_space.move_usage[move_idx] > 0:
                        rate = self.belief_space.move_success[move_idx] / self.belief_space.move_usage[move_idx]
                        move_success_rates[move_idx] = rate

                # Find most successful move
                best_move = -1
                best_rate = 0
                if move_success_rates:
                    best_move = max(move_success_rates.keys(), key=lambda x: move_success_rates[x])
                    best_rate = move_success_rates[best_move]

                # Check if belief guidance is active
                belief_active = self.belief_space.generation_count >= self.use_belief_after_gen

                print(f"\nGeneration {generation:3d}/{self.generations}")
                print(f"  Fitness: Best={best_fitness:6.1f} | Avg={avg_fitness:6.1f} | Min={min(fitness_scores):6.1f} | Max={max(fitness_scores):6.1f}")
                print(f"  Coverage: {unique_squares}/{self.n*self.n} squares ({unique_squares/(self.n*self.n)*100:.1f}%)")
                print(f"  Path Length: {len(self.best_path)} moves")
                print(f"  Level 3 Cultural Metrics:")
                print(f"    - Belief Space Generation: {self.belief_space.generation_count}")
                print(f"    - Belief Guidance: {'✓ ACTIVE' if belief_active else '✗ Inactive (learning phase)'}")
                print(f"    - Total Move Usage: {total_move_usage}")
                if best_move >= 0:
                    print(f"    - Best Move: #{best_move} (success rate: {best_rate:.1%})")
                print(f"    - Elite Knowledge Pool: {len(self.belief_space.best_individuals)} individuals")
                print(f"    - Position Map Size: {len(self.belief_space.mobility_map)} positions tracked")
                print(f"    - Genetic Ops: {self.crossover_count} crossovers (belief-guided), {self.mutation_count} mutations (belief-guided)")

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

        # Verbose: Final summary with belief space analysis
        if self.verbose:
            target_squares = self.n * self.n
            unique_visited = len(set(self.best_path))
            success = unique_visited == target_squares

            print(f"\n{'='*70}")
            print(f"LEVEL 3 FINAL RESULTS")
            print(f"{'='*70}")
            print(f"Success: {'✓ Complete Tour!' if success else '✗ Partial Tour'}")
            print(f"Coverage: {unique_visited}/{target_squares} squares ({unique_visited/target_squares*100:.1f}%)")
            print(f"Path Length: {len(self.best_path)} moves")
            print(f"Best Fitness: {self.best_fitness:.1f}")
            print(f"Final Diversity: {self.population_diversity[-1]:.2f}")

            print(f"\nBelief Space Knowledge Summary:")
            print(f"  Total Generations Learned: {self.belief_space.generation_count}")
            print(f"  Move Success Rates:")
            for move_idx in range(8):
                if self.belief_space.move_usage[move_idx] > 0:
                    rate = self.belief_space.move_success[move_idx] / self.belief_space.move_usage[move_idx]
                    usage_pct = self.belief_space.move_usage[move_idx] / sum(self.belief_space.move_usage.values()) * 100
                    print(f"    Move {move_idx}: {rate:5.1%} success | {usage_pct:4.1f}% usage | {self.belief_space.move_usage[move_idx]} times")

            print(f"\nTotal Genetic Operations:")
            print(f"  - Crossovers (with belief injection): {self.crossover_count}")
            print(f"  - Mutations (belief-guided): {self.mutation_count}")
            print(f"{'='*70}\n")

        target_squares = self.n * self.n
        unique_visited = len(set(self.best_path))
        success = unique_visited == target_squares

        return success, self.best_path
