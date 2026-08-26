"""Order Builder business logic.

Reads go straight to `get_connection()`; every write goes through
`db.transaction()`, which holds a process-wide lock, commits on success and rolls
back on error. That is not optional here — there is one shared connection, so two
concurrent writers using it directly would commit each other's partial work.
"""
import sqlite3
from decimal import Decimal

from app import db
from app.features.orders import pricing, queries
from app.features.orders.errors import (
    CustomerNotFoundError,
    OrderLineNotFoundError,
    OrderNotDraftError,
    OrderNotFoundError,
    PackSizeViolationError,
    ProductNotFoundError,
)
from app.features.orders.schemas import OrderLineResponse, OrderResponse
from app.models.order import OrderStatus


def create_order(customer_id: int) -> OrderResponse:
    with db.transaction() as conn:
        if not queries.customer_exists(conn, customer_id):
            raise CustomerNotFoundError(f'No customer with id {customer_id}.')
        order_id = queries.insert_order(conn, customer_id)
        return _build_response(conn, order_id)


def get_order(order_id: int) -> OrderResponse:
    conn = db.get_connection()
    _require_order(conn, order_id)
    return _build_response(conn, order_id)


def add_order_line(order_id: int, product_id: int, quantity: int) -> OrderResponse:
    """Add units of a product to an order and return the recomputed order.

    A product already on the order has its existing line increased rather than
    gaining a second line. Otherwise two lines of 30 and one line of 60 would
    price differently for the same order, and the volume discount would depend on
    how the rep happened to type it in.
    """
    with db.transaction() as conn:
        order = _require_draft(conn, order_id)
        product = _require_product(conn, product_id)
        _require_pack_multiple(quantity, product)

        existing = queries.find_order_line_for_product(conn, order['id'], product_id)
        if existing is None:
            # The product's current price becomes this line's charged price, and
            # stays put from here on — that is what order_lines.unit_price means.
            queries.insert_order_line(
                conn, order['id'], product_id, quantity, float(product['unit_price'])
            )
        else:
            queries.update_order_line_quantity(
                conn, existing['id'], existing['quantity'] + quantity
            )

        return _build_response(conn, order['id'])


def remove_order_line(order_id: int, line_id: int) -> OrderResponse:
    with db.transaction() as conn:
        order = _require_draft(conn, order_id)
        if queries.find_order_line(conn, order['id'], line_id) is None:
            raise OrderLineNotFoundError(
                f'Order {order_id} has no line with id {line_id}.'
            )
        queries.delete_order_line(conn, line_id)
        return _build_response(conn, order['id'])


def _require_order(conn: sqlite3.Connection, order_id: int) -> sqlite3.Row:
    order = queries.find_order(conn, order_id)
    if order is None:
        raise OrderNotFoundError(f'No order with id {order_id}.')
    return order


def _require_draft(conn: sqlite3.Connection, order_id: int) -> sqlite3.Row:
    order = _require_order(conn, order_id)
    if order['status'] != OrderStatus.DRAFT:
        raise OrderNotDraftError(
            f'Order {order_id} is {order["status"]} and can no longer be changed.'
        )
    return order


def _require_product(conn: sqlite3.Connection, product_id: int) -> sqlite3.Row:
    product = queries.find_product(conn, product_id)
    if product is None:
        raise ProductNotFoundError(f'No product with id {product_id}.')
    return product


def _require_pack_multiple(quantity: int, product: sqlite3.Row) -> None:
    pack_size = product['pack_size']
    if quantity % pack_size != 0:
        raise PackSizeViolationError(
            f'{product["name"]} ships in packs of {pack_size}, so {quantity} '
            f'cannot be ordered. Use a multiple of {pack_size}.'
        )


def _build_response(conn: sqlite3.Connection, order_id: int) -> OrderResponse:
    order = _require_order(conn, order_id)
    lines = []
    priced_lines = []
    for row in queries.list_order_lines(conn, order_id):
        priced = pricing.price_line(_to_decimal(row['unit_price']), row['quantity'])
        priced_lines.append(priced)
        lines.append(
            OrderLineResponse(
                id=row['id'],
                product_id=row['product_id'],
                product_name=row['product_name'],
                quantity=priced.quantity,
                unit_price=float(priced.unit_price),
                discount_rate=float(priced.discount_rate),
                discount_amount=float(priced.discount_amount),
                line_total=float(priced.line_total),
            )
        )
    return OrderResponse(
        id=order['id'],
        customer_id=order['customer_id'],
        status=OrderStatus(order['status']),
        order_date=order['order_date'],
        lines=lines,
        order_total=float(pricing.order_total(priced_lines)),
    )


def _to_decimal(unit_price: float) -> Decimal:
    """Cross from the column's REAL to exact arithmetic.

    Via `str`, never `Decimal(float)` — the latter carries the float's binary
    error into a type chosen to avoid exactly that.
    """
    return Decimal(str(unit_price))
