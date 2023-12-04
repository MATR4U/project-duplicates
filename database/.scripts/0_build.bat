docker build -t project-duplicates-postgres ../
REM docker run -d --name project-duplicates-postgres project-duplicates-postgres
REM docker run -it --rm --link project-duplicates-postgres:postgres-container postgres:latest data /duplicates.db
REM psql -h localhost -U myuser -d mydb
REM docker run -d --name project-duplicates-postgres -e POSTGRES_DB=mydb -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -v ~/postgres-data:/var/lib/postgresql/data postgres:latest