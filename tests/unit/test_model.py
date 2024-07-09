from datetime import date, timedelta

import pytest

from src.allocation.domain import Batch, OrderLine, OutOfStock, allocate

TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)
NEXT_YEAR = TODAY + timedelta(days=365)


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch1", "SMALL-TABLE", 20, TODAY)
    line = OrderLine("order1", "SMALL-TABLE", 4)
    batch.allocate(line)

    assert batch.available_quantity == 16


def make_batch_and_line(
    sku: str, batch_quantity: int, line_quantity: int
) -> tuple[Batch, OrderLine]:
    return (
        Batch("batch1", sku, batch_quantity, eta=TODAY),
        OrderLine("order1", sku, line_quantity),
    )


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 10, 1)
    assert large_batch.can_allocate(small_line)


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 5, 5)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 1, 10)
    assert not small_batch.can_allocate(large_line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch1", "UNCOMFORTABLE-CHAIR", 5, eta=TODAY)
    line_with_different_sku = OrderLine("order1", "EXPENSIVE-TOASTER", 5)
    assert not batch.can_allocate(line_with_different_sku)


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 10, 1)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 10


def test_allocation_is_idempotent():
    large_batch, small_line = make_batch_and_line("ANGULAR-DESK", 10, 1)
    large_batch.allocate(small_line)
    large_batch.allocate(small_line)
    assert large_batch.available_quantity == 9


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 1000, eta=TOMORROW)
    line = OrderLine("orderline", "RETRO-CLOCK", 2)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 98
    assert shipment_batch.available_quantity == 1000


def test_prefers_earlier_batches():
    earliest = Batch("in-stock-batch", "MINIMALIST-SPOON", 100, eta=TODAY)
    medium = Batch("shipment-batch", "MINIMALIST-SPOON", 100, eta=TOMORROW)
    latest = Batch("shipment-batch", "MINIMALIST-SPOON", 100, eta=NEXT_YEAR)
    line = OrderLine("orderline", "MINIMALIST-SPOON", 2)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 98
    assert latest.available_quantity == 100
    assert medium.available_quantity == 100


def test_return_allocated_batch():
    in_stock_batch = Batch("in-stock-batch", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "HIGHBROW-POSTER", 1000, eta=TOMORROW)
    line = OrderLine("orderline", "HIGHBROW-POSTER", 2)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch", "SMALL-FORK", 10, eta=None)
    first_line = OrderLine("line", "SMALL-FORK", 7)
    second_line = OrderLine("line", "SMALL-FORK", 8)

    allocate(first_line, [batch])

    with pytest.raises(OutOfStock, match="SMALL-FORK"):
        allocate(second_line, [batch])
