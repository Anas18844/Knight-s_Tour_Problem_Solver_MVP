# Usage Guide - Knight's Tour Solver

Complete guide for using the Knight's Tour Problem Solver application.

---

## Table of Contents

1. [Installation](#installation)
2. [First Run](#first-run)
3. [Interface Overview](#interface-overview)
4. [Running the Solver](#running-the-solver)
5. [Dashboard Guide](#dashboard-guide)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)

---

## Installation

### Step 1: Install Python
Ensure Python 3.8+ is installed:
```bash
python --version
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- matplotlib >= 3.5.0 (for charts)
- numpy >= 1.21.0 (for calculations)
- Pillow >= 9.0.0 (for knight image)

### Step 3: Run Application
```bash
python main.py
```

---

## First Run

When you first launch the application:

1. **Main Window Opens** (1400×900 pixels)
2. **Left Panel** - Control panel with settings
3. **Right Panel** - Chessboard visualization
4. **Default Settings**:
   - Board Size: 8×8
   - Algorithm: Backtracking
   - Level: 1
   - Start Position: (0, 0)

---

## Interface Overview

### Left Panel (Control Panel)

**Configuration Section:**
- Board Size dropdown (5-12)
- Algorithm dropdown (Backtracking/Cultural)
- Level dropdown (1/2/3)
- Start Position display (click board to change)

**Dashboard Button:** (Large button below Level)
- =Ê OPEN DASHBOARD - Opens analysis window

**Control Buttons:**
- ¶ Run Solver - Start solving
- ù Stop - Stop current run
- é Skip Animation - Jump to result
- =Ñ Clear Board - Reset visualization

**Animation Speed:**
- Slider: 10ms to 1000ms per move
- Shows current value

**Progress Bar:**
- Shows solving progress
- Status messages

**Action Buttons:**
- =Ä Generate Report - Create PDF
- =È View History - See past runs
- S Help - Show help dialog

### Right Panel (Board Display)

- **Chessboard**: Interactive grid
- **Knight Image**: Animated chess piece
- **Path Lines**: Blue arrows showing moves
- **Move Numbers**: Sequential numbering
- **Click Anywhere**: Set starting position

---

## Running the Solver

### Basic Solve

1. **Configure**:
   ```
   Board Size: 8
   Algorithm: Backtracking
   Level: Level 1
   ```

2. **Set Start**: Click any square on the board

3. **Run**: Click "¶ Run Solver"

4. **Watch**: Animation shows knight's path

5. **View Dashboard**: Click "=Ê OPEN DASHBOARD"

### Example Session

**Small Board (5×5):**
- Board Size: 5
- Algorithm: Backtracking
- Start: (0, 0)
- Expected Time: < 0.01 seconds
- Solution: 25 moves

**Medium Board (8×8):**
- Board Size: 8
- Algorithm: Backtracking
- Start: (0, 0)
- Expected Time: 0.01-0.5 seconds
- Solution: 64 moves

**Large Board (10×10):**
- Board Size: 10
- Algorithm: Cultural
- Start: (5, 5) - center
- Expected Time: 5-30 seconds
- Solution: 100 moves

---

## Dashboard Guide

### Opening Dashboard

1. Run solver first
2. Click "=Ê OPEN DASHBOARD"
3. Dashboard window opens with 5 tabs

### Tab 1: Performance Metrics

**Current Run Information:**
- Algorithm, Level, Board Size
- Execution time
- Solution length
- Success status

**Performance Breakdown:**
- Board coverage percentage
- Time per move
- Moves per second

**Backtracking Efficiency:** (if using Backtracking)
- Total recursive calls
- Efficiency ratio
- Backtrack rate

**Historical Comparison:**
- Average time for same configuration
- Performance ranking

### Tab 2: Algorithm Analysis P

**For Backtracking Algorithm:**

**Section 1: Warnsdorff's Heuristic**
- Search space reduction (usually 99.999%+)
- Move selection quality rating
- Average tries per move
- Overhead factor

**Section 2: Backtracking Operations**
- Total recursive calls
- Successful vs failed attempts
- Backtrack rate percentage
- Performance classification (PPPPP)

**Section 3: Complexity Analysis**
- Time complexity (theoretical vs actual)
- Space complexity breakdown
- Execution metrics
- Calls per second

### Tab 3: Visual Analysis

**Four Charts:**

1. **Move Order Heatmap**
   - Color-coded move sequence
   - Darker = earlier moves
   - Shows path pattern

2. **Performance Metrics Bar Chart**
   - Execution time
   - Solution length
   - Recursive calls

3. **Historical Performance Trend**
   - Line graph of past runs
   - Average line shown
   - Trend analysis

4. **Board Size vs Performance**
   - Scatter plot
   - Shows complexity growth
   - Average times per size

### Tab 4: Historical Comparison

**Features:**
- Table of last 50 runs
- Columns: ID, Algorithm, Level, Board, Time, Calls, Status
- Summary statistics box
- Success rate percentage

### Tab 5: Algorithm Details

**Contains:**
- Complete algorithm explanation
- Warnsdorff's heuristic description
- Complexity analysis
- Implementation details
- Strengths & limitations
- Current run statistics

---

## Advanced Features

### Animation Control

**Speed Adjustment:**
- Drag slider left: Faster (10ms)
- Drag slider right: Slower (1000ms)
- Updates in real-time

**Skip Animation:**
- Click "é Skip Animation"
- Shows final path immediately
- Useful for large boards

### Report Generation

1. Run solver successfully
2. Click "=Ä Generate Report"
3. PDF created with:
   - Run statistics
   - Performance charts
   - Path visualization
   - Comparison data

### View History

1. Click "=È View History"
2. See all past runs in table
3. Click "Show Statistics" for summary
4. Filter by algorithm, board size

### Starting Position Strategy

**For Best Results:**

**Corner Start (e.g., (0,0)):**
- More challenging
- May take longer
- Tests algorithm limits

**Edge Start (e.g., (0,4)):**
- Medium difficulty
- Balanced performance

**Center Start (e.g., (4,4) on 8×8):**
- Often easier
- Faster solutions
- Good for testing

---

## Troubleshooting

### Application Won't Start

**Problem:** Python version too old
```bash
python --version
# Must be 3.8 or higher
```

**Problem:** Missing dependencies
```bash
pip install -r requirements.txt
```

**Problem:** tkinter not found
- Windows: Reinstall Python with tcl/tk
- Linux: `sudo apt-get install python3-tk`
- Mac: Included with Python

### Solver Times Out

**Solutions:**
1. Reduce board size
2. Try different starting position
3. Switch to Cultural Algorithm
4. Increase timeout in code:
   ```python
   # In algorithms/backtracking.py
   timeout=120.0  # Increase from 60 to 120 seconds
   ```

### Dashboard Errors

**"No Data" Message:**
- Run solver first before opening dashboard

**"Failed to create dashboard" Error:**
1. Clear Python cache:
   ```bash
   rm -rf __pycache__ gui/__pycache__
   ```
2. Restart application

**Charts Not Showing:**
- Check matplotlib installed: `pip install matplotlib`
- Update matplotlib: `pip install --upgrade matplotlib`

### Performance Issues

**Slow Animation:**
- Increase animation speed (move slider left)
- Skip animation for instant result

**Application Freezes:**
- Large boards (11×11+) may take time
- Watch progress bar
- Wait for completion or click Stop

---

## Tips & Tricks

### Optimal Settings

**For Speed:**
- Board: 6×6 or 7×7
- Algorithm: Backtracking
- Start: Center position

**For Learning:**
- Board: 8×8
- Algorithm: Backtracking
- Animation: 200ms
- Open Dashboard after

**For Research:**
- Board: 10×10
- Algorithm: Cultural
- Multiple runs
- Compare in History

### Understanding Results

**Good Performance Indicators:**
- Backtrack rate < 50%
- Efficiency score > 50
- Quality rating PPPP or higher

**Excellent Performance:**
- Backtrack rate < 10%
- Efficiency score > 90
- Quality rating PPPPP

### Database Management

**Location:** `knights_tour.db` in project folder

**View Data:**
- Use "View History" button
- Or open with SQLite browser

**Clear History:**
- Delete `knights_tour.db` file
- New database created automatically

---

## Keyboard Shortcuts

Currently, the application uses mouse interaction only. Keyboard shortcuts may be added in future versions.

---

## Getting Help

1. **In-App Help**: Click S Help button
2. **Dashboard**: View "Algorithm Details" tab
3. **Documentation**: Read TECHNICAL_DETAILS.md
4. **Code Comments**: Check source code for details

---

## Next Steps

After mastering basic usage:
1. Try all board sizes
2. Compare algorithms
3. Experiment with starting positions
4. Generate and analyze reports
5. Study dashboard metrics
6. Explore historical trends

---

**Enjoy exploring the Knight's Tour problem! ^**
