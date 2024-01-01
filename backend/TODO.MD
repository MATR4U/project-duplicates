source: https://chat.openai.com/c/42d44a57-7fa6-4222-8e5c-9125ec05177a

- 2024-01-01 04:25:24,792 - ERROR - Failed to initialize the database: type object 'Config' has no attribute '_load_config'
  - File "C:\Users\doc1024\Documents\Venture\09_Matr\GitHub\project-duplicates\backend\src\database\Postgresql.py", line 9, in __init__
    super().__init__(config)
        TypeError: object.__init__() takes exactly one argument (the instance to initialize)

- Implement Config File Handler
- Implement Service Class (independence of db instance from the App class and use in the endpoints)
- Implement Circuit Braker (https://pypi.org/project/pybreaker/)
- Implement GraphAPI
- Implement Thread safety in common classes
- Implement Service Broker (MQTT)
- Implement Service Discovery
- Implement Dynamic Service Binding (...)