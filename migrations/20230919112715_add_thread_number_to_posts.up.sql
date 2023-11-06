-- Add up migration script here
ALTER TABLE posts ADD COLUMN thread_number BIGINT NOT NULL;