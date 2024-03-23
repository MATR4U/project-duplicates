CREATE TABLE health_check (
    service_id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    status VARCHAR(255) NOT NULL
);


INSERT INTO health_check (service_name, timestamp, status)
VALUES ('db_service', '2023-12-21 10:00:00', 'OK');