# Quick Start Guide - Knight's Tour Solver

## 🚀 Get Started in 3 Minutes

### Step 1: Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

### Step 2: Run the Application (10 seconds)

```bash
python main.py
```

### Step 3: Solve Your First Knight's Tour (2 minutes)

1. **The GUI will open** showing a chessboard
2. **Click "▶ Run Solver"** with default settings (8×8 board, Backtracking algorithm)
3. **Watch the animation** - the knight will move across the board
4. **Check statistics** in the left panel

---

## 🎮 Quick Demo Scenarios

### Scenario 1: Fast Solution (5×5 board)
1. Change board size to **5**
2. Select **Backtracking** algorithm
3. Click **Run Solver**
4. Solution in < 1 second! ✅

### Scenario 2: Different Starting Position
1. Keep board size at **8**
2. **Click on square (4, 4)** on the chessboard (center)
3. Click **Run Solver**
4. Watch solution from center position

### Scenario 3: Cultural Algorithm
1. Board size: **6**
2. Select **Cultural Algorithm** from dropdown
3. Click **Run Solver**
4. Watch evolutionary approach find solution

### Scenario 4: Animation Control
1. Run any solver
2. Use **speed slider** to adjust animation (10ms - 1000ms)
3. Click **⏩ Skip Animation** to see final result immediately

---

## 📊 Generate Your First Report

After solving:

1. Click **📊 Generate Report**
2. Check `reports/` folder for:
   - CSV file with run data
   - PNG visualization of solution
   - Performance chart
   - Text summary

---

## 🔍 Check Magic Square Properties

After solving:

1. Click **🔍 Check Magic Square**
2. View analysis popup showing:
   - Row and column sums
   - Diagonal sums
   - Magic square classification

---

## 📈 View Run History

1. Click **📈 View History**
2. See all previous runs in database
3. Click **Show Statistics** for aggregate data

---

## 🧪 Run Tests (Optional)

Verify everything works:

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_backtracking.py -v
```

---

## 🎯 Recommended Test Sequence for Demo

### Demo Flow (5 minutes total):

1. **Start with 5×5 Backtracking** (shows fast success)
   - Time: ~0.1s
   - Demonstrates basic functionality

2. **Try 8×8 from center position** (shows different start)
   - Click (4, 4) on board
   - Time: ~1s
   - Shows start position selection

3. **Run 6×6 Cultural Algorithm** (shows alternative approach)
   - Time: ~5-10s
   - Shows evolutionary computation

4. **Generate Report** for last run
   - Shows reporting capabilities
   - Open generated files

5. **Check Magic Square** analysis
   - Shows mathematical properties
   - Educational value

6. **View History**
   - Shows database integration
   - Compare algorithms

---

## ⚡ Performance Expectations

| Board Size | Backtracking | Cultural Algorithm |
|------------|--------------|-------------------|
| 5×5 | < 0.1s ✅ | 1-3s ✅ |
| 6×6 | < 0.5s ✅ | 2-5s ✅ |
| 8×8 | 0.5-2s ✅ | 5-15s ✅ |
| 10×10 | 2-10s ⚠️ | 15-30s ⚠️ |
| 12×12 | 10-60s ⚠️ | 30-60s ⚠️ |

✅ = Fast
⚠️ = May take time (be patient)

---

## 🐛 Quick Troubleshooting

**Problem**: "ModuleNotFoundError: No module named 'matplotlib'"
```bash
pip install matplotlib
```

**Problem**: GUI doesn't appear
- Check Python version: `python --version` (need 3.8+)
- Install tkinter: `sudo apt-get install python3-tk` (Linux)

**Problem**: Solver seems stuck
- Check progress bar - it's working!
- For 12×12 boards, wait up to 60 seconds
- Use Stop button if needed

**Problem**: No reports generated
- Check if `reports/` folder exists (auto-created)
- Check console for error messages
- Run with `python main.py` to see errors

---

## 💡 Pro Tips

1. **Start small** (5×5) to test everything works
2. **Use animation speed slider** to speed up for large boards
3. **Skip animation** for quick results on repeat runs
4. **Try different start positions** - some are harder than others!
5. **Compare algorithms** - run same board with both
6. **Check generated reports** - beautiful visualizations
7. **View history** to see performance trends

---

## 📞 Need Help?

1. Click **❓ Help** button in GUI
2. Read full [README.md](README.md)
3. Check test files for code examples
4. Review console output for errors

---

## 🎓 For Presentation

**Recommended demo order**:

1. Show GUI interface
2. Explain controls
3. Run 5×5 Backtracking (fast win)
4. Show animation controls
5. Run 8×8 Cultural Algorithm (show different approach)
6. Generate and open report
7. Show magic square analysis
8. Display run history database
9. Show code structure briefly

**Time**: 5-7 minutes

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] Application runs without errors
- [ ] Can solve 5×5 board
- [ ] Can solve 8×8 board
- [ ] Animation works
- [ ] Reports generate successfully
- [ ] Database stores runs
- [ ] Tests pass (optional but recommended)

---

**You're ready to go! Enjoy solving Knight's Tours! ♞**
