CREATE DATABASE ${DB_NAME};

CREATE USER ${DB_REPL_USER} REPLICATION LOGIN PASSWORD '${DB_REPL_PASS}';
SELECT pg_create_physical_replication_slot('replication_slot');

\c ${DB_NAME}

CREATE TABLE hba ( lines text );
COPY hba FROM '/var/lib/postgresql/data/pg_hba.conf';
INSERT INTO hba (lines) VALUES ('host all all 0.0.0.0/0 scram-sha-256');
INSERT INTO hba (lines) VALUES ('host replication repl_user 0.0.0.0/0 scram-sha-256');
COPY hba TO '/var/lib/postgresql/data/pg_hba.conf';
SELECT pg_reload_conf();

CREATE TABLE emails (
	id SERIAL PRIMARY KEY,
	email VARCHAR(255)
);
CREATE TABLE phone_num (
	id SERIAL PRIMARY KEY,
	numbers VARCHAR(255)
);
