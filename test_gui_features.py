"""Test script for new GUI features."""

import sys
import io
import tkinter as tk
from gui.main_window import KnightTourGUI

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_gui_initialization():
    """Test that GUI initializes with new features."""
    print("Testing GUI initialization with new features...")

    try:
        root = tk.Tk()
        app = KnightTourGUI(root)

        # Check new variables exist
        assert hasattr(app, 'algorithm_level'), "algorithm_level variable missing"
        assert hasattr(app, 'current_stats'), "current_stats variable missing"

        print("✓ New state variables initialized correctly")

        # Check level dropdown value
        level = app.algorithm_level.get()
        print(f"✓ Algorithm level: {level}")

        # Check that dashboard method exists
        assert hasattr(app, '_show_dashboard'), "Dashboard method missing"
        print("✓ Dashboard method exists")

        # Check other dashboard methods
        methods = ['_create_metrics_tab', '_create_charts_tab',
                   '_create_comparison_tab', '_create_details_tab']
        for method in methods:
            assert hasattr(app, method), f"{method} missing"
        print("✓ All dashboard tab methods exist")

        print("\n✅ All tests passed!")
        print("\nYou can now run the application with: python main.py")

        # Don't start mainloop in test
        root.destroy()
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui_initialization()
    sys.exit(0 if success else 1)
