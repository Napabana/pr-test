"""Immutable runtime policy for the calculator service.

The policy describes which operations are enabled and how batches are
validated. It is a frozen dataclass so a policy instance can be shared
safely: all state is instance state owned by the service, never
module-level mutable state.
"""

from dataclasses import dataclass
from typing import FrozenSet, Optional


@dataclass(frozen=True)
class OperationPolicy:
    """Describe the runtime behavior of a :class:`CalculatorService`.

    Attributes:
        enabled_operations: frozenset of allowed operation names, or
            ``None`` to allow every registered operation.
        max_batch_size: maximum number of requests accepted by
            ``execute_batch``, or ``None`` for no limit.
        strict_validation: when ``True`` each batch request must contain
            exactly the keys ``"operation"`` and ``"args"``.
    """

    enabled_operations: Optional[FrozenSet[str]] = None
    max_batch_size: Optional[int] = None
    strict_validation: bool = False

    def is_operation_enabled(self, operation_name: str) -> bool:
        """Return whether ``operation_name`` is allowed by this policy."""
        if self.enabled_operations is None:
            return True
        return operation_name in self.enabled_operations

    def check_batch_size(self, size: int) -> bool:
        """Return whether a batch of ``size`` items is within the limit.

        ``size == max_batch_size`` is allowed; only a larger batch is
        rejected. ``None`` means no limit.
        """
        if self.max_batch_size is None:
            return True
        return size <= self.max_batch_size


DEFAULT_POLICY = OperationPolicy()
