CREATE TABLE health_check (
    service_id PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    status VARCHAR(255) NOT NULL
);

INSERT INTO health_check (timestamp, status)
VALUES (1, "db_service", '2023-12-21 10:00:00', 'OK');