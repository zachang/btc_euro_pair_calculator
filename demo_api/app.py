import json
from datetime import datetime
from decimal import Decimal
from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

from demo_api.tasks import get_currency_pair_from_cache

app = FastAPI(title="Bitstack Demo API")

class ItemIn(BaseModel):
    amount: int

class ItemOut(BaseModel):
    timestamp: str = ""
    price: Union[float, str] = ""
    quantity: str = ""


@app.on_event("startup")
async def startup_event():
    "call background task to populate cash on or before celerybeat starts schedule"
    pass


@app.get("/")
async def root_get():
    return {"description": "welcome"}


@app.post("/", response_model=ItemOut)
async def root_get(item: ItemIn):
    "Resource for currency pair price"
    currency_pair_from_cache = get_currency_pair_from_cache("currency_pair")
    if item and item.amount > 0 and currency_pair_from_cache:
        print("currency_pair_from_cache",currency_pair_from_cache)
        currency_pair = json.loads(currency_pair_from_cache)
        currency_pair['price'] = Decimal(currency_pair["price"]) * item.amount
        currency_pair['timestamp'] = str(datetime.fromtimestamp(int(currency_pair['timestamp'])))
        return currency_pair
    return item
