import random
from typing import List, Tuple, Set, Dict
from .level3_cultural_ga import CulturalGASolver, BeliefSpace
from .utils import MobilityManager


class AdvancedBeliefSpace(BeliefSpace):

    def __init__(self, n: int):
        super().__init__(n)

        # Advanced tracking beyond Level 3
        self.transition_quality = {}  # Track success/failure of position pairs
        self.dangerous_transitions = set()  # Patterns that lead to poor solutions
        self.good_patterns = []  # Successful 3-move patterns (pattern, fitness)
        self.stagnation_counter = 0  # Count generations without improvement
        self.last_best_fitness = 0  # Track fitness for stagnation detection

    def update(self, population: List[List[int]], fitness_scores: List[float], decoded_paths: List[List[Tuple[int, int]]]):
        # Call parent update for basic belief space learning
        super().update(population, fitness_scores, decoded_paths)

        # Track stagnation - if fitness isn't improving, increase counter
        current_best = max(fitness_scores)
        if abs(current_best - self.last_best_fitness) < 1:
            self.stagnation_counter += 1
        else:
            self.stagnation_counter = max(0, self.stagnation_counter - 1)
        self.last_best_fitness = current_best

        # Learn from top performers (top 20%)
        sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)
        top_count = max(1, len(sorted_indices) // 5)

        for i in range(top_count):
            idx = sorted_indices[i]
            path = decoded_paths[idx]
            fitness = fitness_scores[idx]

            # Track transition quality (pairs of positions)
            for j in range(len(path) - 1):
                current_pos = path[j]
                next_pos = path[j + 1]
                transition = (current_pos, next_pos)

                if transition not in self.transition_quality:
                    self.transition_quality[transition] = {'success': 0, 'failure': 0}

                # High fitness = successful transition
                if fitness > (self.n * self.n) * 7:  # Good solutions (fitness > 7 * board_size)
                    self.transition_quality[transition]['success'] += 1
                else:
                    self.transition_quality[transition]['failure'] += 1

            # Store successful 3-move patterns (for pattern injection)
            if len(path) >= self.n * self.n * 0.7:  # Path covers at least 70% of board
                for k in range(len(path) - 2):
                    pattern = (path[k], path[k + 1], path[k + 2])
                    # Avoid duplicates
                    if pattern not in [p[0] for p in self.good_patterns]:
                        self.good_patterns.append((pattern, fitness))

        # Keep only best patterns (limit memory usage)
        self.good_patterns.sort(key=lambda x: x[1], reverse=True)
        self.good_patterns = self.good_patterns[:15]

        # Learn from failures (bottom 10%)
        bottom_count = max(1, len(sorted_indices) // 10)
        for i in range(bottom_count):
            idx = sorted_indices[-(i + 1)]
            path = decoded_paths[idx]

            # If path is very poor, mark its transitions as dangerous
            if len(path) < self.n * self.n * 0.5:
                for j in range(len(path) - 1):
                    transition = (path[j], path[j + 1])
                    self.dangerous_transitions.add(transition)

    def is_good_transition(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        transition = (pos1, pos2)

        # Avoid known dangerous transitions
        if transition in self.dangerous_transitions:
            return False

        # Check quality data
        if transition in self.transition_quality:
            quality = self.transition_quality[transition]
            return quality['success'] > quality['failure']

        # Unknown transition - assume neutral (True)
        return True

    def get_stagnation_level(self) -> float:
        return min(1.0, self.stagnation_counter / 30.0)


class CulturalAlgorithmSolver(CulturalGASolver):

    def __init__(self, n: int, level: int = 4, use_warnsdorff: bool = True):
        super().__init__(n=n, level=level)
        self.use_warnsdorff = use_warnsdorff

        # Replace basic belief space with advanced one
        self.belief_space = AdvancedBeliefSpace(n)

        # Level 4 specific parameters - ENHANCED FOR BETTER PERFORMANCE
        self.population_size = 150  # Increased from default 100
        self.generations = 300  # Increased from default 100
        self.local_search_freq = 5  # Apply local search more frequently (was 10)
        self.local_search_attempts = 10  # More swap attempts per local search (was 5)
        self.diversity_injection_freq = 15  # Inject diversity every N generations to avoid premature convergence

    def decode(self, chromosome: List[int], start_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        path = [start_pos]
        visited = {start_pos}
        current_pos = start_pos
        mobility_manager = MobilityManager(self.n, visited)

        for move_index in chromosome:
            if len(visited) >= self.n * self.n:
                break

            next_pos = self.apply_move(current_pos, move_index)

            if self.is_valid_position(next_pos[0], next_pos[1]) and next_pos not in visited:
                if self.use_warnsdorff:
                    mobility = mobility_manager.get_mobility(next_pos[0], next_pos[1])
                else:
                    mobility = self._get_mobility(next_pos, visited | {next_pos})
                difficulty = self.belief_space.get_position_difficulty(next_pos)

                if mobility > 0 or (len(visited) < 5 and difficulty < 0.7):
                    path.append(next_pos)
                    visited.add(next_pos)
                    current_pos = next_pos
                    mobility_manager.update_after_move(current_pos, visited)
                    continue

            valid_moves = self.get_valid_moves_from(current_pos[0], current_pos[1], visited)
            if not valid_moves:
                break

            if self.use_warnsdorff:

                move_mobilities = []
                for move in valid_moves:
                    mobility = mobility_manager.get_mobility(move[0], move[1])
                    move_mobilities.append((move, mobility))

                if move_mobilities:
                    min_mobility = min(move_mobilities, key=lambda x: x[1])[1]
                    best_moves = [move for move, mobility in move_mobilities if mobility == min_mobility]

                    if len(best_moves) == 1:
                        best_move = best_moves[0]
                    else:
                        # Tie-breaking with existing scoring function
                        best_move = None
                        max_score = -1
                        for candidate in best_moves:
                            mobility = mobility_manager.get_mobility(candidate[0], candidate[1])
                            future_moves = len(self.get_valid_moves_from(candidate[0], candidate[1], visited | {candidate}))
                            difficulty = self.belief_space.get_position_difficulty(candidate)
                            score = mobility * 2 + future_moves - difficulty * 10
                            if score > max_score:
                                max_score = score
                                best_move = candidate
                        if best_move is None and best_moves:
                            best_move = best_moves[0]
                else:
                    best_move = None
            else:
                # Original scoring logic
                best_move = None
                max_score = -1
                for candidate in valid_moves:
                    mobility = mobility_manager.get_mobility(candidate[0], candidate[1])
                    future_moves = len(self.get_valid_moves_from(candidate[0], candidate[1], visited | {candidate}))
                    difficulty = self.belief_space.get_position_difficulty(candidate)

                    score = mobility * 2 + future_moves - difficulty * 10
                    if score > max_score:
                        max_score = score
                        best_move = candidate

            if best_move is None:
                if valid_moves:
                    best_move = valid_moves[0]
                else:
                    break # No valid moves left

            path.append(best_move)
            visited.add(best_move)
            current_pos = best_move
            mobility_manager.update_after_move(current_pos, visited)

        return path

    def fitness(self, chromosome: List[int], start_pos: Tuple[int, int]) -> float:

        path = self.decode(chromosome, start_pos)
        if not path:
            return 0.0

        unique_count = len(set(path))
        legal_transitions = 0
        consecutive_segments = 0
        current_segment = 1
        low_degree_visits = 0
        total_mobility = 0

        visited_set = set()

        for i, pos in enumerate(path):
            visited_set.add(pos)

            # Track mobility (from Level 2)
            mobility = self._get_mobility(pos, visited_set)
            total_mobility += mobility

            # Track low-degree visits (Warnsdorff heuristic bonus)
            if mobility <= 2:
                low_degree_visits += 1

            # Check transitions
            if i < len(path) - 1:
                x1, y1 = path[i]
                x2, y2 = path[i + 1]
                dx, dy = abs(x2 - x1), abs(y2 - y1)

                # Legal knight move
                if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
                    legal_transitions += 1
                    current_segment += 1
                else:
                    # Illegal move - end current segment and penalize
                    consecutive_segments += current_segment
                    current_segment = 1

        # Add final segment
        consecutive_segments += current_segment

        # Calculate penalties
        repeat_penalty = 0
        if len(path) > unique_count:
            repeat_penalty = (len(path) - unique_count) * 15

        # Calculate average mobility
        avg_mobility = total_mobility / len(path) if len(path) > 0 else 0

        # Advanced fitness calculation
        fitness_score = (
            unique_count * 20 +              # Unique squares (highest weight)
            legal_transitions * 10 +          # Legal moves
            consecutive_segments * 4 +        # Consecutive valid sequences
            avg_mobility * self.mobility_weight +  # Mobility bonus
            low_degree_visits * 5 -           # Warnsdorff bonus
            repeat_penalty                    # Penalty for revisiting
        )

        # Bonus for complete tour
        if unique_count == self.n * self.n:
            fitness_score += 500

        return float(fitness_score)

    def _find_bad_moves(self, chromosome: List[int], start_pos: Tuple[int, int]) -> List[int]:
        """Analyzes a chromosome's path to find indices of bad moves."""
        path = [start_pos]
        visited = {start_pos}
        current_pos = start_pos
        bad_move_indices = []

        for i, move_index in enumerate(chromosome):
            if len(visited) >= self.n * self.n:
                break

            next_pos = self.apply_move(current_pos, move_index)

            if not self.is_valid_position(next_pos[0], next_pos[1]) or next_pos in visited:
                bad_move_indices.append(i)
            else:
                path.append(next_pos)
                visited.add(next_pos)
                current_pos = next_pos
        
        return bad_move_indices


    def local_search(self, chromosome: List[int], start_pos: Tuple[int, int]) -> List[int]:
        current_fitness = self.fitness(chromosome, start_pos)
        best_chromosome = chromosome.copy()
        best_fitness = current_fitness
        improvement_found = True

        # Iterate until no more improvements
        iterations = 0
        max_iterations = 3  # Prevent infinite loop

        while improvement_found and iterations < max_iterations:
            improvement_found = False
            iterations += 1

            # Strategy 1: Random swaps
            for _ in range(self.local_search_attempts):
                if len(chromosome) < 5:
                    break

                i = random.randint(1, len(chromosome) - 4)
                j = random.randint(i + 2, min(i + 8, len(chromosome) - 1))

                test_chromosome = best_chromosome.copy()
                test_chromosome[i], test_chromosome[j] = test_chromosome[j], test_chromosome[i]

                new_fitness = self.fitness(test_chromosome, start_pos)

                if new_fitness > best_fitness:
                    best_fitness = new_fitness
                    best_chromosome = test_chromosome.copy()
                    improvement_found = True

            # Strategy 2: Segment reversals (helps with order-dependent problems)
            for _ in range(self.local_search_attempts // 2):
                if len(chromosome) < 6:
                    break

                i = random.randint(1, len(chromosome) - 5)
                j = random.randint(i + 3, min(i + 10, len(chromosome) - 1))

                test_chromosome = best_chromosome.copy()
                test_chromosome[i:j] = test_chromosome[i:j][::-1]

                new_fitness = self.fitness(test_chromosome, start_pos)

                if new_fitness > best_fitness:
                    best_fitness = new_fitness
                    best_chromosome = test_chromosome.copy()
                    improvement_found = True

            # Strategy 3: Belief-guided replacement (if belief space is mature)
            if self.belief_space.generation_count >= self.use_belief_after_gen:
                for _ in range(self.local_search_attempts // 3):
                    pos = random.randint(0, len(best_chromosome) - 1)
                    suggested = self.belief_space.suggest_move()

                    test_chromosome = best_chromosome.copy()
                    test_chromosome[pos] = suggested

                    new_fitness = self.fitness(test_chromosome, start_pos)

                    if new_fitness > best_fitness:
                        best_fitness = new_fitness
                        best_chromosome = test_chromosome.copy()
                        improvement_found = True

            # Strategy 4: Smarter Swaps (targeting bad moves)
            bad_moves = self._find_bad_moves(best_chromosome, start_pos)
            if bad_moves:
                for _ in range(self.local_search_attempts // 2):
                    bad_move_idx = random.choice(bad_moves)
                    
                    # Try swapping with another random gene
                    swap_with_idx = random.randint(0, len(best_chromosome) - 1)
                    if swap_with_idx == bad_move_idx:
                        continue

                    test_chromosome = best_chromosome.copy()
                    test_chromosome[bad_move_idx], test_chromosome[swap_with_idx] = test_chromosome[swap_with_idx], test_chromosome[bad_move_idx]
                    
                    new_fitness = self.fitness(test_chromosome, start_pos)
                    if new_fitness > best_fitness:
                        best_fitness = new_fitness
                        best_chromosome = test_chromosome
                        improvement_found = True
                        break # Found an improvement, restart the loop

        return best_chromosome

    def mutate(self, chromosome: List[int]) -> List[int]:
        # Adaptive mutation rate based on stagnation
        stagnation = self.belief_space.get_stagnation_level()
        dynamic_rate = self.mutation_rate + (stagnation * 0.3)

        if random.random() > dynamic_rate:
            return chromosome

        mutated = chromosome.copy()

        # More mutations when stagnating
        num_mutations = random.randint(1, 3) if stagnation > 0.5 else random.randint(1, 2)

        use_belief = self.belief_space.generation_count >= self.use_belief_after_gen

        for _ in range(num_mutations):
            pos = random.randint(0, len(mutated) - 1)

            if use_belief and random.random() < 0.7:
                # Use belief space suggestion
                suggested = self.belief_space.suggest_move()
                if pos > 0 and mutated[pos - 1] != suggested:
                    mutated[pos] = suggested
                else:
                    mutated[pos] = random.randint(0, 7)
            else:
                # Random or smart mutation
                if random.random() < 0.2:
                    mutated[pos] = random.randint(0, 7)
                else:
                    # Prefer moves with variety
                    move_scores = []
                    for move_idx in range(8):
                        if pos > 0 and mutated[pos - 1] == move_idx:
                            continue
                        move_scores.append((move_idx, random.random() + (move_idx % 3)))

                    move_scores.sort(key=lambda x: x[1], reverse=True)
                    mutated[pos] = move_scores[0][0] if move_scores else random.randint(0, 7)

        self.mutation_count += 1
        return mutated

    def evolve(self, start_pos: Tuple[int, int]) -> Tuple[bool, List[Tuple[int, int]]]:
        population = self.initialize_population()
        self.generation_best_fitness = []
        self.generation_avg_fitness = []
        self.population_diversity = []
        self.mutation_count = 0
        self.crossover_count = 0
        self.belief_space = AdvancedBeliefSpace(self.n)



        for generation in range(self.generations):
            decoded_paths = [self.decode(chrom, start_pos) for chrom in population]
            fitness_scores = [self.fitness(chrom, start_pos) for chrom in population]

            # Update advanced belief space
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

            # Apply local search to elite individuals periodically
            if generation > 20 and generation % self.local_search_freq == 0:
                # Local search on top 3 individuals (increased from 2)
                sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)
                for i in range(min(3, len(sorted_indices))):
                    idx = sorted_indices[i]
                    improved_chrom = self.local_search(population[idx], start_pos)
                    population[idx] = improved_chrom
                    fitness_scores[idx] = self.fitness(improved_chrom, start_pos)

            # Diversity injection: prevent premature convergence
            if generation > 30 and generation % self.diversity_injection_freq == 0:
                # Check if diversity is too low
                if diversity < 0.3:
                    # Replace bottom 20% of population with fresh random individuals
                    sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)
                    num_to_replace = max(1, len(population) // 5)

                    for i in range(num_to_replace):
                        idx = sorted_indices[-(i + 1)]  # Start from worst individuals
                        population[idx] = [random.randint(0, 7) for _ in range(self.n * self.n * 2)]
                        fitness_scores[idx] = self.fitness(population[idx], start_pos)



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

    # Compatibility method for existing GUI code
    def solve(self, start_x: int = 0, start_y: int = 0) -> Tuple[bool, List[Tuple[int, int]]]:
        start_pos = (start_x, start_y)
        return self.evolve(start_pos)
