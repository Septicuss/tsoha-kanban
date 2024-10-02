CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT
);

CREATE TABLE boards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    name TEXT,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    list_order TEXT DEFAULT ''
);

CREATE TABLE collaborators (
    board_id INTEGER REFERENCES boards ON DELETE CASCADE,
    user_id INTEGER REFERENCES users ON DELETE CASCADE
);

CREATE TABLE lists (
    id SERIAL PRIMARY KEY,
    board_id INTEGER REFERENCES boards ON DELETE CASCADE,
    name TEXT,
    task_order TEXT DEFAULT ''
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    board_id INTEGER REFERENCES boards ON DELETE CASCADE,
    list_id INTEGER REFERENCES lists ON DELETE CASCADE,
    content TEXT
);