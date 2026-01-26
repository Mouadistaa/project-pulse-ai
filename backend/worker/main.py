import os
import redis
from rq import Worker, Queue, Connection
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

listen = ['default']

def main():
    redis_url = settings.REDIS_URL
    conn = redis.from_url(redis_url)

    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()

if __name__ == '__main__':
    main()
