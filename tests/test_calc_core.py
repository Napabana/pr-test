"""Focused tests for the new calc_core architecture."""

import pytest

from calc_core import (
    CalculatorError,
    CalculatorService,
    OperationRegistry,
    UnknownOperationError,
    add,
    clamp,
    divide,
    multiply,
    subtract,
)
from calc_core import operations


# --- operations module preserves behavior ---------------------------------


def test_operations_module_exposes_five_ops():
    assert operations.add(2, 3) == 5
    assert operations.subtract(5, 3) == 2
    assert operations.multiply(4, 3) == 12
    assert operations.divide(10, 2) == 5
    assert operations.clamp(5, 0, 10) == 5


def test_operations_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError, match="division by zero"):
        operations.divide(5, 0)


def test_operations_clamp_invalid_bounds_raises():
    with pytest.raises(ValueError, match="lower must not exceed upper"):
        operations.clamp(5, 10, 0)


# --- errors ----------------------------------------------------------------


def test_unknown_operation_error_is_calculator_error():
    assert issubclass(UnknownOperationError, CalculatorError)


def test_unknown_operation_error_carries_name():
    err = UnknownOperationError("nope")
    assert err.name == "nope"
    assert "nope" in str(err)


# --- registry --------------------------------------------------------------


def test_registry_register_and_resolve():
    registry = OperationRegistry()
    registry.register("add", add)
    assert registry.resolve("add") is add


def test_registry_unknown_name_raises_unknown_operation_error():
    registry = OperationRegistry()
    with pytest.raises(UnknownOperationError):
        registry.resolve("missing")


# --- service ---------------------------------------------------------------


def test_service_has_all_default_operations():
    service = CalculatorService()
    for name in ("add", "subtract", "multiply", "divide", "clamp"):
        assert service.registry.resolve(name) is not None


def test_service_execute_dispatches_by_name():
    service = CalculatorService()
    assert service.execute("add", 2, 3) == 5
    assert service.execute("subtract", 5, 3) == 2
    assert service.execute("multiply", 4, 3) == 12
    assert service.execute("divide", 7, 2) == 3.5
    assert service.execute("clamp", 42, 0, 10) == 10


def test_service_execute_unknown_operation_raises_unknown_operation_error():
    service = CalculatorService()
    with pytest.raises(UnknownOperationError):
        service.execute("does_not_exist", 1, 2)


def test_service_execute_preserves_divide_by_zero():
    service = CalculatorService()
    with pytest.raises(ZeroDivisionError):
        service.execute("divide", 5, 0)


# --- facade ----------------------------------------------------------------


def test_facade_reexports_operations():
    import calculator

    assert calculator.add is operations.add
    assert calculator.subtract is operations.subtract
    assert calculator.multiply is operations.multiply
    assert calculator.divide is operations.divide
    assert calculator.clamp is operations.clamp
