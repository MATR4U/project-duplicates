import redis
import os

class RedisConnector:
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = os.getenv('REDIS_PORT', 6379)
        self.redis_password = os.getenv('REDIS_PASSWORD', None)
        self.client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port, 
            password=self.redis_password,
            decode_responses=True
        )

    def set(self, key, value):
        self.client.set(key, value)

    def get(self, key):
        return self.client.get(key)