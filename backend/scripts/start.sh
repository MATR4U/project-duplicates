#!/usr/bin/env bash

#LOGIN DOCKER
docker login

#DOCKER CREATE NETWORK
docker network create my_network

#CONTAINER BUILD IMAGE FOR DOCKERHUB
docker build -t "doc1024/matr:backend-latest" -f ../Dockerfile ../.
docker push "doc1024/matr:backend-latest"

#STOP AND REMOVE CONTAINER
docker stop matr-backend
docker remove -f matr-backend

#CONTAINER RUN
#docker pull "doc1024/matr:backend-latest"
docker run --network my_network --publish 8000:8000 --publish 80:80 --name matr-backend -d "doc1024/matr:backend-latest"

#CONTAINER CONNECT
#docker ps -all docker exec -it matr-backend /bin/bash

#APP INSTALL
#pip install -r requirements.txt

#RUN BACKEND
#python main.py ./test/data/DataSource ./test/data/DataTarget

#RUN BACKEND-API
#python -m uvicorn app_api:app --reload