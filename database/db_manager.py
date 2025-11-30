import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Tuple, Dict


class DatabaseManager:

    def __init__(self, db_path: str = "knights_tour.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()

    def _initialize_database(self):
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row

            # Read and execute schema
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r') as f:
                schema_sql = f.read()

            self.connection.executescript(schema_sql)
            self.connection.commit()
            print(f"Database initialized at: {self.db_path}")

        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise
        except FileNotFoundError:
            print(f"Schema file not found at: {schema_path}")
            raise

    def insert_run(self, algorithm: str, board_size: int, execution_time: float,steps: int, result: str, solution_path: List[Tuple[int, int]],start_position: Tuple[int, int]) -> int:
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO runs (algorithm, board_size, execution_time, steps,
                                result, solution_path, start_position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                algorithm,
                board_size,
                execution_time,
                steps,
                result,
                json.dumps(solution_path),
                json.dumps(start_position)
            ))
            self.connection.commit()
            return cursor.lastrowid

        except sqlite3.Error as e:
            print(f"Error inserting run: {e}")
            raise

    def insert_report(self, run_id: int, details: str,
                     performance_graph: str, csv_report: str) -> int:
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO reports (run_id, details, performance_graph, csv_report)
                VALUES (?, ?, ?, ?)
            """, (run_id, details, performance_graph, csv_report))
            self.connection.commit()
            return cursor.lastrowid

        except sqlite3.Error as e:
            print(f"Error inserting report: {e}")
            raise

    def get_run_by_id(self, run_id: int) -> Optional[Dict]:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM runs WHERE id = ?", (run_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except sqlite3.Error as e:
            print(f"Error retrieving run: {e}")
            return None

    def get_all_runs(self, algorithm: Optional[str] = None,board_size: Optional[int] = None) -> List[Dict]:
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM runs WHERE 1=1"
            params = []

            if algorithm:
                query += " AND algorithm = ?"
                params.append(algorithm)

            if board_size:
                query += " AND board_size = ?"
                params.append(board_size)

            query += " ORDER BY timestamp DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            print(f"Error retrieving runs: {e}")
            return []

    def get_report_by_run_id(self, run_id: int) -> Optional[Dict]:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM reports WHERE run_id = ?", (run_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except sqlite3.Error as e:
            print(f"Error retrieving report: {e}")
            return None

    def get_statistics(self) -> Dict:
        try:
            cursor = self.connection.cursor()

            # Total runs
            cursor.execute("SELECT COUNT(*) as total FROM runs")
            total = cursor.fetchone()['total']

            # Success rate
            cursor.execute("SELECT COUNT(*) as success FROM runs WHERE result = 'SUCCESS'")
            success = cursor.fetchone()['success']

            # Average execution time by algorithm
            cursor.execute("""
                SELECT algorithm, AVG(execution_time) as avg_time
                FROM runs
                WHERE result = 'SUCCESS'
                GROUP BY algorithm
            """)
            avg_times = {row['algorithm']: row['avg_time'] for row in cursor.fetchall()}

            # Success rate by board size
            cursor.execute("""
                SELECT board_size,
                       COUNT(*) as total,
                       SUM(CASE WHEN result = 'SUCCESS' THEN 1 ELSE 0 END) as success
                FROM runs
                GROUP BY board_size
            """)
            board_stats = {}
            for row in cursor.fetchall():
                board_stats[row['board_size']] = {
                    'total': row['total'],
                    'success': row['success'],
                    'rate': row['success'] / row['total'] if row['total'] > 0 else 0
                }

            return {
                'total_runs': total,
                'successful_runs': success,
                'success_rate': success / total if total > 0 else 0,
                'avg_times_by_algorithm': avg_times,
                'board_size_stats': board_stats
            }

        except sqlite3.Error as e:
            print(f"Error getting statistics: {e}")
            return {}

    def delete_run(self, run_id: int) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM runs WHERE id = ?", (run_id,))
            self.connection.commit()
            return cursor.rowcount > 0

        except sqlite3.Error as e:
            print(f"Error deleting run: {e}")
            return False

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
