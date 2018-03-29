CREATE TABLE IF NOT EXISTS reviews(
  id SERIAL PRIMARY KEY,
  count_value INTEGER DEFAULT 0, -- number of approves
  waiting_from TIMESTAMP NOT NULL,
  issue_number INTEGER NOT NULL,
  pr_name VARCHAR(200) NOT NULL,
  pr_url VARCHAR(400) NOT NULL
);
