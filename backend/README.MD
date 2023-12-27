### MATR BACKEND
ecommerce-backend/
│
├── app/                       # Application Module
│   ├── models/                # SQLAlchemy Models
│   │   ├── user.py            # User Model
│   │   ├── product.py         # Product Model
│   │   ├── order.py           # Order Model
│   │   └── ...
│   │
│   ├── schemas/               # Pydantic Schemas (DTOs)
│   │   ├── user_schema.py     # User Schema
│   │   ├── product_schema.py  # Product Schema
│   │   ├── order_schema.py    # Order Schema
│   │   └── ...
│   │
│   ├── routes/                # API Routes
│   │   ├── user_routes.py     # Routes for User Operations
│   │   ├── product_routes.py  # Routes for Product Operations
│   │   ├── order_routes.py    # Routes for Order Operations
│   │   └── ...
│   │
│   ├── services/              # Business Logic
│   │   ├── user_service.py    # User Service
│   │   ├── product_service.py # Product Service
│   │   ├── order_service.py   # Order Service
│   │   └── ...
│   │
│   ├── config.py              # Configuration Settings
│   ├── database.py            # Database Connection Setup
│   └── main.py                # FastAPI Application Instance
│
├── tests/                     # Test Suite
│   ├── test_user.py           # Tests for User Operations
│   ├── test_product.py        # Tests for Product Operations
│   └── ...
│
├── alembic.ini                # Alembic Configuration
├── Dockerfile                 # Dockerfile for Backend Service
├── requirements.txt           # Python Dependencies
└── .env                       # Environment Variables

# DOCKER CREATE NETWORK
docker network create my_network

# CONTAINER BUILD IMAGE FOR DOCKERHUB
docker build -t "doc1024/matr:backend-latest" -f Dockerfile .
docker push "doc1024/matr:backend-latest"

# CONTAINER RUN
docker pull "doc1024/matr:backend-latest"
docker run --network my_network --publish 8000:8000 --publish 80:80 --name matr-backend -d "doc1024/matr:backend-latest"

# CONTAINER STOP/KILL
docker stop matr-backend
docker remove -f matr-backend

# CONTAINER CONNECT
docker ps -all
docker exec -it matr-backend /bin/bash

# APP INSTALL
pip install -r requirements.txt

# RUN BACKEND
python main.py ./test/data/DataSource ./test/data/DataTarget

# RUN BACKEND-API
python -m uvicorn app_api:app --reload