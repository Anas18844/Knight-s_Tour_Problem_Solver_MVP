"""Unit tests for Database manager."""

import pytest
import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager


class TestDatabaseManager:
    """Test cases for DatabaseManager."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_path = temp_file.name
        temp_file.close()

        # Copy schema to temp location
        import shutil
        schema_src = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'database', 'schema.sql')
        temp_schema = os.path.join(tempfile.gettempdir(), 'schema.sql')

        if os.path.exists(schema_src):
            shutil.copy(schema_src, temp_schema)

        db = DatabaseManager(db_path=temp_path)

        yield db

        # Cleanup
        db.close()
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if os.path.exists(temp_schema):
            os.unlink(temp_schema)

    def test_database_initialization(self, temp_db):
        """Test database initialization."""
        assert temp_db.connection is not None
        assert os.path.exists(temp_db.db_path)

    def test_insert_run(self, temp_db):
        """Test inserting a run record."""
        run_id = temp_db.insert_run(
            algorithm="Backtracking",
            board_size=8,
            execution_time=1.5,
            steps=64,
            result="SUCCESS",
            solution_path=[(0, 0), (2, 1), (3, 3)],
            start_position=(0, 0)
        )

        assert run_id is not None
        assert run_id > 0

    def test_get_run_by_id(self, temp_db):
        """Test retrieving run by ID."""
        # Insert a run
        run_id = temp_db.insert_run(
            algorithm="Cultural Algorithm",
            board_size=8,
            execution_time=2.5,
            steps=64,
            result="SUCCESS",
            solution_path=[(0, 0), (1, 2)],
            start_position=(0, 0)
        )

        # Retrieve it
        run = temp_db.get_run_by_id(run_id)

        assert run is not None
        assert run['id'] == run_id
        assert run['algorithm'] == "Cultural Algorithm"
        assert run['board_size'] == 8
        assert run['execution_time'] == 2.5
        assert run['result'] == "SUCCESS"

    def test_get_run_by_invalid_id(self, temp_db):
        """Test retrieving non-existent run."""
        run = temp_db.get_run_by_id(99999)
        assert run is None

    def test_get_all_runs(self, temp_db):
        """Test retrieving all runs."""
        # Insert multiple runs
        temp_db.insert_run("Backtracking", 8, 1.0, 64, "SUCCESS",
                          [(0, 0)], (0, 0))
        temp_db.insert_run("Cultural Algorithm", 8, 2.0, 64, "SUCCESS",
                          [(0, 0)], (0, 0))

        runs = temp_db.get_all_runs()

        assert len(runs) >= 2
        assert all('algorithm' in run for run in runs)

    def test_get_runs_filtered_by_algorithm(self, temp_db):
        """Test filtering runs by algorithm."""
        temp_db.insert_run("Backtracking", 8, 1.0, 64, "SUCCESS",
                          [(0, 0)], (0, 0))
        temp_db.insert_run("Cultural Algorithm", 8, 2.0, 64, "SUCCESS",
                          [(0, 0)], (0, 0))

        runs = temp_db.get_all_runs(algorithm="Backtracking")

        assert len(runs) >= 1
        assert all(run['algorithm'] == "Backtracking" for run in runs)

    def test_get_runs_filtered_by_board_size(self, temp_db):
        """Test filtering runs by board size."""
        temp_db.insert_run("Backtracking", 6, 1.0, 36, "SUCCESS",
                          [(0, 0)], (0, 0))
        temp_db.insert_run("Backtracking", 8, 2.0, 64, "SUCCESS",
                          [(0, 0)], (0, 0))

        runs = temp_db.get_all_runs(board_size=6)

        assert len(runs) >= 1
        assert all(run['board_size'] == 6 for run in runs)

    def test_insert_report(self, temp_db):
        """Test inserting report record."""
        # First insert a run
        run_id = temp_db.insert_run("Backtracking", 8, 1.0, 64, "SUCCESS",
                                    [(0, 0)], (0, 0))

        # Insert report
        report_id = temp_db.insert_report(
            run_id=run_id,
            details="Test report",
            performance_graph="reports/graph.png",
            csv_report="reports/report.csv"
        )

        assert report_id is not None
        assert report_id > 0

    def test_get_report_by_run_id(self, temp_db):
        """Test retrieving report by run ID."""
        run_id = temp_db.insert_run("Backtracking", 8, 1.0, 64, "SUCCESS",
                                    [(0, 0)], (0, 0))

        report_id = temp_db.insert_report(
            run_id=run_id,
            details="Test details",
            performance_graph="test.png",
            csv_report="test.csv"
        )

        report = temp_db.get_report_by_run_id(run_id)

        assert report is not None
        assert report['run_id'] == run_id
        assert report['details'] == "Test details"

    def test_get_statistics(self, temp_db):
        """Test getting database statistics."""
        # Insert some runs
        temp_db.insert_run("Backtracking", 8, 1.0, 64, "SUCCESS",
                          [(0, 0)], (0, 0))
        temp_db.insert_run("Backtracking", 8, 1.5, 64, "SUCCESS",
                          [(0, 0)], (0, 0))
        temp_db.insert_run("Cultural Algorithm", 8, 2.0, 0, "FAILURE",
                          [], (0, 0))

        stats = temp_db.get_statistics()

        assert 'total_runs' in stats
        assert 'successful_runs' in stats
        assert 'success_rate' in stats
        assert stats['total_runs'] == 3
        assert stats['successful_runs'] == 2
        assert stats['success_rate'] == 2/3

    def test_delete_run(self, temp_db):
        """Test deleting a run."""
        run_id = temp_db.insert_run("Backtracking", 8, 1.0, 64, "SUCCESS",
                                    [(0, 0)], (0, 0))

        # Delete it
        result = temp_db.delete_run(run_id)
        assert result == True

        # Verify it's gone
        run = temp_db.get_run_by_id(run_id)
        assert run is None

    def test_delete_nonexistent_run(self, temp_db):
        """Test deleting non-existent run."""
        result = temp_db.delete_run(99999)
        assert result == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
