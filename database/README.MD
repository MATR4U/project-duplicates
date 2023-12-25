
# BUILD DATABASE CONTAINER
docker build -t "matr/db-postgres:latest" -f Dockerfile .

<!--
docker run -d --name project-duplicates-postgres project-duplicates-postgres
docker run -it --rm --link project-duplicates-postgres:postgres-container postgres:latest data /duplicates.db
psql -h localhost -U myuser -d mydb
docker run -d --name project-duplicates-postgres -e POSTGRES_DB=mydb -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -v ~/postgres-data:/var/lib/postgresql/data postgres:latest
 -->

# RUN CONTAINER
docker ps -all
docker run -d --name matr-db-postgres matr-db-postgres
docker ps -all

<!--
docker run -d --name project-duplicates-postgres -e POSTGRES_DB=mydb -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -p 5432:5432 -v ~/postgres-data:/var/lib/postgresql/data postgres:latest
run -it --rm --link project-duplicates-postgres:postgres postgres:latest psql -h postgres -U myuser -d mydb
psql -h 127.0.0.1 -U myuser -d mydb -p 5432

docker run -d --name project-duplicates-postgres project-duplicates-postgres
docker run -it -v /path/on/host:/data sqlite-container

exec -it matr-db-postgres /bin/bash
--net=host
-p 127.0.0.1:5432:5432
-v ..\docker-entrypoint-initdb.d\:/postgres postgres:latest psql -h postgres -U myuser -d mydb 
-f ../Dockerfile
-p 5432:5432
docker run -d 
--name matr-db-postgres matr-db-postgres

-->

# STOP DATABASE AND KILL CONTAINER
docker kill matr-db-postgres
docker remove matr-db-postgres

# CONNECT ON DATABASE CONTAINER
docker exec -it matr-db-postgres /bin/bash
<!-- psql -h 127.0.0.1 -U myuser -d mydb -p 5432
REM docker exec -it 372a0f0b6fae psql -U postgres -c "SELECT pg_reload_conf();"
-->
