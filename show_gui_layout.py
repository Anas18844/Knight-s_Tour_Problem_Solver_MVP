"""Display the GUI to verify Dashboard button is visible."""

import tkinter as tk
from gui.main_window import KnightTourGUI
import sys

def show_gui_with_highlights():
    """Show GUI with highlighted Dashboard button."""
    root = tk.Tk()

    # Create the GUI
    app = KnightTourGUI(root)

    # Create a popup message after a delay
    def show_message():
        from tkinter import messagebox
        msg = """
🎯 DASHBOARD BUTTON - NEW LOCATION! 🎯

The button has been MOVED to make it easier to find!

NEW LOCATION:
═══════════════════════════════════════════
Look at the LEFT PANEL (Control Panel)

The button is now RIGHT AFTER the "Level" dropdown:

   Board Size: [8]
   Algorithm:  [Backtracking ▼]
   Level:      [Level 1 ▼]
   ─────────────────────────
   📊 OPEN DASHBOARD  ← HERE! Big full-width button
   ─────────────────────────
   Start Position: (0, 0)

═══════════════════════════════════════════

It's a LARGE button that spans the full width
of the control panel, with separator lines
above and below it.

YOU CANNOT MISS IT!

Click it after running the solver to see
detailed performance analysis with charts!
        """

        popup = tk.Toplevel(root)
        popup.title("Dashboard Button Location")
        popup.geometry("500x400")

        text = tk.Text(popup, wrap=tk.WORD, font=('Arial', 11), padx=20, pady=20)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert('1.0', msg)
        text.config(state=tk.DISABLED)

        close_btn = tk.Button(popup, text="Got it! Close this message",
                             command=popup.destroy,
                             font=('Arial', 12, 'bold'),
                             bg='#4CAF50', fg='white',
                             padx=20, pady=10)
        close_btn.pack(pady=10)

    # Show message after 1 second
    root.after(1000, show_message)

    # Run the app
    print("\n" + "="*70)
    print("GUI OPENED - Look for the Dashboard button!")
    print("="*70)
    print("\nLocation: LEFT PANEL → Bottom → 'Dashboard' button")
    print("It's in a grid with other buttons (Generate Report, etc.)")
    print("\nA popup window will show you exactly where to look.")
    print("="*70 + "\n")

    app.run()

if __name__ == "__main__":
    show_gui_with_highlights()
