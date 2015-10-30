CREATE TABLE auth
(
  login TEXT,
  pass TEXT NOT NULL,
  CONSTRAINT authentication PRIMARY KEY (login)
);
