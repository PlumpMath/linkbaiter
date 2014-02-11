CREATE DATABASE IF NOT EXISTS linkbaiter;

USE linkbaiter;
DROP TABLE IF EXISTS website;
CREATE TABLE website (
  guid CHAR(32) PRIMARY KEY,
  name TEXT,
  description TEXT,
  url TEXT,
  processed boolean not null default 0,
  updated DATETIME,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) DEFAULT CHARSET=utf8;

