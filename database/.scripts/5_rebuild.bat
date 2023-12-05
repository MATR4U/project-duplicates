call 2_stop.bat
call 0_build.bat
call 1_run.bat
docker ps -all
docker exec -it project-duplicates-postgres /bin/bash