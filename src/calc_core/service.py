"""High-level calculator service built on top of the registry."""

from typing import Iterable, Mapping, Optional

from . import operations
from .errors import (
    BatchSizeExceededError,
    InvalidRequestError,
    OperationDisabledError,
)
from .policy import DEFAULT_POLICY, OperationPolicy
from .registry import OperationRegistry


class CalculatorService:
    """Execute named arithmetic operations.

    A freshly constructed service has all five default operations
    registered: add, subtract, multiply, divide and clamp.

    Behavior is governed by an optional :class:`OperationPolicy`. The
    default policy preserves the original behavior: every registered
    operation is enabled, batches are unlimited and validation is lenient.
    """

    DEFAULT_OPERATIONS = {
        "add": operations.add,
        "subtract": operations.subtract,
        "multiply": operations.multiply,
        "divide": operations.divide,
        "clamp": operations.clamp,
    }

    def __init__(
        self,
        registry: Optional[OperationRegistry] = None,
        policy: Optional[OperationPolicy] = None,
    ) -> None:
        self.registry = registry if registry is not None else OperationRegistry()
        self.policy = policy if policy is not None else DEFAULT_POLICY
        for name, operation in self.DEFAULT_OPERATIONS.items():
            self.registry.register(name, operation)

    def execute(self, operation_name: str, *args: object) -> object:
        """Execute the operation registered under ``operation_name``."""
        operation = self.registry.resolve(operation_name)
        if not self.policy.is_operation_enabled(operation_name):
            raise OperationDisabledError(operation_name)
        return operation(*args)

    def _validate_request(self, request: object) -> tuple:
        """Return ``(operation_name, args)`` or raise InvalidRequestError."""
        if not isinstance(request, Mapping):
            raise InvalidRequestError(
                "request must be a mapping with 'operation' and 'args'"
            )
        if "operation" not in request or "args" not in request:
            raise InvalidRequestError(
                "request must contain 'operation' and 'args'"
            )
        if self.policy.strict_validation:
            extra = set(request.keys()) - {"operation", "args"}
            if extra:
                raise InvalidRequestError(
                    "request must contain exactly 'operation' and 'args'"
                )
        operation_name = request["operation"]
        if not isinstance(operation_name, str) or not operation_name:
            raise InvalidRequestError("request 'operation' must be a non-empty string")
        args = request["args"]
        if not isinstance(args, (list, tuple)):
            raise InvalidRequestError("request 'args' must be a list or tuple")
        return operation_name, args

    def execute_batch(self, requests: Iterable[object]) -> list:
        """Execute an ordered iterable of requests, one result per item.

        Each result is either ``{"ok": True, "value": ...}`` or
        ``{"ok": False, "error": {"type": ..., "message": ...}}``.
        A failing request never aborts the remaining requests.

        If the policy sets ``max_batch_size`` the batch is measured before
        processing: a batch larger than the limit raises
        :class:`BatchSizeExceededError` without producing results.
        """
        items = list(requests)
        if not self.policy.check_batch_size(len(items)):
            raise BatchSizeExceededError(len(items), self.policy.max_batch_size)
        results = []
        for request in items:
            try:
                operation_name, args = self._validate_request(request)
                value = self.execute(operation_name, *args)
            except Exception as exc:
                results.append(
                    {
                        "ok": False,
                        "error": {
                            "type": type(exc).__name__,
                            "message": str(exc),
                        },
                    }
                )
            else:
                results.append({"ok": True, "value": value})
        return results
