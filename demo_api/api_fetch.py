import json
from datetime import timedelta

import backoff
from decouple import config
from httpx import Client, HTTPError

from demo_api.redis_connect import redis_client


def _fatal_error(error):
    """Return True if the error is not retryable"""
    return 400 <= error.response.status_code < 500


@backoff.on_exception(
    backoff.expo,
    HTTPError,
    max_time=config("MAX_TIME", default=3),
    max_tries=config("MAX_TIME", default=5),
    factor=config("BACKOFF_FACTOR", default=5),
    giveup=_fatal_error,
)
def fetch_currency_pair(subdirectory: str, currency_pair: str):
    "Make API requests"
    with Client(base_url="https://www.bitstamp.net/api/v2") as client:
        pair_resp = client.get(f"{subdirectory}/{currency_pair}")
        if pair_resp.status_code == 200:
            resp_content = pair_resp.json()
    return resp_content


def flush_cache():
    redis_client.flushdb()


def transform_currency_pair(currency_pair_data):
    "Extract needed keys from returned json response into defined dict"
    currency_pair_dict = {}
    if currency_pair_data:
        if (
            currency_pair_data["bids"][0][0] < currency_pair_data["asks"][0][0]
        ):  # assumming bids and asks will always be available
            currency_pair_dict["timestamp"] = currency_pair_data["timestamp"]
            currency_pair_dict["price"] = currency_pair_data["asks"][0][0]
            currency_pair_dict["quantity"] = currency_pair_data["asks"][0][1]
    return currency_pair_dict


def set_currency_pair_to_cache(key: str, value: dict):
    "Set currency pair data to cache with specified key"
    if value:
        expire_cache = config("EXPIRE_REDIS_CACHE", default=180, cast=int)
        data = json.dumps(value)
        state = redis_client.setex(
            key, timedelta(seconds=expire_cache), value=data
        )
        return state


def get_currency_pair_from_cache(key: str):
    "Retrieve currency pair data from cache with specified key"
    currency_pair = redis_client.get(key)
    return currency_pair
