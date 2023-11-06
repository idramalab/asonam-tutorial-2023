-- Add up migration script here
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    post_number BIGINT NOT NULL,
    data JSONB DEFAULT '{}'::jsonb NOT NULL,
    html TEXT
)