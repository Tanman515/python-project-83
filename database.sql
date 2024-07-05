DROP TABLE IF EXISTS urls;
DROP TABLE IF EXISTS url_checks;
CREATE TABLE urls (
  id bigint PRIMARY KEY,
  url VARCHAR(255),
  created_at DATE
);

CREATE TABLE url_checks (
  id INT PRIMARY KEY,
  url_id INT,
  status_code INT,
  h1 VARCHAR(255),
  title VARCHAR(255),
  description TEXT,
  created_at DATE
);
