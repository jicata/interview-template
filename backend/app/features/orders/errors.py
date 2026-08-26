"""Domain errors for the orders feature.

One base class, so the transport layer can translate by category rather than by
enumeration. Nothing here knows about HTTP — `app/api/orders.py` owns the mapping
from these to status codes.
"""


class OrderError(Exception):
    """Base for every orders-feature domain error."""


class OrderNotFoundError(OrderError):
    pass


class OrderNotDraftError(OrderError):
    """An order that has already been placed cannot be built on."""


class ProductNotFoundError(OrderError):
    pass


class CustomerNotFoundError(OrderError):
    pass


class OrderLineNotFoundError(OrderError):
    pass


class PackSizeViolationError(OrderError):
    """The quantity is not a whole number of packs."""
