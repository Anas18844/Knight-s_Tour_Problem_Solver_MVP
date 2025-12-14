# Cultural Algorithm Testing Suite

This folder contains comprehensive tests for the Cultural Algorithm implementation (Levels 0-4).

## Folder Structure

```
testing/
├── unit/                  # Unit tests for individual components
│   ├── test_ca_level1.py # Tests for Level 1 (Simple GA)
│   ├── test_ca_level2.py # Tests for Level 2 (Enhanced GA)
│   └── test_ca_level3.py # Tests for Level 3 (Cultural GA)
├── logic/                 # Logic and integration tests
│   └── test_ca_logic.py  # Tests for algorithm correctness and progression
├── integration/           # Integration tests (future)
├── run_all_tests.py      # Main test runner
└── README.md             # This file
```

## Running Tests

### Run All Tests
```bash
cd testing
python run_all_tests.py
```

### Run Only Unit Tests
```bash
python run_all_tests.py --unit
```

### Run Only Logic Tests
```bash
python run_all_tests.py --logic
```

### Run Specific Test File
```bash
python run_all_tests.py --file test_ca_level1.py
```

### Run Individual Test Files Directly
```bash
cd unit
python test_ca_level1.py
python test_ca_level2.py
python test_ca_level3.py

cd ../logic
python test_ca_logic.py
```

## Test Coverage

### Unit Tests (test_ca_level1.py)
- **Initialization**: Tests solver initialization with correct parameters
- **Population**: Tests population initialization and structure
- **Decoding**: Tests chromosome to path decoding
- **Fitness**: Tests fitness function calculation
- **Selection**: Tests tournament selection
- **Crossover**: Tests 2-point crossover operation
- **Mutation**: Tests mutation operation
- **Repair**: Tests chromosome repair mechanism
- **Solve**: Tests complete solving process

### Unit Tests (test_ca_level2.py)
- **Mobility**: Tests Warnsdorff-inspired mobility calculation
- **Enhanced Fitness**: Tests fitness with mobility component
- **Heuristic Repair**: Tests smart chromosome repair
- **Diversity**: Tests population diversity calculation
- **Enhanced Mutation**: Tests mutation with smart gene selection
- **Diversity Tournament**: Tests diversity-aware selection

### Unit Tests (test_ca_level3.py)
- **Belief Space**: Tests belief space initialization and updates
- **Move Probability**: Tests learning move success rates
- **Position Difficulty**: Tests position difficulty tracking
- **Move Suggestion**: Tests belief-based move suggestions
- **Guided Operators**: Tests belief-guided mutation and crossover
- **Cultural Learning**: Tests knowledge accumulation over generations

### Logic Tests (test_ca_logic.py)
- **Progression**: Tests that each level improves upon previous
- **Inheritance**: Tests proper class hierarchy
- **Knight Move Validity**: Tests all paths use valid knight moves
- **Convergence**: Tests fitness improvement over generations
- **Performance Comparison**: Compares all levels side-by-side

## Test Results Interpretation

### Success Criteria
- ✓ All unit tests pass
- ✓ All logic tests pass
- ✓ Each level produces valid knight tours
- ✓ Higher levels show improvement trends

### Expected Behavior
- **Level 0 (Random)**: Low coverage (< 20%), fast execution
- **Level 1 (Simple GA)**: Moderate coverage (20-40%), moderate speed
- **Level 2 (Enhanced GA)**: Better coverage (30-50%), similar speed
- **Level 3 (Cultural GA)**: Best coverage (40-60%), slightly slower

### Performance Notes
- Tests use reduced generations (10-30) for speed
- Full performance requires 100+ generations
- Success rates vary by starting position
- Larger boards (8×8+) require more generations

## Writing New Tests

### Adding Unit Tests
1. Create new file in `unit/` folder
2. Import unittest and target module
3. Create test class extending `unittest.TestCase`
4. Write test methods starting with `test_`
5. Run to verify

Example:
```python
import unittest
from algorithms.cultural.level1_simple_ga import SimpleGASolver

class TestMyFeature(unittest.TestCase):
    def test_something(self):
        solver = SimpleGASolver(n=5, level=1)
        # Your test here
        self.assertTrue(some_condition)
```

### Adding Logic Tests
1. Create test in `logic/` folder
2. Test algorithmic correctness
3. Test comparisons between levels
4. Test edge cases

## Continuous Integration

These tests can be run in CI/CD pipelines:

```bash
# Exit with error code if tests fail
python run_all_tests.py
echo $?  # 0 = success, 1 = failure
```

## Troubleshooting

### Import Errors
- Ensure you're running from the `testing/` folder
- Check that parent directory is in Python path

### Test Timeouts
- Reduce `generations` parameter in tests
- Use smaller board sizes (5×5 instead of 8×8)

### Random Failures
- Some tests use randomized algorithms
- Re-run if occasional failures occur
- Check seed values for reproducibility

## Future Enhancements

- [ ] Integration tests with GUI
- [ ] Performance benchmarking suite
- [ ] Coverage reporting
- [ ] Test for Level 4 (Advanced CA)
- [ ] Regression tests
- [ ] Stress tests with large boards

## Contact

For questions about testing:
- Check the main project documentation
- Review test code comments
- Run tests with `-v` flag for verbose output
