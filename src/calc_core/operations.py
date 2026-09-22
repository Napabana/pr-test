"""The five core calculator operations.

These functions preserve the behavior of the original top-level
``calculator.py`` implementation:

* ``divide(..., 0)`` raises ``ZeroDivisionError``.
* ``clamp`` raises ``ValueError`` when ``lower > upper``.
"""


def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Return the difference of two integers (a - b)."""
    return a - b


def multiply(a: int, b: int) -> int:
    """Return the product of two integers."""
    return a * b


def divide(a: int, b: int) -> float:
    """Return the quotient of two integers (a / b).

    Raises ZeroDivisionError if b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b


def clamp(value: int, lower: int, upper: int) -> int:
    """将 value 限制在 [lower, upper] 区间内；当 lower 大于 upper 时抛出 ValueError。"""
    if lower > upper:
        raise ValueError("lower must not exceed upper")
    return max(lower, min(value, upper))