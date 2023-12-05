cd ..

REM RUN BACKEND
python main.py ./test/data/DataSource ./test/data/DataTarget

REM RUN BACKEND-API
python -m uvicorn app_api:app --reload

