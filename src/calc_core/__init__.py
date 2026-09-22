"""Public API for the calculator core package.

Re-exports the five operations, the error types, the operation registry
and the high-level service so ``from calc_core import ...`` works.
"""

from . import operations
from .errors import (
    BatchSizeExceededError,
    CalculatorError,
    InvalidRequestError,
    OperationDisabledError,
    UnknownOperationError,
)
from .operations import add, clamp, divide, multiply, subtract
from .policy import OperationPolicy
from .registry import OperationRegistry
from .service import CalculatorService

__all__ = [
    "BatchSizeExceededError",
    "CalculatorError",
    "CalculatorService",
    "InvalidRequestError",
    "OperationDisabledError",
    "OperationPolicy",
    "OperationRegistry",
    "UnknownOperationError",
    "add",
    "clamp",
    "divide",
    "multiply",
    "operations",
    "subtract",
]