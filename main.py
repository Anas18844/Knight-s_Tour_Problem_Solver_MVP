import tkinter as tk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui import KnightTourGUI
except ImportError as e:
    print(f"Error importing GUI: {e}")
    sys.exit(1)


def main():
    root = tk.Tk()
    # Create GUI
    try:
        app = KnightTourGUI(root)
        # run GUI
        app.run()
    # Exception if run failer 
    except Exception as e:
        messagebox.showerror("Application Error")
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
