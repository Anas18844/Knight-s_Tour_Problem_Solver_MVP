"""Main GUI window for Knight's Tour Problem Solver."""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
from typing import Optional, Tuple
import json
from datetime import datetime

from algorithms import BacktrackingSolver, CulturalAlgorithmSolver
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

        # State variables
        self.current_algorithm = tk.StringVar(value="Backtracking")
        self.algorithm_level = tk.StringVar(value="Level 1")
        self.board_size = tk.IntVar(value=8)
        self.animation_speed = tk.IntVar(value=200)
        self.start_position = (0, 0)
        self.current_solution = None
        self.current_stats = None
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

        # Algorithm Level selection
        ttk.Label(parent, text="Level:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        level_combo = ttk.Combobox(parent, textvariable=self.algorithm_level,
                                   values=["Level 0", "Level 1", "Level 2", "Level 3", "Level 4"],
                                   state="readonly", width=20)
        level_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1

        # DASHBOARD BUTTON - Prominent placement
        dashboard_button = ttk.Button(parent, text="📊 OPEN DASHBOARD",
                                      command=self._show_dashboard)
        dashboard_button.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E),
                             padx=10, pady=10, ipady=10)
        row += 1

        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
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

        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="📄 Generate Report",
                  command=self._generate_report, width=22).grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(button_frame, text="📈 View History",
                  command=self._view_history, width=22).grid(row=1, column=0, padx=5, pady=5)

        ttk.Button(button_frame, text="❓ Help",
                  command=self._show_help, width=22).grid(row=2, column=0, padx=5, pady=5)

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

            # Get level from dropdown
            level_str = self.algorithm_level.get()  # e.g., "Level 0", "Level 1"
            level = int(level_str.split()[-1])  # Extract the number

            # Progress callback
            def progress_callback(percent, message):
                self.progress_queue.put(('progress', percent, message))

            # Create solver based on algorithm and level
            if level == 0:
                # Level 0 - Random Walk (baseline)
                from algorithms.level0_random import RandomKnightWalk
                solver = RandomKnightWalk(n=board_size, level=level)

                # Solve
                start_time = datetime.now()
                success, path = solver.solve(start_pos[0], start_pos[1])
                end_time = datetime.now()

                # Build stats dictionary for consistency
                stats = {
                    'algorithm': f'Random Walk (Level {level})',
                    'execution_time': (end_time - start_time).total_seconds(),
                    'total_moves': solver.total_moves,
                    'dead_ends_hit': solver.dead_ends_hit,
                    'coverage_percent': 100 * len(path) / (board_size * board_size) if board_size > 0 else 0
                }

            elif level == 1:
                from algorithms.backtracking import OrderedKnightWalk
                solver = OrderedKnightWalk(n=board_size, level=level)

                start_time = datetime.now()
                success, path = solver.solve(start_pos[0], start_pos[1])
                end_time = datetime.now()

                stats = {
                    'algorithm': f'Ordered Walk (Level {level})',
                    'execution_time': (end_time - start_time).total_seconds(),
                    'total_moves': solver.total_moves,
                    'dead_ends_hit': solver.dead_ends_hit,
                    'coverage_percent': 100 * len(path) / (board_size * board_size) if board_size > 0 else 0
                }

            elif level == 2:
                from algorithms.backtracking import PureBacktracking
                solver = PureBacktracking(n=board_size, level=level)

                start_time = datetime.now()
                success, path = solver.solve(start_pos[0], start_pos[1])
                end_time = datetime.now()

                stats = {
                    'algorithm': f'Pure Backtracking (Level {level})',
                    'execution_time': (end_time - start_time).total_seconds(),
                    'recursive_calls': solver.recursive_calls,
                    'backtrack_count': solver.backtrack_count,
                    'coverage_percent': 100 * len(path) / (board_size * board_size) if board_size > 0 else 0
                }

            elif level == 3:
                from algorithms.backtracking import EnhancedBacktracking
                solver = EnhancedBacktracking(n=board_size, level=level)

                start_time = datetime.now()
                success, path = solver.solve(start_pos[0], start_pos[1])
                end_time = datetime.now()

                stats = {
                    'algorithm': f'Enhanced Backtracking (Level {level})',
                    'execution_time': (end_time - start_time).total_seconds(),
                    'recursive_calls': solver.recursive_calls,
                    'backtrack_count': solver.backtrack_count,
                    'coverage_percent': 100 * len(path) / (board_size * board_size) if board_size > 0 else 0
                }

            elif level == 4 and algorithm == "Backtracking":
                solver = BacktrackingSolver(board_size, start_pos, timeout=60.0,
                                          progress_callback=progress_callback)

                # Solve
                start_time = datetime.now()
                success, path, stats = solver.solve()
                end_time = datetime.now()

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
        self.current_stats = stats
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.skip_anim_button.config(state=tk.NORMAL)

        if success:
            self.status_label.config(text="✓ Solution Found!", foreground="green")
            self.progress_bar['value'] = 100

            # Save to database
            self._save_to_database(success, path, stats, start_time)

            # Start animation
            self.board_canvas.start_animation(path, speed=200)

        else:
            # Calculate coverage percentage
            board_size = self.board_size.get()
            coverage = len(path) / (board_size * board_size) * 100 if board_size > 0 else 0

            self.status_label.config(
                text=f"✗ Partial Solution ({len(path)}/{board_size*board_size} squares, {coverage:.1f}%)",
                foreground="orange"
            )
            self.progress_bar['value'] = coverage

            # Save failed attempt to database
            self._save_to_database(success, path, stats, start_time)

            if path:
                # Animate partial solution with highlighted unvisited cells
                # This shows where the algorithm got stuck
                self.board_canvas.start_animation(path, speed=self.animation_speed.get(), is_partial=True)

    def _handle_error(self, error_msg):
        """Handle error during solving."""
        self.is_running = False
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text=f"Error: {error_msg}", foreground="red")
        messagebox.showerror("Solver Error", f"An error occurred:\n{error_msg}")


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

    def _show_dashboard(self):
        """Show comprehensive dashboard with algorithm analysis."""
        if not self.current_solution or not self.current_stats:
            messagebox.showinfo("No Data", "Please run the solver first to view the dashboard.")
            return

        try:
            # Create dashboard window
            dashboard = tk.Toplevel(self.root)
            dashboard.title("Algorithm Analysis Dashboard")
            dashboard.geometry("1200x800")
            dashboard.resizable(True, True)

            # Create notebook for tabs
            notebook = ttk.Notebook(dashboard)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Tab 1: Performance Metrics
            metrics_frame = ttk.Frame(notebook, padding="10")
            notebook.add(metrics_frame, text="Performance Metrics")
            self._create_metrics_tab(metrics_frame)

            # Tab 2: Algorithm Analysis (NEW - Detailed technical analysis)
            algo_analysis_frame = ttk.Frame(notebook, padding="10")
            notebook.add(algo_analysis_frame, text="Algorithm Analysis")
            self._create_algorithm_analysis_tab(algo_analysis_frame)

            # Tab 3: Visualization Charts
            charts_frame = ttk.Frame(notebook, padding="10")
            notebook.add(charts_frame, text="Visual Analysis")
            self._create_charts_tab(charts_frame)

            # Tab 4: Comparison Analysis
            comparison_frame = ttk.Frame(notebook, padding="10")
            notebook.add(comparison_frame, text="Historical Comparison")
            self._create_comparison_tab(comparison_frame)

            # Tab 5: Algorithm Details
            details_frame = ttk.Frame(notebook, padding="10")
            notebook.add(details_frame, text="Algorithm Details")
            self._create_details_tab(details_frame)

        except Exception as e:
            messagebox.showerror("Dashboard Error", f"Failed to create dashboard:\n{e}")

    def _create_metrics_tab(self, parent):
        """Create performance metrics tab."""
        # Main container with scrollbar
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Title
        title_label = ttk.Label(scrollable_frame, text="Performance Metrics Analysis",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        row = 1

        # Current Run Information
        info_frame = ttk.LabelFrame(scrollable_frame, text="Current Run Information", padding="10")
        info_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)
        row += 1

        info_text = tk.Text(info_frame, width=80, height=12, font=('Courier', 10))
        info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

        info_content = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    CURRENT RUN METRICS                           ║
╚══════════════════════════════════════════════════════════════════╝

Algorithm:           {self.current_stats.get('algorithm', 'N/A')}
Level:               {self.algorithm_level.get()}
Board Size:          {self.board_size.get()}×{self.board_size.get()}
Start Position:      {self.start_position}
Execution Time:      {self.current_stats.get('execution_time', 0):.4f} seconds
Solution Length:     {self.current_stats.get('solution_length', 0)} moves
Success:             {'YES' if len(self.current_solution) == self.board_size.get()**2 else 'NO'}
"""

        if 'recursive_calls' in self.current_stats:
            info_content += f"Recursive Calls:     {self.current_stats['recursive_calls']:,}\n"
            info_content += f"Avg Time/Call:       {self.current_stats.get('execution_time', 0) / max(1, self.current_stats['recursive_calls']) * 1000:.6f} ms\n"

        if 'generations' in self.current_stats:
            info_content += f"Generations:         {self.current_stats['generations']}\n"
            info_content += f"Best Fitness:        {self.current_stats.get('best_fitness', 0)}\n"

        if self.current_stats.get('timed_out'):
            info_content += f"\n⚠ WARNING: Timeout occurred after {self.current_stats.get('timeout', 60)} seconds\n"

        info_text.insert('1.0', info_content)
        info_text.config(state=tk.DISABLED)

        # Performance Analysis
        perf_frame = ttk.LabelFrame(scrollable_frame, text="Performance Analysis", padding="10")
        perf_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)
        row += 1

        perf_text = tk.Text(perf_frame, width=80, height=15, font=('Courier', 10))
        perf_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Calculate additional metrics
        board_cells = self.board_size.get() ** 2
        coverage = (self.current_stats.get('solution_length', 0) / board_cells) * 100
        time_per_move = self.current_stats.get('execution_time', 0) / max(1, self.current_stats.get('solution_length', 1))

        perf_content = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    PERFORMANCE BREAKDOWN                         ║
╚══════════════════════════════════════════════════════════════════╝

Board Coverage:      {coverage:.2f}% ({self.current_stats.get('solution_length', 0)}/{board_cells} cells)
Time per Move:       {time_per_move:.6f} seconds
Moves per Second:    {1/time_per_move if time_per_move > 0 else 0:.2f}

"""

        if 'recursive_calls' in self.current_stats:
            efficiency = (self.current_stats.get('solution_length', 0) / max(1, self.current_stats['recursive_calls'])) * 100
            perf_content += f"""
Backtracking Efficiency:
  Total Calls:       {self.current_stats['recursive_calls']:,}
  Successful Moves:  {self.current_stats.get('solution_length', 0)}
  Efficiency Ratio:  {efficiency:.2f}%
  Backtrack Rate:    {100-efficiency:.2f}%

Search Space Analysis:
  Theoretical Max:   {8 ** board_cells:,} (8 moves per cell)
  Actual Explored:   {self.current_stats['recursive_calls']:,}
  Reduction:         {(1 - self.current_stats['recursive_calls'] / (8 ** board_cells)) * 100:.10f}%
"""

        # Get historical data for comparison
        try:
            all_runs = self.db_manager.get_all_runs()
            same_algo_runs = [r for r in all_runs if r['algorithm'] == self.current_stats.get('algorithm', '')
                             and r['board_size'] == self.board_size.get() and r['result'] == 'SUCCESS']

            if same_algo_runs:
                avg_time = sum(r['execution_time'] for r in same_algo_runs) / len(same_algo_runs)
                perf_content += f"""
Historical Comparison (Same Algorithm & Board Size):
  Total Runs:        {len(same_algo_runs)}
  Average Time:      {avg_time:.4f} seconds
  Current vs Avg:    {((self.current_stats.get('execution_time', 0) - avg_time) / avg_time * 100):+.2f}%
  Rank:              {sorted([r['execution_time'] for r in same_algo_runs]).index(self.current_stats.get('execution_time', 0)) + 1}/{len(same_algo_runs)}
"""
        except:
            pass

        perf_text.insert('1.0', perf_content)
        perf_text.config(state=tk.DISABLED)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_algorithm_analysis_tab(self, parent):
        """Create detailed algorithm analysis tab with technical metrics."""
        # Title
        title_label = ttk.Label(parent, text="Detailed Algorithm Analysis",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Create scrolled text for simple display
        import tkinter.scrolledtext as scrolledtext
        analysis_text = scrolledtext.ScrolledText(parent, width=100, height=40, font=('Courier', 10))
        analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        algo_name = self.current_stats.get('algorithm', 'Unknown')

        # Generate analysis content
        if 'Backtracking' in algo_name:
            content = self._generate_backtracking_analysis()
        elif 'Cultural' in algo_name:
            content = self._generate_cultural_analysis()
        else:
            content = "Detailed analysis not available for this algorithm."

        analysis_text.insert('1.0', content)
        analysis_text.config(state=tk.DISABLED)

    def _generate_backtracking_analysis(self):
        """Generate Backtracking analysis content."""
        total_calls = self.current_stats.get('recursive_calls', 0)
        solution_length = self.current_stats.get('solution_length', 0)
        board_size = self.board_size.get()
        total_cells = board_size ** 2
        execution_time = self.current_stats.get('execution_time', 0)

        # Calculate metrics
        theoretical_calls = min(8 ** total_cells, 10**20)  # Cap for display
        actual_calls = total_calls
        successful_moves = solution_length
        failed_attempts = total_attempts = total_calls
        if solution_length > 0:
            failed_attempts = total_attempts - successful_moves
        backtrack_rate = (failed_attempts / max(1, total_attempts)) * 100

        content = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    DETAILED ALGORITHM ANALYSIS                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

ALGORITHM: {self.current_stats.get('algorithm', 'N/A')}
LEVEL: {self.algorithm_level.get()}
BOARD SIZE: {board_size}×{board_size}

════════════════════════════════════════════════════════════════════════════════
1. WARNSDORFF'S HEURISTIC EFFECTIVENESS
════════════════════════════════════════════════════════════════════════════════

Heuristic Rule:
  "Always move the knight to the square from which it will have the fewest
   onward moves."

Impact on Current Run:
  Theoretical Search Space:  {theoretical_calls:,} nodes (without heuristic)
  Actual Nodes Explored:     {actual_calls:,} nodes (with heuristic)
  Search Space Reduction:    {(theoretical_calls/max(1, actual_calls)):,.2e}x smaller

Heuristic Success Rate:
  Moves Made:                {solution_length}/{total_cells} ({(solution_length/max(1,total_cells))*100:.1f}%)
  Calls per Move:            {actual_calls/max(1, solution_length):.2f}
  Overhead Factor:           {actual_calls/max(1, solution_length):.2f}x

Move Selection Quality:      """

        if solution_length > 0:
            calls_per_move = actual_calls / solution_length
            if calls_per_move < 2:
                quality = "⭐⭐⭐⭐⭐ EXCELLENT - Minimal backtracking"
            elif calls_per_move < 5:
                quality = "⭐⭐⭐⭐ GOOD - Low backtracking rate"
            elif calls_per_move < 10:
                quality = "⭐⭐⭐ MODERATE - Some backtracking needed"
            else:
                quality = "⭐⭐ CHALLENGING - Significant backtracking"
            content += f"{quality}\n  Average Tries per Move:    {calls_per_move:.2f}\n"

        content += f"""

════════════════════════════════════════════════════════════════════════════════
2. BACKTRACKING OPERATIONS ANALYSIS
════════════════════════════════════════════════════════════════════════════════

Call Breakdown:
  Total Recursive Calls:     {total_calls:,}
  Successful Moves:          {successful_moves} (led to solution path)
  Failed Attempts:           {failed_attempts:,} (required backtracking)
  Backtrack Rate:            {backtrack_rate:.2f}%

Backtracking Efficiency:
  Success Ratio:             {(successful_moves/max(1, total_attempts))*100:.2f}%
  Failure Ratio:             {backtrack_rate:.2f}%
  Efficiency Score:          {100 - backtrack_rate:.2f}/100

Search Tree Metrics:
  Branching Factor:          ~8 (knight has max 8 moves)
  Effective Branching:       {total_calls/max(1, solution_length):.2f} (after pruning)
  Pruning Effectiveness:     {(1 - (total_calls/max(1, solution_length))/8)*100:.1f}%

Performance Classification: """

        if backtrack_rate < 10:
            classification = "⭐⭐⭐⭐⭐ OPTIMAL - Almost no backtracking"
        elif backtrack_rate < 30:
            classification = "⭐⭐⭐⭐ EXCELLENT - Minimal backtracking"
        elif backtrack_rate < 50:
            classification = "⭐⭐⭐ GOOD - Moderate backtracking"
        elif backtrack_rate < 70:
            classification = "⭐⭐ FAIR - Significant backtracking"
        else:
            classification = "⭐ CHALLENGING - Heavy backtracking"

        content += f"{classification}\n"

        content += f"""

════════════════════════════════════════════════════════════════════════════════
3. COMPLEXITY ANALYSIS
════════════════════════════════════════════════════════════════════════════════

Time Complexity:
  Theoretical (No Heuristic):  O(8^{total_cells})
  With Warnsdorff's Heuristic: O(n²) to O(n³) typically
  Actual Performance:          {total_calls:,} calls for {board_size}×{board_size} board
  Observed Complexity:         ~O(n^{2 if total_calls < total_cells**2 else 3})

Space Complexity:
  Board Storage:       O(n²) = {total_cells} cells
  Recursion Stack:     O(n²) = max {solution_length} levels
  Path Storage:        O(n²) = {solution_length} positions

Execution Metrics:
  Total Time:          {execution_time:.6f} seconds
  Time per Call:       {(execution_time / max(1, total_calls)) * 1000:.6f} ms
  Calls per Second:    {total_calls/max(0.000001, execution_time):,.0f}
  Time per Move:       {(execution_time/max(1, solution_length))*1000:.3f} ms

════════════════════════════════════════════════════════════════════════════════
END OF ANALYSIS
════════════════════════════════════════════════════════════════════════════════
"""
        return content

    def _generate_cultural_analysis(self):
        """Generate Cultural Algorithm analysis content."""
        generations = self.current_stats.get('generations', 0)
        best_fitness = self.current_stats.get('best_fitness', 0)
        execution_time = self.current_stats.get('execution_time', 0)

        content = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                CULTURAL ALGORITHM ANALYSIS                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

Evolution Metrics:
  Total Generations:         {generations}
  Best Fitness Achieved:     {best_fitness}
  Execution Time:            {execution_time:.4f} seconds
  Time per Generation:       {(execution_time/max(1, generations))*1000:.3f} ms

Population Dynamics:
  Population Size:           100 individuals (default)
  Selection Pressure:        High (elite selection)
  Mutation Rate:             Adaptive

Performance:
  Solution Quality:          {best_fitness} moves
  Board Coverage:            {(self.current_stats.get('solution_length', 0)/self.board_size.get()**2)*100:.1f}%

Note: Detailed Cultural Algorithm analysis will be enhanced in future versions.
"""
        return content

    def _create_charts_tab(self, parent):
        """Create visualization charts tab."""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import numpy as np

        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Algorithm Performance Visualization', fontsize=16, fontweight='bold')

        # Chart 1: Solution Path Heatmap
        if self.current_solution:
            board_size = self.board_size.get()
            heatmap_data = np.zeros((board_size, board_size))
            for idx, (x, y) in enumerate(self.current_solution):
                heatmap_data[y][x] = idx + 1

            im1 = ax1.imshow(heatmap_data, cmap='viridis', aspect='auto')
            ax1.set_title('Move Order Heatmap')
            ax1.set_xlabel('X Position')
            ax1.set_ylabel('Y Position')
            plt.colorbar(im1, ax=ax1, label='Move Number')

        # Chart 2: Performance Metrics Bar Chart
        metrics_labels = ['Execution\nTime (s)', 'Solution\nLength', 'Recursive\nCalls (÷1000)']
        metrics_values = [
            self.current_stats.get('execution_time', 0),
            self.current_stats.get('solution_length', 0),
            self.current_stats.get('recursive_calls', 0) / 1000
        ]
        colors = ['#3498db', '#2ecc71', '#e74c3c']
        ax2.bar(metrics_labels, metrics_values, color=colors, alpha=0.7, edgecolor='black')
        ax2.set_title('Performance Metrics')
        ax2.set_ylabel('Value')
        ax2.grid(axis='y', alpha=0.3)

        # Chart 3: Historical Performance Trend
        try:
            all_runs = self.db_manager.get_all_runs()
            same_algo_runs = [r for r in all_runs if r['algorithm'] == self.current_stats.get('algorithm', '')]

            if len(same_algo_runs) > 1:
                runs_sorted = sorted(same_algo_runs, key=lambda r: r['id'])
                times = [r['execution_time'] for r in runs_sorted]
                run_numbers = list(range(1, len(runs_sorted) + 1))

                ax3.plot(run_numbers, times, marker='o', linewidth=2, markersize=6, color='#9b59b6')
                ax3.axhline(y=np.mean(times), color='r', linestyle='--', label=f'Average: {np.mean(times):.4f}s')
                ax3.set_title(f'Performance Trend - {self.current_stats.get("algorithm", "N/A")}')
                ax3.set_xlabel('Run Number')
                ax3.set_ylabel('Execution Time (s)')
                ax3.legend()
                ax3.grid(True, alpha=0.3)
            else:
                ax3.text(0.5, 0.5, 'Not enough historical data', ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('Performance Trend')
        except Exception as e:
            ax3.text(0.5, 0.5, f'Error loading data:\n{str(e)}', ha='center', va='center', transform=ax3.transAxes)

        # Chart 4: Board Size vs Performance
        try:
            all_runs = self.db_manager.get_all_runs()
            successful_runs = [r for r in all_runs if r['result'] == 'SUCCESS']

            if successful_runs:
                board_sizes = {}
                for run in successful_runs:
                    size = run['board_size']
                    if size not in board_sizes:
                        board_sizes[size] = []
                    board_sizes[size].append(run['execution_time'])

                sizes = sorted(board_sizes.keys())
                avg_times = [np.mean(board_sizes[s]) for s in sizes]

                ax4.scatter(sizes, avg_times, s=100, alpha=0.6, c='#e67e22', edgecolor='black')
                ax4.plot(sizes, avg_times, linestyle='--', alpha=0.5, color='#e67e22')
                ax4.set_title('Board Size vs Average Time')
                ax4.set_xlabel('Board Size (n×n)')
                ax4.set_ylabel('Average Execution Time (s)')
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No successful runs', ha='center', va='center', transform=ax4.transAxes)
        except Exception as e:
            ax4.text(0.5, 0.5, f'Error:\n{str(e)}', ha='center', va='center', transform=ax4.transAxes)

        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _create_comparison_tab(self, parent):
        """Create historical comparison tab."""
        # Title
        title_label = ttk.Label(parent, text="Historical Comparison Analysis",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Create treeview for comparison
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tree = ttk.Treeview(tree_frame, columns=('Run', 'Algorithm', 'Level', 'Board', 'Time', 'Calls', 'Status'),
                          show='headings', height=15)

        tree.heading('Run', text='Run #')
        tree.heading('Algorithm', text='Algorithm')
        tree.heading('Level', text='Level')
        tree.heading('Board', text='Board Size')
        tree.heading('Time', text='Time (s)')
        tree.heading('Calls', text='Recursive Calls')
        tree.heading('Status', text='Status')

        tree.column('Run', width=60)
        tree.column('Algorithm', width=150)
        tree.column('Level', width=80)
        tree.column('Board', width=100)
        tree.column('Time', width=100)
        tree.column('Calls', width=120)
        tree.column('Status', width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate with data
        try:
            all_runs = self.db_manager.get_all_runs()
            for idx, run in enumerate(all_runs[:50], 1):  # Show last 50 runs
                # Extract stats if available
                calls = 'N/A'
                if 'stats' in run:
                    try:
                        stats_dict = json.loads(run.get('stats', '{}'))
                        calls = f"{stats_dict.get('recursive_calls', 'N/A'):,}" if isinstance(stats_dict.get('recursive_calls'), int) else 'N/A'
                    except:
                        pass

                tree.insert('', tk.END, values=(
                    idx,
                    run.get('algorithm', 'N/A'),
                    'N/A',  # Level not in old runs
                    f"{run['board_size']}×{run['board_size']}",
                    f"{run['execution_time']:.4f}",
                    calls,
                    run['result']
                ))
        except Exception as e:
            print(f"Error loading history: {e}")

        # Statistics summary
        summary_frame = ttk.LabelFrame(parent, text="Summary Statistics", padding="10")
        summary_frame.pack(fill=tk.X, padx=10, pady=10)

        try:
            stats = self.db_manager.get_statistics()
            summary_text = f"""
Total Runs: {stats['total_runs']}  |  Successful: {stats['successful_runs']}  |  Success Rate: {stats['success_rate']*100:.1f}%

Average Execution Times by Algorithm:
"""
            for algo, time in stats['avg_times_by_algorithm'].items():
                summary_text += f"  • {algo}: {time:.4f}s\n"

            summary_label = ttk.Label(summary_frame, text=summary_text, font=('Courier', 10))
            summary_label.pack()
        except:
            pass

    def _create_details_tab(self, parent):
        """Create algorithm details tab."""
        # Title
        title_label = ttk.Label(parent, text="Algorithm Implementation Details",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Create text widget with scrollbar
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = scrolledtext.ScrolledText(text_frame, width=100, height=35, font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True)

        algo_name = self.current_stats.get('algorithm', 'Unknown')

        details_content = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ALGORITHM IMPLEMENTATION DETAILS                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

Algorithm: {algo_name}
Level: {self.algorithm_level.get()}

"""

        if 'Backtracking' in algo_name:
            details_content += """
BACKTRACKING WITH WARNSDORFF'S HEURISTIC
─────────────────────────────────────────────────────────────────────────────

Overview:
  The backtracking algorithm systematically explores all possible knight moves
  using a depth-first search approach with intelligent pruning via Warnsdorff's
  heuristic.

Warnsdorff's Rule:
  "Always move the knight to the square from which the knight will have the
   fewest onward moves."

  This heuristic dramatically reduces the search space by prioritizing moves
  that lead to "harder" squares first, reducing the likelihood of getting
  stuck later in the tour.

Algorithm Steps:
  1. Start at the given position and mark it as visited
  2. For the current position:
     a. Calculate the degree (number of unvisited neighbors) for each
        possible next move
     b. Sort moves by ascending degree (Warnsdorff's heuristic)
     c. Try each move in order
  3. If all squares are visited → SUCCESS
  4. If stuck (no valid moves) → BACKTRACK to previous position
  5. Repeat until solution found or all possibilities exhausted

Complexity Analysis:
  Time Complexity:  O(8^(n²)) worst case (8 moves per cell, n² cells)
  Space Complexity: O(n²) for the board representation

  With Warnsdorff's heuristic:
  Practical Time:   O(n²) to O(n³) for most cases
  Success Rate:     Very high for boards ≤ 10×10

Key Optimizations:
  • Warnsdorff's heuristic reduces backtracking significantly
  • Early termination on timeout
  • Efficient board representation using 2D array
  • Move validation caching

Strengths:
  ✓ Guaranteed to find solution if one exists
  ✓ Very fast for small-medium boards (5×5 to 8×8)
  ✓ Memory efficient
  ✓ Deterministic results

Limitations:
  ✗ Can be slow for large boards (>10×10)
  ✗ May timeout on difficult starting positions
  ✗ Single-threaded execution

Performance Characteristics:
  Best Case:    Linear path with no backtracking
  Average Case: Minimal backtracking with heuristic guidance
  Worst Case:   Extensive backtracking before finding solution

Current Run Statistics:
  Board Size:        {self.board_size.get()}×{self.board_size.get()}
  Total Cells:       {self.board_size.get()**2}
  Recursive Calls:   {self.current_stats.get('recursive_calls', 'N/A'):,}
  Execution Time:    {self.current_stats.get('execution_time', 0):.4f}s
  Success:           {'YES' if self.current_stats.get('solution_length', 0) == self.board_size.get()**2 else 'NO'}
"""
        elif 'Cultural' in algo_name:
            details_content += """
CULTURAL ALGORITHM
─────────────────────────────────────────────────────────────────────────────

Overview:
  Cultural algorithms combine evolutionary computation with cultural evolution,
  maintaining both a population space and a belief space that guide the search.

Algorithm Components:
  1. Population Space: Set of candidate solutions (knight tours)
  2. Belief Space: Knowledge extracted from successful individuals
  3. Communication Protocol: Exchange between spaces

Algorithm Steps:
  1. Initialize random population of partial/complete tours
  2. Evaluate fitness of each individual
  3. Update belief space with knowledge from best individuals
  4. Apply belief space knowledge to guide population evolution
  5. Perform selection, crossover, and mutation
  6. Repeat until solution found or max generations reached

Key Features:
  • Dual inheritance (genetic + cultural)
  • Knowledge-guided search
  • Population-based exploration
  • Adaptive search strategies

Current Run Statistics:
  Generations:       {self.current_stats.get('generations', 'N/A')}
  Best Fitness:      {self.current_stats.get('best_fitness', 'N/A')}
  Execution Time:    {self.current_stats.get('execution_time', 0):.4f}s
"""

        text_widget.insert('1.0', details_content)
        text_widget.config(state=tk.DISABLED)

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
