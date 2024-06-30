DROP TABLE IF EXISTS urls;
CREATE TABLE urls (
  id bigint PRIMARY KEY,
  url VARCHAR(255),
  created_at DATE
);