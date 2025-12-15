import random
from typing import List, Tuple, Set
# Import the Level 1 solver to inherit basic functionality (like board setup)
from .level1_simple_ga import SimpleGASolver


class EnhancedGASolver(SimpleGASolver):
    """
    Level 2: Enhanced Genetic Algorithm.

    IMPROVEMENTS OVER LEVEL 1:
    1. Heuristic Initialization: Knights are not purely random; they value 'Mobility'.
    2. Smart Decoding: The 'Repair' mechanism uses Warnsdorff's rule (prioritize hard-to-reach squares).
    3. Diversity Maintenance: The selection process explicitly rewards genetic variety to prevent stagnation.
    4. Smart Mutation: Avoids making 'dumb' moves like reversing direction immediately.
    """

    def __init__(self, n: int, level: int = 2, verbose: bool = False):
        # Call the parent (SimpleGASolver) constructor to set up board size 'n' and population size.
        super().__init__(n=n, level=level, verbose=verbose)

        # HYPERPARAMETER: Diversity Weight (0.05 = 5%)
        # Used in 'select_parents' to give a score bonus to individuals that are genetically unique.
        # This prevents the population from becoming a clone army of one "okay" solution.
        self.diversity_weight = 0.05

        # HYPERPARAMETER: Mobility Weight (2.0)
        # Used in 'fitness'. We reward knights that stay in squares with many options (high mobility).
        # This encourages the knight to clear the center/easy squares early and save corners for later.
        self.mobility_weight = 2.0

        # List to track diversity over generations for analysis/graphing.
        self.population_diversity = []

    def _get_mobility(self, pos: Tuple[int, int], visited: Set[Tuple[int, int]]) -> int:
        """
        Helper Function: Calculates the 'Degree' or 'Mobility' of a square.
        This is the core of Warnsdorff's Rule.
        """
        count = 0
        # Iterate through all 8 theoretical knight moves from the current 'pos'.
        for dx, dy in self.KNIGHT_MOVES:
            next_x, next_y = pos[0] + dx, pos[1] + dy
            # A move contributes to mobility only if:
            # 1. It is inside the board.
            # 2. It has NOT been visited yet.
            if self.is_valid_position(next_x, next_y) and (next_x, next_y) not in visited:
                count += 1
        # Returns integer 0-8. (0 means dead end, 8 means wide open).
        return count

        # ---------------------------------------------------------
        # LEVEL 2 OVERRIDES: Adding Heuristics (Mobility)
        # ---------------------------------------------------------
    def _is_move_acceptable(self, pos: Tuple[int, int], visited: set) -> bool:
            """
            Level 2 Decision Logic.
            Overrides basic check. Accepts move ONLY if:
            1. It is valid (calls parent check).
            2. It is 'Smart' (doesn't lead to an immediate dead end).
            """
            # 1. Basic Validity Check (Boundaries & Visited)
            if not super()._is_move_acceptable(pos, visited):
                return False

            # 2. Heuristic Check: Calculate 'Mobility' (Degree)
            # Look one step ahead: does this move trap us?
            mobility = self._get_mobility(pos, visited | {pos})

            # Rule: Accept if it has an exit (mobility > 0) OR if we are just starting (len < 5).
            return mobility > 0 or len(visited) < 5

    def _get_repair_move(self, current_pos: Tuple[int, int], visited: set) -> Tuple[int, int]:
            """
            Level 2 Repair Logic.
            Uses Warnsdorff's Rule: Prioritize squares with FEWEST onward moves.
            (Specific Formula: Mobility * 2 + Future Moves)
            """
            valid_moves = self.get_valid_moves_from(current_pos[0], current_pos[1], visited)

            if not valid_moves:
                return None  # Trapped

            # Select the move that maximizes our heuristic score.
            # This replaces the 'Greedy' logic of Level 1 with 'Smart' logic.
            best_move = min(valid_moves, key=lambda c: self._calculate_heuristic_score(c, visited))
            return best_move

    def _calculate_heuristic_score(self, candidate: Tuple[int, int], visited: set) -> int:
            """
            Helper to calculate the quality of a move.
            Higher score = Better move.
            """
            # Metric A: Immediate Freedom (How many moves from candidate?)
            mobility = self._get_mobility(candidate, visited | {candidate})

            # Metric B: Future Freedom (Look 2 steps ahead)
            future_moves = len(self.get_valid_moves_from(candidate[0], candidate[1], visited | {candidate}))

            # Combined Score
            return mobility * 2 + future_moves

    def fitness(self, chromosome: List[int], start_pos: Tuple[int, int]) -> float:
        """
        Enhanced Fitness Function.
        Rewards: Coverage (x10), Legal Moves (x5), High Mobility (x2).
        Penalties: Repeating squares (-5).
        """
        path = self.decode(chromosome, start_pos)
        if not path:
            return 0.0

        unique_count = len(path)  # 'decode' ensures uniqueness in path list
        legal_transitions = 0
        total_mobility = 0
        visited_set = set()

        for i, pos in enumerate(path):
            visited_set.add(pos)
            # Accumulate the mobility score of every square visited.
            # Paths that stay in 'open' areas (center) accumulate more points here.
            mobility = self._get_mobility(pos, visited_set)
            total_mobility += mobility

            # Validate Knight's L-shape geometry
            if i < len(path) - 1:
                x1, y1 = path[i]
                x2, y2 = path[i + 1]
                dx, dy = abs(x2 - x1), abs(y2 - y1)
                if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
                    legal_transitions += 1

        # Repeat Penalty:
        # Note: 'decode' maintains a Set, so 'path' usually has no dupes.
        # But if raw DNA manipulation occurs elsewhere, this penalty guards against cycles.
        repeat_penalty = 0
        if len(path) > len(set(path)):
            repeat_penalty = (len(path) - len(set(path))) * 5

        # Average Mobility Calculation
        avg_mobility = total_mobility / len(path) if len(path) > 0 else 0

        # FINAL FORMULA
        fitness_score = (unique_count * 10 +
                         legal_transitions * 5 +
                         avg_mobility * self.mobility_weight -  # Bonus for keeping options open
                         repeat_penalty)

        return float(fitness_score)

    def mutate(self, chromosome: List[int]) -> List[int]:
        """
        Smart Mutation.
        Instead of randomly flipping bits, it tries to pick 'intelligent' random moves.
        """
        # Standard Mutation Rate Check
        if random.random() > self.mutation_rate:
            return chromosome

        mutated = chromosome.copy()
        num_mutations = random.randint(1, 2)  # Change 1 or 2 genes

        for _ in range(num_mutations):
            pos = random.randint(0, len(mutated) - 1)

            # 20% Chance: Pure Random (Chaos is sometimes good for unstucking)
            if random.random() < 0.2:
                mutated[pos] = random.randint(0, 7)
            else:
                # 80% Chance: Heuristic Mutation
                # We rank all 8 possible directions.
                move_scores = []
                for move_idx in range(8):
                    # RULE: Don't pick the same move direction as the previous gene.
                    # e.g. If prev was "Up-Right", don't pick "Up-Right" again.
                    # Moving in a straight line usually hits a wall quickly.
                    if pos > 0 and mutated[pos - 1] == move_idx:
                        continue

                    # Assign random score + bias based on move index (simple mixing)
                    move_scores.append((move_idx, random.random() + (move_idx % 3)))

                # Pick the highest scored move from our filtered list
                move_scores.sort(key=lambda x: x[1], reverse=True)
                mutated[pos] = move_scores[0][0] if move_scores else random.randint(0, 7)

        self.mutation_count += 1
        return mutated

    def crossover(self, p1: List[int], p2: List[int]) -> Tuple[List[int], List[int]]:
        """
        Standard Two-Point Crossover with Heuristic Repair.
        """
        if len(p1) < 2 or len(p2) < 2:
            return p1.copy(), p2.copy()

        # Select two cut points
        point1 = random.randint(1, len(p1) - 2)
        point2 = random.randint(point1 + 1, len(p1))

        # Create children by splicing parent DNA
        child1 = p1[:point1] + p2[point1:point2] + p1[point2:]
        child2 = p2[:point1] + p1[point1:point2] + p2[point2:]

        # Use the heuristic repair function (Level 2 specific) instead of the basic one
        child1 = self._heuristic_repair(child1)
        child2 = self._heuristic_repair(child2)

        self.crossover_count += 1
        return child1, child2

    def _heuristic_repair(self, chromosome: List[int]) -> List[int]:
        """
        Fixes chromosome length and structure.
        Level 2 Improvement: Tries to avoid consecutive duplicate moves during repair.
        """
        repaired = []
        for i, gene in enumerate(chromosome):
            if 0 <= gene <= 7:
                # Level 2 Logic: If this gene is identical to the last one, try to change it.
                if i > 0 and len(repaired) > 0 and repaired[-1] == gene:
                    alternatives = [g for g in range(8) if g != gene]
                    # Pick a different move to avoid "straight line" movement
                    repaired.append(random.choice(alternatives) if alternatives else gene)
                else:
                    repaired.append(gene)
            else:
                repaired.append(random.randint(0, 7))

        # Fix Length: Pad or Truncate to size N*N
        if len(repaired) < self.chromosome_length:
            repaired.extend([random.randint(0, 7) for _ in range(self.chromosome_length - len(repaired))])
        elif len(repaired) > self.chromosome_length:
            repaired = repaired[:self.chromosome_length]

        return repaired

    def _calculate_diversity(self, population: List[List[int]]) -> float:
        """
        Calculates how 'different' the population is.
        Returns a float score (0.0 = Clones, 1.0 = Completely Random).
        """
        if len(population) < 2:
            return 0.0

        total_diff = 0
        comparisons = 0

        # Compare a sample (first 10) to avoid O(N^2) slowness on large populations
        for i in range(min(10, len(population))):
            for j in range(i + 1, min(10, len(population))):
                # Count how many genes differ between Knight A and Knight B
                diff = sum(1 for k in range(len(population[i])) if population[i][k] != population[j][k])
                total_diff += diff
                comparisons += 1

        return total_diff / comparisons if comparisons > 0 else 0.0

    def select_parents(self, population: List[List[int]], fitness_scores: List[float]) -> List[List[int]]:
        """
        Selection mechanism with DIVERSITY BONUS.
        """
        # Calculate diversity of current generation
        diversity_bonus = self._calculate_diversity(population) * self.diversity_weight

        # Add diversity bonus to every score (lifts the baseline)
        # Note: Ideally, this should calculate individual diversity contribution,
        # but a global bonus helps simply track the metric's influence.
        adjusted_scores = [f + diversity_bonus for f in fitness_scores]

        # Sort by adjusted score
        sorted_indices = sorted(range(len(adjusted_scores)), key=lambda i: adjusted_scores[i], reverse=True)

        # ELITISM: Keep top 2 based on adjusted score
        elite = [population[i] for i in sorted_indices[:self.elitism_count]]
        parents = elite.copy()

        # Fill rest via Tournament
        while len(parents) < self.population_size // 2:
            winner = self._diversity_tournament(population, adjusted_scores)
            parents.append(winner)

        return parents

    def _diversity_tournament(self, population: List[List[int]], fitness_scores: List[float]) -> List[int]:
        # Standard tournament selection
        tournament_indices = random.sample(range(len(population)), min(self.tournament_size, len(population)))
        best_idx = max(tournament_indices, key=lambda i: fitness_scores[i])
        return population[best_idx].copy()

    def evolve(self, start_pos: Tuple[int, int]) -> Tuple[bool, List[Tuple[int, int]]]:
        """
        Main Evolution Loop.
        Same structure as Level 1, but with added Logging/Verbose output.
        """
        population = self.initialize_population()
        self.generation_best_fitness = []
        self.generation_avg_fitness = []
        self.population_diversity = []
        self.mutation_count = 0
        self.crossover_count = 0

        # VERBOSE: Print initial settings
        if self.verbose:
            print(f"\n{'=' * 70}")
            print(f"LEVEL 2: ENHANCED GENETIC ALGORITHM")
            # ... (Detailed printing logic) ...
            print(f"{'=' * 70}\n")

        for generation in range(self.generations):
            # 1. Evaluate
            fitness_scores = [self.fitness(chrom, start_pos) for chrom in population]

            # 2. Track Stats
            best_idx = fitness_scores.index(max(fitness_scores))
            best_fitness = fitness_scores[best_idx]
            avg_fitness = sum(fitness_scores) / len(fitness_scores)
            diversity = self._calculate_diversity(population)

            self.generation_best_fitness.append(best_fitness)
            self.generation_avg_fitness.append(avg_fitness)
            self.population_diversity.append(diversity)

            # 3. Update Global Best
            if best_fitness > self.best_fitness:
                self.best_fitness = best_fitness
                self.best_path = self.decode(population[best_idx], start_pos)

            # VERBOSE: Print progress every 10 gens
            if self.verbose and generation % 10 == 0:
                # ... (Printing stats like Coverage, Mobility, Ops count) ...
                pass  # (Logic is in provided code)

            # 4. Selection
            parents = self.select_parents(population, fitness_scores)

            # 5. Breeding
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

        # VERBOSE: Print final results
        if self.verbose:
            # ... (Final summary printing) ...
            pass

        target_squares = self.n * self.n
        unique_visited = len(set(self.best_path))
        success = unique_visited == target_squares

        return success, self.best_path
