docker exec -it project-duplicates-postgres /bin/bash
REM psql -h 127.0.0.1 -U myuser -d mydb -p 5432
REM docker exec -it 372a0f0b6fae psql -U postgres -c "SELECT pg_reload_conf();"