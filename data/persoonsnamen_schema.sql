DROP TABLE IF EXISTS persons CASCADE;
CREATE TABLE persons (
    _id SERIAL PRIMARY KEY,
    name TEXT,
    infix TEXT,
    givenname TEXT,
    life_hint_begin TEXT,
    life_hint_end TEXT
);

DROP TABLE IF EXISTS records CASCADE;
CREATE TABLE records (
    _id SERIAL PRIMARY KEY,
    id TEXT,
    person_id integer,
    database_id integer
);

DROP TABLE IF EXISTS links CASCADE;
CREATE TABLE links (
    _id SERIAL PRIMARY KEY,
    href TEXT
);

DROP TABLE IF EXISTS record_links CASCADE;
CREATE TABLE record_links (
    record_id integer,
    link_id integer
);

DROP TABLE IF EXISTS database CASCADE;
CREATE TABLE database (
    _id SERIAL PRIMARY KEY,
    name TEXT
);

ALTER TABLE records ADD FOREIGN KEY (person_id) REFERENCES persons ON DELETE CASCADE;
ALTER TABLE records ADD FOREIGN KEY (database_id) REFERENCES database ON DELETE CASCADE;
ALTER TABLE record_links ADD FOREIGN KEY (record_id) REFERENCES records ON DELETE CASCADE;
ALTER TABLE record_links ADD FOREIGN KEY (link_id) REFERENCES links ON DELETE CASCADE;

