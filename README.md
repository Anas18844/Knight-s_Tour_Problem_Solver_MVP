# Knight's Tour Problem Solver - MVP

## University AI Project - Full Technical Prototype

A comprehensive Python application that solves the Knight's Tour problem using two different algorithms: **Backtracking with Warnsdorff's Heuristic** and **Cultural Algorithm**.

---

## 🎯 Features

### Core Functionality
- ✅ **Dual Algorithm Implementation**
  - Backtracking with Warnsdorff's Heuristic (optimized for performance)
  - Cultural Algorithm (evolutionary approach with belief space)

- ✅ **Interactive GUI** (Tkinter)
  - Visual chessboard (5×5 to 12×12)
  - Click-to-select starting position
  - Real-time progress tracking
  - Step-by-step knight movement animation

- ✅ **Animation Controls**
  - Speed control slider (10ms - 1000ms per step)
  - Skip animation button
  - Progressive path visualization

- ✅ **Database Integration** (SQLite)
  - Run history storage
  - Performance statistics
  - Solution path reconstruction

- ✅ **Reporting & Analysis**
  - CSV report generation
  - Performance charts (Matplotlib)
  - Solution visualization export
  - Semi-magic square analysis

- ✅ **Error Handling**
  - Algorithm timeout (60 seconds)
  - Invalid input validation
  - Database connection management
  - Thread-safe operations

---

## 🏗️ Project Structure

```
knights_tour_mvp/
├── main.py                          # Entry point
├── requirements.txt                 # Dependencies
├── README.md                        # This file
│
├── algorithms/                      # Algorithm implementations
│   ├── __init__.py
│   ├── backtracking.py             # Backtracking + Warnsdorff's
│   ├── cultural.py                 # Cultural Algorithm
│   └── semi_magic_square.py        # Magic square validator
│
├── database/                        # Database layer
│   ├── __init__.py
│   ├── db_manager.py               # SQLite operations
│   └── schema.sql                  # Database schema
│
├── gui/                            # GUI components
│   ├── __init__.py
│   ├── main_window.py              # Main application window
│   └── board_canvas.py             # Chessboard visualization
│
├── reporting/                      # Report generation
│   ├── __init__.py
│   └── report_generator.py         # CSV & chart generator
│
├── tests/                          # Unit tests
│   ├── __init__.py
│   ├── test_backtracking.py
│   ├── test_cultural.py
│   └── test_database.py
│
└── reports/                        # Generated reports (created at runtime)
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
python main.py
```

---

## 📖 Usage Guide

### Basic Workflow

1. **Set Board Size**: Use spinbox to select board size (5-12)
2. **Choose Starting Position**: Click on the chessboard to select where the knight starts
3. **Select Algorithm**: Choose "Backtracking" or "Cultural Algorithm" from dropdown
4. **Adjust Animation Speed**: Use slider to control visualization speed
5. **Run Solver**: Click "▶ Run Solver" button
6. **View Results**: Watch the animation and check statistics
7. **Generate Reports**: Click "📊 Generate Report" for detailed analysis

### GUI Controls

| Button | Function |
|--------|----------|
| ▶ Run Solver | Start solving with selected algorithm |
| ⏹ Stop | Stop current execution |
| ⏩ Skip Animation | Show final solution immediately |
| 🗑 Clear Board | Reset board and clear solution |
| 📊 Generate Report | Create CSV and charts |
| 🔍 Check Magic Square | Analyze semi-magic properties |
| 📈 View History | Show database of previous runs |
| ❓ Help | Display help information |

---

## 🧠 Algorithms

### 1. Backtracking with Warnsdorff's Heuristic

**How it works:**
- Uses recursive backtracking to explore possible knight moves
- **Warnsdorff's Rule**: Always move to the square with the fewest onward moves
- Dramatically improves performance (essential for boards > 8×8)

**Performance:**
- Board 5×5: < 0.1 seconds
- Board 8×8: < 1 second
- Board 10×10: 1-5 seconds
- Board 12×12: 5-30 seconds

**Key Features:**
- Guaranteed to find solution if one exists
- Deterministic (same input → same output)
- Memory efficient
- Very fast with heuristic

### 2. Cultural Algorithm

**How it works:**
- Population-based evolutionary algorithm
- **Population Space**: Candidate solutions evolve through selection, crossover, mutation
- **Belief Space**: Stores successful patterns to guide evolution
- Combines individual learning with cultural knowledge

**Components:**
- **Individual**: Represents a knight tour path
- **Fitness Function**: Number of unique squares visited
- **Selection**: Tournament selection of parents
- **Crossover**: Path-based crossover
- **Mutation**: Partial path reconstruction
- **Belief Space**: Stores successful move patterns

**Performance:**
- More variable than backtracking
- Better for exploring multiple solutions
- Can find solutions for difficult start positions
- Timeout: 60 seconds (configurable)

---

## 📊 Semi-Magic Square Analysis

A Knight's Tour can be represented as a **semi-magic square** where each square is numbered according to the visit order (1 to n²).

### Properties Checked:
- **Row Sums**: Sum of each row
- **Column Sums**: Sum of each column
- **Diagonal Sums**: Main and anti-diagonal sums
- **Magic Constant**: Ideal sum = n(n²+1)/2

### Classifications:
1. **Magic Square**: All rows, columns, and diagonals sum to magic constant
2. **Semi-Magic Square**: All rows equal, all columns equal (but row ≠ column)
3. **Partially Magic**: Only rows OR columns equal
4. **Non-Magic**: No regular pattern

---

## 🗄️ Database Schema

### Table: `runs`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Unique run ID |
| algorithm | TEXT | Algorithm name |
| board_size | INTEGER | Board size (n×n) |
| execution_time | REAL | Time in seconds |
| steps | INTEGER | Number of moves |
| result | TEXT | 'SUCCESS' or 'FAILURE' |
| solution_path | TEXT | JSON array of coordinates |
| start_position | TEXT | JSON [x, y] |
| timestamp | DATETIME | Run timestamp |

### Table: `reports`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Report ID |
| run_id | INTEGER FK | References runs(id) |
| details | TEXT | Text summary |
| performance_graph | TEXT | Path to chart |
| csv_report | TEXT | Path to CSV |
| timestamp | DATETIME | Report timestamp |

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_backtracking.py -v
pytest tests/test_cultural.py -v
pytest tests/test_database.py -v
```

### Test Coverage

```bash
pytest tests/ --cov=algorithms --cov=database --cov-report=html
```

### Test Categories

1. **Algorithm Tests**
   - Valid move generation
   - Warnsdorff's heuristic correctness
   - Fitness function calculation
   - Solution validation

2. **Database Tests**
   - CRUD operations
   - Query filtering
   - Statistics calculation
   - Error handling

3. **Integration Tests**
   - End-to-end solving
   - GUI-database interaction
   - Report generation

---

## 📈 Generated Reports

### Report Types

1. **CSV Report** (`run_*.csv`)
   - Algorithm details
   - Execution time
   - Solution path (JSON)
   - Statistics

2. **Performance Chart** (`performance_*.png`)
   - Execution time vs board size
   - Success rate by algorithm
   - Comparative analysis

3. **Solution Visualization** (`solution_*.png`)
   - Chessboard with numbered path
   - Start/end markers
   - Move arrows

4. **Summary Text** (`summary_*.txt`)
   - Human-readable summary
   - Key statistics
   - Algorithm details

### Report Location
All reports saved to: `reports/` directory (auto-created)

---

## ⚙️ Configuration

### Adjustable Parameters

**In Code** (algorithms):
```python
# Backtracking
timeout = 60.0  # seconds
start_pos = (0, 0)  # (x, y)

# Cultural Algorithm
population_size = 100
max_generations = 500
timeout = 60.0
```

**In GUI**:
- Board size: 5-12 (spinbox)
- Animation speed: 10-1000ms (slider)
- Starting position: Click board

---

## 🐛 Troubleshooting

### Common Issues

**Problem**: GUI doesn't start
- **Solution**: Check Python version (3.8+), install tkinter: `sudo apt-get install python3-tk` (Linux)

**Problem**: "Module not found" error
- **Solution**: Run `pip install -r requirements.txt`

**Problem**: Solver timeout on large boards
- **Solution**: Use smaller board (≤10) or increase timeout in code

**Problem**: Database locked error
- **Solution**: Close other instances, check file permissions

**Problem**: Animation too fast/slow
- **Solution**: Use speed slider (10-1000ms)

---

## 🚀 Future Enhancements

### Phase 2 - Advanced Features
- [ ] Parallel algorithm execution (compare simultaneously)
- [ ] Neural network-guided heuristics
- [ ] 3D visualization (PyOpenGL)
- [ ] Web interface (Flask/Django)
- [ ] Multi-threaded population evolution

### Phase 3 - Extended Functionality
- [ ] Rectangular boards (m×n)
- [ ] Boards with obstacles
- [ ] Multiple knights tour
- [ ] Tournament mode (algorithm competitions)
- [ ] Export animations as video (MP4)
- [ ] Cloud database (PostgreSQL)
- [ ] REST API for remote solving

### Optimization Ideas
1. **Implement A* search** for pathfinding
2. **GPU acceleration** for Cultural Algorithm population
3. **Caching** of partial solutions
4. **Machine learning** to predict optimal start positions
5. **Distributed computing** for massive board sizes

---

## 📚 Academic References

### Knight's Tour
- Warnsdorff, H. C. (1823). "Des Rösselsprungs einfachste und allgemeinste Lösung"
- Parberry, I. (1997). "An Efficient Algorithm for the Knight's Tour Problem"

### Cultural Algorithms
- Reynolds, R. G. (1994). "An Introduction to Cultural Algorithms"
- Jin, X., & Reynolds, R. G. (1999). "Using Knowledge-Based Evolutionary Computation"

### Semi-Magic Squares
- Jelliss, G. P. (2000). "Knight's Tour Notes"
- Cull, P., & De Curtins, J. (1978). "Knight's Tour Revisited"

---

## 👥 Contributors

**University AI Project Team**
- Algorithm Design & Implementation
- GUI Development
- Database Architecture
- Testing & Documentation

---

## 📄 License

This project is developed for educational purposes as part of a university AI course.

---

## 🙏 Acknowledgments

- Python community for excellent libraries
- Tkinter for GUI framework
- Matplotlib for visualization
- SQLite for database
- Academic researchers for algorithmic foundations

---

## 📞 Support

For issues or questions:
1. Check the Help button in GUI
2. Review this README
3. Check test files for examples
4. Review generated reports for debugging

---

## 🎓 Educational Value

This project demonstrates:
- **Algorithm Design**: Backtracking vs Evolutionary approaches
- **Optimization**: Heuristics for search space reduction
- **Software Engineering**: Modular OOP design
- **Data Management**: Database integration
- **User Experience**: Interactive visualization
- **Testing**: Comprehensive unit tests
- **Documentation**: Clear code comments

**Learning Outcomes**:
✓ Understanding classic AI problems
✓ Implementing search algorithms
✓ Working with evolutionary computation
✓ Building full-stack applications
✓ Performance analysis and optimization
✓ Professional software development practices

---

**Version**: 1.0.0 MVP
**Date**: 2025
**Status**: ✅ Production Ready for University Presentation
