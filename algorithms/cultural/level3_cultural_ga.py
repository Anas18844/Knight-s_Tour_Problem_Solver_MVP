import random
from typing import List, Tuple, Optional

# Import Level 2 solver to inherit the heuristic logic (mobility, diversity)
from .level2_enhanced_ga import EnhancedGASolver


class BeliefSpace:
    """
    The 'Global Brain' or 'Culture' of the algorithm.
    It persists knowledge across generations, allowing new knights to learn
    from the successes and failures of their ancestors.

    Stores two types of knowledge:
    1. Normative Knowledge: Which move directions (0-7) generally work best?
    2. Situational Knowledge: Which specific board squares are 'difficult' or 'easy'?
    """

    def __init__(self, n: int):
        self.n = n

        # NORMATIVE KNOWLEDGE (General Rules):
        # Tracks how many times each move (0-7) contributed to a 'Good' tour (>300 fitness).
        self.move_success = {i: 0 for i in range(8)}
        # Tracks how many times each move was used in total.
        self.move_usage = {i: 0 for i in range(8)}

        # SITUATIONAL KNOWLEDGE (Specific Locations):
        # Maps board coordinates (x,y) to stats about visits vs. success.
        # Structure: {(x,y): {'visits': int, 'success': int}}
        self.mobility_map = {}

        # ELITE ARCHIVE:
        # Stores the absolute best individuals found so far to preserve "Genius" DNA.
        self.best_individuals = []

        self.generation_count = 0

    def update(self, population: List[List[int]], fitness_scores: List[float],
               decoded_paths: List[List[Tuple[int, int]]]):
        """
        Updates the Belief Space based on the performance of the current generation.
        This is the 'Learning' phase where culture is updated.
        """
        self.generation_count += 1

        # 1. IDENTIFY ELITES:
        # Sort current population by fitness to find the best performers.
        sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)

        # Store top 3 individuals in the Elite Archive for later use in Crossover.
        top_n = min(3, len(sorted_indices))
        self.best_individuals = []
        for i in range(top_n):
            idx = sorted_indices[i]
            self.best_individuals.append({
                'chromosome': population[idx].copy(),
                'fitness': fitness_scores[idx],
                'path': decoded_paths[idx].copy()
            })

        # 2. EXTRACT KNOWLEDGE (from Top 5 Performers):
        # We only learn from the best (Top 5), assuming their habits are worth copying.
        for i in range(min(5, len(sorted_indices))):
            idx = sorted_indices[i]
            chromosome = population[idx]
            path = decoded_paths[idx]
            fitness = fitness_scores[idx]

            # Update Move Statistics (Normative Knowledge)
            for move_idx in chromosome:
                if 0 <= move_idx <= 7:
                    self.move_usage[move_idx] += 1
                    # Threshold: If fitness > 300, we consider this a "Successful" strategy.
                    if fitness > 300:
                        self.move_success[move_idx] += 1

            # Update Map Statistics (Situational Knowledge)
            for pos in path:
                if pos not in self.mobility_map:
                    self.mobility_map[pos] = {'visits': 0, 'success': 0}

                self.mobility_map[pos]['visits'] += 1

                # Rule: If a path covers >80% of the board, every square in it
                # is considered part of a "Winning Pattern".
                if len(path) >= self.n * self.n * 0.8:
                    self.mobility_map[pos]['success'] += 1

    def get_move_probability(self, move_idx: int) -> float:
        """
        Calculates the historical success rate of a specific move direction.
        Returns: 0.0 to 1.0
        """
        if self.move_usage[move_idx] == 0:
            return 0.5  # Neutral if no data

        success_rate = self.move_success[move_idx] / self.move_usage[move_idx]
        return success_rate

    def get_position_difficulty(self, pos: Tuple[int, int]) -> float:
        """
        Calculates how 'Difficult' a specific square is.

        Logic:
        - If a square is visited often ('visits' high)...
        - But rarely leads to a full tour ('success' low)...
        - Then it is a 'Trap' or 'Difficult Square'.

        Returns: 0.0 (Easy) to 1.0 (Hard/Trap).
        """
        if pos not in self.mobility_map:
            return 0.5  # Neutral if unknown

        visits = self.mobility_map[pos]['visits']
        if visits == 0:
            return 0.5

        success = self.mobility_map[pos]['success']
        # Difficulty = Failure Rate
        return 1.0 - (success / visits)

    def suggest_move(self) -> int:
        """
        Consults the Normative Knowledge to suggest a move direction.
        Used during Mutation to guide random changes toward historically good moves.
        """
        # Don't give advice if we haven't learned anything yet (first 10 gens).
        if self.generation_count < 10:
            return random.randint(0, 7)

        # Score all 8 moves based on history
        move_scores = []
        for move_idx in range(8):
            prob = self.get_move_probability(move_idx)
            usage = self.move_usage[move_idx]

            # Score balances:
            # 1. Success Rate (70% weight) - Is it good?
            # 2. Usage Frequency (30% weight) - Is it popular?
            score = prob * 0.7 + (usage / max(1, sum(self.move_usage.values()))) * 0.3
            move_scores.append((move_idx, score))

        # Sort by score descending (Best moves first)
        move_scores.sort(key=lambda x: x[1], reverse=True)

        # 20% Chance: Return random anyway (Maintain Exploration)
        if random.random() < 0.2:
            return random.randint(0, 7)

        # 80% Chance: Return the historically BEST move (Exploitation)
        return move_scores[0][0]

class CulturalGASolver(EnhancedGASolver):

        def __init__(self, n: int, level: int = 3, verbose: bool = False):
            super().__init__(n=n, level=level, verbose=verbose)
            self.belief_space = BeliefSpace(n)
            self.use_belief_after_gen = 20

        # ---------------------------------------------------------
        # LEVEL 3 OVERRIDES
        # ---------------------------------------------------------
        def _is_move_acceptable(self, pos: Tuple[int, int], visited: set) -> bool:
            """Level 3: Accept if valid + mobile + NOT difficult."""
            # Use L1 check to avoid recursion loops
            if not (self.is_valid_position(pos[0], pos[1]) and pos not in visited):
                return False

            mobility = self._get_mobility(pos, visited | {pos})
            difficulty = self.belief_space.get_position_difficulty(pos)

            # Accept if mobile OR (early game AND safe)
            return mobility > 0 or (len(visited) < 5 and difficulty < 0.7)

        def _get_repair_move(self, current_pos: Tuple[int, int], visited: set) -> Optional[Tuple[int, int]]:
            """
            Level 3: WARNSDORFF + CULTURE.
            We want MINIMUM score.
            Score = Mobility (Low is good) + Difficulty Penalty (High difficulty adds score).
            """
            valid_moves = self.get_valid_moves_from(current_pos[0], current_pos[1], visited)
            if not valid_moves:
                return None

            def cultural_score(candidate):
                # Base heuristic (Mobility based)
                base_score = self._calculate_heuristic_score(candidate, visited)

                # Difficulty (0.0 to 1.0). High difficulty = 1.0.
                difficulty = self.belief_space.get_position_difficulty(candidate)

                # We want to MINIMIZE this score.
                # So we ADD difficulty (making the score higher/worse for difficult squares).
                return base_score + (difficulty * 10)

            # Pick move with LOWEST cultural score (Low Mobility + Low Difficulty)
            return min(valid_moves, key=cultural_score)

def mutate(self, chromosome: List[int]) -> List[int]:
        """
        Culturally-Guided Mutation.
        Uses Normative Knowledge (Move Success) to pick better random moves.
        """
        if random.random() > self.mutation_rate:
            return chromosome

        mutated = chromosome.copy()
        num_mutations = random.randint(1, 2)

        # Check if culture is established enough to use
        use_belief = self.belief_space.generation_count >= self.use_belief_after_gen

        for _ in range(num_mutations):
            pos = random.randint(0, len(mutated) - 1)

            # CULTURAL INFLUENCE:
            # If belief space is ready, 70% chance to ask for advice.
            if use_belief and random.random() < 0.7:
                # Get a "Smart" random move based on history
                suggested = self.belief_space.suggest_move()

                # Apply if it's different from the previous gene (avoid straights)
                if pos > 0 and mutated[pos - 1] != suggested:
                    mutated[pos] = suggested
                else:
                    # Fallback to pure random
                    mutated[pos] = random.randint(0, 7)
            else:
                # STANDARD HEURISTIC MUTATION (Level 2 fallback)
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
        """
        Crossover with Knowledge Injection.
        Occasionally injects DNA from the global 'Hall of Fame'.
        """
        if len(p1) < 2 or len(p2) < 2:
            return p1.copy(), p2.copy()

        # KNOWLEDGE INJECTION:
        # If belief space is active, 30% chance to ignore Parent 2 and use an Elite instead.
        if self.belief_space.generation_count >= self.use_belief_after_gen and self.belief_space.best_individuals:
            if random.random() < 0.3:
                # Grab the chromosome of the #1 Best Individual ever found.
                best = self.belief_space.best_individuals[0]['chromosome']

                # Splice: Parent 1 + Elite
                point = random.randint(1, len(p1) - 1)
                child1 = p1[:point] + best[point:]
                child2 = p2[:point] + best[point:]
            else:
                # Standard 2-Point Crossover
                point1 = random.randint(1, len(p1) - 2)
                point2 = random.randint(point1 + 1, len(p1))
                child1 = p1[:point1] + p2[point1:point2] + p1[point2:]
                child2 = p2[:point1] + p1[point1:point2] + p2[point2:]
        else:
            # Standard 2-Point Crossover (Early generations)
            point1 = random.randint(1, len(p1) - 2)
            point2 = random.randint(point1 + 1, len(p1))
            child1 = p1[:point1] + p2[point1:point2] + p1[point2:]
            child2 = p2[:point1] + p1[point1:point2] + p2[point2:]

        # Always repair result
        child1 = self._heuristic_repair(child1)
        child2 = self._heuristic_repair(child2)

        self.crossover_count += 1
        return child1, child2

def select_parents(self, population: List[List[int]], fitness_scores: List[float]) -> List[List[int]]:
        """
        Selection with Knowledge Bonus.
        As time goes on, we increase selection pressure.
        """
        # Base Level 2 Bonus (Diversity)
        diversity_bonus = self._calculate_diversity(population) * self.diversity_weight

        # Level 3 Bonus: Age of Culture
        # Slowly increases base scores over time, effectively increasing selection pressure
        # and making small fitness differences more significant.
        if self.belief_space.generation_count >= self.use_belief_after_gen:
            knowledge_bonus = self.belief_space.generation_count * 0.01
            adjusted_scores = [f + diversity_bonus + knowledge_bonus for f in fitness_scores]
        else:
            adjusted_scores = [f + diversity_bonus for f in fitness_scores]

        # Elitism & Tournament (Standard)
        sorted_indices = sorted(range(len(adjusted_scores)), key=lambda i: adjusted_scores[i], reverse=True)
        elite = [population[i] for i in sorted_indices[:self.elitism_count]]
        parents = elite.copy()

        while len(parents) < self.population_size // 2:
            winner = self._diversity_tournament(population, adjusted_scores)
            parents.append(winner)

        return parents

def evolve(self, start_pos: Tuple[int, int]) -> Tuple[bool, List[Tuple[int, int]]]:
        """
        Main Loop for Cultural Algorithm.
        Orchestrates Population Space and Belief Space interaction.
        """
        population = self.initialize_population()
        self.generation_best_fitness = []
        self.generation_avg_fitness = []
        self.population_diversity = []
        self.mutation_count = 0
        self.crossover_count = 0

        # Initialize a fresh Belief Space for this run
        self.belief_space = BeliefSpace(self.n)

        # VERBOSE: Print initial configuration
        if self.verbose:
            print(f"\n{'=' * 70}")
            print(f"LEVEL 3: CULTURAL GENETIC ALGORITHM")
            print(f"{'=' * 70}")
            print(f"Board Size: {self.n}x{self.n} ({self.n * self.n} squares)")
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
            print(f"{'=' * 70}\n")

        for generation in range(self.generations):
            # 1. Decode & Evaluate (Standard)
            decoded_paths = [self.decode(chrom, start_pos) for chrom in population]
            fitness_scores = [self.fitness(chrom, start_pos) for chrom in population]

            # 2. UPDATE BELIEF SPACE (The Learning Step)
            # The population teaches the Belief Space what worked and what didn't.
            self.belief_space.update(population, fitness_scores, decoded_paths)

            # 3. Track Stats
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

                # Calculate belief space statistics for display
                total_move_usage = sum(self.belief_space.move_usage.values())
                move_success_rates = {}
                for move_idx in range(8):
                    if self.belief_space.move_usage[move_idx] > 0:
                        rate = self.belief_space.move_success[move_idx] / self.belief_space.move_usage[move_idx]
                        move_success_rates[move_idx] = rate

                best_move = -1
                best_rate = 0
                if move_success_rates:
                    best_move = max(move_success_rates.keys(), key=lambda x: move_success_rates[x])
                    best_rate = move_success_rates[best_move]

                belief_active = self.belief_space.generation_count >= self.use_belief_after_gen

                print(f"\nGeneration {generation:3d}/{self.generations}")
                print(
                    f"  Fitness: Best={best_fitness:6.1f} | Avg={avg_fitness:6.1f} | Min={min(fitness_scores):6.1f} | Max={max(fitness_scores):6.1f}")
                print(
                    f"  Coverage: {unique_squares}/{self.n * self.n} squares ({unique_squares / (self.n * self.n) * 100:.1f}%)")
                print(f"  Path Length: {len(self.best_path)} moves")
                print(f"  Level 3 Cultural Metrics:")
                print(f"    - Belief Space Generation: {self.belief_space.generation_count}")
                print(f"    - Belief Guidance: {'✓ ACTIVE' if belief_active else '✗ Inactive (learning phase)'}")
                print(f"    - Total Move Usage: {total_move_usage}")
                if best_move >= 0:
                    print(f"    - Best Move: #{best_move} (success rate: {best_rate:.1%})")
                print(f"    - Elite Knowledge Pool: {len(self.belief_space.best_individuals)} individuals")
                print(f"    - Position Map Size: {len(self.belief_space.mobility_map)} positions tracked")
                print(
                    f"    - Genetic Ops: {self.crossover_count} crossovers (belief-guided), {self.mutation_count} mutations (belief-guided)")

            # 4. Selection
            parents = self.select_parents(population, fitness_scores)

            # 5. Breeding (Influence Phase)
            # The Belief Space guides Crossover and Mutation here.
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

            print(f"\n{'=' * 70}")
            print(f"LEVEL 3 FINAL RESULTS")
            print(f"{'=' * 70}")
            print(f"Success: {'✓ Complete Tour!' if success else '✗ Partial Tour'}")
            print(f"Coverage: {unique_visited}/{target_squares} squares ({unique_visited / target_squares * 100:.1f}%)")
            print(f"Path Length: {len(self.best_path)} moves")
            print(f"Best Fitness: {self.best_fitness:.1f}")
            print(f"Final Diversity: {self.population_diversity[-1]:.2f}")

            print(f"\nBelief Space Knowledge Summary:")
            print(f"  Total Generations Learned: {self.belief_space.generation_count}")
            print(f"  Move Success Rates:")
            for move_idx in range(8):
                if self.belief_space.move_usage[move_idx] > 0:
                    rate = self.belief_space.move_success[move_idx] / self.belief_space.move_usage[move_idx]
                    usage_pct = self.belief_space.move_usage[move_idx] / sum(
                        self.belief_space.move_usage.values()) * 100
                    print(
                        f"    Move {move_idx}: {rate:5.1%} success | {usage_pct:4.1f}% usage | {self.belief_space.move_usage[move_idx]} times")

            print(f"\nTotal Genetic Operations:")
            print(f"  - Crossovers (with belief injection): {self.crossover_count}")
            print(f"  - Mutations (belief-guided): {self.mutation_count}")
            print(f"{'=' * 70}\n")

        target_squares = self.n * self.n
        unique_visited = len(set(self.best_path))
        success = unique_visited == target_squares

        return success, self.best_path
