"""Exception types for the calculator core."""


class CalculatorError(Exception):
    """Base class for all calculator errors."""


class UnknownOperationError(CalculatorError):
    """Raised when an operation name cannot be resolved."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"unknown operation: {name}")


class InvalidRequestError(CalculatorError):
    """Raised when a batch request is malformed."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class OperationDisabledError(CalculatorError):
    """Raised when an operation is disabled by the active policy."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"operation disabled: {name}")


class BatchSizeExceededError(CalculatorError):
    """Raised when a batch exceeds the policy's maximum batch size."""

    def __init__(self, size: int, max_batch_size: int) -> None:
        self.size = size
        self.max_batch_size = max_batch_size
        super().__init__(
            f"batch size {size} exceeds maximum of {max_batch_size}"
        )