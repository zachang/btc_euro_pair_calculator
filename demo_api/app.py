import json
from datetime import datetime
from decimal import Decimal
from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

from demo_api.api_fetch import get_currency_pair_from_cache
from demo_api.worker import set_currency_pair

app = FastAPI(title="Bitstack Demo API")


class ItemIn(BaseModel):
    amount: int


class ItemOut(BaseModel):
    timestamp: str = ""
    price: Union[float, str] = ""
    quantity: str = ""


@app.on_event("startup")
def startup_event():
    "call function to populate cash on or before celerybeat starts schedule"
    set_currency_pair() # might be a better way to do this


@app.get("/")
async def root_get():
    return {"description": "welcome to your favourite btc/eur calculator"}


@app.post("/btceur", response_model=ItemOut)
async def btc_eur_price(item: ItemIn):
    "Resource for currency pair price data"
    currency_pair_from_cache = get_currency_pair_from_cache("currency_pair")
    if item and item.amount > 0 and currency_pair_from_cache:
        currency_pair = json.loads(currency_pair_from_cache)
        currency_pair["price"] = Decimal(currency_pair["price"]) * item.amount
        currency_pair["timestamp"] = str(
            datetime.fromtimestamp(int(currency_pair["timestamp"]))
        )
        return currency_pair
    return item
