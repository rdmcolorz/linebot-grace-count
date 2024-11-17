CREATE TABLE IF NOT EXISTS users (
    user_id TEXT NOT NULL,
    group_id TEXT,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);