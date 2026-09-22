"""Focused tests for CalculatorService.execute_batch."""

import pytest

from calc_core import (
    CalculatorError,
    CalculatorService,
    InvalidRequestError,
)


# --- error type ------------------------------------------------------------


def test_invalid_request_error_is_calculator_error():
    assert issubclass(InvalidRequestError, CalculatorError)


# --- happy path ------------------------------------------------------------


def test_execute_batch_preserves_order_and_values():
    service = CalculatorService()
    requests = [
        {"operation": "add", "args": [2, 3]},
        {"operation": "subtract", "args": [5, 3]},
        {"operation": "multiply", "args": [4, 3]},
        {"operation": "divide", "args": [7, 2]},
        {"operation": "clamp", "args": [42, 0, 10]},
    ]
    results = service.execute_batch(requests)
    assert [r["ok"] for r in results] == [True] * 5
    assert [r["value"] for r in results] == [5, 2, 12, 3.5, 10]


def test_execute_batch_accepts_tuple_args():
    service = CalculatorService()
    results = service.execute_batch([{"operation": "add", "args": (1, 2)}])
    assert results == [{"ok": True, "value": 3}]


def test_execute_batch_accepts_any_iterable_and_returns_one_per_item():
    service = CalculatorService()
    results = service.execute_batch(
        iter([{"operation": "add", "args": [1, 1]}, {"operation": "add", "args": [2, 2]}])
    )
    assert results == [{"ok": True, "value": 2}, {"ok": True, "value": 4}]


def test_execute_batch_empty_input_returns_empty_list():
    service = CalculatorService()
    assert service.execute_batch([]) == []


# --- per-item failures do not abort ---------------------------------------


def test_execute_batch_unknown_operation_is_captured_per_item():
    service = CalculatorService()
    results = service.execute_batch(
        [
            {"operation": "nope", "args": [1, 2]},
            {"operation": "add", "args": [1, 2]},
        ]
    )
    assert results[0]["ok"] is False
    assert results[0]["error"]["type"] == "UnknownOperationError"
    assert results[1] == {"ok": True, "value": 3}


def test_execute_batch_divide_by_zero_is_captured_per_item():
    service = CalculatorService()
    results = service.execute_batch(
        [
            {"operation": "divide", "args": [5, 0]},
            {"operation": "multiply", "args": [3, 3]},
        ]
    )
    assert results[0]["ok"] is False
    assert results[0]["error"]["type"] == "ZeroDivisionError"
    assert "message" in results[0]["error"]
    assert results[1] == {"ok": True, "value": 9}


def test_execute_batch_failure_does_not_abort_later_requests():
    service = CalculatorService()
    results = service.execute_batch(
        [
            {"operation": "add", "args": [1, 1]},
            {"operation": "divide", "args": [1, 0]},
            {"operation": "unknown", "args": []},
            {"operation": "add", "args": [5, 5]},
        ]
    )
    assert [r["ok"] for r in results] == [True, False, False, True]
    assert results[3] == {"ok": True, "value": 10}


# --- validation ------------------------------------------------------------


@pytest.mark.parametrize(
    "batch_request",
    [
        "not-a-mapping",
        42,
        None,
        ["operation", "args"],
        {},
        {"operation": "add"},
        {"args": [1, 2]},
        {"operation": "", "args": [1, 2]},
        {"operation": 123, "args": [1, 2]},
        {"operation": "add", "args": "12"},
        {"operation": "add", "args": 12},
    ],
)
def test_execute_batch_invalid_request_is_captured_per_item(batch_request):
    service = CalculatorService()
    results = service.execute_batch([batch_request, {"operation": "add", "args": [1, 1]}])
    assert results[0]["ok"] is False
    assert results[0]["error"]["type"] == "InvalidRequestError"
    assert isinstance(results[0]["error"]["message"], str)
    assert results[1] == {"ok": True, "value": 2}