from app.features.customers import queries
from app.features.customers.schemas import Customer


def list_customers() -> list[Customer]:
    return [Customer.model_validate(row) for row in queries.all_customers()]
