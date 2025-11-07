"""
Knight's Tour Problem Solver - Main Entry Point

University Project MVP
Author: AI Project Team
Date: 2025

This application solves the Knight's Tour problem using two algorithms:
1. Backtracking with Warnsdorff's Heuristic
2. Cultural Algorithm

Features:
- Interactive GUI with chessboard visualization
- Step-by-step animation of solutions
- Performance comparison and reporting
- SQLite database for run history
- Semi-magic square analysis
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui import KnightTourGUI
except ImportError as e:
    print(f"Error importing GUI: {e}")
    print("Please ensure all required packages are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Main entry point for the application."""
    # Create root window
    root = tk.Tk()

    # Set window icon (if available)
    try:
        # You can add a .ico file for Windows
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass

    # Create and run GUI
    try:
        app = KnightTourGUI(root)
        app.run()
    except Exception as e:
        messagebox.showerror("Application Error",
                           f"An error occurred while running the application:\n\n{str(e)}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("="*70)
    print("KNIGHT'S TOUR PROBLEM SOLVER - MVP")
    print("University AI Project")
    print("="*70)
    print("\nStarting application...")
    print("Board size range: 5×5 to 12×12")
    print("Algorithms: Backtracking (with Warnsdorff's), Cultural Algorithm")
    print("Features: GUI, Animation, Database, Reports, Magic Square Analysis")
    print("\nInitializing GUI...")
    print("="*70 + "\n")

    main()
