-- Add up migration script here
-- we want to ensure that all posts are unique;
-- i.e., we don't insert the same post twice
CREATE UNIQUE INDEX ON posts (board, thread_number, post_number);
