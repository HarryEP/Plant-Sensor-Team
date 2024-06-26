DROP DATABASE IF EXISTS plant_monitor;

CREATE DATABASE plant_monitor;

\c plant_monitor;

CREATE TYPE SUNLIGHT_TYPES AS ENUM ('full_sun', 'partial_sun', 'full_shade', 'Null');

CREATE TABLE botanist(
    id SMALLINT GENERATED ALWAYS AS IDENTITY,
    botanist_name VARCHAR NOT NULL UNIQUE,
    email VARCHAR NOT NULL,
    phone VARCHAR NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE plant (
    id SMALLINT GENERATED ALWAYS AS IDENTITY,
    plant_id SMALLINT NOT NULL UNIQUE,
    general_name VARCHAR NOT NULL,
    scientific_name VARCHAR,
    cycle VARCHAR,
    botanist_id SMALLINT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (botanist_id) REFERENCES botanist (id)
);

CREATE TABLE recording (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    recorded TIMESTAMPTZ NOT NULL,
    plant_id SMALLINT NOT NULL,
    temperature FLOAT NOT NULL,
    soil_moisture FLOAT NOT NULL,
    watered TIMESTAMPTZ NOT NULL,
    sunlight SUNLIGHT_TYPES,
    PRIMARY KEY (id),
    FOREIGN KEY (plant_id) REFERENCES plant (id)
);