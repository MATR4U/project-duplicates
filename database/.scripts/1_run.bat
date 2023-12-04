REM docker run -d --name project-duplicates-postgres -e POSTGRES_DB=mydb -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -p 5432:5432 -v ~/postgres-data:/var/lib/postgresql/data postgres:latest
REM docker run -it --rm --link project-duplicates-postgres:postgres postgres:latest psql -h postgres -U myuser -d mydb
REM psql -h 127.0.0.1 -U myuser -d mydb -p 5432

REM docker run -d --name project-duplicates-postgres project-duplicates-postgres
docker run -d --name project-duplicates-postgres project-duplicates-postgres