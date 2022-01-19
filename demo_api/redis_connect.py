import sys

import redis
from decouple import config


def redis_conn():
    try:
        client = redis.Redis(
            host=config("REDIS_CACHE_HOST", default="localhost"),
            port=config("REDIS_CACHE_PORT", default=6380, cast=int),
            password=None,
            socket_timeout=5,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        sys.exit(1)


redis_client = redis_conn()
