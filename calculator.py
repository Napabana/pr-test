"""Compatibility facade for the calculator core.

The operation implementations now live in ``src/calc_core/operations.py``.
These re-exports preserve the original public API exactly.
"""

from calc_core.operations import add, clamp, divide, multiply, subtract

__all__ = ["add", "subtract", "multiply", "divide", "clamp"]