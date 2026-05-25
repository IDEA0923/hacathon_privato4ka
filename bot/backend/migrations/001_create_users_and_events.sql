CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER NOT NULL UNIQUE,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    consent_at TEXT,
    subjects TEXT,
    "class" INTEGER,
    region TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subjects TEXT NOT NULL,
    "class" INTEGER NOT NULL,
    region TEXT NOT NULL,
    event_date TEXT NOT NULL,
    description TEXT,
    link TEXT
);
