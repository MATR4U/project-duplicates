# PYTHON INSTALL
python -m venv .venv
(mac: source) .\.venv\Scripts\activate 
python -m pip install --upgrade pip

# DOCKER CREATE NETWORK
docker network create my_network

# BUILD DATABASE CONTAINER IMAGE
docker login
docker build -t "doc1024/matr-db-postgres:latest" -f Dockerfile .
docker push "doc1024/matr-db-postgres:latest"

# RUN CONTAINER
docker run --network my_network --publish 5432:5432 --name matr-db-postgres -d "doc1024/matr-db-postgres:latest"
docker ps -all

# STOP DATABASE AND KILL CONTAINER
docker kill matr-db-postgres
docker remove -f matr-db-postgres

# CONNECT ON DATABASE CONTAINER
docker exec -it matr-db-postgres /bin/bash
<!-- psql -h 127.0.0.1 -U myuser -d mydb -p 5432
REM docker exec -it 372a0f0b6fae psql -U postgres -c "SELECT pg_reload_conf();"
-->
