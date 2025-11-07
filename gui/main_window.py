"""Main GUI window for Knight's Tour Problem Solver."""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
from typing import Optional, Tuple
import json
from datetime import datetime

from algorithms import BacktrackingSolver, CulturalAlgorithmSolver
from algorithms.semi_magic_square import SemiMagicSquareValidator
from database import DatabaseManager
from reporting import ReportGenerator
from gui.board_canvas import BoardCanvas


class KnightTourGUI:
    """Main GUI application for Knight's Tour Problem Solver."""

    def __init__(self, root):
        """
        Initialize main GUI window.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Knight's Tour Problem Solver - University Project MVP")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)

        # Initialize components
        self.db_manager = DatabaseManager()
        self.report_generator = ReportGenerator()
        self.magic_validator = None

        # State variables
        self.current_algorithm = tk.StringVar(value="Backtracking")
        self.board_size = tk.IntVar(value=8)
        self.animation_speed = tk.IntVar(value=200)
        self.start_position = (0, 0)
        self.current_solution = None
        self.is_running = False

        # Threading
        self.solver_thread = None
        self.progress_queue = queue.Queue()

        # Create UI
        self._create_ui()

        # Start progress monitor
        self._monitor_progress()

    def _create_ui(self):
        """Create all UI elements."""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Left panel - Controls
        left_panel = ttk.Frame(main_container, padding="5")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

        # Right panel - Board and results
        right_panel = ttk.Frame(main_container, padding="5")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)

        self._create_control_panel(left_panel)
        self._create_board_panel(right_panel)

    def _create_control_panel(self, parent):
        """Create control panel with settings."""
        # Title
        title_label = ttk.Label(parent, text="Knight's Tour Solver",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        row = 1

        # Board size input
        ttk.Label(parent, text="Board Size (5-12):", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        board_size_spinbox = ttk.Spinbox(parent, from_=5, to=12, textvariable=self.board_size,
                                        width=10, command=self._on_board_size_change)
        board_size_spinbox.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Algorithm selection
        ttk.Label(parent, text="Algorithm:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        algo_combo = ttk.Combobox(parent, textvariable=self.current_algorithm,
                                 values=["Backtracking", "Cultural Algorithm"],
                                 state="readonly", width=20)
        algo_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Start position display
        ttk.Label(parent, text="Start Position:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.start_pos_label = ttk.Label(parent, text="(0, 0)", foreground="blue")
        self.start_pos_label.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        ttk.Label(parent, text="(Click board to change)", font=('Arial', 8, 'italic')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        row += 1

        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Animation controls
        ttk.Label(parent, text="Animation Speed (ms):", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        row += 1

        speed_frame = ttk.Frame(parent)
        speed_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.speed_slider = ttk.Scale(speed_frame, from_=10, to=1000,
                                     variable=self.animation_speed,
                                     orient=tk.HORIZONTAL, length=200,
                                     command=self._on_speed_change)
        self.speed_slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)

        self.speed_value_label = ttk.Label(speed_frame, text="200 ms")
        self.speed_value_label.grid(row=0, column=1, padx=5)
        row += 1

        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        self.run_button = ttk.Button(button_frame, text="▶ Run Solver",
                                     command=self._run_solver, width=15)
        self.run_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_button = ttk.Button(button_frame, text="⏹ Stop",
                                      command=self._stop_solver, width=15,
                                      state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)

        self.skip_anim_button = ttk.Button(button_frame, text="⏩ Skip Animation",
                                          command=self._skip_animation, width=15,
                                          state=tk.DISABLED)
        self.skip_anim_button.grid(row=1, column=0, padx=5, pady=5)

        self.clear_button = ttk.Button(button_frame, text="🗑 Clear Board",
                                       command=self._clear_board, width=15)
        self.clear_button.grid(row=1, column=1, padx=5, pady=5)

        # Progress bar
        ttk.Label(parent, text="Progress:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        row += 1

        self.progress_bar = ttk.Progressbar(parent, mode='determinate', length=250)
        self.progress_bar.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1

        self.status_label = ttk.Label(parent, text="Ready", foreground="green")
        self.status_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1

        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Statistics display
        ttk.Label(parent, text="Statistics:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1

        stats_frame = ttk.Frame(parent)
        stats_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.stats_text = scrolledtext.ScrolledText(stats_frame, width=35, height=15,
                                                    font=('Courier', 9))
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        row += 1

        # Report buttons
        report_frame = ttk.Frame(parent)
        report_frame.grid(row=row, column=0, columnspan=2, pady=10)

        ttk.Button(report_frame, text="📊 Generate Report",
                  command=self._generate_report, width=18).grid(row=0, column=0, padx=5)

        ttk.Button(report_frame, text="🔍 Check Magic Square",
                  command=self._check_magic_square, width=18).grid(row=0, column=1, padx=5)

        ttk.Button(report_frame, text="📈 View History",
                  command=self._view_history, width=18).grid(row=1, column=0, padx=5, pady=5)

        ttk.Button(report_frame, text="❓ Help",
                  command=self._show_help, width=18).grid(row=1, column=1, padx=5, pady=5)

    def _create_board_panel(self, parent):
        """Create board visualization panel."""
        # Title
        board_title = ttk.Label(parent, text="Chessboard Visualization",
                               font=('Arial', 14, 'bold'))
        board_title.grid(row=0, column=0, pady=10)

        # Board canvas container
        canvas_frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # Create board canvas
        self.board_canvas = BoardCanvas(canvas_frame, board_size=self.board_size.get(),
                                       cell_size=60)
        self.board_canvas.pack(padx=20, pady=20)
        self.board_canvas.set_click_callback(self._on_board_click)

        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

    def _on_board_size_change(self):
        """Handle board size change."""
        size = self.board_size.get()
        if size < 5 or size > 12:
            messagebox.showwarning("Invalid Size",
                                 "Board size must be between 5 and 12.")
            self.board_size.set(max(5, min(12, size)))
            return

        self.board_canvas.set_board_size(size)
        self.start_position = (0, 0)
        self.start_pos_label.config(text="(0, 0)")
        self._clear_stats()

    def _on_speed_change(self, value):
        """Handle animation speed change."""
        speed = int(float(value))
        self.speed_value_label.config(text=f"{speed} ms")
        self.board_canvas.set_animation_speed(speed)

    def _on_board_click(self, x, y):
        """Handle board click to set start position."""
        self.start_position = (x, y)
        self.start_pos_label.config(text=f"({x}, {y})")

    def _run_solver(self):
        """Run the selected algorithm in a separate thread."""
        if self.is_running:
            messagebox.showwarning("Already Running",
                                 "Solver is already running. Please wait or stop it.")
            return

        # Validate inputs
        board_size = self.board_size.get()
        if board_size < 5 or board_size > 12:
            messagebox.showerror("Invalid Input",
                               "Board size must be between 5 and 12.")
            return

        # Clear previous results
        self._clear_board()
        self._clear_stats()

        # Update UI state
        self.is_running = True
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Running...", foreground="blue")
        self.progress_bar['value'] = 0

        # Start solver in separate thread
        self.solver_thread = threading.Thread(target=self._solve_in_thread, daemon=True)
        self.solver_thread.start()

    def _solve_in_thread(self):
        """Execute solver algorithm in separate thread."""
        try:
            algorithm = self.current_algorithm.get()
            board_size = self.board_size.get()
            start_pos = self.start_position

            # Progress callback
            def progress_callback(percent, message):
                self.progress_queue.put(('progress', percent, message))

            # Create solver
            if algorithm == "Backtracking":
                solver = BacktrackingSolver(board_size, start_pos, timeout=60.0,
                                          progress_callback=progress_callback)
            else:  # Cultural Algorithm
                solver = CulturalAlgorithmSolver(board_size, start_pos,
                                               population_size=100,
                                               max_generations=500,
                                               timeout=60.0,
                                               progress_callback=progress_callback)

            # Solve
            start_time = datetime.now()
            success, path, stats = solver.solve()
            end_time = datetime.now()

            # Send results back to main thread
            self.progress_queue.put(('complete', success, path, stats, start_time, end_time))

        except Exception as e:
            self.progress_queue.put(('error', str(e)))

    def _monitor_progress(self):
        """Monitor progress queue and update UI."""
        try:
            while True:
                message = self.progress_queue.get_nowait()

                if message[0] == 'progress':
                    _, percent, text = message
                    self.progress_bar['value'] = percent
                    self.status_label.config(text=text, foreground="blue")

                elif message[0] == 'complete':
                    _, success, path, stats, start_time, end_time = message
                    self._handle_solution(success, path, stats, start_time, end_time)

                elif message[0] == 'error':
                    _, error_msg = message
                    self._handle_error(error_msg)

        except queue.Empty:
            pass

        # Schedule next check
        self.root.after(100, self._monitor_progress)

    def _handle_solution(self, success, path, stats, start_time, end_time):
        """Handle solution completion."""
        self.is_running = False
        self.current_solution = path
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.skip_anim_button.config(state=tk.NORMAL)

        if success:
            self.status_label.config(text="✓ Solution Found!", foreground="green")
            self.progress_bar['value'] = 100

            # Display statistics
            self._display_stats(stats, success)

            # Save to database
            self._save_to_database(success, path, stats, start_time)

            # Start animation
            self.board_canvas.start_animation(path, speed=self.animation_speed.get())

        else:
            self.status_label.config(text="✗ No Solution Found", foreground="red")
            self._display_stats(stats, success)

            # Save failed attempt to database
            self._save_to_database(success, path, stats, start_time)

            if path:
                # Show partial solution
                self.board_canvas.show_solution(path)

    def _handle_error(self, error_msg):
        """Handle error during solving."""
        self.is_running = False
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text=f"Error: {error_msg}", foreground="red")
        messagebox.showerror("Solver Error", f"An error occurred:\n{error_msg}")

    def _display_stats(self, stats, success):
        """Display statistics in text widget."""
        self.stats_text.delete('1.0', tk.END)

        output = "="*40 + "\n"
        output += "SOLVER STATISTICS\n"
        output += "="*40 + "\n\n"

        output += f"Algorithm: {stats.get('algorithm', 'N/A')}\n"
        output += f"Board Size: {self.board_size.get()}×{self.board_size.get()}\n"
        output += f"Start Position: {self.start_position}\n"
        output += f"Result: {'SUCCESS' if success else 'FAILURE'}\n\n"

        output += f"Execution Time: {stats.get('execution_time', 0):.4f}s\n"
        output += f"Solution Length: {stats.get('solution_length', 0)}\n"

        if 'recursive_calls' in stats:
            output += f"Recursive Calls: {stats['recursive_calls']}\n"
        if 'generations' in stats:
            output += f"Generations: {stats['generations']}\n"
            output += f"Best Fitness: {stats.get('best_fitness', 0)}\n"

        if stats.get('timed_out'):
            output += f"\n⚠ Timeout: {stats.get('error', '')}\n"

        self.stats_text.insert('1.0', output)

    def _save_to_database(self, success, path, stats, start_time):
        """Save run results to database."""
        try:
            run_id = self.db_manager.insert_run(
                algorithm=stats.get('algorithm', 'Unknown'),
                board_size=self.board_size.get(),
                execution_time=stats.get('execution_time', 0),
                steps=len(path),
                result='SUCCESS' if success else 'FAILURE',
                solution_path=path,
                start_position=self.start_position
            )
            print(f"Run saved to database with ID: {run_id}")

        except Exception as e:
            print(f"Error saving to database: {e}")

    def _stop_solver(self):
        """Stop the currently running solver."""
        # Note: This is a soft stop - the thread will complete but results will be ignored
        self.is_running = False
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped by user", foreground="orange")
        self.board_canvas.stop_animation()

    def _skip_animation(self):
        """Skip animation and show final solution."""
        if self.current_solution:
            self.board_canvas.show_solution(self.current_solution)
            self.skip_anim_button.config(state=tk.DISABLED)

    def _clear_board(self):
        """Clear the board and reset."""
        self.board_canvas.clear_animation()
        self.board_canvas.draw_board()
        self.current_solution = None
        self.skip_anim_button.config(state=tk.DISABLED)

    def _clear_stats(self):
        """Clear statistics display."""
        self.stats_text.delete('1.0', tk.END)
        self.progress_bar['value'] = 0
        self.status_label.config(text="Ready", foreground="green")

    def _generate_report(self):
        """Generate comprehensive report."""
        if not self.current_solution:
            messagebox.showinfo("No Solution", "Please run the solver first.")
            return

        try:
            # Get recent runs for comparison
            all_runs = self.db_manager.get_all_runs()

            # Prepare run data
            run_data = {
                'algorithm': self.current_algorithm.get(),
                'board_size': self.board_size.get(),
                'start_position': self.start_position,
                'result': 'SUCCESS',
                'execution_time': 0,  # Will be updated from stats
                'steps': len(self.current_solution),
                'timestamp': datetime.now()
            }

            # Generate reports
            report_files = self.report_generator.generate_comprehensive_report(
                run_data, self.current_solution, all_runs
            )

            messagebox.showinfo("Report Generated",
                              f"Reports saved successfully:\n\n" +
                              "\n".join([f"- {k}: {v}" for k, v in report_files.items()]))

        except Exception as e:
            messagebox.showerror("Report Error", f"Failed to generate report:\n{e}")

    def _check_magic_square(self):
        """Check if solution forms a semi-magic square."""
        if not self.current_solution:
            messagebox.showinfo("No Solution", "Please run the solver first.")
            return

        try:
            validator = SemiMagicSquareValidator(self.board_size.get())
            analysis = validator.analyze_path(self.current_solution)

            # Create popup window
            popup = tk.Toplevel(self.root)
            popup.title("Semi-Magic Square Analysis")
            popup.geometry("600x500")

            text_widget = scrolledtext.ScrolledText(popup, width=70, height=30,
                                                    font=('Courier', 9))
            text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            # Format analysis
            output = "="*60 + "\n"
            output += "SEMI-MAGIC SQUARE ANALYSIS\n"
            output += "="*60 + "\n\n"

            output += f"Classification: {analysis['classification']}\n"
            output += f"Board Size: {analysis['board_size']}×{analysis['board_size']}\n"
            output += f"Magic Constant (ideal): {analysis['magic_constant']}\n\n"

            output += f"Row Sums: {analysis['row_sums']}\n"
            output += f"  All Equal: {analysis['row_sums_equal']}\n\n"

            output += f"Column Sums: {analysis['column_sums']}\n"
            output += f"  All Equal: {analysis['column_sums_equal']}\n\n"

            output += f"Main Diagonal: {analysis['main_diagonal_sum']}\n"
            output += f"Anti Diagonal: {analysis['anti_diagonal_sum']}\n\n"

            output += f"Is Semi-Magic: {analysis['is_semi_magic']}\n"
            output += f"Is Full Magic: {analysis['is_magic']}\n"

            text_widget.insert('1.0', output)
            text_widget.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze:\n{e}")

    def _view_history(self):
        """View run history from database."""
        try:
            runs = self.db_manager.get_all_runs()

            if not runs:
                messagebox.showinfo("No History", "No previous runs found in database.")
                return

            # Create popup window
            popup = tk.Toplevel(self.root)
            popup.title("Run History")
            popup.geometry("900x600")

            # Create treeview
            tree_frame = ttk.Frame(popup)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            tree = ttk.Treeview(tree_frame, columns=('ID', 'Algorithm', 'Size', 'Time', 'Steps', 'Result', 'Date'),
                              show='headings')

            tree.heading('ID', text='ID')
            tree.heading('Algorithm', text='Algorithm')
            tree.heading('Size', text='Board')
            tree.heading('Time', text='Time (s)')
            tree.heading('Steps', text='Steps')
            tree.heading('Result', text='Result')
            tree.heading('Date', text='Date')

            tree.column('ID', width=50)
            tree.column('Algorithm', width=150)
            tree.column('Size', width=80)
            tree.column('Time', width=100)
            tree.column('Steps', width=80)
            tree.column('Result', width=100)
            tree.column('Date', width=150)

            # Add scrollbar
            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Populate tree
            for run in runs:
                tree.insert('', tk.END, values=(
                    run['id'],
                    run['algorithm'],
                    f"{run['board_size']}×{run['board_size']}",
                    f"{run['execution_time']:.4f}",
                    run['steps'],
                    run['result'],
                    run['timestamp']
                ))

            # Statistics button
            ttk.Button(popup, text="Show Statistics",
                      command=lambda: self._show_database_stats()).pack(pady=10)

        except Exception as e:
            messagebox.showerror("History Error", f"Failed to load history:\n{e}")

    def _show_database_stats(self):
        """Show database statistics."""
        try:
            stats = self.db_manager.get_statistics()

            msg = f"Total Runs: {stats['total_runs']}\n"
            msg += f"Successful: {stats['successful_runs']}\n"
            msg += f"Success Rate: {stats['success_rate']*100:.1f}%\n\n"

            msg += "Average Times by Algorithm:\n"
            for algo, time in stats['avg_times_by_algorithm'].items():
                msg += f"  {algo}: {time:.4f}s\n"

            messagebox.showinfo("Database Statistics", msg)

        except Exception as e:
            messagebox.showerror("Stats Error", f"Failed to load stats:\n{e}")

    def _show_help(self):
        """Show help information."""
        help_text = """
KNIGHT'S TOUR PROBLEM SOLVER - HELP

HOW TO USE:
1. Select board size (5-12)
2. Click on the board to set starting position
3. Choose algorithm (Backtracking or Cultural)
4. Click "Run Solver" to find solution
5. Adjust animation speed with slider
6. Use "Skip Animation" to see final result

ALGORITHMS:
• Backtracking: Uses Warnsdorff's heuristic for efficient search
• Cultural Algorithm: Evolutionary approach with belief space

FEATURES:
• Real-time visualization
• Semi-magic square analysis
• Performance reports and charts
• Run history database

LIMITATIONS:
• Board size: 5×5 to 12×12
• Timeout: 60 seconds per run
• Larger boards may take longer

For more information, check the generated reports.
        """

        messagebox.showinfo("Help", help_text)

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()

    def __del__(self):
        """Cleanup on exit."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
