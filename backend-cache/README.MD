	
docker run --name matr-backend-cache -d redis redis-server --save 60 1 --loglevel warning
docker network create my-network
​​docker run -it --network my-network --rm redis redis-cli -h matr-backend-cache
