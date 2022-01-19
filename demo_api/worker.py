from celery import Celery
from decouple import config

from demo_api.api_fetch import (fetch_currency_pair,
                                set_currency_pair_to_cache,
                                transform_currency_pair)

# add CELERY_BROKER_URL and CELERY_BROKER_BACKEND to .env with needed value. The default is used here
celery_broker_url = config(
    "CELERY_BROKER_URL", default="redis://localhost:6379"
)  # could be a rabbitmq url
celery_backend_url = config(
    "CELERY_BROKER_BACKEND", default="redis://localhost:6379"
)

celery = Celery("worker", broker=celery_broker_url, backend=celery_backend_url)


@celery.task(name="set_currency_pair", max_retries=5)
def set_currency_pair():
    "Task to run on a schedule time using celery beats when server starts"
    currency_pair_data = fetch_currency_pair("order_book", "btceur")
    if currency_pair_data:
        currency_pair_dict = transform_currency_pair(currency_pair_data)
        set_currency_pair_to_cache("currency_pair", currency_pair_dict)


celery.conf.beat_schedule = {
    "set-currency-pair-task": {
        "task": "set_currency_pair",
        "schedule": config("CELERY_SCHEDULE", default=300.0, cast=float),
    }
}

celery.conf.timezone = "UTC"
