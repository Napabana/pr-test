"""Focused tests for the runtime OperationPolicy (Task C)."""

import dataclasses

import pytest

from calc_core import (
    BatchSizeExceededError,
    CalculatorError,
    CalculatorService,
    InvalidRequestError,
    OperationDisabledError,
    OperationPolicy,
)


# --- error hierarchy -------------------------------------------------------


def test_new_errors_are_calculator_errors():
    assert issubclass(OperationDisabledError, CalculatorError)
    assert issubclass(BatchSizeExceededError, CalculatorError)


def test_operation_disabled_error_carries_name():
    err = OperationDisabledError("divide")
    assert err.name == "divide"
    assert "divide" in str(err)


# --- policy value object ---------------------------------------------------


def test_policy_defaults():
    policy = OperationPolicy()
    assert policy.enabled_operations is None
    assert policy.max_batch_size is None
    assert policy.strict_validation is False


def test_policy_is_immutable():
    policy = OperationPolicy()
    with pytest.raises(dataclasses.FrozenInstanceError):
        policy.max_batch_size = 3


def test_policy_is_operation_enabled():
    assert OperationPolicy().is_operation_enabled("add") is True
    restricted = OperationPolicy(enabled_operations=frozenset({"add"}))
    assert restricted.is_operation_enabled("add") is True
    assert restricted.is_operation_enabled("divide") is False


def test_policy_check_batch_size_boundary():
    assert OperationPolicy().check_batch_size(10 ** 6) is True
    limited = OperationPolicy(max_batch_size=3)
    assert limited.check_batch_size(0) is True
    assert limited.check_batch_size(3) is True
    assert limited.check_batch_size(4) is False


def test_policy_is_instance_state_not_module_global():
    first = CalculatorService()
    second = CalculatorService(policy=OperationPolicy(enabled_operations=frozenset()))
    assert isinstance(first.policy, OperationPolicy)
    assert first.policy.enabled_operations is None
    assert second.policy.enabled_operations == frozenset()
    # Mutating one instance's registry/policy view does not touch the other.
    assert first.policy is not second.policy


# --- default compatibility -------------------------------------------------


def test_default_policy_preserves_execute():
    service = CalculatorService()
    assert service.execute("add", 2, 3) == 5
    assert service.execute("divide", 7, 2) == 3.5


def test_default_policy_preserves_batch_shape_and_order():
    service = CalculatorService()
    results = service.execute_batch(
        [
            {"operation": "add", "args": [2, 3]},
            {"operation": "nope", "args": []},
            {"operation": "multiply", "args": [4, 3]},
        ]
    )
    assert [r["ok"] for r in results] == [True, False, True]
    assert results[0] == {"ok": True, "value": 5}
    assert results[1]["error"]["type"] == "UnknownOperationError"
    assert results[2] == {"ok": True, "value": 12}


def test_default_policy_ignores_extra_keys():
    service = CalculatorService()
    results = service.execute_batch(
        [{"operation": "add", "args": [1, 2], "extra": "ignored"}]
    )
    assert results == [{"ok": True, "value": 3}]


# --- disabled operations ---------------------------------------------------


def test_execute_raises_when_operation_disabled():
    service = CalculatorService(
        policy=OperationPolicy(enabled_operations=frozenset({"add"}))
    )
    assert service.execute("add", 1, 2) == 3
    with pytest.raises(OperationDisabledError):
        service.execute("divide", 6, 2)


def test_execute_batch_captures_disabled_operation_per_item():
    service = CalculatorService(
        policy=OperationPolicy(enabled_operations=frozenset({"add"}))
    )
    results = service.execute_batch(
        [
            {"operation": "divide", "args": [6, 2]},
            {"operation": "add", "args": [1, 2]},
        ]
    )
    assert results[0]["ok"] is False
    assert results[0]["error"]["type"] == "OperationDisabledError"
    assert results[1] == {"ok": True, "value": 3}


def test_unknown_operation_still_reported_when_restricted():
    service = CalculatorService(
        policy=OperationPolicy(enabled_operations=frozenset({"add"}))
    )
    results = service.execute_batch([{"operation": "nope", "args": []}])
    assert results[0]["ok"] is False
    assert results[0]["error"]["type"] == "UnknownOperationError"


# --- max_batch_size --------------------------------------------------------


def test_batch_size_equal_to_limit_is_allowed():
    service = CalculatorService(policy=OperationPolicy(max_batch_size=2))
    results = service.execute_batch(
        [
            {"operation": "add", "args": [1, 1]},
            {"operation": "add", "args": [2, 2]},
        ]
    )
    assert [r["value"] for r in results] == [2, 4]


def test_batch_size_above_limit_raises_deterministically():
    service = CalculatorService(policy=OperationPolicy(max_batch_size=2))
    requests = [
        {"operation": "add", "args": [1, 1]},
        {"operation": "add", "args": [2, 2]},
        {"operation": "add", "args": [3, 3]},
    ]
    with pytest.raises(BatchSizeExceededError) as exc_info:
        service.execute_batch(requests)
    assert exc_info.value.size == 3
    assert exc_info.value.max_batch_size == 2
    # Deterministic: raising again yields the same outcome.
    with pytest.raises(BatchSizeExceededError):
        service.execute_batch(requests)


def test_batch_size_accepts_generators():
    service = CalculatorService(policy=OperationPolicy(max_batch_size=1))
    with pytest.raises(BatchSizeExceededError):
        service.execute_batch(
            {"operation": "add", "args": [i, i]} for i in range(3)
        )


def test_empty_batch_respects_limit():
    service = CalculatorService(policy=OperationPolicy(max_batch_size=0))
    assert service.execute_batch([]) == []
    with pytest.raises(BatchSizeExceededError):
        service.execute_batch([{"operation": "add", "args": [1, 1]}])


# --- strict_validation -----------------------------------------------------


def test_strict_validation_accepts_exact_keys():
    service = CalculatorService(policy=OperationPolicy(strict_validation=True))
    results = service.execute_batch([{"operation": "add", "args": [1, 2]}])
    assert results == [{"ok": True, "value": 3}]


def test_strict_validation_rejects_extra_keys_per_item():
    service = CalculatorService(policy=OperationPolicy(strict_validation=True))
    results = service.execute_batch(
        [
            {"operation": "add", "args": [1, 2], "extra": 1},
            {"operation": "add", "args": [3, 4]},
        ]
    )
    assert results[0]["ok"] is False
    assert results[0]["error"]["type"] == "InvalidRequestError"
    assert results[1] == {"ok": True, "value": 7}


def test_strict_validation_still_enforces_base_rules():
    service = CalculatorService(policy=OperationPolicy(strict_validation=True))
    results = service.execute_batch([{"operation": "add"}])
    assert results[0]["ok"] is False
    assert results[0]["error"]["type"] == "InvalidRequestError"


def test_lenient_default_matches_strict_for_valid_request():
    lenient = CalculatorService()
    strict = CalculatorService(policy=OperationPolicy(strict_validation=True))
    payload = [{"operation": "add", "args": [5, 6]}]
    assert lenient.execute_batch(payload) == strict.execute_batch(payload)
