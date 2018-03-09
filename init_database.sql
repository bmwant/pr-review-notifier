PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS reviews(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  count_value INTEGER DEFAULT 0,
  waiting_from DATE NOT NULL,
  issue_number INTEGER NOT NULL,
  pr_name TEXT NOT NULL,
  pr_url TEXT NOT NULL
);
