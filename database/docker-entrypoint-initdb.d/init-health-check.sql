CREATE TABLE health_check (
    service_id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    status VARCHAR(255) NOT NULL
);

INSERT INTO health_check (service_id, service_name, timestamp, status)
VALUES (1, 'db_service', CURRENT_TIMESTAMP, 'OK')
ON CONFLICT (service_id)
DO UPDATE SET
    service_name = EXCLUDED.service_name,
    timestamp = CURRENT_TIMESTAMP,
    status = EXCLUDED.status;