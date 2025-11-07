"""Report generator for Knight's Tour solver results."""

import os
import csv
import json
from datetime import datetime
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class ReportGenerator:
    """Generates reports, visualizations, and exports for Knight's Tour solutions."""

    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_timestamp(self) -> str:
        """Generate timestamp string for filenames."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def save_csv_report(self, run_data: dict, filename: str = None) -> str:
        """
        Save run data to CSV file.

        Args:
            run_data: Dictionary with run information
            filename: Custom filename (optional)

        Returns:
            Path to saved CSV file
        """
        if filename is None:
            timestamp = self.generate_timestamp()
            algorithm = run_data.get('algorithm', 'unknown').replace(' ', '_')
            board_size = run_data.get('board_size', 0)
            filename = f"run_{algorithm}_{board_size}x{board_size}_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)

        # Flatten nested data for CSV
        flat_data = {}
        for key, value in run_data.items():
            if isinstance(value, (dict, list)):
                flat_data[key] = json.dumps(value)
            else:
                flat_data[key] = value

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=flat_data.keys())
            writer.writeheader()
            writer.writerow(flat_data)

        print(f"CSV report saved: {filepath}")
        return filepath

    def save_performance_chart(self, runs_data: List[dict],
                               filename: str = None) -> str:
        """
        Create and save performance comparison chart.

        Args:
            runs_data: List of run data dictionaries
            filename: Custom filename (optional)

        Returns:
            Path to saved chart
        """
        if not runs_data:
            print("No data to plot")
            return ""

        if filename is None:
            timestamp = self.generate_timestamp()
            filename = f"performance_chart_{timestamp}.png"

        filepath = os.path.join(self.output_dir, filename)

        # Separate data by algorithm
        algorithms = {}
        for run in runs_data:
            algo = run.get('algorithm', 'Unknown')
            if algo not in algorithms:
                algorithms[algo] = {'board_sizes': [], 'times': [], 'success': []}

            algorithms[algo]['board_sizes'].append(run.get('board_size', 0))
            algorithms[algo]['times'].append(run.get('execution_time', 0))
            algorithms[algo]['success'].append(run.get('result', 'FAILURE') == 'SUCCESS')

        # Create plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Plot 1: Execution time vs board size
        for algo, data in algorithms.items():
            ax1.plot(data['board_sizes'], data['times'], marker='o', label=algo, linewidth=2)

        ax1.set_xlabel('Board Size (n×n)', fontsize=12)
        ax1.set_ylabel('Execution Time (seconds)', fontsize=12)
        ax1.set_title('Algorithm Performance: Execution Time vs Board Size', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Success rate by board size
        for algo, data in algorithms.items():
            # Group by board size and calculate success rate
            board_size_success = {}
            for size, success in zip(data['board_sizes'], data['success']):
                if size not in board_size_success:
                    board_size_success[size] = {'total': 0, 'success': 0}
                board_size_success[size]['total'] += 1
                if success:
                    board_size_success[size]['success'] += 1

            sizes = sorted(board_size_success.keys())
            rates = [board_size_success[size]['success'] / board_size_success[size]['total']
                    for size in sizes]

            ax2.plot(sizes, rates, marker='s', label=algo, linewidth=2)

        ax2.set_xlabel('Board Size (n×n)', fontsize=12)
        ax2.set_ylabel('Success Rate', fontsize=12)
        ax2.set_title('Algorithm Success Rate vs Board Size', fontsize=14, fontweight='bold')
        ax2.set_ylim(-0.05, 1.05)
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Performance chart saved: {filepath}")
        return filepath

    def save_solution_visualization(self, path: List[Tuple[int, int]],
                                    board_size: int, algorithm: str,
                                    filename: str = None) -> str:
        """
        Create and save visualization of knight's tour solution.

        Args:
            path: List of (x, y) coordinates
            board_size: Size of the board
            algorithm: Algorithm name
            filename: Custom filename (optional)

        Returns:
            Path to saved visualization
        """
        if filename is None:
            timestamp = self.generate_timestamp()
            filename = f"solution_{algorithm.replace(' ', '_')}_{board_size}x{board_size}_{timestamp}.png"

        filepath = os.path.join(self.output_dir, filename)

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 10))

        # Draw chessboard
        for i in range(board_size):
            for j in range(board_size):
                color = 'wheat' if (i + j) % 2 == 0 else 'saddlebrown'
                square = patches.Rectangle((j, board_size - i - 1), 1, 1,
                                          linewidth=1, edgecolor='black',
                                          facecolor=color)
                ax.add_patch(square)

        # Draw path
        if path:
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]

                # Convert coordinates (flip y for display)
                display_y1 = board_size - y1 - 1
                display_y2 = board_size - y2 - 1

                # Draw line
                ax.plot([x1 + 0.5, x2 + 0.5], [display_y1 + 0.5, display_y2 + 0.5],
                       'b-', linewidth=2, alpha=0.6)

                # Draw arrow at midpoint
                mid_x = (x1 + x2) / 2 + 0.5
                mid_y = (display_y1 + display_y2) / 2 + 0.5
                dx = (x2 - x1) * 0.15
                dy = (display_y2 - display_y1) * 0.15

                ax.arrow(mid_x, mid_y, dx, dy, head_width=0.2, head_length=0.15,
                        fc='blue', ec='blue', alpha=0.7)

            # Mark start position
            start_x, start_y = path[0]
            display_start_y = board_size - start_y - 1
            ax.plot(start_x + 0.5, display_start_y + 0.5, 'go', markersize=15,
                   label='Start', zorder=5)

            # Mark end position
            end_x, end_y = path[-1]
            display_end_y = board_size - end_y - 1
            ax.plot(end_x + 0.5, display_end_y + 0.5, 'ro', markersize=15,
                   label='End', zorder=5)

            # Add move numbers on squares
            for move_num, (x, y) in enumerate(path):
                display_y = board_size - y - 1
                ax.text(x + 0.5, display_y + 0.5, str(move_num + 1),
                       ha='center', va='center', fontsize=8, fontweight='bold',
                       color='darkred')

        ax.set_xlim(0, board_size)
        ax.set_ylim(0, board_size)
        ax.set_aspect('equal')
        ax.set_xticks(range(board_size))
        ax.set_yticks(range(board_size))
        ax.set_xticklabels(range(board_size))
        ax.set_yticklabels(range(board_size - 1, -1, -1))
        ax.set_xlabel('Column', fontsize=12)
        ax.set_ylabel('Row', fontsize=12)
        ax.set_title(f"Knight's Tour Solution\n{algorithm} - {board_size}×{board_size} Board",
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Solution visualization saved: {filepath}")
        return filepath

    def generate_comprehensive_report(self, run_data: dict, path: List[Tuple[int, int]],
                                     all_runs: List[dict] = None) -> Dict[str, str]:
        """
        Generate comprehensive report including CSV, charts, and visualization.

        Args:
            run_data: Current run data
            path: Solution path
            all_runs: Historical runs for comparison (optional)

        Returns:
            Dictionary with paths to all generated files
        """
        timestamp = self.generate_timestamp()
        algorithm = run_data.get('algorithm', 'unknown').replace(' ', '_')
        board_size = run_data.get('board_size', 0)
        base_name = f"{algorithm}_{board_size}x{board_size}_{timestamp}"

        report_files = {}

        # Save CSV report
        csv_file = self.save_csv_report(run_data, f"run_{base_name}.csv")
        report_files['csv'] = csv_file

        # Save solution visualization
        if path:
            viz_file = self.save_solution_visualization(
                path, board_size, run_data.get('algorithm', 'Unknown'),
                f"solution_{base_name}.png"
            )
            report_files['visualization'] = viz_file

        # Save performance chart if historical data available
        if all_runs and len(all_runs) > 0:
            chart_file = self.save_performance_chart(
                all_runs, f"performance_{base_name}.png"
            )
            report_files['performance_chart'] = chart_file

        # Create summary text file
        summary_file = os.path.join(self.output_dir, f"summary_{base_name}.txt")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("KNIGHT'S TOUR PROBLEM SOLVER - RUN SUMMARY\n")
            f.write("="*70 + "\n\n")

            f.write(f"Algorithm: {run_data.get('algorithm', 'N/A')}\n")
            f.write(f"Board Size: {board_size}×{board_size}\n")
            f.write(f"Start Position: {run_data.get('start_position', 'N/A')}\n")
            f.write(f"Result: {run_data.get('result', 'N/A')}\n")
            f.write(f"Execution Time: {run_data.get('execution_time', 0):.4f} seconds\n")
            f.write(f"Steps/Moves: {run_data.get('steps', 0)}\n")
            f.write(f"Timestamp: {run_data.get('timestamp', datetime.now())}\n\n")

            # Add statistics if available
            if 'stats' in run_data:
                f.write("Statistics:\n")
                for key, value in run_data['stats'].items():
                    f.write(f"  - {key}: {value}\n")

            f.write("\n" + "="*70 + "\n")

        report_files['summary'] = summary_file
        print(f"Summary report saved: {summary_file}")

        return report_files

    def create_comparison_table(self, runs: List[dict], filename: str = None) -> str:
        """
        Create CSV comparison table for multiple runs.

        Args:
            runs: List of run data dictionaries
            filename: Custom filename (optional)

        Returns:
            Path to saved comparison table
        """
        if filename is None:
            timestamp = self.generate_timestamp()
            filename = f"comparison_table_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)

        if not runs:
            print("No runs to compare")
            return ""

        # Define columns
        columns = ['id', 'algorithm', 'board_size', 'execution_time',
                  'steps', 'result', 'timestamp']

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()

            for run in runs:
                row = {col: run.get(col, 'N/A') for col in columns}
                writer.writerow(row)

        print(f"Comparison table saved: {filepath}")
        return filepath
