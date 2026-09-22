"""Registry mapping operation names to callables."""

from typing import Callable, Dict

from .errors import UnknownOperationError

Operation = Callable[..., object]


class OperationRegistry:
    """Store operations by name and resolve them back."""

    def __init__(self) -> None:
        self._operations: Dict[str, Operation] = {}

    def register(self, name: str, operation: Operation) -> None:
        """Register ``operation`` under ``name``."""
        self._operations[name] = operation

    def resolve(self, name: str) -> Operation:
        """Return the operation registered under ``name``.

        Raises UnknownOperationError if no such operation exists.
        """
        try:
            return self._operations[name]
        except KeyError:
            raise UnknownOperationError(name) from None