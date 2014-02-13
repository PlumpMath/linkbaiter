CREATE DATABASE IF NOT EXISTS linkbaiter;

USE linkbaiter;

CREATE TABLE IF NOT EXISTS website (
  guid CHAR(32) PRIMARY KEY,
  name TEXT,
  description TEXT,
  url TEXT,
  processed boolean not null default 0,
  updated DATETIME,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) DEFAULT CHARSET=utf8;

