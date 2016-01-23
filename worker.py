import os

import redis
from rq import Worker, Queue, Connection

listen = ['default']

redis_url = os.environ["REDIS_URL"]
redis_pass = os.environ["REDIS_PASS"]

conn = redis.Redis(url=redis_url, passwprd=redis_pass)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
