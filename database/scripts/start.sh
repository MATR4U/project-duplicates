#!/usr/bin/env bash

#LOGIN DOCKER
docker login

#DOCKER CREATE NETWORK
docker network create my_network

#BUILD DATABASE CONTAINER IMAGE
docker build --tag "doc1024/matr-db-postgres:latest" --file Dockerfile .

# PUSH THE IMAGE
docker push "doc1024/matr-db-postgres:latest"

#RUN CONTAINER
docker run --network my_network --publish 5432:5432 --name matr-db-postgres -d "doc1024/matr-db-postgres:latest"

# SHOW ALL CONTAINER
docker describe
docker ps -all

#CONNECT ON DATABASE CONTAINER
docker exec -it matr-db-postgres /bin/bash

#STOP DATABASE AND KILL CONTAINER
#docker kill matr-db-postgres
#docker remove -f matr-db-postgres

