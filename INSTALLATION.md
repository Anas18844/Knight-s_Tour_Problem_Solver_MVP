# Installation & Setup Guide

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 2 GB
- **Storage**: 100 MB free space
- **Display**: 1280×720 minimum resolution

### Recommended Requirements
- **Python**: 3.9 or 3.10
- **RAM**: 4 GB
- **Storage**: 500 MB (for reports and database)
- **Display**: 1920×1080 for optimal experience

---

## Installation Steps

### Option 1: Standard Installation (Recommended)

#### Step 1: Install Python

**Windows:**
1. Download Python from [python.org](https://python.org)
2. Run installer
3. ✅ **Check "Add Python to PATH"**
4. Complete installation

**macOS:**
```bash
# Using Homebrew
brew install python3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
```

#### Step 2: Verify Installation

```bash
python --version
# Should show: Python 3.8.x or higher

pip --version
# Should show: pip 21.x or higher
```

#### Step 3: Clone/Download Project

```bash
# If using git
git clone <repository-url>
cd knights_tour_mvp

# Or download and extract ZIP file
```

#### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

Expected output:
```
Collecting matplotlib>=3.5.0
Collecting numpy>=1.21.0
Collecting pytest>=7.0.0
Installing collected packages: ...
Successfully installed matplotlib-3.x numpy-1.x pytest-7.x
```

#### Step 5: Run Application

```bash
python main.py
```

---

### Option 2: Virtual Environment (Best Practice)

#### Step 1: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 3: Run Application

```bash
python main.py
```

#### Step 4: Deactivate When Done

```bash
deactivate
```

---

### Option 3: Conda Environment

```bash
# Create environment
conda create -n knights_tour python=3.9

# Activate
conda activate knights_tour

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

---

## Troubleshooting

### Issue: "python: command not found"

**Solution:**
- Windows: Reinstall Python with "Add to PATH" checked
- macOS/Linux: Use `python3` instead of `python`

### Issue: "No module named 'tkinter'"

**Solution:**

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**macOS:**
```bash
# Reinstall Python with Homebrew
brew reinstall python-tk
```

**Windows:**
- Tkinter comes with Python
- Reinstall Python with all components

### Issue: "ModuleNotFoundError: No module named 'matplotlib'"

**Solution:**
```bash
pip install matplotlib
```

### Issue: "Permission denied" on Linux/macOS

**Solution:**
```bash
# Option 1: Use --user flag
pip install --user -r requirements.txt

# Option 2: Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: GUI Window Doesn't Appear

**Possible Causes:**
1. Tkinter not installed
2. Display issues on remote systems
3. Python version too old

**Solutions:**
```bash
# Check tkinter
python -c "import tkinter; print('Tkinter OK')"

# Update Python
python --version  # Should be 3.8+
```

### Issue: Tests Fail

**Solution:**
```bash
# Reinstall pytest
pip install --upgrade pytest

# Run tests with verbose output
pytest tests/ -v

# Check specific test
pytest tests/test_backtracking.py -v
```

### Issue: Database Errors

**Solution:**
```bash
# Delete existing database
rm knights_tour.db  # Linux/macOS
del knights_tour.db  # Windows

# Restart application (will create fresh database)
python main.py
```

---

## Verification Checklist

After installation, verify everything works:

### ✅ Basic Checks

```bash
# 1. Python version
python --version
# Should show 3.8 or higher

# 2. Pip version
pip --version
# Should work without errors

# 3. Import test
python -c "import matplotlib; import numpy; print('Dependencies OK')"
# Should print: Dependencies OK

# 4. Tkinter test
python -c "import tkinter; print('Tkinter OK')"
# Should print: Tkinter OK
```

### ✅ Run Tests

```bash
python run_tests.py
# Should show tests passing
```

### ✅ Run Application

```bash
python main.py
# GUI should open without errors
```

### ✅ Quick Functionality Test

1. GUI opens ✓
2. Can change board size ✓
3. Can click on board ✓
4. Can run solver ✓
5. Animation works ✓
6. Reports generate ✓

---

## Platform-Specific Notes

### Windows

**Antivirus:**
- Some antivirus software may flag Python scripts
- Add project folder to exclusions if needed

**File Paths:**
- Uses backslashes: `C:\Users\...\knights_tour_mvp`
- Python handles this automatically

**Terminal:**
- Use Command Prompt or PowerShell
- Git Bash also works

### macOS

**Permissions:**
- May need to allow app in System Preferences → Security
- First run might ask for permission

**Python Versions:**
- macOS comes with Python 2.7 (deprecated)
- Use `python3` and `pip3` commands
- Or install via Homebrew (recommended)

### Linux

**Display Server:**
- X11 required for Tkinter
- WSL users: Install X server (VcXsrv, Xming)

**Permissions:**
- Executable: `chmod +x main.py`
- Database: Check write permissions in project directory

---

## Development Setup (Optional)

For developers who want to modify the code:

### Install Development Tools

```bash
# Code formatter
pip install black

# Linter
pip install pylint flake8

# Type checking
pip install mypy

# Documentation
pip install sphinx
```

### IDE Setup

**VS Code:**
1. Install Python extension
2. Select interpreter (virtual environment)
3. Configure linter and formatter

**PyCharm:**
1. Open project folder
2. Configure Python interpreter
3. Enable pytest integration

---

## Docker Installation (Advanced)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Run application
CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t knights_tour .
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix knights_tour
```

---

## Uninstallation

### Remove Application

```bash
# If using virtual environment
deactivate
cd ..
rm -rf knights_tour_mvp

# If installed globally
pip uninstall matplotlib numpy pytest
```

### Clean Up Data

```bash
# Remove database
rm knights_tour.db

# Remove reports
rm -rf reports/
```

---

## Update Instructions

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Update from Repository

```bash
git pull origin main
pip install --upgrade -r requirements.txt
```

---

## FAQ

**Q: Do I need admin/root privileges?**
A: No, if using virtual environment or `--user` flag.

**Q: Can I run this on Raspberry Pi?**
A: Yes, Python 3.8+ and Tkinter are available on Raspberry Pi OS.

**Q: Does it work on Windows 7?**
A: Python 3.8 is the last version supporting Windows 7. Should work but not recommended.

**Q: Can I run this remotely over SSH?**
A: Yes, but need X11 forwarding for GUI:
```bash
ssh -X user@remote
python main.py
```

**Q: How much disk space do reports take?**
A: ~1-5 MB per report (PNG + CSV + text)

**Q: Can I use Python 3.7?**
A: Not recommended. Some features require 3.8+.

---

## Getting Help

### Resources
1. Check [README.md](README.md) for detailed documentation
2. Read [QUICKSTART.md](QUICKSTART.md) for quick start
3. Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for technical details
4. Check test files for code examples

### Common Commands Reference

```bash
# Installation
pip install -r requirements.txt

# Run application
python main.py

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_backtracking.py

# Clean database
rm knights_tour.db

# Clean reports
rm -rf reports/*

# Check dependencies
pip list

# Update dependencies
pip install --upgrade -r requirements.txt
```

---

## Success!

If you've followed these steps, you should now have a fully functional Knight's Tour Problem Solver running on your system!

**Next steps:**
1. Read [QUICKSTART.md](QUICKSTART.md) for usage guide
2. Try solving your first knight's tour
3. Explore the generated reports
4. Check out the code to learn more

**Happy solving! ♞**
