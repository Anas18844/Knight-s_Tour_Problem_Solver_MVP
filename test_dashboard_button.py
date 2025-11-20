"""Quick test to verify Dashboard button is visible."""

import tkinter as tk
from tkinter import ttk

def test_button_visibility():
    """Test that buttons render correctly."""
    root = tk.Tk()
    root.title("Button Test")
    root.geometry("400x400")

    frame = ttk.Frame(root, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)

    # Test with emoji
    ttk.Button(frame, text="📊 Dashboard (with emoji)",
              command=lambda: print("Dashboard clicked!"),
              width=25).pack(pady=5)

    # Test without emoji
    ttk.Button(frame, text="Dashboard (no emoji)",
              command=lambda: print("Dashboard clicked!"),
              width=25).pack(pady=5)

    # Test other buttons from the GUI
    ttk.Button(frame, text="📄 Generate Report",
              command=lambda: print("Report clicked!"),
              width=25).pack(pady=5)

    ttk.Button(frame, text="🔍 Check Magic Square",
              command=lambda: print("Magic Square clicked!"),
              width=25).pack(pady=5)

    ttk.Button(frame, text="📈 View History",
              command=lambda: print("History clicked!"),
              width=25).pack(pady=5)

    ttk.Button(frame, text="❓ Help",
              command=lambda: print("Help clicked!"),
              width=25).pack(pady=5)

    label = ttk.Label(frame, text="\nIf you can see all buttons above, the GUI is working correctly.\nThe Dashboard button should be at the top.",
                     font=('Arial', 10))
    label.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    print("Testing button visibility...")
    print("Look for the 'Dashboard' button in the window that opens.")
    test_button_visibility()
