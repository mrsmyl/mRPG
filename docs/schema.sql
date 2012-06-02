CREATE TABLE users
  (
     username          TEXT PRIMARY KEY,
     char_name         TEXT,
     password          TEXT,
     char_class        TEXT,
     hostname          TEXT,
     level             NUMERIC,
     ttl               NUMERIC,
     online            INTEGER,
     path_endpointx    TEXT,
     path_endpointy    TEXT,
     cordx             TEXT,
     cordy             TEXT,
     path_ttl          NUMERIC,
     registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
     last_login        TEXT DEFAULT CURRENT_TIMESTAMP,
     admin             BOOL
  )

CREATE TABLE events
  (
     id             INTEGER PRIMARY KEY,
     event_name     TEXT,
     event_type     TEXT,
     event_modifier NUMERIC
  )

CREATE TABLE movement_history
  (
     id            INTEGER PRIMARY KEY,
     char_name     TEXT,
     x             NUMERIC,
     y             NUMERIC,
     movement_date TEXT DEFAULT CURRENT_TIMESTAMP
  )

CREATE TABLE mrpg_meta
  (
     name  TEXT PRIMARY KEY,
     value TEXT
  )

CREATE TABLE item_type
  (
     id               INTEGER PRIMARY KEY,
     item_type        TEXT,
     item_description TEXT
  )

CREATE TABLE items
  (
     id        INTEGER PRIMARY KEY,
     item_type INTEGER,
     item_name TEXT,
     modifier  NUMERIC,
     special   BOOL
  )

CREATE TABLE items_user
  (
     id        INTEGER PRIMARY KEY,
     username  TEXT,
     item_id   INTEGER,
     item_type INTEGER,
     level     INTEGER
  )