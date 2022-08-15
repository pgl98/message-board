-- DROP TABLE IF EXISTS threads;
-- DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS comments;

-- CREATE TABLE threads
-- (
--     thread_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     title TEXT NOT NULL,
--     body TEXT NOT NULL,
--     date_created TEXT NOT NULL,
--     user_poster TEXT NOT NULL
-- );

-- CREATE TABLE users
-- (
--     username TEXT PRIMARY KEY,
--     password_hash TEXT NOT NULL,
--     is_admin INTEGER FALSE,
--     date_created TEXT NOT NULL,
--     about TEXT DEFAULT "",
--     profile_image TEXT DEFAULT ""
-- );

-- CREATE TABLE comments
-- (
--     comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     thread_id INTEGER NOT NULL,
--     username TEXT NOT NULL,
--     date_created TEXT NOT NULL,
--     body TEXT NOT NULL
-- );

-- UPDATE users
-- SET is_admin=1, about="I clean up this place.", profile_image="admin.png"
-- WHERE username="admin";