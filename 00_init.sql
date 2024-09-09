DROP TABLE IF EXISTS email;
DROP TABLE IF EXISTS phone;

create user replicator with replication encrypted password 'replicator_password';
select pg_create_physical_replication_slot('replication_slot');

CREATE TABLE email (id SERIAL PRIMARY KEY, email VARCHAR(40) NOT NULL);
CREATE TABLE phone (id SERIAL PRIMARY KEY, phone VARCHAR(20) NOT NULL);
