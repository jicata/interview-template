import app.db as _db  # noqa: F401 — triggers CSV load at startup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import hello, orders, products
from app.features.orders.errors import OrderError

app = FastAPI(title='Interview Template API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(hello.router)
app.include_router(products.router)
app.include_router(orders.router)

# Domain errors are translated once, here, rather than in a try/except per route.
app.add_exception_handler(OrderError, orders.order_error_handler)
