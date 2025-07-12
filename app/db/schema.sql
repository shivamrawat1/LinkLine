CREATE TABLE research_studies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT,
  description TEXT,
  criteria_json TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE participants (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  research_id INTEGER,
  name TEXT,
  contact_info TEXT,
  source TEXT,
  status TEXT,
  FOREIGN KEY(research_id) REFERENCES research_studies(id)
); 