import asyncio
import json
from datetime import datetime, timedelta

import backoff
from celery import Celery
from httpx import AsyncClient, HTTPError

from demo_api.redis_connect import redis_client


app = Celery("worker", broker="redis://localhost:6379", backend="redis://localhost:6379")

def _fatal_error(error):
    """Return True if the error is not retryable"""
    return 400 <= error.response.status_code < 500

@backoff.on_exception(backoff.expo,
                      HTTPError,
                      max_time=1,
                      max_tries=5,
                      factor=5,
                      giveup=_fatal_error)
async def fetch_currency_pair(subdirectory: str, currency_pair: str):
    "Make API requests "
    async with AsyncClient(base_url="https://www.bitstamp.net/api/v2") as client:
        pair_resp = await client.get(f"{subdirectory}/{currency_pair}")
        resp_content = pair_resp.json()
    return resp_content

def flush_cache():
    redis_client.flushdb()

def transform_currency_pair(currency_pair_data):
    "Extract needed keys from returned json response into defined dict"
    currency_pair_dict = {}
    if currency_pair_data:
        if currency_pair_data["bids"][0][0] < currency_pair_data["asks"][0][0]: # assumming bids and asks will always be available
            currency_pair_dict["timestamp"] = currency_pair_data["timestamp"]
            currency_pair_dict["price"] = currency_pair_data["asks"][0][0]
            currency_pair_dict["quantity"] = currency_pair_data["asks"][0][1]
    return currency_pair_dict


def set_currency_pair_to_cache(key: str, value: dict):
    "Set currency pair data to cache with specified key"
    if value:
        data = json.dumps(value)
        state = redis_client.setex(key, timedelta(seconds=3600), value=data)
        return state


def get_currency_pair_from_cache(key: str):
    "Retrieve currency pair data from cache with specified key"
    val = redis_client.get(key)
    return val

# @app.task(name="set_currency_pair")
async def set_currency_pair():
    "Task to run on a schedule time using celery beats when server starts"
    currency_pair_data = await fetch_currency_pair("order_book", "btceur")
    currency_pair_dict = transform_currency_pair(currency_pair_data)
    set_currency_pair_to_cache("currency_pair", currency_pair_dict)
    
# asyncio.run(set_currency_pair()) # manual test to populate cache before scheduling every 10mins to run on celery beat
