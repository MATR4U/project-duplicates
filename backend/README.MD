### MATR BACKEND

# ENV
docker login

# CONTAINER BUILD
docker build -t doc1024/matr:backend-latest -f Dockerfile_backend .
docker push doc1024/matr:backend-latest

# CONTAINER RUN
docker pull doc1024/matr:backend-latest
docker run --name matr-backend -d doc1024/matr:backend-latest

# CONTAINER STOP/KILL
docker stop matr-backend
docker remove matr-backend

# CONTAINER CONNECT
docker ps -all
docker exec -it matr-backend /bin/bash

# APP INSTALL
pip install -r requirements.txt

# RUN BACKEND
python main.py ./test/data/DataSource ./test/data/DataTarget

# RUN BACKEND-API
python -m uvicorn app_api:app --reload