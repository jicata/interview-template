from fastapi import APIRouter

from app.features.products import handler
from app.features.products.schemas import ProductResponse

router = APIRouter(tags=['products'])


@router.get('/products', response_model=list[ProductResponse])
def list_products() -> list[ProductResponse]:
    """The product catalogue, with each product's pack size and current price."""
    return handler.list_products()
