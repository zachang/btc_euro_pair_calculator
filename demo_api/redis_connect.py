import redis
import sys


def redis_conn():
    try:
        client = redis.Redis(
            host="localhost",
            port=6380,
            password=None,
            socket_timeout=5,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        print("AuthenticationError")
        sys.exit(1)



redis_client = redis_conn()
