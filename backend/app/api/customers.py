from fastapi import APIRouter

from app.features.customers import handler
from app.features.customers.schemas import Customer

router = APIRouter()


@router.get('/customers', response_model=list[Customer])
def list_customers() -> list[Customer]:
    return handler.list_customers()
