CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT
);

CREATE TABLE boards (
    id SERIAL PRIMARY KEY,
    author_id INTEGER REFERENCES users,
    name TEXT
);

CREATE TABLE collaborators (
    board_id INTEGER REFERENCES boards,
    user_id INTEGER REFERENCES users,
    PRIMARY KEY (board_id, user_id)
);

CREATE TABLE lists (
    id SERIAL PRIMARY KEY,
    board_id INTEGER REFERENCES boards,
    name TEXT,
    tasks TEXT[]
);
