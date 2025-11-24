
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    algorithm TEXT NOT NULL,
    board_size INTEGER NOT NULL,
    execution_time REAL NOT NULL,
    steps INTEGER NOT NULL,
    result TEXT NOT NULL,
    solution_path TEXT,
    start_position TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    details TEXT,
    performance_graph TEXT,
    csv_report TEXT,  
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_runs_algorithm ON runs(algorithm);
CREATE INDEX IF NOT EXISTS idx_runs_board_size ON runs(board_size);
CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs(timestamp);
CREATE INDEX IF NOT EXISTS idx_reports_run_id ON reports(run_id);
