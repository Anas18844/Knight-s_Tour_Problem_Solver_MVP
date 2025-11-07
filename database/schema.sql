-- Knight's Tour Problem Solver Database Schema

-- Table to store algorithm run history
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    algorithm TEXT NOT NULL,
    board_size INTEGER NOT NULL,
    execution_time REAL NOT NULL,
    steps INTEGER NOT NULL,
    result TEXT NOT NULL,  -- 'SUCCESS' or 'FAILURE'
    solution_path TEXT,  -- JSON format: list of [x, y] coordinates
    start_position TEXT,  -- JSON format: [x, y]
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table to store report metadata
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    details TEXT,
    performance_graph TEXT,  -- File path to saved graph
    csv_report TEXT,  -- File path to saved CSV
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_runs_algorithm ON runs(algorithm);
CREATE INDEX IF NOT EXISTS idx_runs_board_size ON runs(board_size);
CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs(timestamp);
CREATE INDEX IF NOT EXISTS idx_reports_run_id ON reports(run_id);
