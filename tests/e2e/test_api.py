import uuid

import pytest
import requests

from src.allocation import config


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


@pytest.mark.usefixtures("restart_api")
def test_api_returns_allocation(add_stock):
    sku, other_sku = random_sku(), random_sku("other")
    early_batch = random_batchref("1")
    later_batch = random_batchref("2")
    other_batch = random_batchref("3")

    add_stock(
        [
            (later_batch, sku, 100, "2011-01-02"),
            (early_batch, sku, 100, "2011-01-02"),
            (other_batch, other_sku, 100, "2011-01-02"),
        ]
    )

    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == early_batch
