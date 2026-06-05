from fastapi import APIRouter

from app.features.hello import handler
from app.features.hello.schemas import HelloResponse

router = APIRouter()


@router.get('/hello', response_model=HelloResponse)
def hello(name: str = 'World') -> HelloResponse:
    return HelloResponse(message=handler.get_greeting(name))
