import app.db as _db  # noqa: F401 — triggers CSV load at startup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import hello, reorder

app = FastAPI(title='Interview Template API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(hello.router)
app.include_router(reorder.router)
